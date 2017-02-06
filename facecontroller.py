from PyQt4   import QtCore,QtGui
#### TO BE REVISED COMPLETELY

class DistanceBarFace(faces.StackedBarFace): #, view_manager_gui_actions):
  """ StackedBarFace modified to represent a single value. Two colors are considered (c1, c2), the representation will be something like:
  --------------  
  |xxx|        |     
  --------------
where xxxx is colored with c1 and the blank part with c2. The area of c1 is proportional to where value stands between minvalue and maxvalue """
  def __init__ (self, value, minvalue, maxvalue, width, height, colors=['blue', 'gainsboro'], line_color='black'):
    delta=maxvalue-minvalue
    if not delta: pixels_per_feat=100.0
    else: pixels_per_feat= 100.0/(delta)
    pixels_here=  int((value) *pixels_per_feat)
    percents=[ pixels_here, 100-pixels_here  ]
    faces.StackedBarFace.__init__(self, percents, width=width, height=height, colors=colors, line_color=line_color)

class DistanceColorFace(faces.RectFace): #, view_manager_gui_actions):
  """ RectFace modified to represent a single value in a heat map fashion. Two colors are considered (c1, c2), with the color displayed computed in interpolation of the two according to where value stands between minvalue and maxvalue """
  def __init__ (self, value, minvalue, maxvalue, width=15, height=15, colors=['#0000EE', '#EE0000'], line_color='black'):
    normalized_value=  (value-minvalue) / float((maxvalue-minvalue))
    color_here= color_scale( normalized_value, colors[0], colors[1]  )
    faces.RectFace.__init__(self, width=width, height=height, bgcolor=color_here, fgcolor=line_color, label=None) 

