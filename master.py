from PyQt4   import QtCore
from .common import *
from .data  import *
from .facecontroller import *
from .widgets import *
from  colorsys import rgb_to_hsv, hsv_to_rgb
## see imports below

class MasterContainer(dict, DC_container):
  """ Data storage object; there is one per tree, contains all the information for the GUI (e.g. what is selected, what windows are opened), as well as all features and associated statistics.
  How to start Treedex, given a newick tree file called tree_file, and a comma-separated data file with a 'Species' column called csv_file:

master=MasterContainer()
master.add_tree('default', Tree(tree_file)    )
df=pd.DataFrame( data=pd.read_csv(csv_file, sep=',') )
master.add_database(df, name='someName', node_field='Species')
master.show()

  Basically MasterContainer is just a linker to a number of Manager objects, each of a different subclass to manipulate different kinds of data:
 -windows()    ->  WindowManager     stores pyqt objects for open windows
 -selections() ->  SelectionManager  stores saved selections of nodes and features
 -columns()    ->  ColumnManager     keeps track of FaceControllers, i.e. which columns are present in the main window (ETE)
 -colors()     ->  ColormapManager   stores colormaps, which are ways to define colors for nodes
 -trees()      ->  TreeManager       stores the tree(s) to which this DataContainer is linked
 -data()       ->  MemoryManager     stores all the data in Pandas format, and manage efficient caching
 -scene()      ->  returns the pyqt4 scene
 -clipboard()  ->  returns a link to the system clipboard
 """
  def __init__(self):
    self.container=None
    DC_container.__init__(self)  
    self['data']=      MemoryManager(master_link=self)
    self['selections']=SelectionManager(master_link=self)
    self['columns']=   ColumnManager(master_link=self)   #  column_id ->  FaceController or  name -> FaceController
    self['windows']=   WindowManager(master_link=self)
    self['trees']=     TreeManager(master_link=self)
    self['colors']=    ColorManager(master_link=self)
    self['qapp']=      None
    f=lambda s:   self.trees().update_node_selection_items() if s=='Selected nodes'     else  \
                ( self.trees().update_node_highlight_items() if s=='Highlighted nodes'  else None )
    self.selections().signal_selection_changed.connect( f )
  def add_tree(self, name, tree): return self.trees().add_tree(name, tree)
  def add_database(self, *args, **kargs):     return self.data().add_database(*args, **kargs)
  def windows(self):     return self['windows']
  def selections(self):  return self['selections']
  def columns(self):     return self['columns']
  def colors(self):      return self['colors']
  # def scene(self):       return self.columns().get_column(index=1).title_item.scene() 
  def data(self):        return self['data']
  def trees(self):       return self['trees']
  def clipboard(self):   return QtGui.QApplication.clipboard()
  def qapp(self):        return self['qapp']
  def show(self, qapp=None):       
    dc=DataChannel(self)  #add tables and scatterplot if you want them opened
    dc.muted=True
    #dc.append(DCO_empty())
    dc.append(DCO_database('LifeHistory'))
    dc.append(DCO_select('Node,AdultWeight,MaxLifespan,MLres'))
    dc.append(DCO_log('10|@n|log(@)|r')) 
    dc.append(DCO_trace('WeightedAv'))
    dc.append(DCO_treeInfo('time'))
    dc.append(DCO_table('table1'))
    dc.append(DCO_plot3D('3D.1'))
    dc.append(DCO_newline())

    dc.append(DCO_database('Ions'))
    dc.append(DCO_filter('Tissue=="Liver"'))    
    dc.append(DCO_select('Node,Se78'))
    dc.append(DCO_rename('Selenium=Se78'))
    dc.append(DCO_join('LifeHistory'))
    dc.append(DCO_scatterplot('plot1'))
    dc.append(DCO_newline())


    dc.append(DCO_database('Metabolome'))
    dc.append(DCO_scatterplot('plot2'))
    dc.append(DCO_filter('Tissue=="Liver"'))    
    dc.append(DCO_table('table2'))
    dc.append(DCO_scatterplot('plot3'))






    #dc.append(DCO_scatterplot('plot1'))
    #dc.append(DCO_plot3D('3D.1'))
    if qapp is None:      qapp=QtGui.QApplication(['Treedex'])
    self['qapp']=qapp
    win=DataChannelWidget(dc)  # replace this with analysis notebook
    win.setWindowTitle('Data Channel #1')
    win.show()
    dc.muted=False    
    dc.out()    #triggering graphics since passing through DCO_table and DCO_scatterplot
    return self.trees().default_tree.show(qapp=qapp)

