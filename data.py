from PyQt4 import QtCore
from .common import *
"""DataChannels (DCs) are a series of instructions that start with either a database or antenna DCO, and process the DF in a series of operations. 
DCs are composed of a chain of DataChannelOperations (DCOs), each one of which can be considered an elementary operation.
Each class of DCO correspond to a certain kind of manipulation (e.g., filter rows; or select columns). 
Each particular instance of a DCO correspond to a specific manipulation (e.g., filter out all rows in which column A contains the value 0); 
 a DCO instance is identified by its key (in the example, 'A!=0'). 
Every DC also has a key, which is the concatenation of the keys of its DCOs, preceded by their class name (e.g. "database:db1 |>filter:A!=0").

The memory tree is a prefix-tree-like structure, whose components are MemoryUnit (MU) objects.
Just under the root, you have MUs for the databases and antenna DCOs, which are basically equivalent. 
These MUs store dataframes (DFs) in their .data attribute. 
The memory_tree start the MUs with primary data (DB and antennas). 
At the end of the day, these MUs will have children MUs for any DCOs that was applied to that primary DF, 
 and those MUs will also have children and so on until all operations in any existing DC are covered.


When a DC is run, by calling its out() method, the memory_tree is traversed, and extended if necessary with more MUs, to arrive to the desired result.
If all operations were already computed previously, running out() on a DC will simply determine which node of the memory tree (which MU) is the endpoint.
This MU will be 'linked' to this DC.
Now; certain DCO classes correspond to 'heavy' operations. Treedex tries to execute these only once (for any specific input DF). 
For heavy DCOs, their corresponding MU will survive after the out() call is over, and they will maintain the computed DF in their .data attribute.
For other, 'light' DCO classes, their MUs are instead created on the fly, but their data is not stored. 
 These light MUs are kept alive only as long as they have important descendent MUs (corresponding to a heavy DCO, or to the final result of a DC).
 Otherwise, they are trimmed off the memory_tree.
MU that are endpoints of any DC are always maintained.

This is how out() is executed, in detail:
- In a first round, the program parse down the memory tree, searching the MU which is closest to the final result of the DC (example of a DC: "database:db1 |>filter:A!=0").
 Let's pretend this is the first out() call in Treedex. The memory tree is parsed downs just 1 step, until the MU of the database db1 is reached.
 The program checks whether this MU has a child MU corresponding to the 'filter:A!=0' operation.
 Since there is no such child, at this point the first round ends, keeping a pointer to this MU (let's call it CMU) and its stored DF. 

- In a second round, the program restarts from the CMU. It will compute the second operation (filter in the example), giving some result DF.
 It will thus create a MU child of the CMU, which may be a heavy or light MU depending on the operation.
 It will then cycle again to the third operation and so on, restarting from the newly created MU and computed DF.


The DC/MU model supports also dynamic changes in the DCs, or even changes in the starting data (antennas/databases).
-If a DC is modified (either by adding/removing a DCO, or by changing the parameters of one), a PyQt signal is emitted by the DC: signal_dc_changed
 This is (normally) connected to its out() method so that this function is invoked. 
 When this happens, its endpoint MU is recomputed based on the new structure/parameters, and linked to the DC.
 The old endpoint MU may now host a chain of MUs that are not useful anymore and may be dropped. Thus a 'trim_memory' procedure is invoked on the old MU.
  Its branch is trimmed off, until the end of the branch is a MU corresponding to a heavy operation, and/or a MU which is linked to some other active DC.
-If a database/antenna is modified (e.g. another file is loaded and saved with the same name; or the active node selection changes), 
 then the memory tree is traversed down from its MU, and all DCs linked to any of those MU emit a PyQt signal: signal_value_changed
 This signal is also (normally) connected to its out() method so that it's invoked. 
 Traversing down the tree and the triggering the signal_value_changed of linked DCs is performed in the following way. 
  There is an attribute of MUs called force_recompute. When this is found to be set to True during a out() call, a DCO is computed even if 
  it would appear that there is already a pre-computed MU available in the memory tree. 
  Thus when a database/antenna is modified, simply, the force_recompute attribute of the direct children (as well as its dependants, explained later) of 
  the MU corresponding to that database/antenna is set to True, and the signal_value_changed of all DCs linked anywhere below that MU in the memory tree is emitted.
 Some operations depend on more than an input: for example, the database 'join' operation. This would be practically a child of two parents in the memory tree; 
 but MUs in treedex are kept with a single parent. Instead, MUs may have additional 'dependants'. 
 Like children MUs, dependants must be recomputed if a change occurred in the self MU (called dependency).


There is one factor that complicates the process.
 Some DCOs do not perform computations per se, but instead they set up or retrieve variables. These are called ManagementDCOs.
 The DCO "cache", for example, will create a pointer to a certain DF under a certain name.
 DCO "retrieve", given one such name, returns the previously cached DF. 
 The other ManagementDCOs are "define" and "call", to save and recall DC (instead of their results, which is performed by cache/retrieve);
 and lastly, "var", which sets up simple string variables that can be used inside the parameters of DCOs.

All these ManagementDCOs work on a certain namespace, which corresponds to a certain "DC_container". 
 Normally, a ManagementDCO acts on its direct DC parent (a DC is also a DC_container). 
 Nevertheless, there is also a global namespace ('master'), and also any number of lower level namespaces.
 These are created when a specific DCO class is instantiated: the DCO "group". This is both a DCO, and a DC at the same time.
 As the name suggest, a DCO group conveniently group any number of DCOs that are contained in it.

Regarding the possibilities of changes in database/antenna data or in the structure of any DC, and the DCO caches/retrieve model; 
 the MU corresponding to cache/retrieve DCOs are actually a subtype called PointerUnit (PU). PUs are fundamentally pointers to a MU. 
 PUs are created by a DCO cache; DCO retrieve returns one existing PU. 
 All PUs have no parent, but they have a dependency: the MU they point to.
 PUs may have any number of dependants, which correspond to every DCO coming directly downstream of a DCO_retrieve in any DC.
 In this way, whenever a database upstream of a DCO_cache changes, or if the structure upstream of a DCO_cache changes, 
  the relevant DCs will be recomputed through a out() call. """

DCO_types_to_cache=set(['aggregate', 'pgls', 'trace', 'database', 'antenna',  'root', 'null']) #'join',

# class DataFrame(pd.DataFrame):
#   """ Extension of pandas dataframe. Every instance of this is an homogenous data structure (same columns), typically coming from the same source.
# Init with:
#   -name:    an identifier string that will be used to fetch this dataframe   --> then obtainable by calling self.name()
#   -data:    a pd.DataFrame   (may be returned, for example, by pd.read_csv
#   -node_field:  optionally, the column name that points to the node name. 
# After init, every DataFrame must have a 'Node' column 
# """
#   def __init__(self, data=None, name=None, node_field=None, **kargs):
#     pd.DataFrame.__init__(self, data=data, **kargs)
#     if not name: raise Exception, "ERROR Treedex DataFrame cannot have an empty name!"
#     self._name=name
#     if not node_field is None and node_field!='Node':        
#       if self.index.name==node_field: self.reset_index(inplace=True)
#       self.rename(columns={node_field:'Node'}, inplace=True)
#     # test whether Node is there
    
#     if not 'Node' in self.columns: 
#       if self.index.name=='Node': pass 
#       else: raise Exception, "ERROR Treedex DataFrame {}: the column for 'Node' was not found: {}".format(name, node_field)
#   def name(self): return self._name

  

def are_identical_dataframes(df1, df2):
  # write('checking are same dataframe?', 1)
  # write(df1.head(), 1, how='yellow')
  # if  len(df1)>6:  write(df1.tail(), 1, how='yellow')
  # write(df2.head(), 1, how='magenta')
  # if len(df2)>6:   write(df2.tail(), 1, how='magenta')
  #checking dimensions  of index and columns
  if df1 is None and df2 is None:       return True
  elif df1 is None and not df2 is None: return False
  elif df2 is None and not df1 is None: return False
  return df1.equals(df2) # trying to solve all next cases with this pandas function
  
  # if len(df1.index)!=len(df2.index):             return False
  # if len(df1.columns)!=len(df2.columns):         return False
  # #write('Dimensions are the same', 1, how='reverse')
  # #checking columns
  # for icol, col1 in enumerate(df1.columns):
  #   if df2.columns[icol]!=col1:                  
  #     #write('Columns are different!', 1, how='reverse')
  #     return False
  # #checking index of each row, and each item in the DF
  # for irow, kindex  in enumerate(df1.index):
  #   if df2.index[irow]!=kindex:                  
  #     #write('Indexes are different! {} {} {}'.format(irow, kindex, df2.index[irow]), 1, how='reverse')
  #     return False
  #   for icol, _ in enumerate(df1.columns):
  #     e1=df1.iat[irow,icol]
  #     e2=df2.iat[irow,icol]
  #     #write(e1, 1, how='yellow')
  #     #write(e2, 1, how='magenta')
  #     if  (e1!=e2)     and not all( [pd.isnull(e) for e in (e1,e2)]  ) :   #isnull because otherwise nan!=nan makes true
  #       #write('Elements are different! {} {} '.format(df1.iat[irow,icol], df2.iat[irow,icol]), 1, how='reverse')
  #       return False
  # return True   
 

forbidden_chars=set(':,=><&$')
def check_forbidden_characters(txt, chars=forbidden_chars):
  """Returns True if everything is ok; returns False if any of the forbidden characters is detected in the input txt """
  for c in txt: 
    if c in chars: return False
  return True

def replace_forbidden_characters(txt, chars=forbidden_chars, to='_'):
  """Returns True if everything is ok; returns False if any of the forbidden characters is detected in the input txt """
  return ''.join([c  if not c in chars else to    for c in txt])

