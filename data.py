import pandas as pd
from PyQt4 import QtCore
from .common import *

class DataFrame(pd.DataFrame):
  """ Extension of pandas dataframe. Every instance of this is an homogenous data structure, typically coming from the same source.
Init with:
  -name:    an identifier string that will be used to fetch this dataframe   --> then obtainable by calling self.name()
  -data:    a pd.DataFrame   (may be returned, for example, by pd.read_csv
  -node_field:  optionally, the column name that points to the node name. 
After init, every DataFrame must have a 'Node' column 
"""
  def __init__(self, data=None, name=None, node_field=None, **kargs):
    pd.DataFrame.__init__(self, data=data, **kargs)
    if not name: raise Exception, "ERROR Treedex DataFrame cannot have an empty name!"
    self._name=name
    if not node_field is None:        
      if self.index.name==node_field: self.reset_index(inplace=True)
      self.rename(columns={node_field:'Node'}, inplace=True)
    # test whether Node is there
    if not 'Node' in self.columns: raise Exception, "ERROR Treedex DataFrame {}: the column for 'Node' was not found: {}".format(name, node_field)
  def name(self): return self._name

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
class DC_container(object):
  """ A class that can store stuff, that is to say, dfs, DC_keys, and strings"""
  def __init__(self): self.memory={}
  def save_generic(self, var_name, thing, checktype=None):
    if not checktype is None and not checktype(thing): raise Exception, "ERROR saving {}, wrong data type! object= {}".format(var_name, thing)
    self.memory[var_name]=thing
  def has_generic(self, var_name):            return var_name in self.memory
  def get_generic(self, var_name):            
    #print var_name, 'found in ', self, '=', self.memory[var_name]
    return self.memory[var_name]
    
  def save_cache(self, var_name, df):    self.save_generic(var_name, df, checktype=lambda x:isinstance(x,pd.DataFrame))
  def has_cache(self, var_name):         return self.has_generic(var_name)
  def retrieve_cache(self, var_name):    return self.get_generic(var_name)

  def save_define(self, var_name, dc_key):    self.save_generic(var_name, dc_key, checktype=lambda x:(isinstance(x,str) and x.startswith('#DC#')))
  def has_define(self, var_name):             return self.has_generic(var_name)
  def retrieve_define(self, var_name):        return self.get_generic(var_name)

  def save_var(self, var_name, s):         self.save_generic(var_name, s, checktype=lambda x:isinstance(x,str))
  def has_var(self, var_name):             return self.has_generic(var_name)
  def retrieve_var(self, var_name):        return self.get_generic(var_name)