class Manager(QtCore.QObject):
  def __init__(self, master_link):    
    super(Manager, self).__init__()
    self.master_link=master_link
    #self.key =''
  #def master(self):                   return self.master_link

class TreeManager(Manager):
  signal_tree_list_changed=QtCore.pyqtSignal()
  def __init__(self, master_link): 
    Manager.__init__(self, master_link)
    self.trees={} 
    self.select_items={}  #node -> rectItem
    self.highlight_items={}  #node -> rectItem    
    self.default_tree=None

  def get_available_trees(self):    
    return [self.default_tree.tree_name] + sorted([i for i in self.trees.keys()  if i!=self.default_tree.tree_name])
  
  def add_tree(self, name, tree):
    #if not isinstance(tree, AnnotatedTree):
    tree=AnnotatedTree( newick=tree.write(), master_link=self.master_link, tree_name=name )  #this will call update_tree_order

    if not self.default_tree: self.default_tree=tree
    self.trees[name]=tree
    self.update_tree_order(name)
    #for n in tree.traverse(): n.master_link=self.master_link    
    ## UPDATE WHEN MULTIPLE TREES WILL BE ALLOWED
    self.master_link.selections().add_node_selection('All leaves', NodeSelector([n for n in tree]))  ## this should be treated better   
    tree.treecolor_dc=DataChannel(self.master_link, from_key='antenna:All leaves{sep}trace:WeightedAv{sep}color:m|TreeColor'.format(sep=DataChannel.dco_separator_char))
    self.update_tree_color(name)

  def update_tree_color(self, name):    
    tree=self.get_tree(name)
    c=tree.treecolor_dc.out().set_index('Node')
    for node in tree.traverse():
      node.img_style['fgcolor']='#'+(  c.at[node.name, 'color']   if node.name in c.index else    self.master_link.colors().get_default_color()   )
    if self.master_link.qapp(): tree.redraw()
    self.signal_tree_list_changed.emit()
    ### add controls etc 
  
  def update_tree_order(self, name):
    tree=self.get_tree(name=name)
    #orders=[i for i,n in enumerate(tree)]
    #nodes=pd.Index([n.name for i,n in enumerate(tree)], name='Node') 
    node2order={}
    leaf_n=0
    for n in tree.traverse(strategy='postorder'):
      if n.is_leaf():    
        order=leaf_n
        leaf_n+=1
      else:        
        order=np.average([float(node2order[c.name])  for c in n.children])    
      node2order[n.name]=order

    # ancestors?
    df=pd.DataFrame([node2order[n.name] for n in tree.traverse()], index=pd.Index([n.name for n in tree.traverse()], name='Node'), columns=['order'], dtype='int')
    mm=self.master_link.data()
    mm.add_database(df, overwrite=True, name=name, prefix='treeOrder')

  def get_tree(self, name=None): return self.trees[name] if not name is None else self.default_tree
    
  def update_node_selection_items(self):
    ns=self.master_link.selections().get_node_selection('Selected nodes')
    self.update_items(ns, self.select_items, 'blue', 'silver')

  def update_node_highlight_items(self):
    ns=self.master_link.selections().get_node_selection('Highlighted nodes')
    self.update_items(ns, self.highlight_items, 'red', 'yellow')

  def update_items(self, ns, target, pen, brush):
    """ generic for selected and highlighted"""
    # cleaning up 
    for n in target.keys():
      try:      
        rect=target[n]
        if not n in ns:        
          n.scene().removeItem(rect)
          del target[n]
      except RuntimeError:
        print 'ERROR wrapped C/C++ object of type QGraphicsRectItem etc ... '
        del target[n]

    # adding what needed
    for n in ns:
      if not n in target:        
        item = n.scene().n2i[n]
        rect = QtGui.QGraphicsRectItem(parent=item.content)
        width, height=  n.face_area_size()
        rect.setRect(0, 0,  width, height)
        rect.setPen(QtGui.QColor(pen))
        rect.setBrush(QtGui.QColor(brush))
        rect.setOpacity(0.4)
        target[n]=rect

  def get_node(self, name, tree=None):
    if tree is None: tree=self.default_tree
    return tree.get_node(name)