class GenericTitleItem(QtGui.QGraphicsRectItem):
  """Use this as superclass of title_item_class in all FaceController subclasses; basically a QtGui.QGraphicsRectItem  """
  def __init__(self, fc):       #, *arg, **karg):
    # get style variables from fc.title_style
    bgcolor=fc.title_style['bgcolor'] if 'bgcolor' in fc.title_style else 'white'
    fgcolor=fc.title_style['fgcolor'] if 'fgcolor' in fc.title_style else 'black'
    alpha  =fc.title_style['alpha']   if 'alpha' in fc.title_style   else  0.2;       alpha*=255
    fsize  =fc.title_style['fsize']   if 'fsize' in fc.title_style   else  11
    font   =fc.title_style['font']    if 'font' in fc.title_style    else  'Arial'
    width  =fc.title_style['width']   if 'width' in fc.title_style   else  100
    height =fc.title_style['height']  if 'height' in fc.title_style  else  50
    width_folded=fc.title_style['width_folded']   if 'width_folded' in fc.title_style   else  20
    #color_folded=fc.title_style['color_folded']   if 'color_folded' in fc.title_style   else   (bgcolor if bgcolor!='white' else 'gainsboro')
    fsize_folded=fc.title_style['fsize_folded']   if 'fsize_folded' in fc.title_style   else  11
    color_folded=bgcolor
    if fc.get_state()=='unfolded':
      QtGui.QGraphicsRectItem.__init__(self, 0, 0, width, height) #, *arg, **karg)
      self.setPen( QtGui.QPen(QtCore.Qt.NoPen))
      rect =   QtGui.QGraphicsRectItem(self.rect())
      rect.setParentItem(self)
      qcolor=QtGui.QColor( bgcolor ); qcolor.setAlpha(alpha)
      rect.setBrush( QtGui.QBrush( qcolor ))
      text =  QtGui.QGraphicsTextItem(  fc.get_title()  ) 
      text.setFont( QtGui.QFont(font, fsize) ) 
      text.setDefaultTextColor( QtGui.QColor( fgcolor ))
      text.setParentItem(self)
      tw = text.boundingRect().width();  th = text.boundingRect().height()
      center = self.boundingRect().center()
      text.setPos(center.x()-tw/2, center.y()-th/2)    
      self.setCursor(QtCore.Qt.PointingHandCursor)
      self.setAcceptsHoverEvents(True)

    elif fc.get_state()=='folded':
      QtGui.QGraphicsRectItem.__init__(self, 0, 0, width_folded, height) #, *arg, **karg)
      self.setCursor(QtCore.Qt.PointingHandCursor)
      self.setAcceptsHoverEvents(True)
      rect =   QtGui.QGraphicsRectItem(self.rect())
      rect.setParentItem(self)
      qcolor=QtGui.QColor( color_folded ); qcolor.setAlpha(alpha)
      rect.setBrush( QtGui.QBrush( qcolor))
      text =  QtGui.QGraphicsTextItem(  fc.get_title()  ) 
      text.setFont( QtGui.QFont(font, fsize_folded) ) 
      text.setDefaultTextColor( QtGui.QColor( fgcolor ))
      text.setParentItem(self)
      #center = self.boundingRect().center()
      text.setTransformOriginPoint( 0, 0 ) #text.boundingRect().center() )
      text.setRotation(-90)
      #print 'scenebr', text.sceneBoundingRect()   
      text.boundingRect().width()
      text.setPos( (self.rect().width()-text.boundingRect().height())/2,    (self.rect().height())    )
    elif fc.get_state()=='hidden':
      QtGui.QGraphicsRectItem.__init__(self, 0, 0, 0, 0) 
    else: 
      raise Exception, "ERROR state not recognized! "+str(fc.get_state())
      self.temp_hover=None

  def hoverLeaveEvent (self, e):    self.remove_hover_box()
    
  def hoverEnterEvent (self, e):   
    """ A yellow box to display description for this face controller appears when hovered. If the controllers is folded, the yellow box also contains the title itself and has a different position"""
    text, position = self.hover_box_details()
    self.add_hover_box( text, position )

  def hover_box_details(self):  
    """ Define this function in subclasses to decide what text and where to show when hovering mouse on this title item"""
    return '', 'top'

  def add_hover_box(self, stringtext, position='top'):
    """ remove a yellow box with text added when hovering; possible pos are 'top' and 'bottom' """
    if not stringtext: return
    text =  QtGui.QGraphicsSimpleTextItem( stringtext ) #node.name)
    text.setFont( QtGui.QFont('Arial', 11) )   #, -1, False)     )
    # label box; using 7px margin per side
    br=text.boundingRect(); br.setWidth( br.width()+14 ); br.setHeight( br.height()+14 );         
    rect=QtGui.QGraphicsRectItem(br)
    rect.setBrush( QtGui.QBrush( QtGui.QColor( '#ffffcc' )))
    text.setParentItem(rect)
    text.translate(7, 7)
    # where to put it:
    self.scene().addItem(rect)
    this_title_br=self.mapToScene(self.rect()).boundingRect()
    if   position=='top':    x,y=  this_title_br.left()+5, this_title_br.top()+5
    elif position=='bottom': x,y=  this_title_br.left()+5, this_title_br.bottom()-5 
    rect.translate(x, y) 
    self.temp_hover=[text, rect]

  def remove_hover_box(self):
    """ removing existing yellow box with text of description"""
    if not self.temp_hover is None:
      text, rect = self.temp_hover
      rect.scene().removeItem(rect)
      self.temp_hover=None

class InvisibleTitleItem(GenericTitleItem):
  def __init__(self, fc):
    return QtGui.QGraphicsRectItem.__init__(self, 0, 0, 0, 0) 