###################################################################################################################
class DataChannel(QtCore.QObject, DC_container):
  """ Chain of manipulators (type: DataChannelOperation) to go from a DataFrame to any data shape.
Init with:
  -container:       MasterContainer, or an intermediate container DC
  -chain:        optional, list of instances of DataChannelOperation subclasses. The first one MUST be DCO_database/DCO_pointer
The chain can be populated with self.append(DCO) or self.insert(i, DCO), or shrinked by self.pop(i) 
Main method: self.out()  --> this runs all the operations in order and output a pd.DataFrame or pd.DataSeries"""
  signal_dc_changed=   QtCore.pyqtSignal()   #when structure is modified
  signal_value_changed=QtCore.pyqtSignal()   #when antennas are present, and selections changed; not emitted when signal_dc_changed (although out value has changed)
  dco_separator_char=' |>'
  def __init__(self, container, chain=None, from_key=None): 
    QtCore.QObject.__init__(self)
    DC_container.__init__(self)
    self.container=container
    self.validated=None
    self.antennas=0
    self.locked=set() #index 
    if from_key is None:
      if chain is None: chain=[]
      self.chain=chain
    else:
      self.chain=[]
      s=from_key
      while s:
        #for dco_s in from_key.split(self.dco_separator_char): 
        try:
          ## for every cycle we decide: index_start, index_end referred to the parameters string  (both included)
          ## next_start for reducing s for next cycle
          dco_name=   s[:s.index(':')]          #s.split(':')[0]
          if dco_name=='group':
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

          #if not dco_class.parameters_class is str: 
          #  parameters=eval(parameters) dco_class.parameters_class
          dco= dco_class(parameters)
          self.append(dco, no_emit=True)
          s=s[next_start:]
          #print [s]
          # for false_start in [self.dco_separator_char, ']'+self.dco_separator_char]:
          #   if s.startswith(false_start):             s=s[len(false_start):]
        except:           raise Exception, "DataChannel ERROR initializing invalid Key: {k}".format(k=from_key)
      if self.chain: self.notify_modification()  #catching up with signal emission which we skipped earlier

  def master(self):
    p=self.container
    while not p.container is None: p=p.container
    return p

  def set_lock(self, index, state=True):
    if state:                   self.locked.add(index)
    elif index in self.locked:  self.locked.remove(index) 

  def is_locked(self, index):   return index in self.locked

  def copy(self, index_start=0, index_end=None, keep_lock=False):
    """ Return a copy of this DC. Optionally provide slicing indexes start and end (0-based, included)
    With option keep_lock, the DCO which are locked will retain this property (i.e., read-only)"""
    k=self.key()
    if index_end is None:   index_end=len(self)-1
    if 1: #elif index_start:       
      splt=k.split(self.dco_separator_char)[index_start:index_end+1]
      k=self.dco_separator_char.join( splt )
      #print 'copy', index_start, index_end, splt, k
    dc=DataChannel(self.master(), from_key=k)
    if keep_lock:
      for i in self.locked:
        if i>=index_start and i<=index_end:  dc.set_lock(i+index_start)   
    return dc

  def __iter__(self):        return self.chain.__iter__()
  def __len__(self):         return self.chain.__len__()

  def out(self, df=None, index_end=None):
    """Standard function to start the flux in the DC and get the data coming out. """
    if not self.chain: return None #raise Exception, "ERROR DataChannel is empty!"
    for i, dco in enumerate(self.chain):
      dco.dc_index=i
      if     dco.is_init():
        df=dco.get_dataframe()
      #elif   isinstance(dco, DCO_define) or skipping:  skipping=True; continue
      else:                                          
        df=dco.channel_dataframe(df)
      #if df is None: return None
      if not index_end is None and i==index_end: return df
    return df

  def run_validation(self):
    """the DC is simply tested; None is returned is everything is ok; 
 otherwise a tuple (index, e) is returned; index is the index of the DCO in this DC chain that failed; e is the exception raised"""
    try:  
      if not self.chain: raise Exception, "ERROR DataChannel is empty!"
    except Exception as e:    return (0, e)
    FLAG='whatever';     df=FLAG
    try:
      if isinstance(self.container, DCO_group): #this is not an independent DC; it's a DC of a DCO_group within some DC at higher level
        index_of_dco=self.container.dc_index
        parent_of_dco=self.container.container  ## this is a DC
        print 'validating DCO group', index_of_dco, parent_of_dco
        if index_of_dco>0:
          df=parent_of_dco.out(index_end=index_of_dco-1)
        
      for i, dco in enumerate(self.chain):
        dco.dc_index=i
        if df is None: return None
        if dco.is_init():
          #if i>0 and not isinstance(self.chain[i-1], DCO_pointer): raise Exception, "ERROR InitDC (database and pointer) must occur only after a 'cache' component"
          df=dco.get_dataframe()
        else:
          dco.verify(df)
          if df is FLAG: raise Exception, "ERROR DataChannels must begin with a Database, Retrieve, Antenna or Define components!"
          df=dco.channel_dataframe(df)
    except Exception as  e:  return (i, e)
    return None

  def validate(self):
    self.validated=self.run_validation()
    return self.validated

  # def is_pre(self, index):  return self.pre>index
  # def is_post(self, index): return index>len(self)-self.post-1

  def concatenate(self, dc, index=None, keep_lock=True):
    if index is None:
      if keep_lock:
        for index in dc.locked:  self.set_lock( len(self.chain)+index ) #doing it before to have right len
      for dco in dc:           self.append(dco, no_emit=True)
      self.notify_modification()
    else:  
      for i, dco in enumerate(dc):    self.insert(index+i, dco)

  def append(self, dco, no_emit=False):            
    #if self.post: raise Exception, "ERROR this DC has fixed post, can't append to it!"
    self.chain.append(dco)
    dco.container=self
    dco.was_added_to_dc()   
    if isinstance(dco, DCO_antenna): self.antennas+=1
    if not no_emit: self.notify_modification()
  def insert(self, index, dco, no_emit=False):     
    #print 'insert', index, dco, self.is_pre(index), self.is_post(index-1)
    #if self.is_pre(index) or self.is_post(index-1):    
    #  raise Exception, "ERROR trying to extend this DC: it has fixed pre or post!"
    self.chain.insert(index, dco)
    dco.container=self
    self.locked=set([i if i<index else i+1     for i in self.locked])
    dco.was_added_to_dc()
    if isinstance(dco, DCO_antenna): self.antennas+=1
    if not no_emit: self.notify_modification()
  def pop(self, index=None):             
    if index is None: index=len(self)-1
    #if self.is_pre(index) or self.is_post(index):
    #  raise Exception, "ERROR trying to pop an element from this DC: it has fixed pre or post!"
    dco=self.chain.pop(index) 
    self.locked=set([i if i<index else i-1     for i in self.locked    if i!=index])
    dco.was_removed_from_dc(self)
    if isinstance(dco, DCO_antenna): self.antennas-=1
    self.notify_modification()
    return dco

  def notify_modification(self):            
    print 'emit signal_dc_changed of', self.key()
    self.signal_dc_changed.emit()    
    #if isinstance(self.container, DCO_group): self.parent.parent.notify_modification()  ## self.parent.parent is a DC
  def notify_value_changed(self):           
    print 'emit signal_VALUE_changed of', self.key()
    self.signal_value_changed.emit()

  def has_antennas(self): return bool(self.antennas)

  def key(self, non_redundant=False): #there's a one-to-one correspondance between a Key and the DC output UNLESS the DC.has_antennas   (and unless the DB changes)
    if non_redundant:   return self.dco_separator_char.join([ x.key()   for x in self.chain  if not x.parameters is None])  #skipping useless DCOs  
    else:               return self.dco_separator_char.join([ x.key()   for x in self.chain  ])  
  def get_available_dataframes(self):       return self.master().features().get_available_dataframes()
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
  name='EmptyDCO'
  DCOW_class=None  #define this in subclasses to force using a certain DCO widget
  #parameters_class=str
  def __init__(self, parameters=None):  
    self.container=None   ## set up when added to a DC
    self.update(parameters) #initializing self.parameters
    self.dc_index=None # available only while a DC is run/validated
    #for k in kargs: self.parameters[k]=kargs[k]
  def update(self, parameters):    
    self.parameters=parameters if parameters!='None' else None   
    if not self.container is None: self.container.notify_modification()
  def channel_dataframe(self, df): 
    if df is None: return None
    return df    if self.parameters is None else    self.action(df)
  def key(self): return self.name+':{p}'.format(p=self.parameters)
  def short(self):   return '{}'.format(self.parameters if not self.parameters is None else '')
  def get_dataframe(self): raise Exception, "Data Channels must begin with a 'Database' or 'Pointer' component!"
  def __repr__(self): return self.key()
  def verify(self, df): pass
  def is_init(self): return False
  def was_added_to_dc(self):          pass 
  def was_removed_from_dc(self, dc):  pass 
  def interpreted_params(self, df=None):
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
        if col_index>=len(df.columns): raise Exception, "ERROR dataframe does not have the requested column n.{}! (dataframe only has {} columns)".format(col_index, len(df.columns))
        var_value=df.columns[col_index]
      else:
        p=self.container
        var_value=None
        while not p is None:
          if p.has_var(var_name):    var_value=p.retrieve_var(var_name); break
          p=p.container           
        if var_value is None: raise Exception, "ERROR variable not found: {}".format(var_name)
      out=out[:var_start]+var_value+out[c:]
      var_start=out.find('$', var_start)
    return out

  action=None    #def action(self, df):   return df