class MemoryManager(Manager):
  """This manager does all the job of caching/computing DataChannels. 
  Data is kept as pandas dataframes in a prefix-tree-like structure whose root is self.memory_tree, which is of the type MemoryUnit (see data.py).
  Directly under the root you have the Database data, which is directly loaded from files. At lower levels you have anything computed from it.
  Antenna data (node selections coming from user interacting with the GUI) are also stored like Databases.
  Since DataChannels allow complex manipulations such as storing and retrieving dataframes, the structure of memory_tree may deviate from DataChannels themselves. 
  For example, there is no node in memory_tree corresponding to variable names stored in DataChannels. The memory_tree is thought as minimal and complete caching manager.
  Three type of data are stored outside MemoryManager:   caches, defines, variables. These correspond to operations by DCO_cache, DCO_define, DCO_var.
   All these data is stored in DC_containers, which is generally DataChannels themselves. 
  Most of the code relevant to MemoryManager is stored in the DataChannel class. See its out() function """
  signal_database_list_changed=QtCore.pyqtSignal()
  def __init__(self, master_link): 
    Manager.__init__(self, master_link)
    self.memory_tree=MemoryUnit(name='root:', data=None)  ## starts with db units
    null_mu=MemoryUnit(name='null:', parent=self.memory_tree)

  def get_available_databases(self, prefix='database'):   
    return sorted( [c.name[c.name.index(':')+1:]     for c in self.memory_tree.children.values() if c.name.startswith(prefix) ])

  def add_database(self, df, name, overwrite=False, prefix='database', node_field=None):          
    #if not isinstance(df, DataFrame): raise Exception, "ERROR only Treedex DataFrame instances can be added!"
    is_existing=self.has_database(name, prefix=prefix)
    if is_existing and not overwrite: raise Exception, "ERROR a DataFrame with the same name '{n}' already exists!".format(n=name)
    if not node_field is None: df=df.rename(columns={node_field:'Node'})
    if is_existing: 
      mu=self.memory_tree.children[ prefix+':'+name ]
      mu.data=df
      for c in mu.children.values(): c.force_recompute=True
      for d in mu.dependants:        d.force_recompute=True
      mu.trigger_recompute_in_downstream_DCs()
    else: 
      mu=MemoryUnit(name=prefix+':'+name, data=df, parent=self.memory_tree)
      if prefix=='database': self.signal_database_list_changed.emit()

  def has_database(self, name, prefix='database'):    return prefix+':'+name in self.memory_tree.children     
  
  #def set_dco_types_to_cache(self, dco_names):
  #  self.dcos_to_save=set([x for x in dco_names])

  # def get_farthest_unit_in_memory(self, ks):
  #   """ Provided ks=List of DCO keys --> Returns (u, index)
  #   Where u is the MemoryUnit closest to the end of ks (in the best case, this is the result of the full DC; otherwise, an intermediate result)
  #     and index its position in ks (0-based)
  #   """
  #   index=0;  mindex=None
  #   fu=None;  mfu=None
  #   if ks[index] in self.db_units: 
  #     fu=self.db_units[ks[index]]
  #     mindex=index; mfu=fu
  #     while True:
  #       index+=1
  #       if not ks[index] in fu.children: break
  #       fu=fu.children[ks[index]]               
  #       if not fu.data is None: mindex=index; mfu=fu
  #   return mfu, mindex

  # def add_db_unit(self, name, df):
  #   """ """
  #   n="database:"+name
  #   u=MemoryUnit(n, data=df)
  #   self.db_units[n]=u

  # def remove_db_unit(self, name):
  #   """ """

  # def out_of_dc(self, dc):
  #   if not dc.chain: return None #raise Exception, "ERROR DataChannel is empty!"
  #   ks=dc.computation_keys()  ### SPLIT this in chunks that start with a init_dco
  #   # for every chunk...

  #   fu, index=self.get_farthest_unit_in_memory(ks)
  #   df=fu.data
  #   mfu=fu
  #   while index!=len(ks)-1:
  #     index+=1
  #     dco=dc.chain[index]
  #     k=dc.computation_keys()[index]
  #     dco_name=k[:k.index(':')]
      
  #     #check special cases: cache, retrieve
      
  #     df=dco.channel_dataframe(df)

  #     cache_this=  (dco_name in self.dcos_to_save) or index==len(ks)-1

  #     if cache_this:
  #       data=df 
  #       mfu=fu
  #     else: data=None
      
  #     new_u=MemoryUnit(name=k, data=data, parent=fu)
  #     fu=new_u

  #   dc.link_to_memory_unit(fu)
  #   ## clean up here:   #from fu up to the first mfu 
 
  #   return df

