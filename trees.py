from .master import *
from .common import *
from .facecontroller import *
from .widgets import *
#from PyQt4   import QtGui,QtCore  ### NOTE: in the future you may want to get rid of QtGui here!  #  --> imported by facecontroller



def annotated_tree_layout(node):
  """ Used by AnnotatedTree as default layout"""
  node.img_style['size']=7
  #node.img_style['fgcolor']=node.master().colors().node_color_maps['default'][node.name] if node.is_leaf() else 'grey'
  if   node.is_leaf():   node.img_style['shape']='circle'
  elif node.is_root():   node.img_style['shape']='square'
  else:                  node.img_style['shape']='triangle'
  if not node.is_leaf(): return 
  ### old stuff:
  for col_index in range(1, node.master().columns().n_columns()+1): #controllers:
    the_controller = node.master().columns().get_column(index=col_index)
    if not node in the_controller: continue
    if not the_controller.has_drawn(node):
      col_indices=the_controller.column_indices()
      these_faces=the_controller.get_faces(node) #, set_drawn=1)
      if len(col_indices) != len(these_faces): raise Exception, 'ERROR get_faces() and column_indices() must return the same number of elements!'
      for i in range(len(col_indices)):        node.add_face(these_faces[i], col_indices[i] , 'aligned')
  ##########

