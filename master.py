from PyQt4   import QtCore
from .data  import *
from .common import *

class MasterContainer(dict):
  """ Data storage object; there is one per tree, contains all the information for the GUI (e.g. what is selected, what windows are opened), as well as all features and associated statistics.
  Basically it is just a linker to a number of Manager objects, each of a different subclass to manipulate different kinds of data:

 -windows()    ->  WindowManager     stores pyqt objects for open windows
 -selections() ->  SelectionManager  stores saved selections of nodes and features
 -session()    ->  SessionManager    similar to selections, but for currently active selections (selected, highlighted nodes etc)
 -features()   ->  FeatureManager    manages all features loaded into the tree, as well as associated distances, processing functions etc
 -columns()    ->  ColumnManager     keeps track of FaceControllers, i.e. which columns are present in the main window (ETE)
 -stats()      ->  StatManager       stores results for statistical tests, generally among pairs or groups of features
 -colors()     ->  ColormapManager   stores colormaps, which are ways to define colors for nodes

 -tree()       ->  returns the root of the tree to which this DataContainer is linked
 -scene()      ->  returns the pyqt4 scene
 -redraw()     ->  force full redraw of the main ETE window
 -clipboard()  ->  returns a link to the system clipboard
 """
  def __init__(self, tree_link):
    self['tree_link']=tree_link
    for n in tree_link.traverse(): n.master_link=self
    #self['stats']=     StatManager(data_link=self)
    #self['session']=   SessionManager(data_link=self)
    #self['selections']=SelectionManager(data_link=self)
    self['features']=  FeatureManager(master_link=self)     
    #self['columns']=   ColumnManager(data_link=self)   #  column_id ->  FaceController or  name -> FaceController
    self['windows']=   WindowManager(master_link=self)
    #self['views']  =   ViewManager(data_link=self)
    #self['colors']=    ColormapManager(data_link=self)

  def windows(self):     return self['windows']
  # def plots(self):       return [x for x in  self.windows() if isinstance(self.windows().get_window(x), TreedexWindow)]
  # def stats(self):       return self['stats']
  def features(self):    return self['features']
  # def session(self):     return self['session']
  # def selections(self):  return self['selections']
  # def columns(self):     return self['columns']
  # def colors(self):      return self['colors']
  # def redraw(self):      
  #   fc=self.columns().get_column(index=1)
  #   fc.drawn={}
  #   fc.redraw()
  # def scene(self):       return self.columns().get_column(index=1).title_item.scene() 
  def tree(self):        return self['tree_link']
  def clipboard(self):   return QtGui.QApplication.clipboard()
  #def init_windows(self): return self.windows().init_windows()

class Manager(QtCore.QObject):
  def __init__(self, master_link):    
    super(Manager, self).__init__()
    self.master_link=master_link
    #self.key =''
  def Master(self):                   return self.master_link


class WindowManager(Manager):
  def __init__(self, master_link): 
    Manager.__init__(self, master_link)
    self.windows={} 
    self.category2index={}

  def add_window(self, window, window_name=None, category=None):
    """Stores a window (QWidget) in the self.windows hash.  Two ways to use this:
     -name:    provides a unique identifier for the window. Thought for windows for which it makes sense to have only one at any given moment.      
       Before creating one such window, do: 
       if self.Master().windows().has_window(  win_name  ):    self.Master().windows().get_window(  win_name  ).activateWindow()
       else:         ##create window and add it
     -category:   windows for which you may have multiple. An index is automatically generated. The indexes are not recycled, even if the other windows are closed """
    if window_name is None:
      if not category in self.category2index:    category_index=1
      else:                                      category_index=self.category2index[category]+1
      self.category2index[category]=category_index
      window_name=category+'.'+str(category_index)    
    window.window_name=window_name 
    if self.has_window(window_name): raise Exception, "ERROR add_window: A window with this name '{}' already exists!".format(window_name)
    print 'adding window, name:' +str(window_name)    
    self.windows[window_name]=window   
  
  def has_window(self, window_name): return window_name in self.windows
  def get_window(self, window_name): return self.windows[window_name]
  def remove_window(self, window):   
    """ This is invoked by the closeEvent of every TreedexWindow"""
    print 'remove window '+window.window_name
    del self.windows[window.window_name]
    #print 'remove window, after:' +str(self.windows)    