import pyqtgraph.console as pgconsole
class TreedexConsole(pgconsole.ConsoleWidget, TreedexWindow):
  def window_identifier(self):
    """ must return either {'window_name': something}   or {'category':something} """
    return {'window_name': 'TreedexConsole'}

  def isatty(self): return False 

###################################################################################################################
class WindowManager(Manager):
  plot_window_names=set(['scatterplot', 'plot3d'])
  signal_window_list_changed=QtCore.pyqtSignal()
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
    self.signal_window_list_changed.emit()
  
  def has_window(self, window_name): return window_name in self.windows
  def get_window(self, window_name): return self.windows[window_name]
  def window_list(self): return sorted(self.windows.keys())
  def plot_window_list(self): return sorted([k for k in self.windows.keys() if k.split(':')[0].lower() in self.plot_window_names])
  def remove_window(self, window):   
    """ This is invoked by the closeEvent of every TreedexWindow"""
    print 'remove window '+window.window_name
    del self.windows[window.window_name]
    self.signal_window_list_changed.emit()
    #print 'remove window, after:' +str(self.windows)    


  def open_console(self):
    namespace=globals()
    namespace['pg']=pg  
    namespace['m']=self.master_link      
    #namespace['tree']=self.get_tree_root();  namespace['node']=self
    console = TreedexConsole(namespace=namespace, text='Welcome to the console!')
    console.setWindowTitle('Treedex - interactive console')
    console.show()
    self.add_window(console, 'console')

  # def open_data_explorer(self, dc=None):
  #   if dc is None: dc=DataChannel(self.master_link)
  #   win=TreedexFeatureExplorer(dc)    
  #   win.show()


