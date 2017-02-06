true_all_function=all  #necessary since ete3 replaces 'all' 
from ete3 import *
all=true_all_function
from .master import *
from .common import *
#from .facecontroller import *
from .widgets import *
#from PyQt4   import QtGui,QtCore  ### NOTE: in the future you may want to get rid of QtGui here!  #  --> imported by facecontroller

def annotated_tree_layout(node):
  """ Used by AnnotatedTree as default layout"""
  node.img_style['size']=7
  node.img_style['fgcolor']='grey'    #node.Data().colors().get_default_colormap().get_color_for_node(node)
  if   node.is_leaf():   node.img_style['shape']='circle'
  elif node.is_root():   node.img_style['shape']='square'
  else:                  node.img_style['shape']='triangle'
  if not node.is_leaf(): return 
  # for col_index in range(1, node.Data().columns().n_columns()+1): #controllers:
  #   the_controller = node.Data().columns().get_column(index=col_index)
  #   if not node in the_controller: continue
  #   if not the_controller.has_drawn(node):
  #     col_indices=the_controller.column_indices()
  #     these_faces=the_controller.get_faces(node) #, set_drawn=1)
  #     if len(col_indices) != len(these_faces): raise Exception, 'ERROR get_faces() and column_indices() must return the same number of elements!'
  #     for i in range(len(col_indices)):        node.add_face(these_faces[i], col_indices[i] , 'aligned')

class AnnotatedTree(PhyloTree):
  """ PhyloTree subclass thought for carrying features with some associated operations. AnnotatedTree can have controllers to assign homogenous representations. Use standard Tree method add_feature(feat_name, value) to add features; this can be used by plots and by face controllers (i.e. ete columns)
  Create AnnotatedTree using a newick input (text or file).
"""

  def __init__(self, newick=None,  *args, **kwargs ): 
    PhyloTree.__init__(self, newick=newick, *args, **kwargs)
    self.face_controllers=set() 
    self.actions=[self.action_delegator]  #see below this class    
    if not newick is None: self.init_for_tree()   # just finished loading; this is the root      

  def init_for_tree(self):
    """ Ran once per tree - not per node"""
    print 'init for tree'
    self.master_link=None
    self.tree_style=None
    self.init_master()
    self.fill_node_names()
    # name_face_controller = FeatureFaceController(feature_selector=FeatureSelector(feature_name='name'))
    # all_leaves= [n for n in self.traverse()]
    # for n in all_leaves:  name_face_controller.add_node( n ) #adding all leaves

  def init_master(self):
    write('creating new master container!', 1, how='yellow')
    root=self.get_tree_root()
    MasterContainer(tree_link=root)  #this will link:       for n in root.traverse(): n.data_link=x      
  def Master(self):  return  self.master_link

  def show(self,  *args, **kwargs ):
    """ decorates the default show function to show faces by controllers, through the layout function of this class"""
    if not 'tree_style' in kwargs or kwargs['tree_style'] is None: 
      ts=TreeStyle()
      ts.layout_fn=annotated_tree_layout
      ts.show_leaf_name=True   ##False  ### !
      ts.draw_guiding_lines=True
      self.tree_style=ts
      number_of_columns= 0 #self.Data().columns().n_columns()
      # write( self.Master(), 1, how='blue')
      # for column_index in range(1, number_of_columns+1):
      #   controller=self.Data().columns().get_column(index=column_index)
      #   indices= controller.column_indices()
      #   the_index= indices[0] if indices else 0
      #   the_title_item=controller.make_title_item()
      #   if the_title_item:      self.tree_style.aligned_header.add_face(the_title_item,  the_index  ) 
      kwargs['tree_style']=self.tree_style
    qapp=QtGui.QApplication(["Treedex"])
    #self.Data().init_windows()         ## just for logwindow, to rethink
    kwargs['qapp']=qapp
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

  def open_menu(self):
    """ Right click on the node (in ETE)"""
    qmenu=QtGui.QMenu()
    qmenu.addAction('Explore data', self.open_data_explorer  )
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
    dc=DataChannel(master_link=self.Master())
    win=TreedexFeatureExplorer(dc)    
    win.show()

  def echo(self):    print 'echooooo'
  

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
          print 'clicked', self.node 
          return 

          # if   QtGui.QApplication.keyboardModifiers() == QtCore.Qt.ShiftModifier:
          #   if not self.node in self.node.Data().session().get_selected_nodes():
          #     self.node.Data().session().set_selected_nodes(add= NodeSelector([self.node]))
          # elif QtGui.QApplication.keyboardModifiers() == QtCore.Qt.ControlModifier:
          #   if self.node in self.node.Data().session().get_selected_nodes():
          #     self.node.Data().session().set_selected_nodes(remove= NodeSelector([self.node]))
          #   else: 
          #     self.node.Data().session().set_selected_nodes(add= NodeSelector([self.node]))
          # else: ## normal behavior: select this node
          #   self.node.Data().session().set_selected_nodes( NodeSelector([self.node]) )

        #self.scene().view.set_focus(self.node) # copied from nodes_actions
        #pass    #left button
        #Tree.mouseReleaseEvent(self, e)
    def hoverEnterEvent (self, e):     
      return 
      #if self.node:  self.node.Master().session().set_highlighted_nodes( NodeSelector([self.node]) )

    def hoverLeaveEvent(self,e):       pass 
  #_______________ inset finish ________________________________________#
  # continue: AnnotatedTree




















  def traverse_by_level(self):
    """ Like traverse, but returns (relative_level, node) instead.   The first element will always be (0, self) """
    tovisit = [self]
    level=0
    next_level_flag= object()
    while len(tovisit)>0:
      node = tovisit.pop(0)
      if node == next_level_flag:
        level+=1
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
    #self.redraw()




#####################################################################################################################