###################################################################################################################
NoData=object()
class MemoryUnit(object):
  """ Base of treedata structure. Each one correspond to a DCO"""
  def __init__(self, name, data=NoData, parent=None):
    self.name=name
    self.parent=parent
    self.children={}  # name to data unit
    self.dependencies=set()
    self.dependants=set()
    self.pointers=set()
    self.data=data
    self.count_requested=0
    self.DCs=set()
    if not parent is None:      parent.children[self.name]=self
    self.force_recompute=False #debug

  # @property
  # def force_recompute(self):   return True
  # @force_recompute.setter  #just so the self.parameters=None in the DCO init will not make python freak out
  # def force_recompute(self, value): 
  #   write( (self.name, ' trying to set force recompute to', value),   1, how='blue,reverse')
  #   pass
  
  ## note: call dc.link_to_memory_unit instead
  def add_dc(self, dc):       self.DCs.add(dc)
  def remove_dc(self, dc):    self.DCs.remove(dc)
  def has_dc(self, dc):       return dc in self.DCs

  # def add_dependant(self, pu): 
  #   #print 'ADD DEPENDANT self= ', self.name, self, ' dependant= ', pu.name, pu
  #   self.dependants.add(pu)
  #   pu.dependencies.add(self)

  # def remove_dependant(self, pu): 
  #   self.dependants.remove(pu)
  #   pu.dependencies.remove(self)

  def traverse_tree(self, include_dependants=True):
    stack = [self]
    while stack:
      node = stack.pop()
      yield node
      if not isinstance(node, PointerUnit):
        for child in node.children.values():   stack.append(child)
      if include_dependants:
        for dep in node.dependants:          stack.append(dep)
        if not isinstance(node, PointerUnit):
          for pu in node.pointers:
            stack.append(pu)


  def trigger_recompute_in_downstream_DCs(self):
    """ "Invoked on a Database memory unit when this is overwritten with a different value"""
    if not 'Highlighted' in self.name:   write('Trigger recompute start', 1)
    dc_triggered=set()
    for mu in self.traverse_tree():      
      if not 'Highlighted' in self.name:  write('Trigger traversing: '+mu.name, 1)
      if isinstance(mu, PointerUnit):
        dcs=[i for i in mu.data_channels]
      else:
        dcs=[i for i in mu.DCs]

      for dc in dcs:
        print '?trigger dc ->', dc
        if not dc in dc_triggered:
          if not 'Highlighted' in self.name:      
            write('** Trigger recompute MU:{} -> id{} par:{} \ndc:{}'.format(self.name, id(dc), dc.container, dc), 1, how='magenta')
          #dc.signal_value_changed.emit()
          dc.recompute_dc=True
          dc.out( dc_triggered=dc_triggered  )
          #dc_triggered.add(dc)

    #   all_dcs.update(n.DCs)
    # for dc in all_dcs:           
    #  dc.signal_value_changed.emit()  # this will force out being called if important
    # for c in self.children.values():        
    #   c.trigger_recompute_in_downstream_DCs()
    # for d in [i for i in self.dependants]:  
    #   d.trigger_recompute_in_downstream_DCs()

  #untrimmable=set(['root:','null:'])
  def trim_memory(self):
    """ Start from this mu, goes up and down and remove useless MUs from the memory tree. 
Useless means: MU does not have any saved data, not even in any children or further down relatives.
To qualify as having save data, the MU must be of the appropriate name, defined in MemoryManager
Having a linked DC also qualifies.
This function is used recursively. It returns True when trimming occurred"""
    #write('trim memory start from {}'.format(self.summary()), 1, how='yellow,reverse')
    all_children_were_trimmed=  all([  c.trim_memory()  for c in       self.children.values()  ])  #if no children, this is true
    all_dependants_were_trimmed=all([  d.trim_memory()  for d in [i for i in self.dependants]  ])       #same here #avoiding changed size during iteration
    all_pointers_were_trimmed=  all([  p.trim_pointer() for p in [i for i in self.pointers]    ])       #same here #avoiding changed size during iteration

    if all_children_were_trimmed and all_dependants_were_trimmed and all_pointers_were_trimmed:
      dco_name=self.name[:self.name.index(':')]
      trim_this=  not dco_name in DCO_types_to_cache and \
                   not self.DCs 
      #write( 'trimThis:{} {}'.format(trim_this, self), 1, how='yellow')
      if trim_this: 
        # if isinstance(self, PointerUnit):
        #   self.pointed.dependants.remove(self)
        #   self.pointed.trim_memory()
        # else:
        if not isinstance(self, ErrorUnit):  self.data=NoData
        for dup in self.dependencies: dup.dependants.remove(self)
        if not self.parent is None: #only case: errorunit  # which has no parent but may have children;    and pointerunit
          if self.name in self.parent.children:
            del self.parent.children[ self.name ]
          else: pass          
          self.parent.trim_memory()
        return True

  # def add_child(self, unit):
  #   if unit.name in self.children: raise Exception, "ERROR adding unit, parent has already unit with same name"
  #   unit.parent=self

  def summary(self, level=0, dep=False):
    o='{I:<34} D:{d} R:{r} DC:[{ds}]'.format(  #d.down:[{dd:<25}] d.up [{du:25}]  C:{c:<5}
      #dd=' & '.join([x.name for x in self.dependants]), 
      #du=' & '.join([x.name for x in self.dependencies]),   
      r=int(self.force_recompute),
      I='{s}{x}{n}{e}'.format(s=' '*level, n=self.name, x='|' if not dep else '~', e='   ' if not isinstance(self, ErrorUnit) else ' E!'), 
      d=int(not self.data is NoData), ds='] # ['.join([str(x) for x in self.DCs]), c=self.count_requested)
    for u in sorted(self.children.values(), key=lambda x:x.name):     o+='\n'+u.summary(level+1)
    for d in sorted(self.dependants, key=lambda x:x.name):            o+='\n'+d.summary(level+1, dep=True)     
    return o
  __repr__=summary

class PointerUnit(object): #MemoryUnit):
  """This is the MU built by DCO_cache. It never stores data. 
  A PointerUnit (PU) is stored as a value in the .caches dictionary of a DC_container. 
  The key in that dictionary is the variable name in the DCO_cache.
  The fundamental property of a PU is the only value in its .dependencies set attribute. 
  This value is the MU to which this PU points to.
  """
  def __init__(self, name, pointed):
    #MemoryUnit.__init__(self, name=name, parent=None
    self.name=name
    self.pointed=pointed      #memory unit
    self.data_channels=set()  #DC that used this PU while executing
    self.dependants=set()     #e.g. DCO_join that wants what this is pointing to
    self.pointed.pointers.add(self)

    #self.parent=None
    #self.children={}          # always empty 
    #self.dependencies=set() #actually only one value, the linked MU
    #self.data=False
    #self.count_requested=0
    #self.DCs=None
    #if not parent is None:      parent.children[self.name]=self
    #self.force_recompute=False 

  def summary(self, level=0, dep=False):
    o='{I:<34}       R:{r} ->DC:[{ds}]'.format(  
      r=int(self.force_recompute),
      I='{s}{x}{n}{e}'.format(s=' '*level, n=self.name, x='|' if not dep else '~', e='   ' if not isinstance(self, ErrorUnit) else ' E!'), 
      ds='} # {'.join([str(x) for x in self.data_channels]))
    for d in sorted(self.dependants, key=lambda x:x.name):            o+='\n'+d.summary(level+1, dep=True)     
    return o
  __repr__=summary

  def trim_pointer(self):
    all_dependants_were_trimmed=all([  d.trim_memory() for d in [i for i in self.dependants]  ])       #same here #avoiding changed size during iteration
    if all_dependants_were_trimmed and not self.data_channels:
      self.pointed.pointers.remove(self)
      return True


  # @property
  # def data(self):        return [i for i in self.dependencies][0].data #there's always only one dependency for pointerunit
  # @data.setter  
  # def data(self, value): 
  #   if not value is NoData: raise Exception   #the .value=noData is happening when this unit is trimmed. if anywhere else, something's wrong

import traceback
class ErrorUnit(MemoryUnit):
  """If a DC ends up linked to this, something bad happened. 
  """
  def __init__(self, name, parent, dco, exception):
    write('ERROR during dco {} index {} err={}'.format(dco, dco.dc_index, exception), 1, how='reverse,red')
    #write(traceback.format_exc(), 1, how='red')
    #MemoryUnit.__init__(self, name=name, parent=None
    self.name=name 
    self.parent=parent
    self.children={}  # name to data unit
    self.dependencies=set() 
    self.dependants=set()
    #self.data=data
    self.pointers=set()
    self.count_requested=0
    self.DCs=set()  
    if not parent is None:      parent.children[self.name]=self
    self.error=(dco, exception)    
    self.force_recompute=False 

  @property
  def data(self):        return None
  @data.setter  
  def data(self, value):  #   if not value is NoData: 
    raise Exception

###################################################################################################################
class DC_container(object):
  """ Basically a namespace. It stores:
    .caches    To store pre-computed dataframes. Written by DCO_cache,  read by DCO_retrieve
      k:     the parameter (variable name) in a DCO_cache 
      value: a PointerUnit instance, linking the right MU in the memory tree (through the .dependencies attribute of the PU).
    .defines   To define custom functions.       Written by DCO_define, read by DCO_call
      k:     the parameter (variable name) in a DCO_define
      value: a string, which is the key for the DC defined as a function
    .variables To define variables usable in DCOs. Written by DCO_var, read by any subsequent DCO in the DC.
      k:     the parameter (variable name) in a DCO_define
      value: any string.   """
  def __init__(self):     self.reset_memory()
  def reset_memory(self): 
    #print 'RESET MEMORY OF DCC '
    self.caches={}        #name -> MemoryUnit
    self.defines={}       #name -> DC key  (string)
    self.variables={}     #name -> value   (string)
  
  def save_cache(self, var_name, pu):        
    # write('saveCache     var={v} DC_container type={t} str={s}  df={rs}x{cs}'.format(v=var_name, t=type(self), s=str(self), 
    #    d=(pu.data.tail() if not (pu.data is NoData or pu.data is None) else pu.data), 
    #     rs=(len(pu.data)          if not (pu.data is NoData or pu.data is None) else pu.data),
    #     cs=(len(pu.data.columns)  if not (pu.data is NoData or pu.data is None) else pu.data)), 1, how='red,reverse')
    self.caches[var_name]=pu
  def has_cache(self, var_name):             return var_name in self.caches
  def retrieve_cache(self, var_name):        
    pu=self.caches[var_name]
    # write('retrieveCache var={v} DC_container type={t} str={s}  df={rs}x{cs}'.format(v=var_name, t=type(self), s=str(self), 
    #    d=(pu.data.tail() if not (pu.data is NoData or pu.data is None) else pu.data), 
    #     rs=(len(pu.data)           if not (pu.data is NoData or pu.data is None) else pu.data),
    #     cs=(len(pu.data.columns)   if not (pu.data is NoData or pu.data is None) else pu.data)), 1, how='red,reverse')
    return pu
  def save_define(self, var_name, dc_key):   
    write('SAVE DEFINE {} kEY="{}"'.format(var_name, dc_key), 1, how='magenta,reverse,blink')
    self.defines[var_name]=dc_key
  def has_define(self, var_name):            return var_name in self.defines
  def retrieve_define(self, var_name):       return self.defines[var_name]
  def save_var(self, var_name, s):           self.variables[var_name]=s
  def has_var(self, var_name):               return var_name in self.variables
  def retrieve_var(self, var_name):          return self.variables[var_name]