###################################################################################################################
class SelectionManager(Manager):
  """ """
  default_order=[ 'Selected nodes',  'Highlighted nodes', 'All leaves', 'None' ]
  signal_selection_list_changed=QtCore.pyqtSignal()  
  signal_selection_changed     =QtCore.pyqtSignal(str) ## emits the name of the selection that changed  
  #ignored_features=set(['species', 'name', 'support', 'dist'])
  #virtual_features=set(['Tree'])
  def __init__(self, master_link): 
    Manager.__init__(self, master_link)
    #self.node_selections={}
    #self.add_node_selection( 'All leaves', NodeSelector([n for n in self.master_link.selections()] ) )  ## this is done in MasterContainer.add_tree
    self.add_node_selection( 'None', NodeSelector([]) )
    self.add_node_selection( 'Selected nodes',    NodeSelector([]) )
    self.add_node_selection( 'Highlighted nodes', NodeSelector([]) )

  def add_node_selection(self, name, ns):
    assert isinstance(ns, NodeSelector)
    if self.has_node_selection(name): raise Exception, "ERROR trying to add a node selection whose name already exists! {}".format(name)
    selection_df=pd.DataFrame( data=sorted([n.name for n in ns]), columns=['Node'] )
    self.master_link.data().add_database(selection_df, prefix='antenna', name=name)
    #self.node_selections[name]=ns
    self.signal_selection_list_changed.emit()
    self.signal_selection_changed.emit(name)

  def edit_node_selection(self, name, ns):
    assert isinstance(ns, NodeSelector)
    if not self.has_node_selection(name): raise Exception, "ERROR trying to edit a non-existing node selection! {}".format(name)
    new_selection_df=      pd.DataFrame( data=sorted([n.name for n in ns]), columns=['Node'] )
    existing_selection_df= self.get_node_selection_df(name)

    if not are_identical_dataframes(new_selection_df, existing_selection_df):          
      self.master_link.data().add_database(new_selection_df, name=name, prefix='antenna', overwrite=True)      
      self.signal_selection_changed.emit(name)   

  def has_node_selection(self, name):    return self.master_link.data().has_database(name, prefix='antenna')
  def get_node_selection_df(self, name): return self.master_link.data().memory_tree.children [ 'antenna:'+name ].data
  def get_node_selection(self, name):    
    df=self.get_node_selection_df(name)
    tm=self.master_link.trees()
    return NodeSelector([ tm.get_node(node_name)  for node_name in  df.loc[:,'Node']])

  def get_available_node_selections(self):
    the_list=self.master_link.data().get_available_databases(prefix='antenna')
    the_list.sort(  key= lambda x:x if not x in self.default_order else   ' '*(self.default_order.index(x))  )#making sure the default selections show up on top
    for i in range(len(the_list)): 
      if the_list[i]=='None': the_list.pop(i); break
    return the_list
                  
##############################################################################################################
class ColumnManager(Manager):
  def __init__(self, master_link): 
    Manager.__init__(self, master_link)
    self.last_index=0
    self.name2column={}
    self.name2index={}
    self.index2name={}

  def n_columns(self):    return self.last_index
  def next_column(self):         self.last_index+=1
  def add_column(self, face_controller): #, col_index=None):  
    if not isinstance(face_controller, FaceController): raise Exception, "ERROR wrong type"
    self.next_column()
    new_col_index= self.n_columns()
    print 'adding column index: ', new_col_index
    col_name=face_controller.get_title()
    self.name2column[col_name]    =face_controller
    self.index2name[new_col_index]=col_name
    self.name2index[col_name]     =new_col_index
    face_controller.set_start_column(new_col_index)

  def remove_column(self, index=None, name=None):
    if index is None and name is None: raise Exception, "remove_column ERROR you must provide index or name of the column you want to remove"
    if not index is None:      name= self.index2name[index]
    else:                      index=self.name2index[name]      
    del self.name2column[name]
    del self.name2index[name]
    del self.index2name[index]

  def get_column(self, name=None, index=None):
    if not name is None: return self.name2column[name]     
    else:                name=self.index2name[index]; return self.name2column[name]          
  def get_all_columns(self):    return self.name2column.values()
  def has_column(self, name=None, index=None):
    if not name is None: return name in self.name2column 
    else:                return index in self.index2name