###################################################################################################################
class FeatureManager(Manager):
  """ """
  signal_dataframe_list_changed=QtCore.pyqtSignal()
  #ignored_features=set(['species', 'name', 'support', 'dist'])
  #virtual_features=set(['Tree'])
  def __init__(self, master_link): 
    Manager.__init__(self, master_link)
    self.dataframes={}     #name to dataframe
    self.data_channels={}  #name to datachannel
    # self.feature2nodes={} # feature_name -> NodeSelector    
    # self.distance2function={}   
    # self.mds_cache=         CachedExecutor()
    # self.anc_feature_cache= CachedExecutor()
    ### add general functions in geometry
    #self.add_distance_function('no distance defined', lambda x,y:0)

    # self.add_distance_function('difference',          lambda x,y:abs(x-y))
    # self.add_distance_function('difference of log10', lambda x,y:abs(log10(x)-log10(y)) )
    # self.add_distance_function('hamming',           hamming_distance)
    # self.add_distance_function('gapless_hamming',   gapless_hamming)
    # self.add_distance_function('blosum',            blosum_distance)
    # self.add_distance_function('gapless_blosum',    gapless_blosum)
    # self.add_distance_function('distance_in_tree',  PhyloTree.get_distance, takes_node_args=True)

  def get_available_dataframes(self):   return sorted(self.dataframes.keys())
  def add_dataframe(self, df, overwrite=False):          
    if not isinstance(df, DataFrame): raise Exception, "ERROR only Treedex DataFrame instances can be added!"
    if df.name() in self.dataframes:  
      if not overwrite: raise Exception, "ERROR a DataFrame with the same name '{n}' already exists!".format(n=df.name())
    self.dataframes[df.name()]=df
    self.signal_dataframe_list_changed.emit()
  def remove_dataframe(self, name):          
    del self.dataframes[name]
    self.signal_dataframe_list_changed.emit()
  def get_dataframe(self, name):        return self.dataframes[name]
  def has_dataframe(self, name):        return name in self.dataframes


#   def get_nodes_with_feature(self, feature_selector, nodes=None):
#     """If nodes is provided, it is used as a superset of possible nodes to return  """
#     return self.get_nodes_with_features([feature_selector], nodes)

#   def get_nodes_with_features(self, feature_selectors, nodes=None):
#     """Same as above but with a list of features; If nodes is provided, it is used as a superset of possible nodes to return  """
#     for feature_selector in feature_selectors:
#       if not feature_selector.feature_name in self.virtual_features:
#         ns=self.feature2nodes[feature_selector.feature_name] if feature_selector.feature_name in self.feature2nodes else NodeSelector([])
#       else: 
#         ns=self.Data().selections().get_node_selection(selection_name='All nodes')
#       if nodes is None:    nodes=ns
#       else:                nodes=nodes.intersection(ns)
#     return nodes if not nodes is None else NodeSelector([])

#   def get_feature_for_node(self, feature_selector, node, processing_fn=None):
# #    print node
#     if not node.is_leaf(): raise Exception
#     if processing_fn is None and feature_selector.processing: processing_fn=feature_selector.processing
#     #write((node.name, node.features), 1)
#     fv= getattr(node, feature_selector.feature_name)
#     return fv if processing_fn is None else processing_fn(fv)

#   def get_feature_for_ancestor(self, feature_selector, node, processing_fn=None): 
#     return self.get_reconstructed_feature_in_ancestors(feature_selector, processing_fn=processing_fn)[node]

#   def get_reconstructed_feature_in_ancestors(self, feature_selector, processing_fn=None):
#     return self.anc_feature_cache.cache_execute(self.run_reconstructed_feature_in_ancestors, feature_selector, processing_fn)
    
#   def run_reconstructed_feature_in_ancestors(self, feature_selector, processing_fn=None):
#     out_dict={}
#     leaves=self.get_nodes_with_feature(feature_selector)
#     anc_nodes=leaves.walk_tree(up=True, only_ancestors=True)
#     for n in leaves: 
#       parent=n.up
#       while parent and not parent in out_dict: #going up as long as we can; if any sister has not been parsed yet, go to next n
#         sisters=[x for x in parent.children if x in leaves or x in anc_nodes]
#         if any([not  (x.is_leaf() or x in out_dict)  for x in sisters]): break   
#         #write('parent: '+parent.name, 1, how='blue')
#         #write('children: '+join([n.name+' '+str(n.dist) for n in sisters], ' '), 1, how='magenta')
#         tot_dist_sisters=   sum( [x.dist for x in sisters] )
#         proportion_per_sister=  [tot_dist_sisters/x.dist  for x in sisters]
#         tot_weigth=         sum(proportion_per_sister)
#         weight_per_sister    =  [w/tot_weigth for w in proportion_per_sister]
#         out_dict[parent]=   sum([( float(self.get_feature_for_node(feature_selector, x, processing_fn))   if x.is_leaf() else out_dict[x])*weight_per_sister[sis_i]  for sis_i, x in enumerate(sisters)])
#         parent=parent.up
#     return out_dict