################################################################
################ FACE CONTROLLERS
class FaceController(NodeSelector):
  """ Object that manage a number of 'face columns' in all nodes of a AnnotatedTree to which it is linked. Thought to add the same face to many nodes and then control those faces dynamically (e.g. distance from a reference, you can change the reference point).

Master methods:
  -add_node(self, node):  puts node (AnnotatedTree instance) under the control of this controller. Initialising with nodes=[n1, n2 .. ] argument is equivalent of calling this on every node.
  -has_drawn(self, node)  // set_drawn(self, node, value)  // self.redraw():  
    control lazy drawing of the scene. 'drawn' are 0 or 1 values kept for every node in self.nodes; keeps track of whether faces were already added -- when something changes, 'drawn' is set to 0 and the scene is redrawn. Typical usage (in subclasses, when some modification requires things to be redrawn):
    for n in self.nodes:       self.set_drawn(n, 0)
    self.redraw()
  -column_indices(self): returns a list of column_index integers, corresponding to the node columns controlled. Based on self.start_column and self.n_columns
  -make_title_item(self) // title_item_constructor(self)
    these functions are used by the layout function of the AnnotatedTree to build a single face for each controller, that is placed in the .title of the tree_style. The class attribute title_item_class is instantiated to produce the object.

Useful attributes of instances:
  -nodes:      dictionary with all nodes linked to this controller as keys. Values here (0 or 1) keep track if faces must be added or if they are already present (as returned by has_drawn(self, node))
  -title_item  pointer to class used to construct the graphical title item (top of each column)
  -title       name displayed in the title item; taken from self.name if not specified in subclasses
  -state       keeps track of state effects, e.g. folding column in graphical environment

Subclasses of FaceController must define:
  -get_faces(self, node):  returns a list of n_columns faces for this node. This is normally called only when necessary, if not self.has_drawn(node)
  -n_columns(self):        returns the number  of faces returned by get_faces
  -[class] attribute name      -- name of this face controller (category)
  -[class] attribute title_item_class: this links the class of the object that is used as title_item; 
  -get_node_actions(self, node):  not compulsory; allow to add items to the right-click menu on AnnotatedTree nodes with this controller. Must return list of [string, function]

"""
  name=None
  title_item_class = GenericTitleItem

  def __init__(self, nodes=[],  title=None, title_style={}, late=False):
    NodeSelector.__init__(self)
    self.start_column=0
    self.title_item=None
    self.title=title if title else  capitalize(str(self.name))
    self.title_style=title_style
    if nodes: self.add_nodes(nodes)
    self.state='folded'
    self.drawn={} #node -> bool

    if late:
      the_title_item=self.make_title_item()
      self.Data().columns().add_column(self)
      the_index=self.Data().columns().n_columns()
      self.Data().tree().tree_style.aligned_header.add_face(the_title_item,  the_index  ) 

  def Data(self):
    if not self.nodes: return None
    else:              
      for n in self.nodes: return n.Data()

  def get_title(self):         return self.title

  def set_state(self, state):  
    """The state attribute serves to keep track of whether the column for this face is currently folded or not, or other state-based things"""
    self.state=state

  def get_state(self):         return self.state

  def summary(self):
    return '## Face controller: {name}  | Title: {title} \n#  Column indices: {cols}\n'.format(name=self.name, title=self.get_title(), cols=self.column_indices()) #, nodes= [x.name for x in self.nodes]  )
  #__repr__=summary

  def add_nodes(self, nodes): 
    for n in nodes: self.add_node(n)

  def add_node(self, node): 
    if not self.has_node(node):
      NodeSelector.add_node(self, node)
      if not node.Data().columns().has_column(   self.get_title()   ):
        print 'adding column while adding to node ', node.name
        node.Data().columns().add_column(self)
      node.face_controllers.add(self)

  def get_faces(self, node, **kargs):    raise Exception, "FaceController ERROR get_faces method must be defined in subclasses!"
  def get_node_actions(self, node):      return [      ]

  def redraw(self):
    """ update the scene """
    self.clear_faces()
    if self.title_item:   self.title_item.scene().GUI.redraw()
  
  def has_drawn(self, node):          
    """ this returns True if node._faces contains the faces corresponding to this controller"""
    return self.drawn[node] if node in self.drawn else False
  def set_drawn(self, node, value):          self.drawn[node]=bool(value)

  def n_columns(self):    raise Exception, "FaceController ERROR n_columns method must be defined in subclasses!"    ## must be defined in subclasses to be as long as what returned by function get_faces

  def column_indices(self):    
    """ Returns the column indices of the faces controlled (same in all nodes)"""
    return [self.start_column + i  for i in range(self.n_columns())]

  def set_start_column(self, index):
    self.start_column = index

  def clear_faces(self):
    """ Clear the faces drawn by this controller; called before redrawing"""
    #write('clear faces '+self.title, 1, how='blue')
    for n in self.nodes:
      if hasattr(n, '_faces'):
        #write(' cols '+str(self.column_indices()), 1, how='green')       
        for col_index in self.column_indices():
          if col_index in n._faces.aligned: 
            #write(' del col: '+str(col_index), 1, how='green')       
            del n._faces.aligned[col_index]

  def make_title_item(self): 
    """ Function called by the layout function of all AnnotatedTree that have this controller. Returns a faces.DynamicItemFace by calling title_item_constructor ;  which reads class attribute self.title_item_class"""
    return faces.DynamicItemFace(self.title_item_constructor) #if not self.title_item_class is None else None

  def title_item_constructor(self, node, *args, **kargs):
    """ Constructor function passed to faces.DynamicItemFace. Returns a QtGui.QGraphicsItem; this is made by instantiating self.title_item_class"""
    ## Creates a main master Item that will contain all other elements
    ## Items can be standard QGraphicsItem
    masterItem = self.title_item_class(self) #*args, **kargs) 
    self.title_item=masterItem
    masterItem.face_controller=self
    return masterItem