class TypeSelector(DataChannelOperation):
  accepted_types=[pd.types.dtypes.np.number]  
  def verify(self, df):
    for col in df.columns:
      if not df[col].dtype in self.accepted_types: raise Exception, "ERROR wrong data type! Expected number, got: {}".format(df[df.columns[0]].dtype)

class ShapeSelector(DataChannelOperation):
  accepted_shapes=[ None, None, None ]  # [len, nrows, ncols ]
  def verify(self, df):
    shape=df.shape
    req_length=self.accepted_shapes[0]
    if not req_length is None and len(shape)!=req_length: raise Exception, "ERROR wrong data shape: {}".format(shape)
    req_r,req_c=accepted_types
    if not req_r is None and shape[0]!=req_r: raise Exception, "ERROR There must be only exactly n={} rows! Wrong data shape: {}".format(shape[0], shape)
    if not req_c is None and shape[0]!=req_c: raise Exception, "ERROR There must be only exactly n={} columns! Wrong data shape: {}".format(shape[1], shape)

class NumericSelector(TypeSelector):  accepted_types=[pd.types.dtypes.np.number]
class FeatureSelector(ShapeSelector): accepted_shapes=[2,None,1] #dataframe, any n of rows, 1 column

class NumericFeatureSelector(NumericSelector, FeatureSelector):
  def verify(self, df):
    NumericSelector.verify(self, df)
    FeatureSelector.verify(self, df)