###################################################################################################################
class ColorManager(Manager, DC_container):
  signal_colormap_list_changed=QtCore.pyqtSignal()
  def __init__(self, master_link): 
    Manager.__init__(self, master_link)
    DC_container.__init__(self)  
    self.container=master_link
    self.node_color_maps={}   #name of tree ->  {node to color}   color like #rrggbb in hex
    self.default_color='777777'
    self.colormap_DCs={} # define_name -> DC
    self.default_colormap='TreeColor'
    self.create_colormap(name='TreeColor', dc_key=\
'select:@color{sep}cache:c{sep}antenna:All leaves{sep}trace:WeightedAv{sep}treeInfo:order{sep}color:g|order@h0.0:FF0000,1.0:FF00FF;{defcol}{sep}select:Node,color{sep}cache:o{sep}retrieve:c{sep}join::o'.format(sep=DataChannel.dco_separator_char, defcol=self.default_color) )


  def create_colormap(self, name, dc_key): 
    """creates a colormap with this name, from the provided dc_key. 
    Conveniently returns the DC created, so that it can be edited for lockable/modifiable attributes
    """
    if name in self.colormap_DCs: raise Exception, "ERROR existing colormap name {}".format(name)
    dc=DataChannel(self, from_key='lockinsert:None{sep}define:{name}@1[{k}]{sep}lockappend:None'.format(
      k=dc_key, name=name, sep=DataChannel.dco_separator_char))
    dc.signal_dc_changed.connect( lambda x=name:self.colormap_changed(name=x)  )
    self.colormap_DCs[name]=dc
    dc.out() #this will add an entry to self.defines
    self.signal_colormap_list_changed.emit()
    return dc

  def colormap_changed(self, name):
    write('COLORMAP CHANGED NAME! we\'re doomed', 1)  
    ### addd codeeee to change pointer in self.colormap_DCs

  def get_available_colormaps(self):
    #write( ('defines:', self.defines.keys(),   'mapKeys:', self.colormap_DCs.keys()), 1)
    assert sorted(self.defines.keys()) == sorted( self.colormap_DCs.keys() )
    return sorted([self.default_colormap] + [i for i in self.colormap_DCs.keys() if i!=self.default_colormap])

  def get_default_color(self):    return self.default_color    
  # def add_node_color_map(self, tree, tree_name):
  #     ### rough but effective: based on order in the tree. Need to generalize soon
  #     node2order={n:i  for i, n in enumerate(tree)}
  #     for anc in tree.traverse(strategy='postorder'): 
  #       if anc.is_leaf(): continue
  #       node2order[anc]=sum( [node2order[c]  for c in anc.children]  )/float(len(anc.children))  ## ancestors: average of children
        
  #     ticks= [(0.0, (255, 0, 153, 255)), (1, (255, 115, 0, 255))]
  #     mode= 'hsv'
  #     vmin, vmax = 0.0, float(len(node2order)-1)
  #     node2color={} #node:self.get_color_for_node(node)       for node in nodes}
  #     for node in tree.traverse():
  #       vnode=  node2order[node]  #self.get_value_for_node(node, 'gradient_value')
  #       x=rescale(vnode, 0.0, 1.0, vmin, vmax)  # between 0.0 and 1.0
       
  #       ### following code is adapted from pg.widgets.GradientEditorItem.getColor to have a good correspondance with the color in the gradient widget
  #       #ticks = self.gradient['ticks'] #listTicks()
  #       if x <= ticks[0][0]:
  #         r,g,b,_ = ticks[0][1]
  #       elif x >= ticks[-1][0]:
  #         r,g,b,_ = ticks[-1][1]
  #       else:
  #         x2 = ticks[0][0]
  #         for i in range(1,len(ticks)):
  #           x1 = x2
  #           x2 = ticks[i][0]
  #           if x1 <= x and x2 >= x:
  #             break
  #         dx = (x2-x1)
  #         if dx == 0:          f = 0.
  #         else:                f = (x-x1) / dx
  #         c1 = ticks[i-1][1] #.color
  #         c2 = ticks[i][1]   #.color
  #         if mode  == 'rgb':
  #           r = int( c1[0] * (1.-f) + c2[0] * f )
  #           g = int( c1[1] * (1.-f) + c2[1] * f )
  #           b = int( c1[2] * (1.-f) + c2[2] * f )
  #           #a = 255 #c1[3] * (1.-f) + c2[3] * f
  #         elif mode == 'hsv':
  #           r1,g1,b1=c1[:3] #0-255 
  #           r2,g2,b2=c2[:3] #0-255
  #           h1,s1,v1=rgb_to_hsv(r1/255.0, g1/255.0, b1/255.0)  #0-1
  #           h2,s2,v2=rgb_to_hsv(r2/255.0, g2/255.0, b2/255.0)  #0-1
  #           h = h1 * (1.-f) + h2 * f
  #           s = s1 * (1.-f) + s2 * f
  #           v = v1 * (1.-f) + v2 * f
  #           r,g,b= map(lambda x: int(x*255),  hsv_to_rgb(h,s,v))     #0-255

  #       color='#{r:02X}{g:02X}{b:02X}'.format(r=r, g=g, b=b)
  #       node2color[node.name]=color
  #     self.node_color_maps[tree_name]=node2color