###################################################################################################################
class DataChannel(QtCore.QObject, DC_container):
  """ Chain of manipulators (type: DataChannelOperation) to go from a DataFrame to any other.
Init with:
  -container:  MasterContainer, or any other DC_container (even another DC)
  -chain:      optional, list of instances of DataChannelOperation subclasses. The first one MUST be DCO_database/DCO_pointer
  -from_key:   alternative to chain to populate. Give a DC key to automatically create the corresponding DCOs and append them to self.chain.
The chain can also be populated with self.append(DCO) or self.insert(i, DCO), or shrinked by self.pop(i) 
Main method: self.out()  --> this runs all the operations in order and output a pd.DataFrame or pd.DataSeries
Two signals:
  .signal_dc_changed      This is emitted when the DC structure changes, or any of its components change
  .signal_value_changed   This is emitted when the output of the DC may be altered due to other reasons; e.g., the starting database was modified
Use self.muted=True to manipulate a DC without the signals being emitted; then restore it to self.muted=False.
Normally these two signals are connected to self.out;  use auto_update=False to avoid this
  """
  signal_dc_changed=   QtCore.pyqtSignal()   #when structure is modified
  signal_value_changed=QtCore.pyqtSignal()   #when antennas are present, and selections changed; not emitted when signal_dc_changed (although out value has changed)
  dco_separator_char=' |>'
  def __init__(self, container, chain=None, from_key=None, auto_update=True): 
    QtCore.QObject.__init__(self)
    DC_container.__init__(self)
    self.container=container  # if not isinstance(container, MasterContainer) else container.data() # pointing to MemoryManager instead
    self.reset()
    self.memory_unit=None
    self.recompute_dc=False
    self.pointers_retrieved=set()    
    self.muted=False
    if   not chain    is None: self.chain=chain
    elif not from_key is None: self.build_from_key(from_key)
    if auto_update:
      self.signal_dc_changed.connect(self.force_out)
    #   self.signal_value_changed.connect(self.out)
    
    
  def force_out(self):       self.recompute_dc=True; return self.out()
  def __iter__(self):        return self.chain.__iter__()
  def __len__(self):         return self.chain.__len__()

  def reset(self):
    self.locked={} #index to state;   state=1 --> not modifiable and not removable;       state=2 --> not removable
    self.chain=[]
  
  # def link_to_memory_unit(self, mu):
  #   """ Executed at the end of self.out(). This DC is linked to a certain MU in the memory tree. 
  #   If this DC was already linked to some other MU x, then a process of memory trimming is initiated starting from the MU x. 
  #   """
  #   previous_mu=None
  #   if not self.memory_unit is None: 
  #     if self.memory_unit is mu: return 
  #     write('unlinking DC: {}\nfrom MU: {}'.format(self, self.memory_unit.name), 1, how='blue')
  #     previous_mu=self.memory_unit
  #     previous_mu.remove_dc(self)

  #   if not mu is None:
  #     if mu.name=='root:':          mu=mu.children['null:']
  #     write('linking DC:   {}\nto   MU: {}'.format(self, mu.name if not mu is None else None), 1, how='blue,reverse')
  #     mu.add_dc(self)
  #     self.memory_unit=mu

  #   if previous_mu:  
  #     previous_mu.trim_memory()
  #     ### trim PUs?????

  # def unlink_from_memory_unit(self): self.link_to_memory_unit(mu=None)

  def build_from_key(self, from_key):    
    write('build from k "{}"'.format(from_key), 1, how='magenta')
    s=from_key
    while s:
      try:
        ## for every cycle we decide: index_start, index_end referred to the parameters string  (both included)
        ## next_start for reducing s for next cycle
        dco_name=   s[:s.index(':')]          #s.split(':')[0]
        dco_class=  DCO_name2class[dco_name]
        if issubclass(dco_class, DCO_group) and not issubclass(dco_class, DCO_smart): 
        #if dco_name in self.group_like_DCOs:
          index_start=len(dco_name)+1   #after :[
          par_open, par_close=1, 0
          index_end=None
          for index in range(index_start, len(s)):  #making sure to catch the correct closing parenthesis
            if  s[index:index+len(self.dco_separator_char)+1]==']'+self.dco_separator_char \
             or s[index:index+1]==']':               
              par_close+=1              
            elif  s[index:index+len(self.dco_separator_char)+1]==self.dco_separator_char+'[':      
              par_open+=1
            if par_close==par_open:  
              index_end=index
              #next_start=index_end + 2 + len(self.dco_separator_char)  # if s is shorter will result in empty string later, which is ok
              break
          if index_end is None: raise Exception, "ERROR wrong key syntax! Unmatched left parenthesis!"             

        else:
          index_start=len(dco_name)+1  #after :
          index_end= s.find(self.dco_separator_char)  -1
          if index_end==-2: index_end=len(s)
        next_start=index_end + 1 + len(self.dco_separator_char)
        parameters=s[index_start:index_end+1]
        dco_class=  DCO_name2class[dco_name]        
        dco= dco_class(parameters)
        self.append(dco, no_emit=True)
        s=s[next_start:]
      except:           
        write("DataChannel ERROR initializing invalid Key: {k}".format(k=from_key), 1, how='red,reverse')
        raise 
    #if self.chain: self.notify_modification()  #catching up with signal emission which we skipped earlier

  def master(self):
    """ returns a pointer to the treedex MasterContainer"""
    p=self.container
    while not p.container is None: p=p.container
    return p

  def set_lock(self, index, state=1):
    """ Lock the DCO with this index. A locked DCO cannot be modified in the GUI."""
    if not state and index in self.locked:     del self.locked[index]
    else:                                      self.locked[index]=state

  def is_locked(self, index):       return index in self.locked
  def is_modifiable(self, index):   return not index in self.locked or self.locked[index]==2

  def key_for_copy(self):
    """ The key() method returns a string for computing. The key_for_copy() returns a key useful for copying.
    Differences: - for the DCO_smart components    
                 - and for components that do not like to be copied (DCO_gui)

    """
    return self.dco_separator_char.join([dco.key()  if not isinstance(dco, DCO_smart) else dco.unexpanded_key()    for dco in self.chain  if dco.copiable] )    

  def copy(self, index_start=0, index_end=None, keep_lock=False, auto_update=True):
    """ Return a copy of this DC. Optionally provide slicing indexes start and end (0-based, included)
    With option keep_lock, the DCO which are locked will retain this property (i.e., read-only)"""
    k=self.key_for_copy()
    if index_end is None:   index_end=len(self)-1
    if 1: #elif index_start:       
      splt=k.split(self.dco_separator_char)[index_start:index_end+1]
      k=self.dco_separator_char.join( splt )
      #print 'copy', index_start, index_end, splt, k
    dc=DataChannel(self.container, from_key=k, auto_update=auto_update)
    if keep_lock:
      for i in self.locked:
        if i>=index_start and i<=index_end:  dc.set_lock(i+index_start)   
    return dc

  def out(self, dc_triggered=None): #, restart=None, link_memory_unit=True, return_mu=False): 
    """ Main function of DC. See doc at the top of data.py for explanations.
  Normally returns a pd.DataFrame or DataSeries;   or None
  With return_mu==True, instead it returns (df, mu), where mu is the final MemoryUnit reached in the memory_tree.
  At the end of out(), that mu (even if not returned) is normally linked to this DC. Use link_memory_unit=False to avoid this.
  You can provide a (df,mu) tuple as restart argument; in this case, this is equivalent to this DC being concatenated to the DC that has output such (df,mu)
  """
    if not self.recompute_dc and not self.memory_unit is None:
      mu=self.memory_unit
      write('out - using linked memory unit for KEY={k} -> {rs} x {cs}'.format(k=self.key(),
        rs=(len(mu.data)           if not (mu.data is NoData or mu.data is None) else mu.data),
        cs=(len(mu.data.columns)   if not (mu.data is NoData or mu.data is None) else mu.data)  ), 1, how='reverse')
      #if 'ilter:in_inpu' in self.key():        print 'LINKEDOUT=', self.memory_unit.data
      return self.memory_unit.data
    #value_changed=False
    value_changed=None 
    if dc_triggered is None: dc_triggered=set()
    else:   value_changed=True                #when out() is called because of a retrigger, let's assume a change happened (for DC containing only DCO_retrieve)
    if not self.chain:                    return None  ##

    mm=self.master().data()
    root=mm.memory_tree
    mu=root
    df=None
    write('out called with KEY={k}'.format(k=self.key()), 1, how='reverse') #r=not restart is None, l=link_memory_unit, rm=return_mu,  restart={r} link={l} return_mu={rm}; 
    run_chain= [dco    for dco in self.chain    if not dco.skip_this()] 

    #write('BEFORE OUT of {k}\n container: cache={c} vars={v} defines={d}\nroot memory: \n{m}'.format(d=self.defines, c=self.caches, v=self.variables, m=root, k=self.key()), 1, how='yellow')
    #if not restart is None:  df, mu=restart    # useful for DCO_group

    previous_pointers=set([p for p in self.pointers_retrieved])
    for p in previous_pointers:      p.data_channels.remove(self)
    self.pointers_retrieved=set()    
    self.pointers_to_trigger=set()

    cmu=mu         #cmu= last mu with .data stored
    cmu_i=-1       #index of DCO linked to last cmu
    first_i=0
    while first_i<len(run_chain):
      dco=run_chain[first_i]
      #write('     within first round -> {} {}'.format(first_i, dco), 1)
      #dco.dc_index=first_i
      if   isinstance(dco, ManagementDCO):
        df, mu=dco.manage_dataframe(df, mu, self)    
        ## DCO_cache: if overwriting something, will add to self.pointers_to_trigger    
        ## DCO_retrieve:  every pu added to pointers_retrieved
        if not mu.data is NoData: cmu=mu; cmu_i=first_i
      elif isinstance(dco, ExtensionDCO):  
        run_chain.pop(first_i)
        dco.extend_run_chain(run_chain, first_i)
        continue        #restart next cycle from same first_i
      elif isinstance(mu, ErrorUnit):         pass
      elif isinstance(dco, VerificationDCO):  pass #df, mu=dco.channel_dataframe(df, mu)    #in this case df,mu in input are the same as in output 
      else:
        ## is memory tree already available? Note that memory units may be there but no data stored
        k=dco.interpreted_key(df=None)  # this will parse up self.container looking for variables BUT it will not try to solve $1,$2 etc
        if k in mu.children:          
          mu=mu.children[k]
          if mu.force_recompute: break
          if not mu.data is NoData: cmu=mu; cmu_i=first_i
        else: break #it's not! let start second round, where we compute every step
      #mu.count_requested+=1


      first_i+=1 

    #write('first down: DCOi={i} mu=|\n{m}\n| cmu_i={ci} cmu=|\n{c}\n|' .format(i=first_i, m=mu, ci=cmu_i, c=cmu), 1, how='reverse')
    #write('first down of k {} cmu_i={} df={} cmu_df={}' .format(self.key(), cmu_i, df.head() if not df is None else df, cmu.data), 1, how='yellow')


    #### Splitting in two parsing for one reason:  we may not have all intermediates, but we may have checkpoints after missing data, which we don't want to skip
    ### now first_run_i is the index of the first DCO for which there's no MU, and mu is the parent of what will be its MU
    ##  and cmu is the last mu with precomputed data; cmu_i is the index of its DCO in self.chain
    ##  and df_i is the index of the DCO for which we have df in memory  
    if cmu_i!=-1:               mu=cmu; df=cmu.data   #standard case
    # elif not restart is None:   
    #   df, mu=restart       #nothing useful in memory tree, and we're running a DCO_group
      #write('cmu_i == -1 and restart is not none. mu= {} df= {}'.format(mu.name, df), 1)

    second_i=cmu_i+1
    while second_i<len(run_chain):
      dco=run_chain[second_i]
      #dco.dc_index=second_i
      #write('    within second round -> {} {}'.format(second_i, dco), 1)

      if   isinstance(dco, ManagementDCO):   
        next_df, next_mu=dco.manage_dataframe(df, mu, self)
        #dependants_to_trigger.update(dependants)
      elif isinstance(dco, ExtensionDCO):  
        run_chain.pop(second_i)
        dco.extend_run_chain(run_chain, second_i)
        continue        #restart next cycle from same first_i    
      elif isinstance(mu,  ErrorUnit):        next_df, next_mu=df, mu #pass
      elif isinstance(dco, VerificationDCO):  next_df, next_mu=dco.channel_dataframe(df, mu)    #in this case df,mu in input are the same as in output 
      else:
        k=dco.interpreted_key(df=None)  # this will parse up self.container looking for variables BUT it will not try to solve $1,$2 etc
        next_mu=mu.children[k]  if k in mu.children else None  
        if   next_mu is None:  
          # we have to extend the memory tree with a new memory unit
          write('computing DCO with interpreted k='+str(k)+' (first time ever)', 1, how='red')
          next_df, next_mu=dco.channel_dataframe(df, mu, dc=self) #this will create next_mu
          value_changed=True
        ############ next_mu exists already
        elif next_mu.data is NoData:
          # previously we didn't cache next_mu.data, and now we need to know this value
          write('computing DCO with interpreted k='+str(k)+' (did not memorize it before)', 1, how='red')
          write(('force_recompute:', next_mu.force_recompute), 1, how='red')
          next_df, next_mu=dco.channel_dataframe(df, mu, next_mu, dc=self) #this will return the same next_mu
          if next_mu.force_recompute:
            next_mu.force_recompute=False #although this mu will always be recomputed since it's not cached
            for c in next_mu.children.values():               c.force_recompute=True
            for d in next_mu.dependants:                      d.force_recompute=True      
            for p in next_mu.pointers:                      
              for pd in p.dependants:                         pd.force_recompute=True                    
          #value_changed=True

        elif next_mu.force_recompute:
          # something changed so that this next_mu must be recomputed
          write('computing DCO with interpreted k='+str(k)+' (force recompute)', 1, how='red')
          next_mu.force_recompute=False
          old_data=next_mu.data
          next_df, next_mu=dco.channel_dataframe(df, mu, next_mu, dc=self) #this will create next_mu
          if not are_identical_dataframes(old_data, next_df):
            for c in next_mu.children.values():               c.force_recompute=True
            for d in next_mu.dependants:                      d.force_recompute=True      
            for p in next_mu.pointers:                      
              for pd in p.dependants:                         pd.force_recompute=True                    
                    
            # dependants_to_trigger.add(c)
            #  #dependants_to_trigger.add(d)
            value_changed=True              
          else: 
            write('DCO with interpreted k='+str(k)+' came out with same result! force_recompute will not be inherited', 1, how='red')
            value_changed=False

        else: 
          next_df=next_mu.data

      second_i+=1
      df=next_df; mu=next_mu  
      mu.count_requested+=1

    # if not self.memory_unit is None:
    #   write( ( self.memory_unit.name, type(self.memory_unit), mu.name, type(mu)), 1, how='blue')


    if value_changed is None:
      if self.memory_unit is None or not self.memory_unit is mu:    value_changed=True      

    self.recompute_dc=False
    dc_triggered.add(self)
    ## Endpoint of DC: we landed on mu  and data is df    
    if mu.data is NoData: mu.data=df #caching the final result of the DC      

    for p in self.pointers_retrieved:       p.data_channels.add(self)
    if mu.name=='root:':          mu=mu.children['null:']

    previous_mu=None 
    if not self.memory_unit is mu:
      if not self.memory_unit is None:
        previous_mu=self.memory_unit
        previous_mu.remove_dc(self)                    
      mu.add_dc(self)
      self.memory_unit=mu

    #self.link_to_memory_unit(mu) # this will trigger trim_memory if this dc was already linked to a MU
    if value_changed: self.notify_value_changed()
  
    write('out of KEY={k}; df {rs}x{cs}'.format(k=self.key(),  
        rs=(len(mu.data)           if not (mu.data is NoData or mu.data is None) else mu.data),
        cs=(len(mu.data.columns)   if not (mu.data is NoData or mu.data is None) else mu.data)), 1, how='yellow,reverse')

    #write('retrigger... main: {k}'.format(k=self.key()), 1)
    for pu in self.pointers_to_trigger:
      for dc in pu.data_channels:
        if not dc in dc_triggered: 
          dc.recompute_dc=True
          write(' ->  retrigger out on DC:'+ dc.key(), 1)
          dc.out(dc_triggered) #, recompute_dc=True)    
    #write('retrigger... done.  {k}'.format(k=self.key()), 1)        

    if not previous_mu is None:
      previous_mu.trim_memory()

    # for start_pu in self.pointers_to_trigger:
    #   write(' retrigger start from:'+start_mu.name, 1)
    #   # if start_mu in mu_traversed: 
    #   #   write(' retrigger skip this start mu:'+start_mu.name, 1)
    #   #   continue
    #   for downstream_mu in start_mu.traverse_tree():
    #     write('  retrigger downstream is: {}  '.format(downstream_mu.name), 1)

    #     # if downstream_mu in mu_traversed:           
    #     #   write(' retrigger break at this downstream mu:'+downstream_mu.name, 1)
    #     #   break
    #     for dc in [i for i in downstream_mu.DCs]:
          
    #       if dc in dc_triggered:
    #         write('   retrigger out on DC, skip:'+ dc.key(), 1)
    #       else:
    #         dc.recompute_dc=True
    #         write('   retrigger out on DC:'+ dc.key(), 1)
    #         dc.out(dc_triggered)
    #         #dc_triggered.add(dc)   --> done within out() 
    # write('retrigger... done.  {k}'.format(k=self.key()), 1)        


    #write('AFTER OUT of {k}\n container: cache={c} vars={v} defines={d}\nroot memory: \n{m}'.format(d=self.defines, c=self.caches, v=self.variables, m=root, k=self.key()), 1, how='magenta')
    #write('out of KEY={k}; df head={d}'.format(k=self.key(), d=df.tail() if not df is None else df), 1, how='magenta,reverse')
    return df  #  if not return_mu    else (df,mu)

  def delete(self):
    """ Delete this DC. Memory tree is trimmed. Also, any window linked to DCOs in this DC will be removed. """
    for p in self.pointers_retrieved:       p.data_channels.remove(self)
    self.pointers_retrieved=set()    

    #self.unlink_from_memory_unit() #this will trigger memory trim
    if not self.memory_unit is None:
      self.memory_unit.remove_dc(self)              
      self.memory_unit.trim_memory()

    self.muted=True
    while self.chain: self.pop()   #this will trigger associated effects when certain DCOs are eliminated (DCO_window)
    self.muted=False 
    self.recompute_dc=True

  def concatenate(self, dc, index=None, keep_lock=True):
    """ Append all DCOs of another DC to this one."""
    if index is None:
      if keep_lock:
        for index in dc.locked:  self.set_lock( len(self.chain)+index ) #doing it before to have right len
      for dco in dc:           self.append(dco, no_emit=True)
      self.notify_modification()
    else:  
      for i, dco in enumerate(dc):    self.insert(index+i, dco)

  def append(self, dco, no_emit=False):            
    """ Append a DCO instance to the self.chain"""
    self.chain.append(dco)
    dco.container=self
    dco.was_added_to_dc()   
    if not no_emit: self.notify_modification()

  def insert(self, index, dco, no_emit=False):     
    """ Insert a DCO instance to the self.chain in position index"""
    self.chain.insert(index, dco)
    dco.container=self
    self.locked={(i if i<index else i+1):self.locked[i]          for i in self.locked}
    dco.was_added_to_dc()
    if not no_emit: self.notify_modification()

  def pop(self, index=None, no_emit=False):             
    """ Remove the DCO with this index from self.chain """
    if index is None: index=len(self)-1
    dco=self.chain.pop(index) 
    self.locked={(i if i<index else i-1):self.locked[i]     for i in self.locked    if i!=index}
    dco.was_removed_from_dc(self)
    if not no_emit: self.notify_modification()
    return dco

  def notify_modification(self):            
    if self.muted: return 
    print 'emit signal_dc_changed of', self.key()
    self.signal_dc_changed.emit()    

  def notify_value_changed(self):           
    if self.muted: return 
    print 'emit signal_VALUE_changed of', self.key()
    self.signal_value_changed.emit()

  def key(self): return self.dco_separator_char.join([ x.key()   for x in self.chain  ])  
    #, non_redundant=False): #there's a one-to-one correspondance between a Key and the DC output (unless the DB/antenna changes)
    #if non_redundant:   return self.dco_separator_char.join([ x.key()   for x in self.chain  if not x.parameters is None])  #skipping useless DCOs  
    #else:               
  def get_available_databases(self):       return self.master().data().get_available_databases()
  __repr__=key