# #### to rethink upon panda transition:
#   def get_features_in_node(self, node):       
#     #write((node.name, node.features), 1)
#     return node.features.difference(self.ignored_features).union(self.virtual_features)

#   def get_common_features_in_nodes(self, nodes):
#     #write('get common features, n nodes='+str(len(nodes)), 1, how='blue')
#     feats=None
#     for n in nodes: 
#       if feats is None: feats=self.get_features_in_node(n)
#       else:             feats=feats.intersection(self.get_features_in_node(n))
#     return feats    if not feats is None else set()

#   def get_any_features_in_nodes(self, nodes):
#     #write('get common features, n nodes='+str(len(nodes)), 1, how='blue')
#     feats=None
#     for n in nodes: 
#       if feats is None: feats=self.get_features_in_node(n)
#       else:             feats=feats.union(self.get_features_in_node(n))
#     return feats    if not feats is None else set()

#   def add_feature_to_node(self, feature_name, feature_value, node): 
#     """ Will require form rewriting on panda transition"""
#     #write(('add feat to node', feature_name, node.name), 1)
#     Tree.add_feature(node, feature_name, feature_value)     # this add to node.features
#     if not feature_name in self.feature2nodes: self.feature2nodes[feature_name]=NodeSelector()
#     self.feature2nodes[feature_name].add_node(node)

#   def remove_feature_from_node(self, feature_name, node):
#     if not feature_name in self.feature2nodes or not node in self.feature2nodes[feature_value]:
#       raise Exception, "FeatureManager->remove_feature_from_node ERROR node {n} does not have feature {f} ".format(n=node.name, f=feature_name)
#     self.feature2nodes[feature_name].remove(node)
#     if not self.feature2nodes[feature_name]: del self.feature2nodes[feature_name]
# ############# done 

#   def get_all_features(self):
#     return set(self.feature2nodes.keys())

#   # how to set a feature filter??
#   def add_distance_function(self, name, function, takes_node_args=False): 
#     if name in self.distance2function: raise Exception, "FeatureManager->add_distance_function ERROR a function with this name already exists: "+str(name)
#     new_fn= lambda *args,**kargs : function(*args, **kargs)    ## doing this to make sure I can add an attribute to the function (see line below)
#     new_fn.takes_node_args=takes_node_args
#     self.distance2function[name] = new_fn

#   def get_distance_function(self, name): return self.distance2function[name]
  
#   def get_distance_between_nodes(self, node1, node2, distance_name, feature_selector=None):
#     ## implement caching here!
#     dist_fn= self.get_distance_function(distance_name)
#     if    dist_fn.takes_node_args: 
#       return dist_fn(node1, node2)
#     else:
#       if feature_selector is None: raise Exception, "DistanceManager->get_distance_between_nodes ERROR you must provide a feature_selector! (unless function has flag takes_node_args)"
#       return dist_fn( self.Data().features().get_feature_for_node(feature_selector, node1), self.Data().features().get_feature_for_node(feature_selector, node2) )
      
#   def get_mds(self, n_dimensions, nodes, distance_name, feature_selector=None):
#     """Computes a MDS analysis to the specified number of dimensions, computed on these nodes as points, computing the distances using distance_name and feature_selector (which is not required only if the distance specified has a True flag takes_node_args
#     Returns a dictionary with K: node -> V: the new MDS coordinates as np.array
#     The MDS space is scaled, to reside between the global variables MDS_DIMENSION_MIN and MDS_DIMENSION_MAX"""
#     return self.mds_cache.cache_execute(self.run_mds, n_dimensions, nodes, distance_name, feature_selector)

#   def run_mds(self, n_dimensions, nodes, distance_name, feature_selector=None):
#     distance_matrix= np.array( [ [self.get_distance_between_nodes(inode, jnode, distance_name=distance_name, feature_selector=feature_selector)  for jnode in nodes] for inode in nodes] )
#     coords_matrix  = mds_coordinate_matrix(distance_matrix, n_dimensions)
#     out_dict={ node: coords_matrix[index]    for index, node in enumerate(nodes) }
#     return out_dict

