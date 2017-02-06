import pandas as pd
from PyQt4 import QtCore

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

forbidden_chars=set(':,=><&')
def check_forbidden_characters(txt, chars=forbidden_chars):
  """Returns True if everything is ok; returns False if any of the forbidden characters is detected in the input txt """
  for c in txt: 
    if c in chars: return False
  return True

def replace_forbidden_characters(txt, chars=forbidden_chars, to='_'):
  """Returns True if everything is ok; returns False if any of the forbidden characters is detected in the input txt """
  return ''.join([c  if not c in chars else to    for c in txt])

###################################################################################################################
###################################################################################################################
class DataChannel(QtCore.QObject):
  """ Chain of manipulators (type: DataChannelOperation) to go from a DataFrame to any data shape.
Init with:
  -master_link:    MasterContained associated to a AnnotatedTree
  -chain:        optional, list of instances of DataChannelOperation subclasses. The first one MUST be DCO_database
The chain can be populated with self.append(DCO), or by editing self.chain by any mean
Main method: self.out()  --> this runs all the operations in order and output a pd.DataFrame or pd.DataSeries"""
  #default_pre =[]
  #default_post=[]
  signal_dc_changed=QtCore.pyqtSignal()
  def __init__(self, master_link, chain=None, from_key=None): #prechain=default_pre, postchain=default_post, 
    super(DataChannel, self).__init__()
    self.master_link=master_link
    self.validated=None
    if from_key is None:
      # self.chain=prechain
      # self.pre=len(prechain)  
      # self.chain.extend(chain)
      # self.post=len(postchain)
      # self.chain.extend(postchain)    
      if chain is None: chain=[]
      self.chain=chain
    else:
      self.chain=[]; #self.pre=0; self.post=0 
      for dco_s in from_key.split(' |>'): 
        try:
          dco_name=   dco_s.split(':')[0]
          parameters= dco_s[len(dco_name)+1:]
          dco_class=  DCO_name2class[dco_name]
          #if not dco_class.parameters_class is str: 
          #  parameters=eval(parameters) dco_class.parameters_class
          dco= dco_class(parameters)
          self.chain.append(dco)
        except:           raise Exception, "DataChannel ERROR initializing invalid Key: {k}".format(k=from_key)

  def copy(self, index_start=None, index_end=None): #, keep_fixed=False):
    """ Return a copy of this DC. Optionally provide slicing indexes start and end (0-based)
    With option keep_fixed, the DCO which are part of the PRE or POST will retain this property (i.e., read-only)"""
    k=self.key()
    if not (index_start is None and index_end is None):
      if index_start is None: index_start=0
      if index_end is None:   index_end=len(self)-1
      k=' |>'.join( k.split(' |>')[index_start:index_end+1] )
    else: 
      index_start=0
      index_end=len(self)-1
    # dc=DataChannel(self.master_link, from_key=k)
    # if keep_fixed:
    #   dc.pre=max([self.pre-index_start, 0])
    #   dc.post=max([self.post-len(self)-index_end-1, 0])
    return dc

  def __iter__(self):        return self.chain.__iter__()
  def __len__(self):         return self.chain.__len__()
  def Master(self):          return self.master_link

  def out(self):
    """Standard function to start the flux in the DC and get the data coming out. """
    if not self.chain: return None #raise Exception, "ERROR DataChannel is empty!"
    df=self.chain[0].get_dataframe(self.master_link)
    for dco in self.chain[1:]:            df=dco.channel_dataframe(df)
    return df

  def run_validation(self):
    """the DC is simply tested; in this case, None is returned is everything is ok; 
 otherwise a tuple (index, e) is returned; index is the index of the DCO in this DC chain that failed; e is the exception raised"""
    try:  
      if not self.chain: raise Exception, "ERROR DataChannel is empty!"
    except Exception as e:    return (0, e)
    try:        df=self.chain[0].get_dataframe(self.master_link)
    except Exception as  e:   return (0, e)
    for i, dco in enumerate(self.chain[1:]):
      try:      df=dco.channel_dataframe(df)
      except Exception as e:  return (i+1, e)
    try:      self.additional_validation(df)
    except Exception as e:  return ( len(self.chain)-1, e )
    return None

  def additional_validation(self, out):
    """ Define this function in subclasses to add layers of validation at the end of the DC; the out that will be passed as argument is equivalent to what is output by out()
    If anything is wrong with it (e.g. its data shape, or any necessary columns are missing) then raise an Exception"""
    pass

  def validate(self):
    self.validated=self.run_validation()
    return self.validated

  # def is_pre(self, index):  return self.pre>index
  # def is_post(self, index): return index>len(self)-self.post-1

  def concatenate(self, dc, index=None):
    if index is None:
      for dco in dc:                  self.append(dco)
    else:  
      for i, dco in enumerate(dc):    self.insert(index+i, dco)

  def append(self, dco):            
    #if self.post: raise Exception, "ERROR this DC has fixed post, can't append to it!"
    self.chain.append(dco)
    self.notify_modification()
  def insert(self, index, dco):     
    #print 'insert', index, dco, self.is_pre(index), self.is_post(index-1)
    #if self.is_pre(index) or self.is_post(index-1):    
    #  raise Exception, "ERROR trying to extend this DC: it has fixed pre or post!"
    self.chain.insert(index, dco)
    self.notify_modification()
  def pop(self, index=None):             
    if index is None: index=len(self)-1
    #if self.is_pre(index) or self.is_post(index):
    #  raise Exception, "ERROR trying to pop an element from this DC: it has fixed pre or post!"
    self.chain.pop(index) 
    self.notify_modification()

  def notify_modification(self):            self.signal_dc_changed.emit()
  def summary(self):                        return ' |>'.join(map(lambda x:x.summary(), self.chain))
  def get_available_dataframes(self):       return self.Master().features().get_available_dataframes()
  __repr__=summary
  key=summary