DC=DataChannel
 
allowed_in_var_names=set(uppercase+lowercase+digits+'_')
digits_set=set(digits)
###################################################################################################################
class DataChannelOperation(object):
  """ (=DCO) Base class for all elementary operations allowed in a DataChannel. 
All the information of an operation is contained in the type of DCO (subclass, and name class attribute) and its self.parameters (single string).  
To allow complex, programming language-like operations, the self.parameters are 'interpreted' before being run, so that variables are replaced by their value.
Variables are specified as $v (v can be any string of alphanumeric characters, with at least one non-number)
Variables must be 'declared' before being used in the DC, using the DCO_var. The name scope is always the current DC, then its container, then its container etc... 
A scope is implemented as a DC_container object. The ultimate DC_container is the MasterContainer itself.
"""
  copiable=True
  name='EmptyDCO'
  DCOW_class=None  #define this in subclasses to force using a certain DCO widget
  #parameters_class=str
  def __init__(self, parameters=None):  
    self.container=None   ## set up when added to a DC
    self.parameters=None
    self.update(parameters) #initializing self.parameters
    self.dc_index=None # available only after out() is called 
  def update(self, parameters):    
    """Update the parameters and notify the container. Returns True if notification is sent, otherwise False """
    p=parameters if parameters!='None' else None   
    notify=self.parameters!=p
    self.parameters=p
    if not self.container is None and notify: 
      self.container.notify_modification()
      return True
    else: return False

  def channel_dataframe(self, df, mu, next_mu=None, dc=None): 
    """If next_mu is None (standard case), it is the first time that this DCO is executed (at least with these parameters).
        In this case a new memory unit is created (next_mu).
If next_mu is provided (it is a child of mu): 
Either we're recomputing something since something upstream changed (next_mu.force_recompute was True)
    or next_mu data is NoData and we need to know its real value. """
    try:
      next_df=self.action(df)    if not df is None else None
    except Exception as e:
      eu=ErrorUnit(name=self.interpreted_key(df=None), parent=mu, dco=self, exception=e)
      return (None,eu)
    data=next_df                if self.memorize_this() else NoData  #to init/update next_mu
    if next_mu is None:         next_mu=MemoryUnit(name=self.interpreted_key(df=None), data=data, parent=mu)
    else:                       next_mu.data=data  #
    return next_df, next_mu

  def skip_this(self):                return self.parameters is None
  def key(self):                      return '{n}:{p}'.format(n=self.name, p=self.parameters)
  def interpreted_key(self, df=None): return '{n}:{p}'.format(n=self.name, p=self.interpreted_params(df=df))
  def short(self):                    return '{}'.format(self.parameters if not self.parameters is None else '')
  def get_dataframe(self): raise Exception, "Data Channels must begin with a 'Database' or 'Pointer' component!"
  def __repr__(self): return self.key()
  def memorize_this(self):  return self.name in DCO_types_to_cache
  def was_added_to_dc(self):          pass 
  def was_removed_from_dc(self, dc):  pass 
  def interpreted_params(self, df=None):
    """ providing df is necessary if there are $1, $2 in self.parameters"""
    if self.parameters is None: return None
    out=self.parameters  #adding not allowed char to simplify things downstream
    var_start=out.find('$')
    while var_start!=-1:
      for c in range(var_start+1, len(out)):
        if not out[c] in allowed_in_var_names: break
        c+=1 #using this as flag of last char being legal
      var_name=out[var_start+1:c]
      if not var_name: raise Exception, "ERROR wrong syntax for variable! {}".format(out)
      if all( [v in digits_set  for v in var_name] ):  
        col_index=int(var_name)-1
        if not df is None and not col_index>=len(df.columns): #raise Exception, "ERROR dataframe does not have the requested column n.{}! (dataframe only has {} columns)".format(col_index+1, len(df.columns))
          var_value=df.columns[col_index]
        else: var_name=None; var_start+=1
      else:
        p=self.container
        var_value=None
        while not p is None:
          if p.has_var(var_name):    var_value=p.retrieve_var(var_name); break
          p=p.container           
        if var_value is None: raise Exception, "ERROR variable not found: {}".format(var_name)
      if not var_name is None:  #using this as flag. If None, only one possibility: df is None or not enough columns. Will crash in runtime
        out=out[:var_start]+var_value+out[c:]
      var_start=out.find('$', var_start)
    return out

  action=None    #def action(self, df):   return df
  def master(self):
    p=self
    while not p.container is None: p=p.container
    return p