#   def get_mds_ancestral(self, n_dimensions, nodes, distance_name, feature_selector=None):
#     """Returns the positions of all ancestral nodes (e.g., non leafs) in the MDS with the same arguments; nodes provided are leafs; anc.nodes returned as key of a dictionary are all nodes encountered while going back to root from any of leaf inputs.
#     Returns a dictionary with K: node -> V: the new MDS coordinates as np.array
#     The MDS space is scaled, to reside between the global variables MDS_DIMENSION_MIN and MDS_DIMENSION_MAX"""
#     return self.mds_cache.cache_execute(self.run_mds_ancestral, n_dimensions, nodes, distance_name, feature_selector)

#   def run_mds_ancestral(self, n_dimensions, nodes, distance_name, feature_selector=None):
#     mds_dict=self.get_mds(n_dimensions, nodes, distance_name, feature_selector)
#     out_dict={}
#     all_nodes=nodes.walk_tree(up=True)
#     anc_nodes=NodeSelector([n for n in all_nodes if not n.is_leaf()])   
#     for n in nodes: 
#       parent=n.up
#       while parent and not parent in out_dict: #going up as long as we can; if any sister has not been parsed yet, go to next n
#         sisters=[x for x in parent.children if x in all_nodes]
#         if any([not  (x.is_leaf() or x in out_dict)  for x in sisters]): break   
#         coords=[]
#         #write('parent: '+parent.name, 1, how='blue')
#         #write('children: '+join([n.name+' '+str(n.dist) for n in sisters], ' '), 1, how='magenta')
#         tot_dist_sisters=   sum( [x.dist for x in sisters] )
#         proportion_per_sister=  [tot_dist_sisters/x.dist  for x in sisters]
#         tot_weigth=         sum(proportion_per_sister)
#         weight_per_sister    =  [w/tot_weigth for w in proportion_per_sister]
#         for i in range(n_dimensions):
#           coords.append(sum([(mds_dict[x][i] if x.is_leaf() else out_dict[x][i])*weight_per_sister[sis_i]  for sis_i, x in enumerate(sisters)]))
#         out_dict[parent]=coords
#         parent=parent.up
#     return out_dict


#   def get_example_features(self, feature_selector, n=3):
#     feature_examples=[]
#     for n in self.get_nodes_with_feature(feature_selector):
#       feature_examples.append(n.get_feature(feature_selector))
#       if len(feature_examples)>n: break
#     return feature_examples

#   def get_feature_class(self, feature_selector):
#     examples=self.get_example_features(feature_selector)
#     if not examples or all([e is None for e in examples]): return None
#     for c in (str, int, float, bool): 
#       if all([isinstance(e,c) or e is None for e in examples]): return c

#     if all([isinstance(e,float ) or isinstance(e,int) or e is None for e in examples]): return float
#     print [ [type(e),e] for e in examples  ]
#     #raise Exception, 'mixed class type!'
#     return None  #mixed classes?      

#   def get_available_distances_for_feature(self, feature_selector=None, feature_example=None):
#     """ Try and except strategy to test distances"""
#     if feature_selector.feature_name=='Tree': return ['distance_in_tree'] #, 'tree_order']

#     if not feature_example is None:  feature_examples=[feature_example]
#     else:                            feature_examples=self.get_example_features(feature_selector) 
#     possible_distances=set(self.distance2function.keys()).difference(set(['distance_in_tree']))    
#     fe1= feature_examples[0]
#     remove={}
#     if len(feature_examples)==1: feature_examples=[fe1, fe1]
#     for fe2 in feature_examples[1:]:
#       for d in possible_distances:
#         try: dist=self.get_distance_function(d); dist(fe1, fe2)
#         except: remove[d]=1
#     return sorted(   possible_distances.difference( set(remove) )  )

#   def load_feature_file(self, filename, field_separator='\t', speciesid=('col', 'index', 1), conversion={None:'AUTO'}, skip_values=set(['NA', 'None', '']), add_faces=False, log_box=None):
#     """ Load a tabular file as features
#     add_faces: if bool(add_faces) -> we add a columnview element for each feature  
#       you can provide a dict to specify more inputs, e.g. title, barwidth, digits etc
# """

#     row_or_col, index_or_name, with_value=speciesid
#     print 'trying to load: ', filename
#     field_names=None
#     added_feats_values=0
#     added_feats=set()
#     species_not_found=[]
#     species2node={}
#     if row_or_col!='col': raise Exception