class AnnotatedTree(PhyloTree):
  """ PhyloTree subclass thought for carrying features with some associated operations. AnnotatedTree can have controllers to assign homogenous representations. Use standard Tree method add_feature(feat_name, value) to add features; this can be used by plots and by face controllers (i.e. ete columns)
  Create AnnotatedTree using a newick input (text or file).
"""

  def __init__(self, newick=None,  master_link=None, tree_name=None, *args, **kwargs ): 
    PhyloTree.__init__(self, newick=newick, *args, **kwargs)
    self.face_controllers=set() 
    self.actions=[self.action_delegator]  #see below this class    
    if not newick is None: self.init_for_tree(master_link, tree_name)   # just finished loading; this is the root      

  def init_for_tree(self, master_link, tree_name):
    """ Ran once per tree - not per node"""
    print 'init for tree'
    for n in self.traverse(): n.master_link=master_link    

    self.tree_name=tree_name
    self.tree_style=None
    #self.init_master()
    self.fill_node_names()
    self.name2node= { n.name: n  for n in self.traverse() }      
    self.name2order=None #leaf_name:0-index top to bottom         #{ n.name: i  for i, n in enumerate(self) }      
    #self.recompute_order()   ---> this is called at the end of __init__ (see master.add_tree)
    for n in self.traverse():
      if not n.up:     n.time=0.0; continue
      n.time=n.up.time+n.dist

    name_face_controller = FeatureNameFaceController()
    all_leaves= [n for n in self.traverse()]
    for n in all_leaves:  name_face_controller.add_node( n ) #adding all leaves

  # def init_master(self):
  #   write('creating new master container!', 1, how='yellow')
  #   root=self.get_tree_root()
  #   MasterContainer(tree_link=root)  #this will link:       for n in root.traverse(): n.data_link=x      
  def master(self):  return  self.master_link

  def get_node(self, name): return self.name2node[name]
  def recompute_order(self):   self.master_link.trees().update_tree_order(self.tree_name)

  def copy_topology(self):  return Tree(newick=self.write())

  def show(self,  *args, **kwargs ):
    """ decorates the default show function to show faces by controllers, through the layout function of this class"""
    if not 'tree_style' in kwargs or kwargs['tree_style'] is None: 
      ts=TreeStyle()
      ts.layout_fn=annotated_tree_layout
      ts.show_leaf_name=False  ### 
      ts.draw_guiding_lines=True
      self.tree_style=ts
      #### old stuff
      number_of_columns= self.master().columns().n_columns()
      #write( self.master(), 1, how='blue')
      for column_index in range(1, number_of_columns+1):
        controller=self.master().columns().get_column(index=column_index)
        indices= controller.column_indices()
        the_index= indices[0] if indices else 0
        the_title_item=controller.make_title_item()
        if the_title_item:      self.tree_style.aligned_header.add_face(the_title_item,  the_index  ) 
      ####### 
      kwargs['tree_style']=self.tree_style
    if not 'qapp' in kwargs or not kwargs['qapp']:
      kwargs['qapp']=QtGui.QApplication()
    #self.Data().init_windows()         ## just for logwindow, to rethink
    PhyloTree.show(self, *args, **kwargs)

  def fill_node_names(self, only_unnamed=True):
    """ assigning names to nodes without one, going, from root to leaves:  a, b, c, ... z, aa, ab, ...zz, aaa etc """
    name_string=lowercase
    prefix_indexes=[]  # e.g. if [2, 0] --> prefix is 'ac'
    current_index=-1
    for node in self.traverse():
      if not only_unnamed or not node.name: 
        current_index+=1
        if len(name_string)==current_index:
          if not prefix_indexes or prefix_indexes[-1]+1==len(name_string): 
            prefix_indexes=[ 0 for i in range(len(prefix_indexes)+1)]
          else: prefix_indexes[-1]+=1
          current_index=0
        new_name= ''.join( [name_string[index] for index in prefix_indexes])+name_string[current_index]
        node.name=new_name

  # def add_context_menu_actions(self, menu):
  #   """ Adding gui actions; thanks to this you have an additional field "Controllers" when you right click any AnnotatedTree node (see submenu).
  #   This add_gui_actions function is called within the treeview/node_gui_actions.py modified module of ete3 ... this is the modification:
  #       contextMenu.addAction( "Show newick", self.show_newick)
  #       #### MM ADDED 
  #       if hasattr(self.node, 'add_context_menu_actions'):             self.node.add_context_menu_actions(contextMenu)
  #       #############
  #       contextMenu.exec_(QtGui.QCursor.pos())""" 
  #   menu.addSeparator()
  #   menu.addAction("Echo", self.echo)
  def print_memory_tree(self):
    print self.master().data().memory_tree.summary()

  def open_console(self):
    self.master().windows().open_console()
          
  def get_distance_from_root(self):
    p=self;  o=0.0
    while not p.up is None:   o+=p.dist; p=p.up
    return o

  def open_menu(self):
    """ Right click on the node (in ETE)"""
    qmenu=QtGui.QMenu()
    a=qmenu.addAction('Node: '+self.name);   a.setEnabled(False)

    qmenu.addAction('Print memory tree', self.print_memory_tree  )
    qmenu.addAction('Open python console', self.open_console  )

    #qmenu.addAction('Explore data', self.open_data_explorer  )
    #qmenu.addAction('Open Scatterplot', self.open_scatterplot  )
    #qmenu.addAction('Edit', self.edit_data_channel  )
    qmenu.exec_(QtGui.QCursor.pos())

    # menu.addAction( "Put on top", self.put_on_top   )
    # if self.get_face_controllers():     
    #   the_submenu=self.submenu()
    #   if not the_submenu is None:       menu.addAction( "Controllers...", lambda : menu.addMenu( the_submenu )   )        
    # menu.addAction( "Open Console",   self.open_console )  
    # menu.addAction( "Node selection manager",   self.open_node_selection_manager )  
    # menu.addAction( "Run statistical test",     self.open_stat_test )  
    # menu.addAction( "Load features ...",     self.open_feature_loader )  
    #menu.addAction( "Color test",   self.Data().colors().get_default_colormap().open_gradient_editor )  
    #menu.addAction(     "test simings",   self.test_simings )  # debug

  def open_data_explorer(self):
    self.master().windows().open_data_explorer()
    # dc=DataChannel(parent=self.master())
    # win=TreedexFeatureExplorer(dc)    
    # win.show()

  # def open_scatterplot(self):
  #   dc=DataChannel(parent=self.master())
  #   win=ScatterPlotWindow(master_link=self.master())
  #   win.add_plot_item(piclass=NodeScatterPlotItem)
  #   win.show()

  def echo(self):    print 'echooooo'
  def scene(self):   return self.master_link.columns().get_column(index=1).title_item.scene() 
  def redraw(self):  self.scene().GUI.redraw()

  def face_area_size(self):
    """ Return the [width, height] in pixels of the area for the faces of this node"""
    main_item = self.scene().n2i[self]
    noderect = main_item.mapToScene(main_item.fullRegion).boundingRect()
    rightmost_x = noderect.right()
    if len(main_item.mapped_items):
      last_item=main_item.mapped_items[-1] 
      the_iterator=last_item.childItems if ( hasattr(last_item, 'column2faces') and last_item.column2faces ) else lambda :[last_item]
      for f in the_iterator(): #useful only if last item has multiple columns
        rect = f.mapToScene(f.boundingRect()).boundingRect() 
        rightmost_x= rect.right()
    return [ rightmost_x-noderect.left(), noderect.height() ]

  #
  #_______________inset: action for any nodes of this class_____________#
  class action_delegator(object): 
    """ All methods here defined will replace those of the graphics items deriving from this tree"""
    def mousePressEvent(self, e):      pass
    def mouseReleaseEvent(self, e):      
      if e.button() == QtCore.Qt.RightButton:        
        write('popup node '+self.node.name, 1, how='yellow')
        self.node.open_menu()
        #self.showActionPopup()
      else: 
        # click on this node, or face for this node
        if self.node:
          ns=self.node.master_link.selections().get_node_selection( 'Selected nodes' ).copy()
          if not self.node.is_leaf():             new_ns=NodeSelector([n for n in self.node])
          else:                                   new_ns=NodeSelector([self.node])           
          if   QtGui.QApplication.keyboardModifiers() == QtCore.Qt.ShiftModifier:
            ns.update(new_ns)
          elif QtGui.QApplication.keyboardModifiers() == QtCore.Qt.ControlModifier:
            for node in new_ns:
              if not node in ns:
                ns.add(node)                      
              else:                           
                ns.remove(node)                      
          else: ## normal behavior: select this node
            ns=new_ns
          self.node.master_link.selections().edit_node_selection('Selected nodes', ns)            


        #self.scene().view.set_focus(self.node) # copied from nodes_actions
        #pass    #left button
        #Tree.mouseReleaseEvent(self, e)
    def hoverEnterEvent (self, e):     
      if not self.node.is_leaf():             ns=NodeSelector([n for n in self.node])
      else:                                   ns=NodeSelector([self.node])           
      self.node.master_link.selections().edit_node_selection('Highlighted nodes', ns)            
      #if self.node:  self.node.Master().session().set_highlighted_nodes( NodeSelector([self.node]) )

    def hoverLeaveEvent(self,e):       
      self.node.master_link.selections().edit_node_selection('Highlighted nodes',  NodeSelector([]))            
  #_______________ inset finish ________________________________________#
  # continue: AnnotatedTree


  def traverse_by_level(self, exclude_fn=None):
    """ Like traverse, but returns (relative_level, node) instead.   The first element will always be (0, self) 
    if you provide exclude_fn, this is tested to stop traversing from that node (these nodes are never returned)
    """
    tovisit = [self]
    level=0
    next_level_flag= object()
    while len(tovisit)>0:
      node = tovisit.pop(0)
      if node == next_level_flag:
        level+=1
        continue
      if not exclude_fn is None and exclude_fn(node): 
        continue
      yield (level, node)
      if not node.is_leaf():
        tovisit.append(next_level_flag)         
        tovisit.extend(node.children)

  def put_on_top(self):
    """ Swap branches from the root up to here, to make sure this node is the first one in the visualization """
    root=self.get_tree_root();  parent=self.up;  child=self
    while parent!=root:
      parent.children.sort(key= lambda x: 0 if x==child else 1)
      child=child.up
      parent=child.up
    self.recompute_order()

  def swap_children(self):
    PhyloTree.swap_children(self)
    self.recompute_order()
    self.redraw()



#####################################################################################################################