# class NumericSelector(TypeSelector):  
#   accepted_types=[pd.types.dtypes.np.number]
#   expected_name='numeric'

# class ShapeSelector(DataChannelOperation):
#   """Verifies that input DF has columns a certain type. 
#    Use class attribute self.accepted_types  (list or other iterable) in subclasses to decide what is accepted,
#     and class attribute self.expected_name for pretty printing of the error raised; put here a string describing what is expected, e.g. 'numeric'   """  
#   accepted_shapes=[ None, None, None ]  # [len, nrows, ncols ]
#   def verify(self, df):
#     shape=df.shape
#     req_length,req_r,req_c=self.accepted_shapes[0]
#     if not req_length is None and len(shape)!=req_length: raise Exception, "ERROR wrong data shape: {}".format(shape)
#     req_r,req_c=accepted_types
#     if not req_r is None and shape[0]!=req_r: raise Exception, "ERROR There must be only exactly n={} rows! Wrong data shape: {}".format(shape[0], shape)
#     if not req_c is None and shape[0]!=req_c: raise Exception, "ERROR There must be only exactly n={} columns! Wrong data shape: {}".format(shape[1], shape)

# class FeatureSelector(ShapeSelector): accepted_shapes=[2,None,1] #dataframe, any n of rows, 1 column

# class NumericFeatureSelector(NumericSelector, FeatureSelector):
#   def verify(self, df):
#     NumericSelector.verify(self, df)
#     FeatureSelector.verify(self, df)

class ManagementDCO(DataChannelOperation):
  """Those that deal with saving or retrieving """
  # def channel_dataframe(self, df, mu):
  #   try:
  #     next_df, next_mu=self.manage_dataframe(df,mu)
  #   except Exception as e:
  #     eu=ErrorUnit(name=self.interpreted_key(df), parent=mu, dco=self, exception=e)
  #     return (None,eu)    
  #   return next_df, next_mu

  def manage_dataframe(self, df, mu, dc): raise Exception, "this must be defined in ManagementDCO subclasses"

class StyleDCO(ManagementDCO):
  """ This has no effect on the DC, just tells Treedex something about style."""
  def skip_this(self): return True

class DCO_newline(StyleDCO):     
  """ Goes on the next line in the DCW"""
  name='newline'
class DCO_empty(StyleDCO):       
  """ Force displaying the empty DCO widget for non-empty DCs"""
  name='empty'
class DCO_lockinsert(StyleDCO):  
  """ Forbid the insertion of a DCO at this position. Found at the beginning of a DC"""
  name='lockinsert'
class DCO_lockappend(StyleDCO):  
  """ Forbid the insertion of a DCO at this position. Found at the beginning of a DC"""
  name='lockappend'

def common_fn_get_database(self, df, mu, dc, k=None):
  """ Used by DCO_database and DCO_join. Note: input mu is ignored"""
  root=self.master().data().memory_tree 
  k=self.interpreted_key() if k is None else k     #this is just to recycle code in DCO_join
  if not k in root.children: raise Exception, "ERROR database request not found: {}".format(k)
  mu=root.children[k]
  return mu.data, mu

class DCO_database(ManagementDCO):
  """Init with: Database name to be extracted from MasterContainer->FeatureManager """
  name='database'
  manage_dataframe=common_fn_get_database

class DCO_antenna(DCO_database):
  """ Database like, but thought to retrieve node selections. Only parameter is: selection name"""
  name='antenna'
  def __init__(self, parameters='Selected nodes'):   super(DCO_antenna, self).__init__(parameters=parameters)

class VerificationDCO(DataChannelOperation):
  """Verification step. For example, checks whether columns are of the desired type. 
  Subclasses must define its verify(df) method, and raise an Exception if something is wrong
  Useful to be included in DCO_smarts that do complicate things """
  def verify(self, df): pass    
  def channel_dataframe(self, df, mu): 
    if not df is None: 
      try:      self.verify(df)
      except Exception as e:
        eu=ErrorUnit(name=self.interpreted_key(df=None), parent=mu, dco=self, exception=e)
        return (None,eu)      
    return (df,mu)

class DCO_typecheck(VerificationDCO):
  """Verifies that input DF has columns with a certain type. 
  Parameters:    column_name=typeflags&column_name2=type_flags      
  typeflags:   f  numpy float       
               i  numpy integer     
               n  any numeric (i or f)
               s  string
               d  datetime64
               b  boolean
               t  timedelta64
e.g. $1=i  to check that the first col is an integer
  Multiple typeflags can be combined by concatenation (any of those will be considered valid). 
  Multiple columns can be provided in column_name   e.g. name1,name2=i
  If you want to test all columns, you can use ':' as column_name"""  
  name='typecheck'
  flag2typecheck_fn={'f':pd.types.api.is_float_dtype,  'i':pd.types.api.is_integer_dtype,          'n':pd.types.api.is_numeric_dtype, 
                     's':pd.types.api.is_string_dtype, 'd':pd.types.api.is_datetime64_any_dtype,   'b':pd.types.api.is_bool_dtype,     't':pd.types.api.is_timedelta64_dtype    }
  type_descriptions={'f':'floating point number', 'i':'integer number', 'n':'numeric', 's':'string', 'd':'datetime', 'b':'boolean', 't':'timedelta'}
  def verify(self, df):
    ip=self.interpreted_params(df)
    if not ip: return 
    for block in ip.split('&'):
      cols,typeflags=block.split('=')
      if cols==':': columns_to_check=df.columns
      else:         columns_to_check=cols.split(',')
      for col in columns_to_check:
        if not col in df.columns:  raise Exception, "ERROR missing column! Was searching for: {}".format(col)
        if not any([  self.flag2typecheck_fn[flag]( df[col].dtype )    for flag in typeflags ]): 
          raise Exception, "ERROR wrong data type for column {c}! Expected {e}; Instead got: {g}".format(c=col, g=df[col].dtype, 
              e=', or '.join([self.type_descriptions[flag] for flag in typeflags]) )

class DCO_shapecheck(VerificationDCO):
  """Verifies that input DF has a certain number of rows/columns; and/or 
      that a certain column is present, or a row_index is present (string only)
  Parameters examples:    r=2      c>5     r<5&c>2     r>2&r<6&c=1      Node@c    r>2&Node@c
  Possible operators are = > <  
"""  
  name='shapecheck'
  def verify(self, df):
    ip=self.interpreted_params(df) #nothing to interpret here though
    if not ip: return 
    for block in ip.split('&'):
      splt=block.split('@')
      if len(splt)>1: 
        requested, r_or_c = splt
        if    r_or_c=='r':        index=df.index
        elif  r_or_c=='c':        
          if len(df.shape)<2: raise Exception, "ERROR wrong data shape! Input has a single dimension!"
          index=df.columns
          test_ok=   requested in index
          if not test_ok:
            raise Exception, 'ERROR wrong data shape! "{}" should be among the index of {} but it is not present!'.format(requested, {'r':'rows', 'c':'columns'}[r_or_c])
      else:
        r_or_c=block[0]
        operator=block[1]
        number=int(block[2:])
        if    r_or_c=='r':                w=df.shape[0]
        elif  r_or_c=='c':      
          if len(df.shape)<2: raise Exception, "ERROR wrong data shape! Input has a single dimension!"
          w=df.shape[1]
        if   operator=='=':   test_ok= w==number
        elif operator=='>':   test_ok= w>number
        elif operator=='<':   test_ok= w<number
        else:                 raise Exception, "ERROR DCO_shapecheck wrong syntax! parameters='{}'".format(ip)
        if not test_ok: 
          raise Exception, 'ERROR wrong data shape! {} should be {} but they are {} instead!'.format({'r':'rows', 'c':'columns'}[r_or_c],  block[1:], w)

class DCO_generator(DataChannelOperation):
  """Create a new empty dataframe.
Parameters:   nrows&cols&fill    or  nrows&cols          where
 nrows is always an int  (can be 0)
 cols can be an empty string (no columns, index only);       or a comma-separated list of column names  a,b,c,d;    or a ^N   format (N being an integer)
 fill, if provided, is the value used to fill the dataframe (normally: NaN).      
  You can use a prefix to force the type of fill. Normally it's a float.   ^ -> type: int     @  -> type: string """
  name='generator'
  def channel_dataframe(self, df, mu, next_mu=None, dc=None): 
    root=self.master().data().memory_tree 
    ip=self.interpreted_params()
    k=self.name+':'+ip
    next_mu=root.children[k]  if k in root.children else None
    if next_mu is None or next_mu.data is NoData:
      try:
        splt=ip.split('&')
        if not len(splt) in [2,3]:  raise Exception, "DCO generator wrong syntax!! {}".format(k)
        nrows=int(splt[0])
        aindex=range(nrows)
        cols=splt[1]
        if    not cols:             columns=None
        elif  cols.startswith('^'): columns=map(str, range(1, int(cols[1:])+1))
        else:                       columns=cols.split(',')
        if    len(splt)!=3:             fill=None
        elif  splt[2].startswith('^'):  fill=int(splt[2][1:])
        elif  splt[2].startswith('@'):  fill=splt[2][1:]
        else:                           fill=float(splt[2])
        next_df=pd.DataFrame(index=aindex, columns=columns)      
        if not fill is None:    next_df.fillna(fill, inplace=True)
        data=next_df if  self.memorize_this() else NoData
        if next_mu is None:        next_mu=MemoryUnit(name=k, data=data, parent=root)
        else:                      next_mu.data=data
        return next_df, next_mu
      except Exception as e:
        eu=ErrorUnit(name=self.interpreted_key(df), parent=mu, dco=self, exception=e)
        return (None,eu)
    else:
      return next_mu.data, next_mu

class DCO_add_column(DataChannelOperation):
  """ Parameters:    colname=value   value by default is a float.  
  start with   ^ -> type: int     @  -> type: string     !  -> type: bool 
  """
  name='add_column'
  def action(self, df):
    colname,value=self.interpreted_params(df).split('=')
    if    value.startswith('^'):  value=int(value[1:])
    elif  value.startswith('@'):  value=value[1:]
    elif  value.startswith('!'):  value=bool(value[1:])
    elif not value:               value=None
    else:                         value=float(value)
    return df.assign(**{colname:value})   

#### other DCOs
class DCO_select(DataChannelOperation):
  name='select'
  """Init with: column name to be selected. optionally, multiple col names, comma-separated. 
  Typically the first one is 'Node';  
  Position, 1-based indexes can be also queried using '$'  for example Node,$3 
  The ":" special character means: all other fields not explicitly specified in this select. 
   This is useful to reorder columns; E.g: you want to bring column A as first:  'select:A,:'
  If parameters start with '@', selection is inverted: these columns are not selected
  """
  def action(self, df):    
    x=self.interpreted_params(df)
    if x.startswith('@'):   
      invfields=set(x[1:].split(','))
      fields=[f for f in df.columns if not f in invfields]
    else:
      fields=x.split(',')   
      if ':' in fields:
        explicitly_selected=set([f for f in fields if f!=':'])
        others=[f for f in df.columns if not f in explicitly_selected]
        for i in range(len(fields)-1, -1, -1): #parsing positions backwards
          if fields[i]==':': 
            fields.pop(i)
            for f in others: fields.insert(i, f)
    return df[fields].copy()

  def short(self): return DataChannelOperation.short(self) if self.parameters is None or not self.parameters.startswith('@')      else  '!'+self.parameters[1:]