DC=DataChannel

class FeatureSelector(DataChannel):
  def additional_validation(self, out):
    shape=df.shape
    if len(shape)!=2: raise Exception, "ERROR wrong data shape: {d}".format(shape)
    r,c=shape
    if c!=2: raise Exception, "ERROR There must be only two columns! Wrong data shape: {d}".format(shape)
    



###################################################################################################################
class DataChannelOperation(object):
  """ Base class for all elementary operations allowed in a DataChannel"""
  name='EmptyDCO'
  parameters_class=str
  def __init__(self, parameters=None):  self.parameters=parameters
      #for k in kargs: self.parameters[k]=kargs[k]
  def update(self, parameters):    self.parameters=parameters   
  def channel_dataframe(self, df): return df if self.parameters is None else    self.action(df)
  def summary(self): return self.name+':{p}'.format(p=self.parameters)
  def short(self):   return '{}'.format(self.parameters if not self.parameters is None else '')
  def get_dataframe(self, master_link): raise Exception, "Data Channels must begin with a 'Database' component!"
  __repr__=summary

class DCO_database(DataChannelOperation):
  """Init with: Database name to be extracted from DataContainer """
  name='database'
  def get_dataframe(self, master_link): return master_link.features().get_dataframe(self.parameters) if not self.parameters is None else None
  def action(self, df): raise Exception, "'Database' component can be only found first in a Data Channel!"

class DCO_select(DataChannelOperation):
  name='select'
  """Init with: column name to be selected. optionally, multiple col names, comma-separated.
  Typically the first one is 'Node' """
  def action(self, df):    return df[self.parameters.split(',')]  #[x.strip() for x in self.parameters.split(',')] ]

class DCO_filter(DataChannelOperation):
  name='filter'
  """Init with: query string. Examples:     
      DCO_filter( 'Node.startwith("P")' )  
      DCO_filter( 'ML > 100' )    """
  def action(self, df):    return df.query(self.parameters)

class DCO_process(DataChannelOperation):
  name='process'
  """Init with: eval string. Examples:     
      DCO_process( 'ML+FTM' )  
      DCO_process( 'c=ML/10' )    """
  def contain_assignment(self):
    index=0;      lens=len(self.parameters)
    accepted_pre=set('><=!'); accepted_post=set('=')
    f=self.parameters.find('=', index)
    while f!=-1:
      if f==0 or f==lens-1: raise Exception, "ERROR invalid expression! {e}".format(e=self.parameters)
      if not ( self.parameters[f-1] in accepted_pre or self.parameters[f+1] in accepted_post ):        return True
      index+=1
      f=self.parameters.find('=', index)
    return False
      
  def action(self, df):    
    use_inplace=not self.contain_assignment()
    return df.eval(self.parameters, inplace=use_inplace)

class DCO_rename(DataChannelOperation):
  name='rename'
  """Init with:  oldField1>newField1
     or with:    oldField1>newField1,oldField2>newField2  """
  def action(self, df):
    rename_hash={}
    for pair in self.parameters.split(','):  
      oldK, newK= pair.split('>')
      rename_hash[oldK]=newK
    return df.rename(columns=rename_hash)

class DCO_aggregate(DataChannelOperation):
  name='aggregate'
  """Init with:                 field&operation   e.g.   ML&sum
     or with multiple fields:   f1,f2,f3&mean
  'operation' is passed as a string to the aggregate method of pandas grouped elements; all functions available for dataframes are available """
  def action(self, df):
    fields, operation=self.parameters.split('&') 
    if fields.count(','): fields=fields.split(',')
    return df.groupby(fields).aggregate(operation).reset_index()
DCO=DataChannelOperation

###################################################################################################################
available_DCOs=['database', 'select', 'filter', 'process', 'rename', 'aggregate']
DCO_name2class={'database':DCO_database, 'select':DCO_select, 'filter':DCO_filter, 
                'process':DCO_process, 'rename':DCO_rename, 'aggregate':DCO_aggregate}
###################################################################################################################