###################################################################################################################
# class FeatureManager(Manager):
#   """ """
#   signal_dataframe_list_changed=QtCore.pyqtSignal()
#   #ignored_features=set(['species', 'name', 'support', 'dist'])
#   #virtual_features=set(['Tree'])
#   def __init__(self, master_link): 
#     Manager.__init__(self, master_link)
#     self.dataframes={}     #name to dataframe
#     # self.dc_cache={}    #name to dataframe
#     # self.dc_define={}  #name to datachannel keys
#     # self.feature2nodes={} # feature_name -> NodeSelector    
#     # self.distance2function={}   
#     # self.mds_cache=         CachedExecutor()
#     # self.anc_feature_cache= CachedExecutor()
#     ### add general functions in geometry
#     #self.add_distance_function('no distance defined', lambda x,y:0)

    # self.add_distance_function('difference',          lambda x,y:abs(x-y))
    # self.add_distance_function('difference of log10', lambda x,y:abs(log10(x)-log10(y)) )
    # self.add_distance_function('hamming',           hamming_distance)
    # self.add_distance_function('gapless_hamming',   gapless_hamming)
    # self.add_distance_function('blosum',            blosum_distance)
    # self.add_distance_function('gapless_blosum',    gapless_blosum)
    # self.add_distance_function('distance_in_tree',  PhyloTree.get_distance, takes_node_args=True)

  # def save_DC_cache(self, df, var_name):         self.dc_cache[var_name]=df
  # def has_DC_cache(self, var_name):              return var_name in self.dc_cache
  # def retrieve_DC_cache(self, var_name):         return self.dc_cache[var_name]

  # def save_DC_define(self, dc_key, var_name):    self.dc_define[var_name]=dc_key
  # def has_DC_define(self, var_name):             return var_name in self.dc_define
  # def retrieve_DC_define(self, var_name):        return self.dc_define[var_name]
  


  # def get_available_databases(self):   return sorted(self.dataframes.keys())
  # def add_database(self, df, overwrite=False):          
  #   if not isinstance(df, DataFrame): raise Exception, "ERROR only Treedex DataFrame instances can be added!"
  #   if df.name() in self.dataframes:  
  #     if not overwrite: raise Exception, "ERROR a DataFrame with the same name '{n}' already exists!".format(n=df.name())
  #     ### trim memory!
  #     #self.master_link.data().remove_db_unit(df.name())
  #   self.dataframes[df.name()]=df
  #   #self.master_link.data().add_db_unit(df.name(), df)  
  #   self.signal_dataframe_list_changed.emit()


  # def remove_dataframe(self, name):          
  #   del self.dataframes[name]
  #   self.signal_dataframe_list_changed.emit()
  # def get_dataframe(self, name):        return self.dataframes[name]
  # def has_dataframe(self, name):        return name in self.dataframes


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


from .trees import AnnotatedTree, NodeSelector