class DCO_filter(DataChannelOperation):
  name='filter'
  """Init with: query string. Examples:     
      DCO_filter( 'Node.startwith("P")' )  
      DCO_filter( 'ML > 100' )    """
  def action(self, df):    return df.query(self.interpreted_params(df))

class DCO_eval(DataChannelOperation):  #just to avoid duplicating the code for process and compute
  engine=None
  def contain_assignment(self, s):
    index=0;      lens=len(s)
    accepted_pre=set('><=!'); accepted_post=set('=')
    f=s.find('=', index)
    while f!=-1:
      if f==0 or f==lens-1: raise Exception, "ERROR invalid expression! {e}".format(e=s)
      if not ( s[f-1] in accepted_pre or s[f+1] in accepted_post ):        return True
      index+=1
      f=s.find('=', index)
    return False
      
  def action(self, df):    
    x=self.interpreted_params(df)
    use_inplace=not self.contain_assignment(x)
    return df.eval(x, inplace=use_inplace, engine=self.engine)
  
class DCO_process(DCO_eval):
  name='process'
  engine='python'

class DCO_compute(DCO_eval):
  name='compute'
  engine='numexpr'

class DCO_rename(DataChannelOperation):
  name='rename'
  """Init with:  new1=old1
     or with:    new1=old1,new2=old2"""
  def action(self, df):
    rename_hash={}
    for pair in self.interpreted_params(df).split(','):  
      newK, oldK= pair.split('=')
      rename_hash[oldK]=newK
    return df.rename(columns=rename_hash)

class DCO_index(DataChannelOperation):           
  name='index'
  """Manipulate the index of the input DF. 
  parameters=='reset' to reset the index to numeric, range  """
  def action(self, df):
    if self.interpreted_params(df)=='reset': return df.reset_index()
    else: raise Exception     

class DCO_aggregate(DataChannelOperation):           ### Finish/add transform
  name='aggregate'
  """Init with:                 field&operation   e.g.   ML&sum
     or with multiple fields:   f1,f2,f3&mean
  'operation' is passed as a string to the aggregate method of pandas grouped elements; all functions available for dataframes are available """
  def action(self, df):
    fields, operation=self.interpreted_params(df).split('&') 
    if fields.count(','): fields=fields.split(',')
    return df.groupby(fields).aggregate(operation).reset_index()


class DCO_column_transform(DataChannelOperation):
  """ no name: just utility superclass to perform operations on numerical columns
Parameters template:       subclass_params|cols|prefix@suffix|r_or_a              
 cols  can be a comma-separated list of columns;  
       or @n   for the list of numerical columns; n can be actually be any another type flag, or concatenation of flags for any of those types
       or empty for all cols
 r_or_a can be r (replace columns) or a (add them)
 Every single of these pieces can have the ^ suffix to signal to the DCOW that this part cannot be changed

  Subclasses must define    column_action(self, series, subclass_params)   
    and for the DCOW, also class attributes: 
     accepted_types, string with concatenated flags acceptable for this DCO
     default_parameters
  """

  # def __init__(self, parameters=None):           
  #   if parameters is None: parameters= str(self.default_parameters)
  #   DataChannelOperation.__init__(self, parameters=parameters)

  def action(self, df):
    subclass_params, col_spec, rename, r_or_a=self.parameters.split('|')
    col_spec=col_spec.rstrip('^')
    r_or_a=r_or_a.rstrip('^')
    prefix, suffix=rename.split('@')
    prefix=prefix.rstrip('^')
    suffix=suffix.rstrip('^')
    if not col_spec:                 columns=[c for c in df.columns]
    elif col_spec.startswith('@'):   columns=[c for c in df.columns  if  any([ DCO_typecheck.flag2typecheck_fn[x](df[c].dtype) for x in col_spec[1:]])   ]
    else:                            
      columns=col_spec.split(',')
      missing_columns=[colname      for colname in columns if not colname in df.columns]
      if any(missing_columns): raise Exception, "ERROR requested column{} w{} not found: {}".format('s' if len(missing_columns)>1 else '', 'ere' if len(missing_columns)>1 else 'as', ', '.join(missing_columns)) 

    if   r_or_a=='r':            rename_dict={}
    for colname in columns: 
      new_col_name=prefix+ colname +suffix
      column=self.column_action(df[colname], subclass_params)
      if    r_or_a=='r':        
        df=df.assign(  **{colname:column} )
        rename_dict[colname]=new_col_name
      elif  r_or_a=='a':        df=df.assign(  **{new_col_name:column} )

    if  r_or_a=='r':            df=df.rename(columns=rename_dict)
    return df

class DCO_log(DCO_column_transform):
  """ Apply a log function to all numerical columns (or the one specified to the motherclass DCO_column_transform). 
     Subclass parameters: base of log. Can be any integer, or 'e' for natural log """
  name='log'
  accepted_types='nif'  #used in its DCOW
  default_dcow_parameters='10|@n|log(@)|r'
  def column_action(self, series, subclass_params):
    if   subclass_params=='10': logfn=np.log10
    elif subclass_params=='2':  logfn=np.log2
    elif subclass_params=='e':  logfn=np.log
    else:                       logfn=lambda x,n=int(subclass_params):np.emath.logn(n,x)
    return series.apply(logfn)

  def short(self): 
    if self.parameters is None: return 'None'
    splt=self.parameters.split('|')
    return ('log'+splt[0])+ ('' if splt[1].startswith('@') else splt[1])


class DCO_scale(DCO_column_transform):
  """ Scale input numerical columns to a min or max. 
  Parameters:    minIn:maxIn:minOut:maxOut     
    with @ that can be used in place of maxIn and/or minIn to indicate to use the max/min of the input df
"""
  name='scale'
  accepted_types='n'  #used in its DCOW
  default_dcow_parameters='@:@:0:1|@n|@[scaled]|r'
  def column_action(self, series, subclass_params):
    min_in, max_in, min_out, max_out=map(lambda x:x.rstrip('^'),  subclass_params.split(':'))
    if min_in=='@': min_in=float( series.min() )
    if max_in=='@': max_in=float( series.max() )
    min_out=float(min_out)
    max_out=float(max_out)
    return min_out+  (max_out-min_out)*( (series-min_in)/(max_in-min_in) )

  def short(self):
    if self.parameters is None: return 'None' 
    subclass_params, col_spec, rename, r_or_a=self.parameters.split('|')
    min_in, max_in, min_out, max_out=map(lambda x:x.rstrip('^'),  subclass_params.split(':')) 
    if    min_in=='@' and max_in=='@': w=''
    elif  min_in=='@':                 w='@:{} to '.format(max_in) 
    elif  max_in=='@':                 w='{}:@ to '.format(min_in) 
    else:                              w='{}:{} to '.format(min_in, max_in) 
    c='' if col_spec.startswith('@') else col_spec.rstrip('^')+'#'
    return  '{c}{w}{i}:{a}'.format(i=min_out, a=max_out, w=w, c=c  )


class DataChannelOperationWithDependencies(DataChannelOperation):
  """ no name: just utility superclass for DCOs with dependencies other than the direct parent. 
  Subclasses must define action_with_dependencies(self, df)  that return   next_df, list_of_dependency_MUs"""
  def channel_dataframe(self, df, mu, next_mu=None, dc=None): 
    try:
      next_df, dependencies=self.action_with_dependencies(df)    if not df is None else  (None, [])
    except Exception as e:
      eu=ErrorUnit(name=self.interpreted_key(df), parent=mu, dco=self, exception=e)
      return (None,eu)
    data=next_df                if self.memorize_this() else NoData  #to init/update next_mu
    if next_mu is None:         
      next_mu=MemoryUnit(name=self.interpreted_key(), data=data, parent=mu)

      for dependency_mu in dependencies:  # dependency_mu can be PointerUnit, or MemoryUnit corresponding to a DB_DCO
        if isinstance(dependency_mu, PointerUnit): 
          pu=dependency_mu
          dc.pointers_retrieved.add(pu)          
          pu.dependants.add(next_mu)   
          
        else:
          dependency_mu.dependants.add(next_mu)   
    else:                       next_mu.data=data  
    return next_df, next_mu

class DCO_join(DataChannelOperationWithDependencies):
  name='join'
  possible_types=['left', 'right', 'outer', 'inner'] #this is used by the DCOW
  """Init with:             db_name&field    e.g.  Metabolome&Node         or   :cache_name&field
  Default field is actually 'Node', in that case this can be omitted
  The modifier @ can be used to define the type of join (left, right, outer, inner)
  Ex: Metabolome@right   :cache_name&field@inner  """
  def action_with_dependencies(self, df):
    x=self.interpreted_params(df)
    splt=x.split('@')
    if   len(splt)==1:  join_type='left'
    elif len(splt)==2:  x,join_type=splt
    splt=x.split('&')
    if   len(splt)==1:   field='Node'; dbname=splt[0]
    elif len(splt)==2:   dbname,field=splt
    else:                raise Exception, "ERROR initiating DCOW_join!"
    if dbname.startswith(':'): #actually a cache!
      pu=None  #flag
      p=self.container
      while not p is None:
        if p.has_cache(dbname[1:]): pu=p.retrieve_cache(dbname[1:]); break     
        p=p.container
      if pu is None: raise Exception, "'join' component: cache requested not found! {}".format(dbname)
      dependency_mu=pu
      df2=pu.pointed.data
    else: #db (or antenna)
      prefix='database:'
      if dbname.startswith('^'):
        prefix='antenna:'
        dbname=dbname[1:]
      df2, dependency_mu=common_fn_get_database(self, df, mu=None, dc=None, k=prefix+dbname)  #mu and dc are ignore in this function anyway
      #like old: =self.container.master().features().get_dataframe(dbname)    
    if df2 is None: raise Exception, "'join' component: joining with 'None' dataframe!"
    if df2.index.name!=field:      df2=df2.set_index(field)
    if df is None: next_df=None
    else:          next_df= df.join(df2, on=field, how=join_type)   ##### RUNNING JOIN HERE
    #write('JOIN \ndf1=\n{}\n\ndf2=\n{}\n\nout={}'.format(df, df2, next_df), 1, how='blue,reverse')

    return (next_df, [dependency_mu])

class DCO_append(DataChannelOperationWithDependencies):
  name='append'
  possible_types=['top', 'bottom'] #used by DCOW
  """Add the rows from the input DF to a retrieved DF (database, antenna or cache)  
  Init with either     database_name  or  :cache_name  or   ^antenna_name
  Normally the input DF rows are put on top. Add @ at the end of parameters to put it at the end
  """
  def action_with_dependencies(self, df): 
    dbname=self.interpreted_params(df)   
    if dbname.endswith('@'):        
      append_type='top'
      dbname=dbname[:-1]
    else:      append_type='bottom'    
    if dbname.startswith(':'): #actually a cache!
      pu=None  #flag
      p=self.container
      while not p is None:
        if p.has_cache(dbname[1:]): pu=p.retrieve_cache(dbname[1:]); break     
        p=p.container
      if pu is None: raise Exception, "'append' component: cache requested not found! {}".format(dbname)
      dependency_mu=pu
      df2=pu.data
    else: #db (or antenna)
      prefix='database:'
      if dbname.startswith('^'):
        prefix='antenna:'
        dbname=dbname[1:]
      df2, dependency_mu=common_fn_get_database(self, df, mu, k=prefix+dbname)
      #like old: =self.container.master().features().get_dataframe(dbname)
    
    if df2 is None: raise Exception, "'append' component: appending a 'None' dataframe!"
    if append_type=='bottom': df, df2 = df2, df
    #if isinstance(df, DataFrame): df=pd.DataFrame(df)   ## problem: append init a new dataframe by type. This make sure that treedex does not attempt to init a treedex.DataFrame (which would crash), instead a pd.DataFrame
    if not df.columns.equals(df2.columns):
      if df.columns.sort_values().equals( df2.columns.sort_values() ): df2=df2[df.columns]  #making sure the output will have same order as df      
      else:   raise Exception, "ERROR append: the two dataframes do not have the same columns!"
    next_df=df.append(df2, ignore_index=True)
    return (next_df, [dependency_mu])