class DCO_logarithm(NumericSelector):
  name='logarithm'
  parameters=False #no parameters
  def action(self):
    return df.apply(np.log)

class InitDCO(DataChannelOperation):
  """Those with which a functional DC can start with """
  def is_init(self): return True

class StopDCO(DataChannelOperation):
  """Those that can be followed by a InitDCO """

class DCO_group(InitDCO, DC_container): # can be a init or not, see below is_init
  """ Basically a DC inside a DC. This is a list of DCOs. Init with:   'name[dc_key]'   (name is optional)"""
  name='group'
  def __init__(self, parameters=None):  
    InitDCO.__init__(self, parameters)    ## this also call self.update
    DC_container.__init__(self)  
  def update(self, parameters):    
    self.parameters=parameters if parameters!='None' else None     
    k=self.parameters[ self.parameters.index('[')+1:-1 ]  if not self.parameters is None else None
    self.dc=DataChannel(self, from_key=k  ) #passing DC key only
    if not self.container is None: self.container.notify_modification()

  def get_dataframe(self): return self.action(df=None)
  def action(self, df): 
    if not self.dc.chain: return None
    return self.dc.out(df=df)
  #def key(self):     return self.name+':[{p}]'.format(p=self.parameters)
  def short(self):
    name=self.parameters[:self.parameters.index('[')] if self.parameters else None
    return name if name else self.dc.key() 
  def is_init(self): 
    return self.dc.chain[0].is_init() if self.dc.chain else True

#### init DCOs
class DCO_database(InitDCO):
  """Init with: Database name to be extracted from MasterContainer->FeatureManager """
  name='database'
  def get_dataframe(self): 
    x=self.interpreted_params()
    if x is None: return None
    return self.container.master().features().get_dataframe(x) 
  def action(self, df): raise Exception, "'Database' component can be only found first in a Data Channel!"