#     for line in open(filename):
#       for lin in line[:-1].split('\r'):
#         splt=lin.split(field_separator)
#         if lin.startswith('#') or not splt or splt==['']: continue
#         if field_names is None: 
#           field_names=splt
#           if row_or_col=='col':
#             if   index_or_name=='name':
#               species_col_index=field_names.index(with_value)
#             elif index_or_name=='index':
#               species_col_index=int(with_value)-1 ### 1 to 0 basis
#               assert( species_col_index < len(field_names) )
#           skip_index= set([species_col_index])
#           write('defined fields'+str(field_names), 1, how='red')
#           continue
#         #write(splt, 1, how='yellow')
#         species=    splt[species_col_index]

#         try:         
#           if not species in species2node:
#             node=self.Data().tree()&species
#             species2node[species]=node
#           else:             node=species2node[species]
#         except:      species_not_found.append(species); continue

#         for index, value in enumerate(splt):
#           if index in skip_index: continue
#           feat_name=field_names[index]
#           if conversion[None]=='AUTO':            feat_value=auto_convert(value)
#           ## improve this! 
#           else: raise Exception, " ... "         
#           if feat_value in skip_values: continue
#           added_feats.add(feat_name)
#           added_feats_values+=1
#           print 'adding ', species, feat_name, feat_value
#           node.add_feature(feat_name, feat_value)

#     if add_faces:
#       kargs=add_faces if not add_faces in (True, 1) else {}
#       kargs['late']=1
#       if not 'colors' in kargs:        kargs['colors']=['black', 'white']
#       if not 'barwidth' in kargs:      kargs['barwidth']=40      
#       #parts=kargs['parts']

#       ### extract this as automatic procedure
#       for feat_name in sorted(added_feats):
#         fs=FeatureSelector(feature_name=feat_name)
#         ns=self.Data().features().get_nodes_with_feature(fs)
#         fclass=self.Data().features().get_feature_class(fs)
#         title=str(fs)
#         ##
        
#         if add_faces['distance_name']=='auto':
#           poss_distances=self.Data().features().get_available_distances_for_feature(fs)
#           write( (feat_name, fclass, poss_distances), 1, how='yellow')
#           distance_name=poss_distances[0]
#           kargs['distance_name']=distance_name
#         # title=feat_name
#         # if 1: # fclass in (float, int):
#           #if   fclass in [float, int]:           parts.append('bar')
#           #elif fclass == bool:                   parts.append('colormap')
#         # else:
#         #   dist='no distance defined'
#         #  fc=DistanceFaceController(fs, parts=parts, nodes=ns, title=title,  **kargs)
#         fc=DistanceFaceController(fs, nodes=ns,  title=title, description=title, **kargs)
#         fc.set_reference('min')


#       if added_feats: self.Data().tree().redraw()
          
#     warning= '' if not species_not_found else 'WARNING these species were not found: '+join(species_not_found, ', ')+'\n\n'
#     if len(warning)>400: warning=warning[:350]+'\n...\n'+warning[-50:]

#     if not added_feats: message='{w}:(  -- No features were added'.format(w=warning)
#     else: message='{w}These features were added: {fs}\n\nDone! {ns} different features were added, with a total of {vs} values added to the tree'.format(ns=len(added_feats), vs=added_feats_values, w=warning, fs=join(sorted(added_feats), ', '))
#     if log_box: log_box.setText(message)
#     else:       printerr(message, 1)
        
      

#   def get_available_processing_for_feature(self, feature_selector):
#     """ No filter right now! need to finish!"""
#     #if 'distance_name'=='tree_order': return []
#     return ['MDS1', 'MDS2', 'MDS3', 'raw value', 'log10']

#   def get_available_parameters(self, processing_name, feature_selector=None):
#     """ only MDS thought now! 
#     returns:  [  ['parameter name':[..options..]]  ]"""
#     if   not processing_name: return []
#     elif     processing_name.startswith('MDS'):
#       n_dimensions=int(processing_name[3:])
#       index_list=[]
#       for  i in  range(1, n_dimensions+1):         index_list.append(str(i))
#       for  i in  range(1, n_dimensions+1):         index_list.append(str(i)+'(-)')        
#       available_distances=self.get_available_distances_for_feature(feature_selector)
#       return [ ['Distance', available_distances],  ['Dimension', index_list ]     ]
#     elif  processing_name=='raw value':
#       return []
#     elif  processing_name=='log10':
#       return []
#     else:
#       raise Exception, "get_available_parameters_for_processing only MDS supported now!"