class ExtensionDCO(DataChannelOperation):
  """ """

class DCO_group(ExtensionDCO, DataChannel): # can be a init or not, see below is_init
  """ Basically a DC inside a DC. This is a list of DCOs. Init with:   'name[dc_key]'   (name is optional)"""
  name='group'
  def __init__(self, parameters=None):  
    #write('init DCO group, params= {}'.format(parameters), 1, how='blue')
    self.group_name=''
    self.group_name_in_progress=None  # used by its DCOW
    DataChannel.__init__(self, container='flag', auto_update=False)  #this is replaced when out() is called        
    DataChannelOperation.__init__(self, parameters)    ## this also call self.update

  def key(self): return '{cn}:{n}[{dck}]'.format(cn=self.name, n=self.group_name, dck=DataChannel.key(self))

  def interpreted_key(self, df=None):    raise Exception      
    #return self.dco_separator_char.join([ x.interpreted_key(df=None)         for x in self.chain  ])
    #return self.dco_separator_char.join([ x.key()         for x in self.chain  ])

  #, non_redundant=False):    #, non_redundant=non_redundant))
  ### making sure self.parameters always reflects the key of DCOs in self.chain
  @property
  def parameters(self):   return self.key()[len(self.name)+1:]  #skipping 'group:'
  @parameters.setter  #just so the self.parameters=None in the DCO init will not make python freak out
  def parameters(self, value): pass   

  def update(self, parameters):    
    #self.parameters=parameters if parameters!='None' else None         
    k=parameters[ parameters.index('[')+1:-1 ]  if not parameters is None else None
    group_name=parameters[:parameters.index('[')]      if not parameters is None else ''
    #self.dc=DataChannel(self, from_key=k  ) #passing DC key only
    #write('UPDATE dco group param={}    key={}'.format(parameters, k), 1, how='yellow')
    old_k=self.key();   old_k=old_k[old_k.index('[')+1:-1]
    if old_k!=k or self.group_name!=group_name:
      #write("DCO GROUP update this! old='{}'  new='{}'  ".format(old_k, k), 1, how='reverse')
      self.reset()
      self.group_name=group_name
      #write('chain before {}  p={}'.format(self.chain, self.parameters), 1)
      was_muted=self.muted
      self.muted=True
      self.build_from_key(k)
      self.muted=was_muted
      #write('chain after  {}  p={}'.format(self.chain, self.parameters), 1)
      self.notify_modification()
      #if not self.container is None: self.container.notify_modification()
      return True
    else: return False
  def notify_modification(self):
    DataChannel.notify_modification(self)
    if not self.container is None and not self.muted: self.container.notify_modification()

  def skip_this(self): return not self.chain
  def extend_run_chain(self, run_chain, index):
    i=0
    for dco in self.chain: 
      if   dco.skip_this():     continue
      elif isinstance(dco, ExtensionDCO) and not isinstance(dco, DCO_define):
        i+=dco.extend_run_chain(run_chain, index+i)
      else:          
        run_chain.insert(index+i, dco)      
        i+=1
    return i

  def channel_dataframe(self, df, mu, next_mu=None, dc=None):    raise Exception
    # #ignoring input next_mu
    # next_df, next_mu=self.out( restart=(df,mu), link_memory_unit=False, return_mu=True)
    # return next_df, next_mu
    
  #def key(self):     return self.name+':[{p}]'.format(p=self.parameters)
  def short(self): 
    #name=self.parameters[:self.parameters.index('[')] if self.parameters else None
    return self.group_name if self.group_name else self.key() 
  # def is_init(self): 
  #   return self.chain[0].is_init() if self.chain else True

class DCO_smart(DCO_group):
  """ An elegant way to make DCO subclasses that, given few parameters, can make something complex 
  by actually creating a combination of many DCOs, some of which will depend on the parameters. 
  main fns: 
    -expand_parameters(parameters)     --> parameters of the DCO group that do the job 
    -backtrace_parameters(parameters)  --> reverse of expand; extract the parameters of this smart DCO from the parameters of the expanded DCO group
  """
  #name='group'   ### group
  default_parameters=None  #use this to define the default parameters of smart subclasses
  def __init__(self, parameters=None):           
    if parameters is None: parameters= str(self.default_parameters)
    #initialized with the resulting DC key. let's backtrace to get the essential
    #parameters=self.backtrace_parameters(parameters)
    #exp_parameters=self.expand_parameters(parameters)
    DCO_group.__init__(self, parameters=parameters) #'test[select:$2]')       ## this also call self.update
  def update(self, parameters):
    """ Overriding DCO_group.update to change parameters (expand it)"""
    parameters=self.expand_parameters(parameters)
    #print 'UPDATING exp=', parameters
    return DCO_group.update(self, parameters)

  def short(self): return self.backtrace_parameters(self.parameters)
  def expand_parameters(self, parameters):    raise Exception, "ERROR expand_parameters    must be defined in DCO_smart subclasses"
  def backtrace_parameters(self, parameters): raise Exception, "ERROR backtrace_parameters must be defined in DCO_smart subclasses"
  def unexpanded_key(self):  return '{n}:{k}'.format(n=self.name, k=self.backtrace_parameters(self.parameters))

class DCO_define(ManagementDCO, DCO_group):
  name='define'
  """Init with:  save_name[dc_key]      
  When you want to save in a namespace different from the direct container of this DCO,
   then include @:     global_varname@=dc_key      or    varname_2_levels_up@2=dc_key """
  #def channel_dataframe(self, df): return self.action(df)  #making sure input None does not stop this
  #def get_dataframe(self): return self.action(df=None)
  #def action(self, df=None):
  # this is necessary to avoid smart DCOs being written down with their expanded parameters
  # defining key will affect self.parameters as well (see DCO_group)
  def key(self): return '{cn}:{n}[{dck}]'.format(cn=self.name, n=self.group_name, dck=self.key_for_copy()   )

  def manage_dataframe(self, df, mu, dc): #, trigger_fn=None):    
    x=self.parameters 
    if not x: return df, mu
    if not x.endswith(']'): raise Exception, "ERROR invalid parameters for DCO_define!"        
    i=x.index('[')
    var_name=x[:i]
    dc_key=x[i+1:-1]
    splt2=var_name.split('@')
    container=self.container
    if len(splt2)==2:
      var_name=splt2[0]     
      if not splt2[1]:
        while not  container.container is None: container=container.container
      else:
        n_up=int(splt2[1])
        for _ in range(n_up): container=container.container
    if not var_name: raise Exception, "'Define' component: illegal function name!"
    container.save_define(var_name, dc_key)
    #if not trigger_fn is None: trigger_fn(var_name)
    return df, mu

class DCO_call(ExtensionDCO):
  """Init with: var_name previously defined"""
  name='call'
  #def get_dataframe(self):  raise Exception, "'Retrieve' component can be only found first in a Data Channel!"
  #def manage_dataframe(self, df, mu, target_container=None): 
  def extend_run_chain(self, run_chain, index, target_container=None):
    # getting dc key
    p=self.container
    x=self.interpreted_params(df=None)
    if target_container is None:
      while not p is None:
        if p.has_define(x): 
          target_container=p
          break
        p=p.container 
    if target_container is None:   raise Exception, "ERROR defined function {f} not found!".format(f=x)

    dcg_params='dco_call[{}]'.format( target_container.retrieve_define(x) )      
    print 'CALL', x, 'dc recovered from k!', dcg_params
    dcg=DCO_group()
    # dcg.muted=True
    # print 'CALL muting'
    dcg.update(dcg_params)    #DataChannel(self, from_key=dc_key) #this a DC_group, i.e. a DCO and a DC at the same time
    # print 'CALL unmuting'
    # dcg.muted=False
    dcg.container=self.container
    return dcg.extend_run_chain(run_chain, index)

    # df, mu =dcg.out( restart=(df, mu), link_memory_unit=False, return_mu=True )
    # return df, mu

class DCO_retrieve(ManagementDCO):
  """Init with: var_name previously cached  """
  name='retrieve'
  def manage_dataframe(self, df, mu, dc): 
    x=self.interpreted_params()
    p=self.container
    while not p is None:
      #write('retrieve going up searching {}, now in: {}  --> mem_keys {}'.format(x, p, p.caches), 1, how='magenta')
      if p.has_cache(x): 
        pu=p.retrieve_cache(x)    
        # assert len(pu.dependencies)==1
        # linked_mu=[m for m in pu.dependencies][0]
        linked_mu=pu.pointed
        #write('retrieve varname {} DF={}'.format(x, df.head() if not df is None else df), 1, how='yellow,reverse')
        dc.pointers_retrieved.add(pu)
        #if not dc in pu.data_channels: pu.data_channels[dc]=0
        pu.data_channels.add(dc) #]+=1
        df, mu=linked_mu.data, linked_mu       
        return df, mu
      p=p.container
    raise Exception, "ERROR DCO_retrieve cache '{}' not found!".format(x)
  #def action(self, df): raise Exception, "'Retrieve' component can be only found first in a Data Channel!"

class DCO_cache(ManagementDCO):
  """Init with:  save name. If not local, followed by @n  where n is the number of levels to go up. 0=self.container   
  example: cache:x   cache:globalvar@   cache:plotData@1  """  
  name='cache'
  def manage_dataframe(self, df, mu, dc):
    ip=self.interpreted_params(df)
    splt=ip.split('@')
    #var_name=splt[0]
    container=self.container
    if len(splt)==2:
      if not splt[1]:
        while not  container.container is None: container=container.container
      else:
        n_up=int(splt[1])
        for _ in range(n_up): container=container.container
    df,pu=write_cache_fn(df, mu, ip, container, dc) 
    return df,mu #,ds)  #NOTE: not returning pu