class DCO_retrieve(InitDCO):
  """Init with: var_name previously cached  """
  name='retrieve'
  def get_dataframe(self): 
    x=self.interpreted_params()
    p=self.container
    while not p is None:
      if p.has_cache(x): return p.retrieve_cache(x)     
      p=p.container
  def action(self, df): raise Exception, "'Retrieve' component can be only found first in a Data Channel!"

class DCO_antenna(InitDCO):
  """ This is an active DCO, meaning that it can receive signals"""
  name='antenna'
  def __init__(self, parameters='Selected nodes'):    super(DCO_antenna, self).__init__(parameters=parameters)
  def get_dataframe(self): 
    x=self.interpreted_params()
    if x is None: return None
    sel_manager=self.container.master().selections()
    if not sel_manager.has_node_selection(x): raise Exception, "ERROR 'Antenna' component: selection name not found!"
    ns=sel_manager.get_node_selection(x)
    return pd.DataFrame( [n.name for n in ns], columns=['Node'] )
    #return self.dc.master_link.features().get_dataframe(self.parameters) if not self.parameters is None else None
  def action(self, df): raise Exception, "'Antenna' component can be only found first in a Data Channel!"

  def was_added_to_dc(self):
    sel_manager=self.container.master().selections()
    sel_manager.signal_selection_changed.connect( self.selection_changed )
  def was_removed_from_dc(self, dc):    
    sel_manager=dc.master().selections()
    sel_manager.signal_selection_changed.connect( self.selection_changed )

  def selection_changed(self, selection_name):
    if selection_name==self.parameters: self.container.notify_value_changed()

class DCO_generator(InitDCO):
  name='generator'
  def get_dataframe(self): 
    raise Exception, "to implement!"
    #return self.dc.master_link.features().get_dataframe(self.parameters) if not self.parameters is None else None
  def action(self, df): raise Exception, "'Generator' component can be only found first in a Data Channel!"

class DCO_define(InitDCO):
  name='define'
  """Init with:  save name    """
  def channel_dataframe(self, df): return self.action(df)  #making sure input None does not stop this
  def get_dataframe(self): return self.action(df=None)
  def action(self, df=None):
    var_name=self.interpreted_params(df)
    index_start= self.dc_index+1 #.chain.index(self) #0based included
    index_stop=  None                                #0based included
    for i,dco in enumerate(self.container.chain[index_start:]):     
      if dco.is_init():   break
      index_stop=index_start+i
    if index_stop is None: raise Exception, "'Define' component must be followed by at least one non-init component!"
    dc_key= '#DC#'+  self.container.copy(index_start=index_start, index_end=index_stop).key()
    print 'save define', var_name, dc_key
    self.container.save_define(var_name, dc_key)
    return df

class DCO_call(DataChannelOperation, DC_container):
  """Init with: var_name previously defined"""
  name='call'
  def get_dataframe(self):  raise Exception, "'Retrieve' component can be only found first in a Data Channel!"

  def action(self, df): 
    p=self.container
    x=self.interpreted_params(df)
    while not p is None:
      if p.has_define(x): 
        dc_key=p.retrieve_define(x)     
        dc_key=dc_key[len('#DC#'):]
        dc=DataChannel(self, from_key=dc_key)
        print 'CALL', x, 'dc recovered from k!', dc_key
        return dc.out(df=df) #piping data through the DC previously saved
      p=p.container
    raise Exception, "ERROR defined function {f} not found!".format(f=x)

class DCO_cache(StopDCO):
  name='cache'
  """Init with:  save name. If not local, followed by @target    e.g.  normalizedExpr@master    """
  def action(self, df):
    var_name=self.interpreted_params(df)    
    self.container.save_cache(var_name, df)
    return df