class FeatureFaceController(FaceController):
  """ Simple Text Face for a feature"""
  title_item_class=InvisibleTitleItem

  def n_columns(self): return 1

  def __init__(self, feature_selector, **kargs):
    FaceController.__init__(self, **kargs)
    self.feature_selector=feature_selector
    self.title= str(self.feature_selector)
    self.set_text_color_control(None)

  def get_faces(self, node, set_drawn=True):

    #write('get faces ffc '+self.title, 1, how='yellow')
    feat_to_show =  node.get_feature(self.feature_selector) # getattr(node, self.feature_selector.feature_name) # 

    #feat_to_show2 =  node.Data().features()[self.feature_name].get_feature_for_node(node)
    #if feat_to_show != feat_to_show2: raise Exception, str(feat_to_show)+ ' ' +str(feat_to_show2)
    the_color= 'black' if self.text_color_control is None else self.text_color_control.get_color_for_node(node)
    tf=TextFace(feat_to_show, fgcolor=the_color)
    if set_drawn: self.set_drawn(node, 1)
    return [ tf ]

  def set_text_color_control(self, color_control):
    self.text_color_control = color_control
    

class DistanceFaceController(FaceController):
  """ NEEDS UPDATE
  Face controller to display float/int distances. 
  Distances are computed on the node attribute called as init argument *feature_name*; by calling the *distance_fn* function  (if not provided, subtraction is used). The distance is computed calling get_distance_for_node, which wraps distance_fn, between each node and a reference node; the reference (self.ref) can be set by init argument *ref*, or later by calling function set_reference.
  Returns a max of three faces: a text face with the value (black), a text face with  distance value (colored), and a DistanceBarFace (colored) representing graphically the distance. Both distance faces display positive distances with blue and red, or the values provided with init argument colors (two element list)
  
  Other options:
   -digits:      number of digits after floating point which are shown
   -parts:       control which  components ('value', 'dist', 'bar') are displayed, providing a dict with 0/1 values  (if 'None', it's not displayed and this cannot be changed)
   -barwidth:    width of the bar shown
   -barheight:   height of the bar shown
   -title_style: hash defining style elements for the title item. possible keys:  bgcolor, fgcolor, alpha, fsize, font, width, height, width_folded, color_folded
   -title:       string defining the title displayed in the title item
   -description: string that, if provided, is displayed when hovering over title_item and in other occasions
"""
  name='Distance' 
  available_parts= {'value':0, 'dist':1, 'bar':1, 'colormap':0}

  def __init__(self, feature_selector, distance_name='difference', ref=None, colors=['blue', 'red'],  parts=None, digits=3, barheight=12, barwidth=80, colormap_size=12, colormap_colors=['#FFFFFF', '#000000'], title=None, description='', reference='min',  fold_columns=False, *args, **keyargs):
    self.feature_selector=feature_selector
    if title is None: title=capitalize(self.name)+':'+str(self.feature_selector)
    keyargs['title']=title # passing it to master class FaceController
    self.description=description
    self.ref=ref
    self.distance_name = distance_name   ## default distance: subtraction
    self.maxdistance = None
    self.colors=colors;    self.digits=digits;  self.barwidth=barwidth; self.barheight=barheight
    self.colormap_size=colormap_size; self.colormap_colors=colormap_colors
    self.color_control=None
    self.parts=dict(self.available_parts)
    if not parts is None:
      if not type(parts)==dict: 
        for k in self.parts: self.parts[k]=0  # if an non dict iterable is provided, it is assumed it is a list of the only things we want displayed
      for k in parts:
        if not k in self.available_parts: raise Exception, 'ERROR this part is not available for this FaceController: {p}  | Available parts: {av}'.format(p=k, av=join(self.available_parts.keys(), ' '))
        if     type(parts)==dict: self.parts[k]=parts[k]
        else:   self.parts[k]=1
    #self.distance_data=symmetrical_dict()    # numpy, node2index   ## old
    #self.mds_data={}   # key:  n_dimensions   ->   coordinate_matrix
    FaceController.__init__(self,  *args, **keyargs)
    self.set_reference(reference)
    if fold_columns:     self.set_state('folded')
    else:                self.set_state('unfolded')

  #
  #_____________inset: graphical item used as title for DistanceFaceController _____________#
  class title_item_class(GenericTitleItem):
    def hover_box_details(self):
      if self.face_controller.get_state()=='folded':
        # making text label with face controller title
        stringtext= self.face_controller.get_title()
        if self.face_controller.description: stringtext+='\n'+self.face_controller.description
        pos='top'
      else:   #unfolded
        stringtext=self.face_controller.description
        pos='bottom'
      if stringtext: stringtext+='\n'
      if self.face_controller.ref.name: name = self.face_controller.ref.name
      elif  self.face_controller.ref==self.face_controller.ref.get_tree_root(): name = '<root>'
      else: name = '<unnamed>'
      stringtext+='Current reference: '+name
      return stringtext, pos

    def mousePressEvent(self,e):      pass  #necessary to have mouseReleaseEvent
    def mouseReleaseEvent(self, e):     
      if e.button() == QtCore.Qt.RightButton:       self.show_menu_popup()
    def show_menu_popup(self):
      """ Menu displayed on right click on this title item"""
      #build_icons()
      menu=QtGui.QMenu()
      a=menu.addAction(self.face_controller.get_title()); a.setEnabled(False)
      menu.addSeparator()
      menu.addAction('See scatterplot', self.face_controller.plot_scatterplot  )
      menu.addAction('See 3D plot', self.face_controller.plot_tridimensionalplot  )
      #menu.addAction('Compose plot...', self.face_controller.plot_dialog )      
      menu.addSeparator()
      if self.face_controller.get_state()=='folded':
        menu.addAction('Unfold column', self.face_controller.unfold )      
      elif self.face_controller.get_state()=='unfolded':
        menu.addAction('Fold column', self.face_controller.fold )      
        menu.addSeparator()
        #print Qicons['check'].pixmap().isEmpty()
        for part in sorted(self.face_controller.available_parts):
          current_state=self.face_controller.parts[part]  #True or False, depending on whether this part is shown or not
          if current_state is None: continue      
          menu.addAction({False:'Show ', True:'Hide '}[current_state]+part, lambda part=part, current=current_state:self.face_controller.toggle_part(part=part, show=not current))

      menu.exec_(QtGui.QCursor.pos())

  #_________________________________inset title_item_class finish________________________#
  #

  #
  #________________inset2: actions attributed to all faces under this controller__________#
  class face_decorator(object): #QtGui.QGraphicsItem):
    def __init__(self):
      self.setCursor(QtCore.Qt.PointingHandCursor)
      self.setAcceptsHoverEvents(True)
    def mousePressEvent(self,e): pass  #necessary to have mouseReleaseEvent
    def mouseReleaseEvent(self, e):     
      if e.button() == QtCore.Qt.RightButton:       self.show_menu_popup()
      elif self.node:          
        if   QtGui.QApplication.keyboardModifiers() == QtCore.Qt.ShiftModifier:
          if not self.node in self.node.Data().session().get_selected_nodes():
            self.node.Data().session().set_selected_nodes(add= NodeSelector([self.node]))
        elif QtGui.QApplication.keyboardModifiers() == QtCore.Qt.ControlModifier:
          if self.node in self.node.Data().session().get_selected_nodes():
            self.node.Data().session().set_selected_nodes(remove= NodeSelector([self.node]))
          else: 
            self.node.Data().session().set_selected_nodes(add= NodeSelector([self.node]))
        else: ## normal behavior: select this node
          self.node.Data().session().set_selected_nodes( NodeSelector([self.node]) )
        
    def show_menu_popup(self):
      menu=QtGui.QMenu()
      a=menu.addAction(self.face.face_controller.get_title()); a.setEnabled(False)
      #if self.face.face_controller.description:  a=menu.addAction(self.face.face_controller.description); a.setEnabled(False)
      menu.addSeparator()
      a=menu.addAction(self.node.name); a.setEnabled(False)
      menu.addSeparator()
      menu.addAction("Set as reference", lambda c=self : c.face.face_controller.set_reference(c.node)  ) 
      menu.exec_(QtGui.QCursor.pos())
  #_________________________________inset face_decorator finish________________________#
  # continue: DistanceFaceController

  def toggle_part(self, part, show=None):
    """Set a certain part (e.g. bar, text etc) so that it is shown or hidden; redraw is called """
    if show is None: show= not bool(self.parts[part])
    self.parts[part]=int(bool(show))
    for n in self.nodes:       self.set_drawn(n, 0)
    self.redraw()
  
  def n_columns(self):    return 1 # sum(self.parts.values())

  # def set_color_control(self, color_control_fc):
  #   """ To make plots, we tell this FaceController to take the color of each point from  this color_face_controller"""
  #   if not isinstance(color_control_fc, ColorlabelFaceController): raise Exception, "set_color_control ERROR you must provide a ColorlabelFaceController with this function!"
  #   self.color_control=color_control_fc

  def get_distance_for_node(self, node, ref=None):
    """ Return the distance between node and the current self.ref; lazy computed; assuming symmetric distances
    If ref is None, self.ref is used. """
    if ref is None:     ref=self.ref
    elif not self.ref:  raise Exception, 'ERROR DistanceFaceController: cannot compute distance if self.ref is not defined!'
    #if not self.distance_data.has_keys(node, ref):
    d=  self.Data().features().get_distance_between_nodes(node, ref, self.distance_name, self.feature_selector)
      #self.distance_fn(  self.get_value_for_node(node),   self.get_value_for_node(ref) )
    #  self.distance_data[node][ref]=d
    return d #self.distance_data[node][ref]

  def get_value_for_node(self, node):
    """ Return the absolute value for a node"""
    return self.Data().features().get_feature_for_node(self.feature_selector, node)

  def get_faces(self, node, set_drawn=True):
    """ Returns the faces to be added to node (see class doc) """
    
    #write('get faces dfc '+self.title, 1, how='magenta')

    if self.get_state()=='folded':      return [faces.TextFace('')]
    out=[]
    dist_value= self.get_distance_for_node(node)
    fgcolor=   self.colors[0]
    restcolor= self.colors[1]
    #dist_value_face=faces.TextFace(  ('{v:.'+str(self.digits)+'f}').format(v=dist_value), fgcolor=fgcolor )
    if self.parts['colormap']:
      cmap_face=  DistanceColorFace( abs(dist_value), 0, self.maxdistance, colors= self.colormap_colors, width=self.colormap_size, height=self.colormap_size )
      cmap_face.margin_left=3;       cmap_face.margin_right=3
      out.append(cmap_face)
    if self.parts['bar']:
      bar_face=  DistanceBarFace( abs(dist_value), 0, self.maxdistance, colors=[fgcolor, restcolor], height=self.barheight, width=self.barwidth)
      bar_face.margin_left=3;       bar_face.margin_right=3
      out.append(bar_face)
    if self.parts['value'] :
      feature_value=self.get_value_for_node(node)
      if type(feature_value)==float: 
        feature_value=round(feature_value, self.digits) 
        if not self.digits: feature_value=int(feature_value)
      value_face=faces.TextFace(  str(feature_value), fgcolor='black' )
      value_face.margin_left=3;       value_face.margin_right=3     
      out.append(value_face)
    if self.parts['dist'] :
      if type(dist_value)==float: 
        dist_value=round(dist_value, self.digits) 
        if not self.digits: dist_value=int(dist_value)     
      dist_value_face=faces.TextFace(  dist_value, fgcolor=fgcolor )
      dist_value_face.margin_left=3;       dist_value_face.margin_right=3     
      out.append(dist_value_face)
    if set_drawn: self.set_drawn(node, 1)
    face_controller_face=FaceAligner(out, actions=[self.face_decorator],  face_controller=self ) 
    return [face_controller_face]

  def set_reference(self, node): 
    """ Set the current self.ref to this node. You can use a detached node which has the current feature to use any value. 
Special values are 'min' or 'max' to sort nodes by feature value and set the node with min or max values"""
    if node in ['min', 'max']: 
      sorted_nodes=sorted(self.nodes, key=lambda n:self.get_value_for_node(n))
      node= sorted_nodes[0] if  node=='min' else sorted_nodes[-1]
    self.ref= node
    self.maxdistance =    max(  [abs(self.get_distance_for_node(n))   for n in self.nodes ])
    for n in self.nodes:       self.set_drawn(n, 0)
    self.redraw()
    #write(self.feature_name+' '+node.name, 1, how='blue') 

  #def get_node_actions(self, node):  return  [] #[["Set as reference -> "+self.get_title(), lambda c=self: self.set_reference(node) ]]

  def fold(self):
    """ Activated when this action is selected through the right click menu. Compress this column. Forces redrawing"""
    if self.get_state()=='unfolded': 
      self.set_state('folded')
      for n in self.nodes: self.set_drawn(n, 0)
      self.redraw()

  def unfold(self):
    """ Activated when this action is selected through the right click menu. Uncompress this column. Forces redrawing"""
    if self.get_state()=='folded': 
      self.set_state('unfolded')
      for n in self.nodes: self.set_drawn(n, 0)
      self.redraw()

  def get_controlled_nodes(self):   
    """ Returns the nodes directly controlled by this FaceController (in most cases, leaves only); this order is used for matrix data such as MDS, and does not depend on topology"""
    return sorted(self.nodes,  key=lambda x:x.name)

  def get_all_nodes(self, ret_dict=False):
    """ Returns a list of all nodes considered by this FaceController, including the leaves that are directly controlled, and all the parents up to the root (always included for any FaceController with at least one node)"""
    #    for node in self.nodes.keys()[0].get_tree_root():
    out={}
    for n in self.get_controlled_nodes():
      out[n]=None
      while n.up and not n.up in out: 
        out[n.up]=None
        n=n.up
    return out.keys() if not ret_dict else out

  def plot_scatterplot(self):
    """ Open a pyqtgraph scatter in 2D based on the MDS analysis in 2 dimensions of this feature"""
    plot_title= 'Treedex - scatterplot #'
    plot_title+=str(self.Data().windows().next_window_index(plot_title))
    coordinate_selectors=[ CoordinateSelector(data_link=self.Data(), category='Feature Distance', feature_selector=self.feature_selector,
                                              processing='MDS2', parameters={'Dimension':'1', 'Distance':self.distance_name}), \
                           CoordinateSelector(data_link=self.Data(), category='Feature Distance', feature_selector=self.feature_selector, 
                                              processing='MDS2', parameters={'Dimension':'2', 'Distance':self.distance_name})]
    first_data_series= DataSeries(data_link=self.Data(), node_selection_name='All nodes', coordinate_selectors=coordinate_selectors)
    #test_transform=Transformation(rotation=None, translation=np.array([+2, +2]) )
    #first_data_series.set_transform(test_transform)
    plot_window=ScatterPlotWindow(data_link= self.Data(),  plot_title=plot_title, data_series=[first_data_series])
    plot_window.show()
    self.Data().windows().add_window(plot_title, plot_window)

  def plot_tridimensionalplot(self): 
    """ Open a pyqtgraph scatter-like in 3D based on the MDS analysis in 3 dimensions of this feature"""
    plot_title= 'Treedex - tridimensional plot #'
    plot_title+=str(self.Data().windows().next_window_index(plot_title))
    coordinate_selectors=[ CoordinateSelector(data_link=self.Data(), category='Feature Distance', feature_selector=self.feature_selector, processing='MDS3', parameters={'Dimension':'1', 'Distance':self.distance_name}), \
                           CoordinateSelector(data_link=self.Data(), category='Feature Distance', feature_selector=self.feature_selector, processing='MDS3', parameters={'Dimension':'2', 'Distance':self.distance_name}), \
                           CoordinateSelector(data_link=self.Data(), category='Feature Distance', feature_selector=self.feature_selector, processing='MDS3', parameters={'Dimension':'3', 'Distance':self.distance_name})]

    first_data_series= DataSeries(data_link=self.Data(), node_selection_name='All nodes', coordinate_selectors=coordinate_selectors)
    plot_window=TridimensionalPlotWindow(data_link= self.Data(),  plot_title=plot_title, data_series=[first_data_series])
    plot_window.show()
    self.Data().windows().add_window(plot_title, plot_window)