def write_cache_fn(df, mu, ip, container, dc):
    """ Utility to do the DCO_cache job  (I split the code to reuse it in DCO_add_to_plot)"""
    var_name=ip.split('@')[0]
    #write('CACHE {v} in container {c}  --> df {d}'.format(v=var_name, c=container, d=df.head() if not df is None else df), 1, how='green')
    if mu.name=='root:':    mu=mu.children['null:'] #caching nothing.
    if mu.data is NoData:   mu.data=df ## making sure it's actually stored
    if not container.has_cache(var_name): #first time we cache this
      write('init cache: {}    link to: {}'.format(var_name, mu.name), 1, how='green')
      pu=PointerUnit(name= 'cache:'+ip, pointed=mu) # self.interpreted_key()   )
      container.save_cache(var_name, pu)
    else:  #cache is already there
      pu=container.retrieve_cache(var_name)
      #assert len(pu.dependencies)==1
      #linked_mu=[m for m in pu.dependencies][0] # pu only have one dependency
      linked_mu=pu.pointed
      if not linked_mu is mu: #   or  pu.force_recompute:         
        # if pu.force_recompute:
        #   write('cache: {} force recompute -> descendants will inherit this'.format(var_name) , 1, how='green')         
        #   pu.force_recompute=False
        # else:
          ## replacing the pointer in the existing pu to the correct mu. then, trigger recompute in children and dependants
        if 1:
          write('cache: {} changing pointer to a different mu. \nFrom this: \t{}\nTo   this: {}'.format(var_name, linked_mu.name, mu.name) , 1, how='green')
          if pu in linked_mu.pointers:          
            linked_mu.pointers.remove(pu)           #std case
          elif not linked_mu.name=='null:':
            write('ERROR changing pointer; {} is not among dependants of {}. These is the list of its dependants:{}'.format(pu.name, linked_mu.name, ', '.join([d.name for d in linked_mu.dependants])), 1, how='green');           raise Exception

          mu.pointers.add(pu)
          pu.pointed=mu
          #mu_to_be_triggered.add(pu)
        dc.pointers_to_trigger.add(pu)

        # for c in pu.children.values():   
        #   c.force_recompute=True
        for d in pu.dependants:  d.force_recompute=True   #no children: not cycling them
        #if d==pu: raise Exception
        #pu.trigger_recompute_in_downstream_DCs() 
      else:
        write('existing cache, nothing to do: {}'.format(var_name), 1, how='green')
      #if var_name.startswith('_'):        write('CACHE {} \n{}'.format(var_name, df), 1, how='yellow')
    return df, pu

class DCO_var(ManagementDCO):
  """Init with:  var_name=value
  When the variable is to be defined in a namespace different from the direct container of this DCO, 
   then include @:     global_varname@=value      or    varname_2_levels_up@2=value
   """
  name='var'
  def manage_dataframe(self, df, mu, dc): 
    x=self.interpreted_params(df)
    splt=x.split('=')
    var_name=splt[0]
    value=splt[1]
    splt2=var_name.split('@')
    container=self.container
    if len(splt2)==2:
      var_name=splt2[0]     
      if not splt2[1]:
        while not  container.container is None: container=container.container
      else:
        n_up=int(splt2[1])
        for _ in range(n_up): container=container.container
    if not var_name: raise Exception, "'Var' component: illegal variable name!"
    #write('DCO var saving var_name {} with value {}'.format(var_name, value)  , 1, how='blue,reverse')
    container.save_var(var_name, value)
    return df, mu

  #def interpreted_key(self, df=None):  return None

class DCO_nodeFilter(DCO_smart):
  """ Filter the input DF to keep only those lines that are found in a certain nodeSelector, saved in master().selections()
  Parameters= name_of_selection          
   Optionally preceded by @ to filter in the ancestors of that selection instead
   Optionally followed by ^ to flag that the presence/absence of @ cannot be changed by the user in the GUI
  """
  name='nodeFilter'
  default_parameters='All leaves'
  def backtrace_parameters(self, parameters):
    flag='^'    if parameters.startswith('f')  else   ''          #parameters.startswith('d')
    parameters=parameters[1:]      
    if parameters.startswith('[cache:'): #filtering for ancestors
      return '@'+parameters.split(DataChannel.dco_separator_char)[1].split(':')[1]+flag
    else:
      return parameters.split('^')[1].split('@')[0]+flag

  def expand_parameters(self, parameters):
    if parameters.endswith('^'):  
      parameters=parameters[:-1]
      flag='f'
    else:
      flag='d'
    if parameters.startswith('@'):       #filtering for ancestors
      parameters=parameters[1:]
      return '{flag}[cache:i{sep}antenna:{a}{sep}trace:WeightedAv@{sep}cache:a{sep}retrieve:i{sep}join::a@inner]'.format(
        sep=DataChannel.dco_separator_char, a=parameters, flag=flag)
    else:                     
      return '{flag}[join:^{p}@inner]'.format(p=parameters, flag=flag)

  def short(self):
    """ Trick to show useful writings when the selection is All leaves, Selected nodes or Highlighted nodes"""
    p=self.backtrace_parameters(self.parameters)
    if p.endswith('^'): p=p[:-1]
    if not p.startswith('@'): return p
    else: 
      if    p.endswith(' leaves'):        return p[1:].replace(' leaves', ' ancestors')
      elif  p.endswith(' nodes'):         return p[1:].replace(' nodes',  ' ancestors')
      else: return p

class DCO_treeInfo(DataChannelOperation):
  possible_values=['order', 'branch lenght', 'time', 'parent', 'support']
  """ Fetch information from the tree in memory.  Input DF must have a column or an index named 'Node'
  Init with:    xxx:tree_name    (:tree_name may be omitted for default tree)     
   xxx can be:  order, parent, branch length, support
  """
  name='treeInfo'
  def action(self, df): 
    splt=self.interpreted_params(df).split(':')
    what=splt[0]
    if not what in self.possible_values:     raise Exception, "ERROR TreeInfo: request '{}' not accepted! Possible values: {}".format(what, self.possible_values.join(', '))
    tree_name=splt[1] if len(splt)>1 else self.container.master().trees().default_tree.tree_name
    tree=self.container.master().trees().get_tree(tree_name) #default tree for None tree_name
    init_value= {'order':0, 'branch lenght':0.0, 'time':0.0, 'parent':None, 'support':0.0 }[what]   ##making sure new column will come out of the right dtype
    df_next=df.assign(**{what:init_value})  #creating new column
    if what == 'order':
      dforder= self.master().data().memory_tree.children[ 'treeOrder:'+tree_name  ].data  #indexed by node name
      #write(dforder, 1, how='reverse,magenta')

    if    'Node' == df.index.name:  by_index=True
    elif  not 'Node' in df.columns: raise Exception, "ERROR TreeInfo: the input dataframe must contain a 'Node' column!"
    else:                           by_index=False
    for i, row_i in enumerate(df.index):
      node_name=df.at[row_i, 'Node']   if not by_index else row_i
      node=tree.get_node(node_name)
      if   what == 'branch lenght':    value=node.dist
      elif what == 'support':          value=node.support
      elif what == 'parent':           value=node.up.name
      elif what == 'order':            value=dforder.at[node_name,'order']
      elif what == 'time':             value=node.time #get_distance_from_root() #not computing it!
      df_next.at[row_i,what]=value
    return df_next

  
####
class DCO_trace(DataChannelOperation):
  """ perform ancestral state reconstruction using one of the builtin procedures.
  Parameters:  procedure_name        or     
               procedure_name:tree_name    to select a specific tree,   or
               procedure_name:tree_name@   to return only the computed data, instead of appending to the df in input  (:tree_name can be omitted)               
  """
  name='trace'
  def action(self, df): 
    x=self.interpreted_params(df)
    if not x.endswith('@'):   append_to_input=True
    else:                     append_to_input=False; x=x[:-1]
    splt=x.split(':')
    trace_procedure=splt[0]
    tree_name=splt[1] if len(splt)>1 else None
    tree=self.container.master().trees().get_tree(tree_name) #default tree for None tree_name
    df_next=trace_procedures[trace_procedure](df, tree)
    if append_to_input:
      #if isinstance(df, DataFrame): df=pd.DataFrame(df)   ## problem: append init a new dataframe by type. This make sure that treedex does not attempt to init a treedex.DataFrame (which would crash), instead a pd.DataFrame
      if not df.columns.equals(df_next.columns):
        if df.columns.sort_values().equals( df_next.columns.sort_values() ): df_next=df_next[df.columns]  #making sure the output will have same order as df      
        else:   raise Exception, "ERROR trace: the reconstructed dataframe do not have the same columns as the original!"      
      return df.append(df_next, ignore_index=True)
    else: return df_next

def trace_by_weighted_average(df, tree):
  """ df is a dataframe with a Node column which can be an index. 
  Returns a df with the same structure, but with names of ancestral nodes, linked to predicted ancestral states for any features (any column other than Node)
  All ancestral nodes for the leaves in input are reported. 
  If multiple NaN are present in input, this may cause some ancestral nodes in output to contain NaN if not prediction at all can be done.
  Any number of columns can be present in input; the prediction will be performed for all of them (must be numeric)
  NOTE the output DF is indexed by Node
  """
  original_node_col_index=None
  if df.index.name!='Node':  
    if not 'Node' in df.columns: raise Exception, "ERROR the trace procedure requires a 'Node' column or index!"
    original_node_col_index=df.columns.get_loc('Node')
    df=df.set_index('Node')
    
  leaves=NodeSelector( [  tree.get_node(name) for name in df.index  ] )
  anc_nodes=leaves.walk_tree(up=True, only_ancestors=True)
  out=pd.DataFrame(columns=df.columns, index=[anc.name for anc in anc_nodes], dtype='float')
  df_not_nan=pd.notnull(df)
  for column in df.columns:
    leaves_no_nan=NodeSelector([n for n in leaves if df_not_nan.at[n.name, column] ])
    anc_nodes_no_nan=leaves_no_nan.walk_tree(up=True, only_ancestors=True)
    for n in leaves_no_nan: 
      parent=n.up
      while parent and (  pd.isnull( out.at[parent.name, column] )  ): #going up as long as we can; if any sister has not been parsed yet, go to next n
        sisters=[x for x in parent.children if x in leaves_no_nan or x in anc_nodes_no_nan]
        if any(    [not  (x.is_leaf() or pd.notnull( out.at[x.name, column] ) )  for x in sisters]    ): break   
        #write('parent: '+parent.name, 1, how='blue')
        #write('children: '+join([n.name+' '+str(n.dist) for n in sisters], ' '), 1, how='magenta')
        tot_dist_sisters=   sum( [x.dist for x in sisters] )
        proportion_per_sister=  [tot_dist_sisters/x.dist  for x in sisters]
        tot_weigth=         sum(proportion_per_sister)
        weight_per_sister    =  [w/tot_weigth for w in proportion_per_sister]
        out.at[parent.name, column]=   sum([( float(df.at[x.name,column])   if x.is_leaf() else out.at[x.name, column])*weight_per_sister[sis_i]  for sis_i, x in enumerate(sisters)])
        parent=parent.up

  out.index.name='Node'
  if not original_node_col_index is None:
    out.reset_index(inplace=True)          
  #else: # restore Node col positions --> not necessary, taken care in DCO_trace before append
  return out

trace_procedures={'WeightedAv':trace_by_weighted_average}
DCO=DataChannelOperation

###################################################################################################################
DCO_name2class={'database':DCO_database, 'antenna':DCO_antenna,   'generator':DCO_generator,   
                'retrieve':DCO_retrieve, 'cache':DCO_cache,   
                'define':DCO_define,     'call':DCO_call,
                'var':DCO_var,
                'select':DCO_select,     'filter':DCO_filter,  'nodeFilter':DCO_nodeFilter,   
                'add_column':DCO_add_column,
                'compute':DCO_compute,   'process':DCO_process,   
                'rename':DCO_rename,     'aggregate':DCO_aggregate, 
                'join':DCO_join,         'append':DCO_append,
                'trace':DCO_trace,       'group':DCO_group,
                'treeInfo':DCO_treeInfo, 
                'typecheck':DCO_typecheck, 'shapecheck':DCO_shapecheck,
                'newline':DCO_newline,   'empty':DCO_empty,
                'lockinsert':DCO_lockinsert, 'lockappend':DCO_lockappend, 
                'index':DCO_index,   'log':DCO_log,  'scale':DCO_scale,
}
###################################################################################################################

from .master import *
from .extra_data_channels import *
from .widgets import *