class DCO_var(DataChannelOperation):
  name='var'
  def action(self, df):
    x=self.interpreted_params(df)
    splt=x.split('=')
    var_name=splt[0]
    value=x[len(var_name)+1:]
    if not var_name: raise Exception, "'Var' component: illegal variable name!"
    self.container.save_var(var_name, value)
    return df

class DCO_trace(DataChannelOperation):
  name='trace'
  def action(self, df): raise Exception, "'Trace' component to implement!"


# class DCO_pointer(InitDCO):
#   """Init with: DC that act as providing the dataframe with its out() method.  """
#   name='pointer'
#   def __init__(self, parameters=None, label=None):  
#     if not isinstance(parameters, DataChannel): 
#       raise Exception, "ERROR DCO_pointer must be initialized with a DataChannel object! Got this: {}".format(parameters)
#     self.parameters=parameters    
#     self.label=label

#   def short(self):   
#     if not self.label is None: return self.label
#     return '{}'.format(self.parameters if not self.parameters is None else '')  #the whole key of the DC
#   def get_dataframe(self):
#     return self.parameters.out() if not self.parameters is None else None
#   def action(self, df): raise Exception, "'Pointer' component can be only found first in a Data Channel!"
#   def key(self): return self.parameters.key() if not self.parameters is None else 'pointer:None'



#### other DCOs
class DCO_select(DataChannelOperation):
  name='select'
  """Init with: column name to be selected. optionally, multiple col names, comma-separated. 
  Typically the first one is 'Node';  position, 1-based indexes can be also queried using '$'  for example Node,$3 
  The ":" special character means: all other fields not explicitly specified in this select. This is useful to reorder columns; E.g: you want to bring column A as first:  'select:A,:'
  """
  def action(self, df):    
    fields=self.interpreted_params(df).split(',')   
    if ':' in fields:
      explicitly_selected=set([f for f in fields if f!=':'])
      others=[f for f in df.columns if not f in explicitly_selected]
      for i in range(len(fields)-1, -1, -1): #parsing positions backwards
        if fields[i]==':': 
          fields.pop(i)
          for f in others: fields.insert(i, f)
    return df[fields]  

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
  enging='numexpr'

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

class DCO_aggregate(DataChannelOperation):           ### Finish/add transform
  name='aggregate'
  """Init with:                 field&operation   e.g.   ML&sum
     or with multiple fields:   f1,f2,f3&mean
  'operation' is passed as a string to the aggregate method of pandas grouped elements; all functions available for dataframes are available """
  def action(self, df):
    fields, operation=self.interpreted_params(df).split('&') 
    if fields.count(','): fields=fields.split(',')
    return df.groupby(fields).aggregate(operation).reset_index()

class DCO_join(DataChannelOperation):
  name='join'
  """Init with:             db_name&field    e.g.  Metabolome&Node
  Default field is actually 'Node', in that case this can be omitted
  """
  def action(self, df):    
    dbname, field=self.interpreted_params(df).split('&') 
    if not field: field='Node'         #if field.count(','): field=field.split(',')  #needs multi index
    df2=self.container.master().features().get_dataframe(dbname)
    if df2.index.name!=field:      df2=df2.set_index(field)
    return df.join(df2, on=field)
DCO=DataChannelOperation

###################################################################################################################
available_DCOs=['database', 'cache','retrieve','define','call', 'select', 'filter', 'process', 'rename', 'aggregate', 'join']
DCO_name2class={'database':DCO_database, 
                'retrieve':DCO_retrieve, 'cache':DCO_cache, 'define':DCO_define, 'call':DCO_call,
                'select':DCO_select, 'filter':DCO_filter, 'var':DCO_var, 'compute':DCO_compute,
                'process':DCO_process, 'rename':DCO_rename, 'aggregate':DCO_aggregate, 'join':DCO_join,
                'antenna':DCO_antenna, 'trace':DCO_trace, 'group':DCO_group,
}
###################################################################################################################

from .master import *

