from .baseplots import *  
import pyqtgraph.opengl as gl
from OpenGL.GL   import glRasterPos2f, glColor3f
from OpenGL.GLUT import glutBitmapCharacter, GLUT_BITMAP_HELVETICA_18, glutInit

glutInit()

def rgbcolor2glcolor(rgbstring, alpha=1.0, maxout=1.0, maxin=255.0):
  """Given a certain hexRGB color (e.g. F50587; where the max value for each color is 255, in hex code),
     returns the color as wanted by the OpenGL library, which is (r, g, b, alpha) where every value as max value of 1.0 """
  #rgbstring=rgbstring.lstrip('#')
  r, g, b = rgbstring[:2], rgbstring[2:4], rgbstring[4:]
  r, g, b = map(lambda x:(x/maxin)*maxout,   [int(r, 16), int(g, 16), int(b, 16)] )
  return (r, g, b, alpha)

################################################################################
class ToolbarViewMenu(ToolbarMenu):
  """ """
  def __init__(self, plot_item):
    super(ToolbarViewMenu, self).__init__(plot_item=plot_item)
    self.layout=QtGui.QVBoxLayout()
    self.setLayout(self.layout)

   ########     leafSpots section   #######
    # [v] Points for leaf nodes       Node filter:[NSW]      Color: [cm]
    #      Shape: [cb]/or dc/     Size: |___|[n]/or dc/    Alpha: |___|[n]/or dc/
    ls_options= self.plot_item.options['LeafSpots']
    ls_layout=  QtGui.QVBoxLayout()
    row1_layout=QtGui.QHBoxLayout()
    ls_checkbox=QtGui.QCheckBox(checked=ls_options['point_visible'])
    ls_checkbox.setText('Spots for leaf nodes')
    ls_checkbox.stateChanged.connect(self.clicked_leaf_spots_visible_checkbox)
    row1_layout.addWidget(ls_checkbox)
    #row1_layout.addSpacing(30)
    row1_layout.addWidget(VerticalLine('lightgrey'))
    ls_dcw=DataChannelWidget(plot_item.leaf_spots.dc)
    row1_layout.addWidget(ls_dcw)
    row1_layout.addStretch()

    row2_layout=QtGui.QHBoxLayout()
    row2_layout.addSpacing(30) #30 non stretchable pixels at the left end

    row2_layout.addWidget(QtGui.QLabel('Shape:'))
    shape=ls_options['shape']
    self.ls_shape_combobox=QtGui.QComboBox()
    self.ls_shape_combobox.possible_values=[('sphere','sphere'), ('cone','cone'), ('cylinder','cylinder'), ]
    for _,desc in self.ls_shape_combobox.possible_values: self.ls_shape_combobox.addItem(desc)
    self.ls_shape_combobox.setCurrentIndex(  [s for s,_ in self.ls_shape_combobox.possible_values].index(shape)   )
    self.ls_shape_combobox.currentIndexChanged[int].connect(self.activated_leaf_spots_shape_combobox)
    row2_layout.addWidget(self.ls_shape_combobox)
    row2_layout.addWidget(VerticalLine('lightgrey'))

    size=ls_options['size'] # from 0.1 to 2.0,   20 ticks
    row2_layout.addWidget(QtGui.QLabel('Size:'))
    self.ls_size_slider= QtGui.QSlider(QtCore.Qt.Horizontal)
    self.ls_size_slider.setMinimum(1);      self.ls_size_slider.setMaximum(20);    self.ls_size_slider.setValue(int(size*10))
    self.ls_size_slider.setTickInterval(1)
    self.ls_size_slider.valueChanged.connect( self.moved_leaf_spots_size_slider )
    self.ls_size_slider.resize(10,10)  #it's actually hitting below the minimum width limit, but that's fine
    self.ls_size_slider.setSizePolicy(fixed_size_policy)
    row2_layout.addWidget(self.ls_size_slider)
    self.ls_size_textbox=QtGui.QLineEdit()
    self.ls_size_textbox.setText(str(size))
    self.ls_size_textbox.setMaximumWidth(35) 
    self.ls_size_textbox.editingFinished.connect(self.edited_leaf_spots_size_textbox)   
    row2_layout.addWidget(self.ls_size_textbox)   
    # ls_fixed_size_checkbox=QtGui.QCheckBox(checked=ls_options['fixed_size'])  
    # ls_fixed_size_checkbox.setText('Independent of zoom')
    # ls_fixed_size_checkbox.stateChanged.connect(self.clicked_leaf_spots_fixed_size_checkbox)
    # row2_layout.addWidget(ls_fixed_size_checkbox)    
    row2_layout.addWidget(VerticalLine('lightgrey'))

    alpha=ls_options['alpha']
    row2_layout.addWidget(QtGui.QLabel('Alpha:'))
    self.ls_alpha_slider= QtGui.QSlider(QtCore.Qt.Horizontal)
    self.ls_alpha_slider.setMinimum(1);      self.ls_alpha_slider.setMaximum(10);    self.ls_alpha_slider.setValue(int(alpha*10))
    self.ls_alpha_slider.setTickInterval(1)
    self.ls_alpha_slider.valueChanged.connect( self.moved_leaf_spots_alpha_slider )
    self.ls_alpha_slider.setSizePolicy(fixed_size_policy)
    self.ls_alpha_slider.resize(10,10)  #hitting below the minimum height limit
    row2_layout.addWidget(self.ls_alpha_slider)
    self.ls_alpha_textbox=QtGui.QLineEdit()
    self.ls_alpha_textbox.setText( "{:.0%}".format(alpha) )
    self.ls_alpha_textbox.setMaximumWidth(40) 
    self.ls_alpha_textbox.editingFinished.connect(self.edited_leaf_spots_alpha_textbox)   
    row2_layout.addWidget(self.ls_alpha_textbox)   

    row2_layout.addStretch()  
    ls_layout.addLayout(row1_layout)
    ls_layout.addLayout(row2_layout)
    self.layout.addLayout(ls_layout)
    self.layout.addWidget(HorizontalLine('grey'))

    ########     leafLabels section   #######
    ll_options= self.plot_item.options['LeafLabels']
    ll_layout=  QtGui.QVBoxLayout()
    row1_layout=QtGui.QHBoxLayout()
    ll_checkbox=QtGui.QCheckBox(checked=ll_options['label_visible'])
    ll_checkbox.setText('Labels for leaf nodes')
    ll_checkbox.stateChanged.connect(self.clicked_leaf_labels_visible_checkbox)
    row1_layout.addWidget(ll_checkbox)
    #row1_layout.addSpacing(30)
    row1_layout.addWidget(VerticalLine('lightgrey'))
    ll_dcw=DataChannelWidget(plot_item.leaf_labels.dc)
    row1_layout.addWidget(ll_dcw)
    row1_layout.addStretch()  

    row2_layout=QtGui.QHBoxLayout()
    row2_layout.addSpacing(30) #30 non stretchable pixels at the left end
    label_field=ll_options['label_field']
    self.ll_label_field_textbox=QtGui.QLineEdit()
    self.ll_label_field_textbox.setText(label_field)
    self.ll_label_field_textbox.setMaximumWidth(75) 
    self.ll_label_field_textbox.editingFinished.connect(self.edited_leaf_labels_label_field_textbox)   
    row2_layout.addWidget(QtGui.QLabel('Display:'))
    row2_layout.addWidget(self.ll_label_field_textbox)

    fontsize=ll_options['font_size']
    row2_layout.addWidget(QtGui.QLabel('Font size:'))
    self.ll_size_slider= QtGui.QSlider(QtCore.Qt.Horizontal)
    self.ll_size_slider.setMinimum(4);      self.ll_size_slider.setMaximum(20);    self.ll_size_slider.setValue(fontsize)
    self.ll_size_slider.setTickInterval(1)
    self.ll_size_slider.valueChanged.connect( self.moved_leaf_labels_size_slider )
    self.ll_size_slider.resize(10,10)  #it's actually hitting below the minimum width limit, but that's fine
    self.ll_size_slider.setSizePolicy(fixed_size_policy)
    row2_layout.addWidget(self.ll_size_slider)
    self.ll_size_textbox=QtGui.QLineEdit()
    self.ll_size_textbox.setText(str(fontsize))
    self.ll_size_textbox.setMaximumWidth(25) 
    self.ll_size_textbox.editingFinished.connect(self.edited_leaf_labels_size_textbox)   
    row2_layout.addWidget(self.ll_size_textbox)   
    row2_layout.addWidget(VerticalLine('lightgrey'))

    # row2_layout.addWidget(QtGui.QLabel('Placed:'))
    # horiz_label=QtGui.QLabel();    horiz_label.setPixmap( get_pixmap('horizontal')  )
    # row2_layout.addWidget(horiz_label)#  QtGui.QLabel('horizontal'))
    # hanchor, vanchor= ll_options['anchor']
    # self.ll_anchor_h_combobox=QtGui.QComboBox()
    # self.ll_anchor_h_combobox.possible_values=[(1.0,'left'), (0.5,'center'),(0.0,'right')]
    # for _,desc in self.ll_anchor_h_combobox.possible_values: self.ll_anchor_h_combobox.addItem(desc)
    # self.ll_anchor_h_combobox.setCurrentIndex(  [s for s,_ in self.ll_anchor_h_combobox.possible_values].index(hanchor)   )
    # self.ll_anchor_h_combobox.currentIndexChanged[int].connect(self.activated_leaf_labels_anchor_h_combobox)
    # row2_layout.addWidget(self.ll_anchor_h_combobox)
    # row2_layout.addSpacing(5)
    # vert_label=QtGui.QLabel();    vert_label.setPixmap( get_pixmap('vertical')  )
    # row2_layout.addWidget(vert_label)#  QtGui.QLabel('horizontal'))
    # self.ll_anchor_v_combobox=QtGui.QComboBox()
    # self.ll_anchor_v_combobox.possible_values=[(1.0,'above'), (0.5,'center'),(0.0,'below')]
    # for _,desc in self.ll_anchor_v_combobox.possible_values: self.ll_anchor_v_combobox.addItem(desc)
    # self.ll_anchor_v_combobox.setCurrentIndex(  [s for s,_ in self.ll_anchor_v_combobox.possible_values].index(vanchor)   )
    # self.ll_anchor_v_combobox.currentIndexChanged[int].connect(self.activated_leaf_labels_anchor_v_combobox)
    # row2_layout.addWidget(self.ll_anchor_v_combobox)
    # row2_layout.addWidget(VerticalLine('lightgrey'))

    row2_layout.addStretch()  

    ll_layout.addLayout(row1_layout)
    ll_layout.addLayout(row2_layout)
    self.layout.addLayout(ll_layout)

  #############
  ## active feedback
  def clicked_leaf_spots_visible_checkbox(self, boxstate):
    self.plot_item.options['LeafSpots']['point_visible']=boxstate
    self.plot_item.update_item()
  def activated_leaf_spots_shape_combobox(self, index):    #index=self.ls_symbol_combobox.currentIndex()
    self.plot_item.options['LeafSpots']['shape']=self.ls_shape_combobox.possible_values[index][0]
    self.plot_item.update_item()

  def moved_leaf_spots_size_slider(self, value):
    real_value=value/10.
    self.plot_item.options['LeafSpots']['size']=real_value
    self.ls_size_textbox.setText(str(real_value))
    self.plot_item.update_item()

  def edited_leaf_spots_size_textbox(self):
    text=str(self.ls_size_textbox.text())
    try:     value=int(text.strip()); assert value>0 and value <=3
    except ValueError, AssertionError:
      QtGui.QMessageBox.warning(self, 'Error', 'Invalid value! Please enter a number between 1 and 20', QtGui.QMessageBox.Ok)
      self.ls_size_textbox.setText(str(self.plot_item.options['LeafSpots']['size']))
      return 
    self.plot_item.options['LeafSpots']['size']=value
    self.ls_size_slider.setValue( max([value, self.ls_size_slider.maximum()]) )
    self.plot_item.update_item()
  # def clicked_leaf_spots_fixed_size_checkbox(self, state):
  #   self.plot_item.options['LeafSpots']['fixed_size']=state
  #   self.plot_item.update_item()

  def moved_leaf_spots_alpha_slider(self, value): 
    alpha=round(value/10.0, 1)  # 1-10 range to  0.1-1.0
    self.plot_item.options['LeafSpots']['alpha']=alpha
    self.ls_alpha_textbox.setText("{:.0%}".format(alpha))
    self.plot_item.update_item()
  def edited_leaf_spots_alpha_textbox(self):
    text=str(self.ls_alpha_textbox.text())
    try:     alpha=float(text.rstrip('%'))/100; assert alpha>=0.01 and alpha<=1.0   # 1-100%   (or without % )   --> 0.01 - 1.0 
    except ValueError, AssertionError:
      QtGui.QMessageBox.warning(self, 'Error', 'Invalid value! Please enter a number between 1% and 100%', QtGui.QMessageBox.Ok)
      self.ls_alpha_textbox.setText("{:.0%}".format(self.plot_item.options['LeafSpots']['alpha']))
      return     
    self.plot_item.options['LeafSpots']['alpha']=alpha
    self.ls_alpha_slider.setValue(int(alpha*10))
    self.plot_item.update_item()

  ### LeafLabels
  def clicked_leaf_labels_visible_checkbox(self, boxstate):
    self.plot_item.options['LeafLabels']['label_visible']=boxstate
    self.plot_item.update_item()
  def edited_leaf_labels_label_field_textbox(self):
    text=str(self.ll_label_field_textbox.text()).strip()
    self.plot_item.options['LeafLabels']['label_field']=text
    self.plot_item.update_item()
  def moved_leaf_labels_size_slider(self, value):
    self.plot_item.options['LeafLabels']['font_size']=value
    self.ll_size_textbox.setText(str(value))
    self.plot_item.update_item()
  def edited_leaf_labels_size_textbox(self):
    text=str(self.ll_size_textbox.text())
    try:     value=int(text.strip()); assert value>0 and value<50
    except ValueError, AssertionError:
      QtGui.QMessageBox.warning(self, 'Error', 'Invalid value! Please enter a number between 1 and 50', QtGui.QMessageBox.Ok)
      self.ll_size_textbox.setText(str(self.plot_item.options['LeafLabels']['font_size']))
      return 
    self.plot_item.options['LeafLabels']['font_size']=value
    self.ll_size_slider.setValue( max([value, self.ll_size_slider.maximum()]) )
    self.plot_item.update_item()
  # def activated_leaf_labels_anchor_h_combobox(self, index):
  #   self.plot_item.options['LeafLabels']['anchor'][0]=self.ll_anchor_h_combobox.possible_values[index][0]
  #   self.plot_item.update_item()
  # def activated_leaf_labels_anchor_v_combobox(self, index):
  #   self.plot_item.options['LeafLabels']['anchor'][1]=self.ll_anchor_v_combobox.possible_values[index][0]
  #   self.plot_item.update_item()


class ToolbarAncestorsMenu(ToolbarMenu):
  """ """
  def __init__(self, plot_item):
    super(ToolbarAncestorsMenu, self).__init__(plot_item=plot_item)
    self.layout=QtGui.QVBoxLayout()
    self.setLayout(self.layout)

    ########     leafSpots section   #######
    # [v] Points for leaf nodes       Node filter:[NSW]      Color: [cm]
    #      Symbol: [cb]/or dc/     Size: |___|[n]/or dc/    Alpha: |___|[n]/or dc/
    as_options= self.plot_item.options['AncestralSpots']
    as_layout=  QtGui.QVBoxLayout()
    row1_layout=QtGui.QHBoxLayout()
    as_checkbox=QtGui.QCheckBox(checked=as_options['point_visible'])
    as_checkbox.setText('Spots for ancestral nodes')
    as_checkbox.stateChanged.connect(self.clicked_ancestral_spots_visible_checkbox)
    row1_layout.addWidget(as_checkbox)
    #row1_layout.addSpacing(30)
    row1_layout.addWidget(VerticalLine('lightgrey'))
    as_dcw=DataChannelWidget(plot_item.ancestral_spots.dc)
    row1_layout.addWidget(as_dcw)
    row1_layout.addStretch()

    row2_layout=QtGui.QHBoxLayout()
    row2_layout.addSpacing(30) #30 non stretchable pixels at the left end

    row2_layout.addWidget(QtGui.QLabel('Shape:'))
    shape=as_options['shape']
    self.as_shape_combobox=QtGui.QComboBox()
    self.as_shape_combobox.possible_values=[('sphere','sphere'), ('cone','cone'), ('cylinder','cylinder'), ] 
    for _,desc in self.as_shape_combobox.possible_values: self.as_shape_combobox.addItem(desc)
    self.as_shape_combobox.setCurrentIndex(  [s for s,_ in self.as_shape_combobox.possible_values].index(shape)   )
    self.as_shape_combobox.currentIndexChanged[int].connect(self.activated_ancestral_spots_shape_combobox)
    row2_layout.addWidget(self.as_shape_combobox)
    row2_layout.addWidget(VerticalLine('lightgrey'))

    size=as_options['size']
    row2_layout.addWidget(QtGui.QLabel('Size:'))
    self.as_size_slider= QtGui.QSlider(QtCore.Qt.Horizontal)
    self.as_size_slider.setMinimum(1);      self.as_size_slider.setMaximum(20);    self.as_size_slider.setValue(int(size*10))
    self.as_size_slider.setTickInterval(1)
    self.as_size_slider.valueChanged.connect( self.moved_ancestral_spots_size_slider )
    self.as_size_slider.resize(10,10)  #it's actually hitting below the minimum width limit, but that's fine
    self.as_size_slider.setSizePolicy(fixed_size_policy)
    row2_layout.addWidget(self.as_size_slider)
    self.as_size_textbox=QtGui.QLineEdit()
    self.as_size_textbox.setText(str(size))
    self.as_size_textbox.setMaximumWidth(35) 
    self.as_size_textbox.editingFinished.connect(self.edited_ancestral_spots_size_textbox)   
    row2_layout.addWidget(self.as_size_textbox)   
    row2_layout.addWidget(VerticalLine('lightgrey'))

    alpha=as_options['alpha']
    row2_layout.addWidget(QtGui.QLabel('Alpha:'))
    self.as_alpha_slider= QtGui.QSlider(QtCore.Qt.Horizontal)
    self.as_alpha_slider.setMinimum(1);      self.as_alpha_slider.setMaximum(10);    self.as_alpha_slider.setValue(int(alpha*10))
    self.as_alpha_slider.setTickInterval(1)
    self.as_alpha_slider.valueChanged.connect( self.moved_ancestral_spots_alpha_slider )
    self.as_alpha_slider.setSizePolicy(fixed_size_policy)
    self.as_alpha_slider.resize(10,10)  #hitting below the minimum height limit
    row2_layout.addWidget(self.as_alpha_slider)
    self.as_alpha_textbox=QtGui.QLineEdit()
    self.as_alpha_textbox.setText( "{:.0%}".format(alpha) )
    self.as_alpha_textbox.setMaximumWidth(40) 
    self.as_alpha_textbox.editingFinished.connect(self.edited_ancestral_spots_alpha_textbox)   
    row2_layout.addWidget(self.as_alpha_textbox)   

    row2_layout.addStretch()  
    as_layout.addLayout(row1_layout)
    as_layout.addLayout(row2_layout)
    self.layout.addLayout(as_layout)
    self.layout.addWidget(HorizontalLine('grey'))

    ########     leafLabels section   #######
    al_options= self.plot_item.options['AncestralLabels']
    al_layout=  QtGui.QVBoxLayout()
    row1_layout=QtGui.QHBoxLayout()
    al_checkbox=QtGui.QCheckBox(checked=al_options['label_visible'])
    al_checkbox.setText('Labels for ancestral nodes')
    al_checkbox.stateChanged.connect(self.clicked_ancestral_labels_visible_checkbox)
    row1_layout.addWidget(al_checkbox)
    #row1_layout.addSpacing(30)
    row1_layout.addWidget(VerticalLine('lightgrey'))
    al_dcw=DataChannelWidget(plot_item.ancestral_labels.dc)
    row1_layout.addWidget(al_dcw)
    row1_layout.addStretch()  

    row2_layout=QtGui.QHBoxLayout()
    row2_layout.addSpacing(30) #30 non stretchable pixels at the left end
    label_field=al_options['label_field']
    self.al_label_field_textbox=QtGui.QLineEdit()
    self.al_label_field_textbox.setText(label_field)
    self.al_label_field_textbox.setMaximumWidth(75) 
    self.al_label_field_textbox.editingFinished.connect(self.edited_ancestral_labels_label_field_textbox)   
    row2_layout.addWidget(QtGui.QLabel('Display:'))
    row2_layout.addWidget(self.al_label_field_textbox)

    fontsize=al_options['font_size']
    row2_layout.addWidget(QtGui.QLabel('Size:'))
    self.al_size_slider= QtGui.QSlider(QtCore.Qt.Horizontal)
    self.al_size_slider.setMinimum(4);      self.al_size_slider.setMaximum(20);    self.al_size_slider.setValue(fontsize)
    self.al_size_slider.setTickInterval(1)
    self.al_size_slider.valueChanged.connect( self.moved_ancestral_labels_size_slider )
    self.al_size_slider.resize(10,10)  #it's actually hitting below the minimum width limit, but that's fine
    self.al_size_slider.setSizePolicy(fixed_size_policy)
    row2_layout.addWidget(self.al_size_slider)
    self.al_size_textbox=QtGui.QLineEdit()
    self.al_size_textbox.setText(str(fontsize))
    self.al_size_textbox.setMaximumWidth(25) 
    self.al_size_textbox.editingFinished.connect(self.edited_ancestral_labels_size_textbox)   
    row2_layout.addWidget(self.al_size_textbox)   
    row2_layout.addWidget(VerticalLine('lightgrey'))

    # row2_layout.addWidget(QtGui.QLabel('Placed:'))
    # horiz_label=QtGui.QLabel();    horiz_label.setPixmap( get_pixmap('horizontal')  )
    # row2_layout.addWidget(horiz_label)#  QtGui.QLabel('horizontal'))
    # hanchor, vanchor= al_options['anchor']
    # self.al_anchor_h_combobox=QtGui.QComboBox()
    # self.al_anchor_h_combobox.possible_values=[(1.0,'left'), (0.5,'center'),(0.0,'right')]
    # for _,desc in self.al_anchor_h_combobox.possible_values: self.al_anchor_h_combobox.addItem(desc)
    # self.al_anchor_h_combobox.setCurrentIndex(  [s for s,_ in self.al_anchor_h_combobox.possible_values].index(hanchor)   )
    # self.al_anchor_h_combobox.currentIndexChanged[int].connect(self.activated_ancestral_labels_anchor_h_combobox)
    # row2_layout.addWidget(self.al_anchor_h_combobox)
    # row2_layout.addSpacing(5)
    # vert_label=QtGui.QLabel();    vert_label.setPixmap( get_pixmap('vertical')  )
    # row2_layout.addWidget(vert_label)#  QtGui.QLabel('horizontal'))
    # self.al_anchor_v_combobox=QtGui.QComboBox()
    # self.al_anchor_v_combobox.possible_values=[(1.0,'above'), (0.5,'center'),(0.0,'below')]
    # for _,desc in self.al_anchor_v_combobox.possible_values: self.al_anchor_v_combobox.addItem(desc)
    # self.al_anchor_v_combobox.setCurrentIndex(  [s for s,_ in self.al_anchor_v_combobox.possible_values].index(vanchor)   )
    # self.al_anchor_v_combobox.currentIndexChanged[int].connect(self.activated_ancestral_labels_anchor_v_combobox)
    # row2_layout.addWidget(self.al_anchor_v_combobox)
    # row2_layout.addWidget(VerticalLine('lightgrey'))
    row2_layout.addStretch()  

    al_layout.addLayout(row1_layout)
    al_layout.addLayout(row2_layout)
    self.layout.addLayout(al_layout)
    self.layout.addWidget(HorizontalLine('grey'))

    # ### AncestralPaths
    ap_options= self.plot_item.options['AncestralPaths']
    ap_layout=  QtGui.QVBoxLayout()
    row1_layout=QtGui.QHBoxLayout()
    ap_checkbox=QtGui.QCheckBox(checked=ap_options['line_visible'])
    ap_checkbox.setText('Feature paths')
    ap_checkbox.stateChanged.connect(self.clicked_ancestral_paths_visible_checkbox)
    row1_layout.addWidget(ap_checkbox)
    #row1_layout.addSpacing(30)
    row1_layout.addWidget(VerticalLine('lightgrey'))
    ap_dcw=DataChannelWidget(plot_item.ancestral_paths.dc)
    row1_layout.addWidget(ap_dcw)

    row1_layout.addStretch()  

    row2_layout=QtGui.QHBoxLayout()
    row2_layout.addSpacing(30) #30 non stretchable pixels at the left end
    width=ap_options['line_width']
    row2_layout.addWidget(QtGui.QLabel('Width:'))
    self.ap_width_slider= QtGui.QSlider(QtCore.Qt.Horizontal)
    self.ap_width_slider.setMinimum(1);      self.ap_width_slider.setMaximum(10);    self.ap_width_slider.setValue(int(width*2))
    self.ap_width_slider.setTickInterval(1)
    self.ap_width_slider.valueChanged.connect( self.moved_ancestral_paths_width_slider )
    self.ap_width_slider.resize(10,10)  #it's actually hitting below the minimum width limit, but that's fine
    self.ap_width_slider.setSizePolicy(fixed_size_policy)
    row2_layout.addWidget(self.ap_width_slider)
    self.ap_width_textbox=QtGui.QLineEdit()
    self.ap_width_textbox.setText("{:.1f}".format(width))
    self.ap_width_textbox.setMaximumWidth(30) 
    self.ap_width_textbox.editingFinished.connect(self.edited_ancestral_paths_width_textbox)   
    row2_layout.addWidget(self.ap_width_textbox)   
    row2_layout.addWidget(VerticalLine('lightgrey'))

    alpha=ap_options['line_alpha']
    row2_layout.addWidget(QtGui.QLabel('Alpha:'))
    self.ap_alpha_slider= QtGui.QSlider(QtCore.Qt.Horizontal)
    self.ap_alpha_slider.setMinimum(1);      self.ap_alpha_slider.setMaximum(10);    self.ap_alpha_slider.setValue(int(alpha*10))
    self.ap_alpha_slider.setTickInterval(1)
    self.ap_alpha_slider.valueChanged.connect( self.moved_ancestral_paths_alpha_slider )
    self.ap_alpha_slider.setSizePolicy(fixed_size_policy)
    self.ap_alpha_slider.resize(10,10)  #hitting below the minimum height limit
    row2_layout.addWidget(self.ap_alpha_slider)
    self.ap_alpha_textbox=QtGui.QLineEdit()
    self.ap_alpha_textbox.setText( "{:.0%}".format(alpha) )
    self.ap_alpha_textbox.setMaximumWidth(40) 
    self.ap_alpha_textbox.editingFinished.connect(self.edited_ancestral_paths_alpha_textbox)   
    row2_layout.addWidget(self.ap_alpha_textbox)   

    row2_layout.addStretch()  

    ap_layout.addLayout(row1_layout)
    ap_layout.addLayout(row2_layout)
    self.layout.addLayout(ap_layout)    


  #ancestral spots
  def clicked_ancestral_spots_visible_checkbox(self, boxstate):
    self.plot_item.options['AncestralSpots']['point_visible']=boxstate
    self.plot_item.update_item()
  def activated_ancestral_spots_shape_combobox(self, index):    #index=self.ls_symbol_combobox.currentIndex()
    self.plot_item.options['AncestralSpots']['shape']=self.as_shape_combobox.possible_values[index][0]
    self.plot_item.update_item()

  def moved_ancestral_spots_size_slider(self, value):
    real_value=value/10.
    self.plot_item.options['AncestralSpots']['size']=real_value
    self.as_size_textbox.setText(str(real_value))
    self.plot_item.update_item()

  def edited_ancestral_spots_size_textbox(self):
    text=str(self.as_size_textbox.text())
    try:     value=int(text.strip()); assert value>0 and value <=3
    except ValueError, AssertionError:
      QtGui.QMessageBox.warning(self, 'Error', 'Invalid value! Please enter a number between 1 and 20', QtGui.QMessageBox.Ok)
      self.as_size_textbox.setText(str(self.plot_item.options['AncestralSpots']['size']))
      return 
    self.plot_item.options['AncestralSpots']['size']=value
    self.as_size_slider.setValue( max([value, self.as_size_slider.maximum()]) )
    self.plot_item.update_item()
  # def clicked_leaf_spots_fixed_size_checkbox(self, state):
  #   self.plot_item.options['LeafSpots']['fixed_size']=state
  #   self.plot_item.update_item()

  def moved_ancestral_spots_alpha_slider(self, value): 
    alpha=round(value/10.0, 1)  # 1-10 range to  0.1-1.0
    self.plot_item.options['AncestralSpots']['alpha']=alpha
    self.as_alpha_textbox.setText("{:.0%}".format(alpha))
    self.plot_item.update_item()
  def edited_ancestral_spots_alpha_textbox(self):
    text=str(self.as_alpha_textbox.text())
    try:     alpha=float(text.rstrip('%'))/100; assert alpha>=0.01 and alpha<=1.0  # 1-100%   (or without % )   --> 0.01 - 1.0 
    except ValueError, AssertionError:
      QtGui.QMessageBox.warning(self, 'Error', 'Invalid value! Please enter a number between 1% and 100%', QtGui.QMessageBox.Ok)
      self.as_alpha_textbox.setText("{:.0%}".format(self.plot_item.options['AncestralSpots']['alpha']))
      return     
    self.plot_item.options['AncestralSpots']['alpha']=alpha
    self.as_alpha_slider.setValue(int(alpha*10))
    self.plot_item.update_item()

  ### AncestralLabels
  def clicked_ancestral_labels_visible_checkbox(self, boxstate):
    self.plot_item.options['AncestralLabels']['label_visible']=boxstate
    self.plot_item.update_item()
  def edited_ancestral_labels_label_field_textbox(self):
    text=str(self.al_label_field_textbox.text()).strip()
    self.plot_item.options['AncestralLabels']['label_field']=text
    self.plot_item.update_item()
  def moved_ancestral_labels_size_slider(self, value):
    self.plot_item.options['AncestralLabels']['font_size']=value
    self.al_size_textbox.setText(str(value))
    self.plot_item.update_item()
  def edited_ancestral_labels_size_textbox(self):
    text=str(self.al_size_textbox.text())
    try:     value=int(text.strip()); assert value>0 and value<50
    except ValueError, AssertionError:
      QtGui.QMessageBox.warning(self, 'Error', 'Invalid value! Please enter a number between 1 and 50', QtGui.QMessageBox.Ok)
      self.al_size_textbox.setText(str(self.plot_item.options['AncestralLabels']['font_size']))
      return 
    self.plot_item.options['AncestralLabels']['font_size']=value
    self.al_size_slider.setValue( max([value, self.al_size_slider.maximum()]) )
    self.plot_item.update_item()
  # def activated_ancestral_labels_anchor_h_combobox(self, index):
  #   self.plot_item.options['AncestralLabels']['anchor'][0]=self.al_anchor_h_combobox.possible_values[index][0]
  #   self.plot_item.update_item()
  # def activated_ancestral_labels_anchor_v_combobox(self, index):
  #   self.plot_item.options['AncestralLabels']['anchor'][1]=self.al_anchor_v_combobox.possible_values[index][0]
  #   self.plot_item.update_item()

  ### AncestralPaths
  def clicked_ancestral_paths_visible_checkbox(self, boxstate):
    self.plot_item.options['AncestralPaths']['line_visible']=boxstate
    self.plot_item.update_item()
  def moved_ancestral_paths_width_slider(self, value):
    width=round(value/2.0, 1)  # 1-10 range to  0.5-5.0
    self.plot_item.options['AncestralPaths']['line_width']=width
    self.ap_width_textbox.setText("{:.1f}".format(width))
    self.plot_item.update_item()
  def edited_ancestral_paths_width_textbox(self):
    text=str(self.ap_width_textbox.text())
    try:     width=float(text); assert width>=0.5 and width<=5.0
    except ValueError, AssertionError:
      QtGui.QMessageBox.warning(self, 'Error', 'Invalid value! Please enter a number between 0.5 and 5.0', QtGui.QMessageBox.Ok)
      self.ap_width_textbox.setText("{:.1f}".format(self.plot_item.options['AncestralPaths']['line_width']))
      return     
    self.plot_item.options['AncestralPaths']['line_width']=width
    self.ap_width_slider.setValue(int(width*2))
    self.plot_item.update_item()
  def moved_ancestral_paths_alpha_slider(self, value): 
    alpha=round(value/10.0, 1)  # 1-10 range to  0.1-1.0
    self.plot_item.options['AncestralPaths']['line_alpha']=alpha
    self.ap_alpha_textbox.setText("{:.0%}".format(alpha))
    self.plot_item.update_item()
  def edited_ancestral_paths_alpha_textbox(self):
    text=str(self.ap_alpha_textbox.text())
    try:     alpha=float(text.rstrip('%'))/100; assert alpha>=0.01 and alpha<=1.0  # 1-100%   (or without % )   --> 0.01 - 1.0 
    except ValueError, AssertionError:
      QtGui.QMessageBox.warning(self, 'Error', 'Invalid value! Please enter a number between 1% and 100%', QtGui.QMessageBox.Ok)
      self.ap_alpha_textbox.setText("{:.0%}".format(self.plot_item.options['AncestralPaths']['line_alpha']))
      return     
    self.plot_item.options['AncestralPaths']['line_alpha']=alpha
    self.ap_alpha_slider.setValue(int(alpha*10))
    self.plot_item.update_item()





class ToolbarInteractivityMenu(ToolbarMenu):
  """ """
  def __init__(self, plot_item):
    super(ToolbarInteractivityMenu, self).__init__(plot_item=plot_item)
    self.layout=QtGui.QVBoxLayout()
    self.setLayout(self.layout)

    row1=QtGui.QHBoxLayout()
    row1.addWidget(QtGui.QLabel('Clicking a spot '))
    self.click_combobox=QtGui.QComboBox()
    self.click_combobox.possible_values=[('s', 'select nodes'), ('h', 'highlight nodes'), ('n', 'has no effect')]
    for index, (value, displayed) in enumerate(self.click_combobox.possible_values):
      self.click_combobox.addItem(displayed)
      if self.plot_item.options['on_click']==value:  self.click_combobox.setCurrentIndex(index)
    self.click_combobox.currentIndexChanged[int].connect(self.activated_click_combobox)
    row1.addWidget(self.click_combobox)
    row1.addStretch()
    self.layout.addLayout(row1)

    row2=QtGui.QHBoxLayout()
    self.mark_combobox=QtGui.QComboBox()
    self.mark_combobox.possible_values=[('s', 'Selected nodes'), ('h', 'Highlighted nodes'), ('n', '(Nothing)')]
    for index, (value, displayed) in enumerate(self.mark_combobox.possible_values):
      self.mark_combobox.addItem(displayed)
      if self.plot_item.options['mark_what']==value:  self.mark_combobox.setCurrentIndex(index)
    self.mark_combobox.currentIndexChanged[int].connect(self.activated_mark_combobox)
    row2.addWidget(self.mark_combobox)
    row2.addWidget(QtGui.QLabel(' are marked with projections of color '))
    self.mark_color_button=TreedexColorButton()
    self.mark_color_button.load_color( self.plot_item.options['mark_color'] )
    self.mark_color_button.sigColorChanged.connect(self.picked_mark_color)
    row2.addWidget(self.mark_color_button)
    row2.addStretch()
    self.layout.addLayout(row2)

   
  def activated_click_combobox(self, index):
    self.plot_item.options['on_click']=self.click_combobox.possible_values[index][0]

  def activated_mark_combobox(self, index):
    self.plot_item.options['mark_what']=self.mark_combobox.possible_values[index][0]
    self.plot_item.leaf_spots.update_marking_dc() 

  def picked_mark_color(self):
    self.plot_item.options['mark_color']=self.mark_color_button.get_color()
    self.plot_item.leaf_spots.update_marking_dc()

################################################################################

class NodePlot3DToolbar(PlotItemToolbar): 
  view_menu=ToolbarViewMenu    
  ancestors_menu=ToolbarAncestorsMenu
  interactivity_menu=ToolbarInteractivityMenu 
    
################################################################################
class NodePlot3DItem(PlotItem):
  plot_type='plot3D'
  defaults={ 'name':None, 
             'mark_color':'DDDDDD',  'mark_alpha':0.6,  'mark_width':1.0, 'mark_what':'s',  'on_click':'s',              
             'LeafSpots': {'point_visible':True,  'size':0.3,      'shape':'sphere',        'alpha':0.5,        },
             'LeafLabels':{'label_visible':False, 'font_size':7, 'anchor':[0.5, 0.5, 1.0], 'label_field':'Node',},
             'AncestralSpots': { 'point_visible':False, 'size':0.3,         'shape':'cone',   'alpha':0.5,    },
             'AncestralLabels': {'label_visible':False, 'font_size':7,    'anchor':[0.5, 1.0], 'label_field':'Node',},
             'AncestralPaths': { 'line_visible': False, 'line_width':1.5, 'line_alpha':0.5,                         }
} 
  #'fixed_size':True, ## pg bug when pxMode != True
  toolbar_class=NodePlot3DToolbar

  ################ Is all this identical to Scatterplot??
  ##### 
  def init_data_channel(self, cache_name):    
    #if   self.dc is None: 
    self.dc=DataChannel(self.plot_object.plot_window.dco_link)      #the container of the self.dc is a DCO_group (actually DCO_smart-> DCO_scatterplot) which is present in some visible DCW
    ### here: may add from dc_string   as in duplicate_item
    # elif type(self.dc) == str:  #a DC key was provided ##### NOPE
    #   self.dc=DataChannel(self.plot_object.plot_window.dco_link, from_key=self.dc)           

    dc=self.dc
    dc.muted=True
    if not dc.chain    or dc.chain[0].name!= 'lockinsert':         dc.insert(0, DCO_lockinsert())
    if len(dc.chain)<2 or dc.chain[1].key()!='retrieve:PlotInput': dc.insert(1, DCO_retrieve('PlotInput'))
    dc.set_lock(1, state=2)  #### make MODIFIABLE BUT NOT DELETABLE
    #if len(dc.chain)>2 and isinstance)dc.chain[2].name=='adapter' and dc.chain[2].parameters[:dc.chain[2].parameters.index('[')]=='scatterplot' :      
    #  dco_adapter_w_base_type=dc.pop()   # this is a basic group type, instead of DCO_adapter
    #  dc.insert(2, self.DCO_adapter(dco_adapter_w_base_type.parameters, backtrace=True) )
    #else:
    dc.insert(2, self.DCO_adapter() )   

    piname=self.options['name']
    cache_name=piname+'@1'
    if dc.chain[-1].name!='lockappend':         dc.append(DCO_lockappend())
    if dc.chain[-2].key()!='cache:'+cache_name: dc.insert(len(dc.chain)-1, DCO_cache(cache_name))
    dc.set_lock(len(dc.chain)-2)
    if dc.chain[-3].name!='lockappend':         dc.insert(len(dc.chain)-2, DCO_lockappend())
    if dc.chain[-4].name!='scale':              dc.insert(len(dc.chain)-3, DCO_scale('@:@:0^:1^|@n^|^@^|r^')       )
    dc.set_lock(len(dc.chain)-4, 2)
    if dc.chain[-5].name!='color:':             dc.insert(len(dc.chain)-4,   DCO_color('m|TreeColor'))  #initializing with parameters None
    dc.set_lock(len(dc.chain)-5, 2)
    if dc.chain[-6].name!='trace:':             dc.insert(len(dc.chain)-5,   DCO_trace())  #initializing with parameters None
    dc.muted=False
    dc.notify_modification()

    store_headers_fn=lambda:self.store_headers(3)
    dc.signal_value_changed.connect(store_headers_fn)
    dc.signal_value_changed.connect(self.plot_object.plot_window.update_axis)
    #dc.signal_dc_changed.connect(   store_headers_fn)
    #dc.signal_dc_changed.connect(   self.plot_object.plot_window.update_axis)


  def init_item(self):
    print 'init plot3d, ', self.options['name'], id(self.options)
    self.leaf_spots=     self.LeafSpots( self, 'LeafSpots', marking=True) 
    self.leaf_labels=    self.LeafLabels(self, 'LeafLabels') 
    self.ancestral_spots= self.AncestralSpots(self,  'AncestralSpots') 
    self.ancestral_labels=self.AncestralLabels(self, 'AncestralLabels') 
    self.ancestral_paths= self.AncestralPaths(self,  'AncestralPaths') 
    self.store_headers(3)

    ### add other components

  def update_item(self):
    delta=self.delta_options()
    print 'updating plot3d? n={n} delta={d}'.format(n=self.options['name'], d=delta)
    updated_some_component=False
    if 'name' in delta:   
      piname=self.options['name']
      cache_name=piname+'@1'    
      self.toolbar.plotitem_label.setText(piname)
      ## updating cache DCO in pi.dc and retrieve DCOs and pi_components .dc
      self.dc.chain[-2].update(cache_name)
      self.leaf_spots.dc.chain[1].update(piname)
      self.leaf_labels.dc.chain[1].update(piname)
      self.ancestral_spots.dc.chain[1].update(piname)
      self.ancestral_labels.dc.chain[1].update(piname)
      self.ancestral_paths.dc.chain[1].update(piname)
      updated_some_component=True

    if 'LeafSpots' in delta:
      print '  -update leafspots'
      self.leaf_spots.update_plot()    #'LeafSpots')
      self.leaf_spots.update_marking() #'LeafSpots')
      updated_some_component=True

    if 'LeafLabels' in delta:
      print '  -update leaflabels'
      self.leaf_labels.update_plot() #'LeafLabels')
      updated_some_component=True

    if 'AncestralSpots' in delta:
      print '  -update ancestralspots'
      self.ancestral_spots.update_plot() #'AncestralSpots')
      updated_some_component=True

    if 'AncestralLabels' in delta:
      print '  -update ancestrallabels'
      self.ancestral_labels.update_plot() #'AncestralLabels')
      updated_some_component=True

    if 'AncestralPaths' in delta:
      print '  -update ancestralpaths'
      self.ancestral_paths.update_plot() #'AncestralPaths')
      updated_some_component=True
    # update other components..

    if updated_some_component: #not self.computed_data is FLAG:   
      # self.store_headers(self.computed_data, 2)
      # self.plot_object.plot_window.update_axis()
      self.store_plot_options()

  def delete_item(self):
    ### add remove DC! # also link close window to run this
    self.dc.delete()
    self.leaf_spots.dc.delete()
    self.leaf_spots.marking_dc.delete()    
    self.leaf_spots.update_plot() #      'LeafSpots')
    self.leaf_labels.dc.delete()    
    self.leaf_labels.update_plot() #     'LeafLabels')
    self.ancestral_labels.dc.delete()
    self.ancestral_labels.update_plot() #'AncestralLabels')
    self.ancestral_spots.dc.delete()
    self.ancestral_spots.update_plot() # 'AncestralSpots') 
    self.ancestral_paths.dc.delete()
    self.ancestral_paths.update_plot() # 'AncestralPaths')
    print 'delete item!'

  ################ Is all this identical to Scatterplot??  --END


  ############## The DCO adapter used by this PlotItem
  #
  class DCO_adapter(DCO_smart):
    """ """
    icon_name='plot3D'
    #name='adapter'
    default_parameters='$2;$3;$4;Y'
    tooltip='plot3D'
    def short(self): return 'Adapter'    
    def expand_parameters(self, parameters):
      x_selector,y_selector,z_selector,discard_others=parameters.split(';')
      p='plot3D_adapter[shapecheck:c>2&Node@c{sep}var:xfield={x}{sep}var:yfield={y}{sep}var:zfield={z}{sep}\
typecheck:$xfield,$yfield,$zfield=n{sep}select:$xfield,$yfield,$zfield,Node{d}]'.format(
        sep=DataChannel.dco_separator_char, x=x_selector, y=y_selector, z=z_selector,  d=',:' if discard_others=='N' else '')
      return p  #{sep}process:label=Node
    def backtrace_parameters(self, parameters):
      splt=parameters.split(DataChannel.dco_separator_char)
      x_selector=splt[1][splt[1].index('=')+1:]
      y_selector=splt[2][splt[2].index('=')+1:]
      z_selector=splt[3][splt[3].index('=')+1:]
      p='{};{};{};{}'.format(x_selector, y_selector, z_selector, 'N' if parameters.endswith(',:]') else 'Y' )
      return p
   
   ############# the widget of this DCO:
    class DCOW_class(DCOW):
      def __init__(self, dcw, dco):
        DCOW.__init__(self, dcw, dco)   #super(DCOW_class, self).__init__(dcw, dco) 
        self.layout=QtGui.QVBoxLayout(); self.layout.setContentsMargins(0,0,0,0); self.layout.setSpacing(2)
        self.setLayout(self.layout)
        x_selector,y_selector,z_selector,discard_others=self.dco.backtrace_parameters( self.dco.parameters ).split(';')

        row1=QtGui.QHBoxLayout();  row1.setContentsMargins(1,1,1,1); row1.setSpacing(5)
        self.textbox_x=QtGui.QLineEdit(x_selector, self)
        self.textbox_x.setMaximumWidth(100)
        self.textbox_y=QtGui.QLineEdit(y_selector, self)
        self.textbox_y.setMaximumWidth(100)
        self.textbox_z=QtGui.QLineEdit(z_selector, self)
        self.textbox_z.setMaximumWidth(100)
        row1.addWidget(QtGui.QLabel('x='))
        row1.addWidget(self.textbox_x)
        row1.addWidget(QtGui.QLabel('y='))
        row1.addWidget(self.textbox_y)
        row1.addWidget(QtGui.QLabel('z='))
        row1.addWidget(self.textbox_z)
        self.layout.addLayout(row1)

        row2=QtGui.QHBoxLayout();  row2.setContentsMargins(1,1,1,1); row2.setSpacing(5)
        self.discard_others_checkbox=QtGui.QCheckBox()
        self.discard_others_checkbox.setText('Discard other columns')
        if discard_others: self.discard_others_checkbox.setChecked(True)
        row2.addWidget(self.discard_others_checkbox)
        self.layout.addLayout(row2)        

      def save(self):
        new_text='{};{};{};{}'.format(str(self.textbox_x.text()).strip(), str(self.textbox_y.text()).strip(), str(self.textbox_z.text()).strip(),  {True:'Y',False:'N'}[self.discard_others_checkbox.isChecked()] )
        self.update_dco(new_text)  #expand_parameters happening under the hood



  ########################  
  ### PlotItem Components
  class LeafSpots(object):
    dc_template_key='lockinsert:None{sep}retrieve:{name}{sep}nodeFilter:All leaves^{sep}lockappend:None'
    def __init__(self, plot_item, options_key,  marking=False):      
      self.plot_item=plot_item
      self.options_key=options_key
      piname=self.plot_item.options['name']
      self.dc=DataChannel(plot_item.plot_object.plot_window.dco_link, 
                          from_key=self.dc_template_key.format(sep=DataChannel.dco_separator_char, name=piname))
      self.dc.set_lock(1)     ##### unmodifiable
      self.dc.set_lock(2, state=2)  # unremovable
      self.dc.signal_value_changed.connect(self.update_plot)# fn_update)
      #self.dc.signal_dc_changed.connect(self.update_plot)
      self.df_index2spot={}
      self.dc.out()  #-> #self.update_plot()
      if marking: 
        self.dc.signal_dc_changed.connect(self.update_marking_dc)
        self.plot_item.dc.signal_dc_changed.connect(self.update_marking_dc)
        self.update_marking_dc(first_run=True)      

    def update_plot(self): 
      df=self.dc.out()
      write( 'update plot item 3d '+self.options_key, 1, how='blue')
      for ball in self.df_index2spot.values():      
        #write( ('remove ball 3d ', ball), 1, how='blue')
        self.plot_item.plot_object.removeItem(ball)  #cleaning up
      # ## debug for console
      # self.plot_item.plot_object.plot_window.master().ls=self
      local_options=self.plot_item.options[self.options_key]
      self.df_index2spot={}
      s=self.plot_item.plot_object.active_space_size   # scaling factor; input is 0-1 and must fill the 3D space
      if df is None: pass
      else:
        if local_options['point_visible']: 
          try: 
            default_color=self.plot_item.plot_object.plot_window.master().colors().get_default_color()
            for i, row_i in enumerate(df.index):
              is_visible=smart_get('point_visible', local_options, df, row_i)
              if not is_visible: continue
              node_name=df.at[row_i, 'Node']        if not df.index.name=='Node' else row_i
              xcoord=float(df.iat[i,0])*s            #df.at[row_i,xdf.columns[0]])  
              ycoord=float(df.iat[i,1])*s            #df.at[row_i,ydf.columns[0]])
              zcoord=float(df.iat[i,2])*s            #df.at[row_i,ydf.columns[0]])

              shape=smart_get('shape', local_options, df, row_i )
              size= smart_get('size', local_options, df, row_i )
              alpha=smart_get('alpha', local_options, df, row_i ) 
              color= smart_get('color', local_options, df, row_i, default=default_color)  #without '#'
              glcolor= rgbcolor2glcolor(color, alpha)
              mesh=self.plot_item.plot_object.meshes[shape]
              spot = gl.GLMeshItem(meshdata=mesh, smooth=True, color=glcolor, shader='balloon', glOptions='additive')              
              t=pg.Transform3D([size, 0.0, 0.0, xcoord, 0.0, size, 0.0, ycoord, 0.0, 0.0, size, zcoord, 0.0, 0.0, 0.0, 1.0])
              spot.setTransform(t)
              self.plot_item.plot_object.addItem(spot)
              self.df_index2spot[ row_i ] = spot
              spot.df_index=row_i
              spot.plot_item=self.plot_item
              #

          except IndexError as e: #Exception as e:
            QtGui.QMessageBox.warning(self.plot_item.plot_object.plot_window, 'Error', 'Error while plotting {} !\n{}'.format(self.options_key, e), QtGui.QMessageBox.Ok)
            
          # so that later you can do get the spot for any given row_i  -- which here is spot.data()

    def update_marking_dc(self, first_run=False):
      write( ('update marking DC start'), 1, how='red,reverse')
      if not first_run: 
        self.marking_dc.delete()        
        for line_pack in self.df_index2line_items.values():   
          for line_item in line_pack:          self.plot_item.plot_object.removeItem(line_item)
      selname= {'n':None, 's':'Selected nodes', 'h':'Highlighted nodes'} [self.plot_item.options['mark_what']]
      self.df_index2line_items={}
      if selname is None:    
        self.marking_dc=DataChannel(self.dc.container)      #self.dc.copy() #auto_update=False)
        self.update_marking() #options_key)               #restoring everything as non marked
      else:
        self.marking_dc=self.dc.copy() #auto_update=False)     ##the out of this DC will be with a '_mark' column that is True if this spot needs to be marked, NaN otherwise
        self.marking_dc.muted=True
        #self.marking_dc.append(DCO_nodeFilter(selname))      
        self.marking_dc.append(DCO_select('Node,color'))      
        self.marking_dc.append(DCO_nodeFilter('All leaves'))      
        self.marking_dc.append(DCO_cache('_w'))      
        self.marking_dc.append(DCO_antenna(selname))      
        self.marking_dc.append(DCO_add_column('_mark=!1'))      
        self.marking_dc.append(DCO_cache('_n'))      
        self.marking_dc.append(DCO_retrieve('_w'))      
        self.marking_dc.append(DCO_join(':_n@outer'))      
        self.marking_dc.muted=False
        write( ('update marking DC now is: ', self.marking_dc), 1, how='red,reverse')
        self.update_marking() #options_key)
        self.marking_dc.signal_value_changed.connect( self.update_marking )

    def update_marking(self):
      write( 'update marking!', 1, how='magenta,reverse')
      mdf=self.marking_dc.out()
      #write( 'update marking ->\n{}'.format(mdf), 1, how='magenta,reverse')
      if mdf is None: return 
      if not self.df_index2spot: 
        print 'skip marking, no self.df_index2spot'
        return  #skipping marking since an error occurred while plotting
      s=self.plot_item.plot_object.active_space_size
      line_glcolor=rgbcolor2glcolor(self.plot_item.options['mark_color'],  self.plot_item.options['mark_alpha']);   
      line_width=self.plot_item.options['mark_width']
      for i, row_i in enumerate(mdf.index):
        spot=self.df_index2spot[row_i]
        try:        
          mark_this=not pd.isnull(mdf.at[row_i, '_mark'])
        except ValueError:
          print mdf.at[row_i, '_mark']
          print row_i, mdf.loc[row_i,]
          raise
        if not row_i in self.df_index2line_items:
          _, _, _, _, _, _, _, _, _, _, _, _, x, y, z, _ = spot.transform().data()
          #print self.dc.out()[row_i]
          xline= gl.GLLinePlotItem(   pos=np.array([ [0, y, z], [s, y, z] ]), color=line_glcolor,   width=line_width )
          yline= gl.GLLinePlotItem(   pos=np.array([ [x, 0, z], [x, s, z] ]), color=line_glcolor,   width=line_width )
          zline= gl.GLLinePlotItem(   pos=np.array([ [x, y, 0], [x, y, s] ]), color=line_glcolor,   width=line_width)
          self.plot_item.plot_object.addItem(xline)
          self.plot_item.plot_object.addItem(yline)
          self.plot_item.plot_object.addItem(zline)
          self.df_index2line_items[row_i]=[xline, yline, zline]
        else: 
          xline, yline, zline=self.df_index2line_items[row_i]

        xline.setVisible( mark_this )
        yline.setVisible( mark_this )
        zline.setVisible( mark_this )


  class LeafLabels(object):
    """ text labels in 3d """
    dc_template_key='lockinsert:None{sep}retrieve:{name}{sep}color:f|A1A1A1{sep}nodeFilter:All leaves^{sep}lockappend:None'
    def __init__(self, plot_item, options_key): 
      self.plot_item=plot_item
      self.options_key=options_key
      self.labels=[] #list of pg.TextItem, which is QtGui.QGraphicsTextItem really
      piname=self.plot_item.options['name']
      self.dc=DataChannel(plot_item.plot_object.plot_window.dco_link, 
                          from_key=self.dc_template_key.format(sep=DataChannel.dco_separator_char, name=piname))
      self.dc.set_lock(1)     ##### unmodifiable
      self.dc.set_lock(3, state=2)  # unremovable
      #self.dc.set_lock(4)         # unmodifiable
      #fn_update=lambda options_key=options_key:self.update_plot(options_key)
      self.dc.signal_value_changed.connect(self.update_plot) #   fn_update)
      #self.dc.signal_dc_changed.connect(self.update_plot)    #fn_update)
      self.update_plot() #options_key)

    def update_plot(self): #, options_key):
      print 'update labels', self.options_key
      self.plot_item.plot_object.clear_text(self.plot_item)
      local_options=self.plot_item.options[self.options_key]
      df=self.dc.out()   
      s=self.plot_item.plot_object.active_space_size   # scaling factor; input is 0-1 and must fill the 3D space
      if df is None: return  self.plot_item.plot_object.update()
      if local_options['label_visible']: 
        try: 
          default_color=self.plot_item.plot_object.plot_window.master().colors().get_default_color()        
          for i, row_i in enumerate(df.index):
            is_visible=smart_get('label_visible', local_options, df, row_i)
            if not is_visible: continue
            node_name=df.at[row_i, 'Node']        if not df.index.name=='Node' else row_i
            label_field=local_options['label_field']
            text='{}'.format(df.at[row_i,label_field]   if not df.index.name==label_field else row_i ) 
            xcoord=float(df.iat[i,0])*s     #    df.at[row_i,xdf.columns[0]])  #better way?
            ycoord=float(df.iat[i,1])*s            #df.at[row_i,ydf.columns[0]])
            zcoord=float(df.iat[i,2])*s            #df.at[row_i,ydf.columns[0]])
            size=  smart_get('font_size', local_options, df, row_i)
            anchor=pg.Point( local_options['anchor'] )  #arg: (0.5, 1)
            color= smart_get('color', local_options, df, row_i, default=default_color)           

            r, g, b, _ =map(int, rgbcolor2glcolor(color, maxout=255.))
            qpen= QtGui.QPen(  QtGui.QColor(r, g, b)  )
            qfont=QtGui.QFont('Arial', size)
            coords=[xcoord, ycoord, zcoord]

            self.plot_item.plot_object.plot_window.master().po=self.plot_item.plot_object

            if any(pd.isnull(coords)): continue
            self.plot_item.plot_object.add_text(self.plot_item, text, coords, qfont, qpen, None)
            
        except Exception as e:
          QtGui.QMessageBox.warning(self.plot_item.plot_object.plot_window, 'Error', 'Error while plotting {} !\n{}'.format(self.options_key, e), QtGui.QMessageBox.Ok)

      #self.plot_item.plot_object.updateGL()
      self.plot_item.plot_object.update()
      #self.plot_item.plot_object.paintGL()

  class AncestralSpots(LeafSpots):
    dc_template_key='lockinsert:None{sep}retrieve:{name}{sep}nodeFilter:@All leaves^{sep}lockappend:None'

  class AncestralLabels(LeafLabels):
    dc_template_key='lockinsert:None{sep}retrieve:{name}{sep}color:f|A1A1A1{sep}nodeFilter:@All leaves^{sep}lockappend:None'

  class AncestralPaths(object):
    dc_template_key='lockinsert:None{sep}retrieve:{name}{sep}lockappend:None'
    def __init__(self, plot_item, options_key):
      self.plot_item=plot_item
      self.options_key=options_key
      self.lines=[] #list of GLLinePlotItem 
      piname=self.plot_item.options['name']
      self.dc=DataChannel(plot_item.plot_object.plot_window.dco_link, 
                          from_key=self.dc_template_key.format(sep=DataChannel.dco_separator_char, name=piname))
      self.dc.set_lock(1)     ##### unmodifiable
      #self.dc.set_lock(2, state=2)     ##### unremovable
      #fn_update=lambda options_key=options_key:self.update_plot(options_key)
      self.dc.signal_value_changed.connect(self.update_plot) #fn_update)
      #self.dc.signal_dc_changed.connect(self.update_plot)    # fn_update)
      self.dc.out() #-> #self.update_plot() #options_key)

    def update_plot(self): #, options_key):      
      write('update ancestralpaths 3d!', 1)
      local_options=self.plot_item.options[self.options_key]
      for line in self.lines: 
        self.plot_item.plot_object.removeItem(line)
      self.lines=[]       
      df=self.dc.out()   
      if df is None: return   
      if df.index.name!='Node': df=df.set_index('Node')
      s=self.plot_item.plot_object.active_space_size   # scaling factor; input is 0-1 and must fill the 3D space
      if local_options['line_visible']: 
        try: 
          #for i, row_i in enumerate(df.index):
          default_color=self.plot_item.plot_object.plot_window.master().colors().get_default_color()
          tree=self.plot_item.plot_object.plot_window.master().trees().get_tree(None)   ### NOTE! if anc_dc is modified to allow non default tree, this has to be modified
          #for df in ldf, adf:   #first let's start from leaf nodes, then ancestors
          first_column, second_column, third_column=df.columns[:3]
          for i, row_i in enumerate(df.index):
            is_visible=smart_get('line_visible', local_options, df, row_i)
            if not is_visible: continue
            node_name=df.at[row_i, 'Node']        if not df.index.name=='Node' else row_i
            x1coord=float(df.at[row_i,first_column])*s
            y1coord=float(df.at[row_i,second_column])*s
            z1coord=float(df.at[row_i,third_column])*s
            parent=tree.get_node(node_name).up
            if parent is None: continue
            if not parent.name in df.index:
              write('AncestorsPath cannot find this parent in DF: {} df=\n{} ; aborting all lines'.format(parent.name, df), 1, how='blue,reverse')
              self.lines=[]
              return 
            x2coord=float(df.at[parent.name,first_column])*s
            y2coord=float(df.at[parent.name,second_column])*s
            z2coord=float(df.at[parent.name,third_column])*s

            line_width=smart_get('line_width', local_options, df, row_i)
            color=smart_get('color', local_options, df, row_i, default=default_color)
            alpha=smart_get('line_alpha', local_options, df, row_i)
            line_glcolor=rgbcolor2glcolor(color, alpha);   
            #print 'line', line_glcolor, color, alpha, [x1coord, y1coord, z1coord], [x2coord, y2coord, z2coord] 
            line_item=gl.GLLinePlotItem(   pos=np.array([ [x1coord, y1coord, z1coord], [x2coord, y2coord, z2coord] ]), 
                                      color=line_glcolor,   width=line_width )

            self.lines.append(line_item)
        except Exception as e: 
          QtGui.QMessageBox.warning(self.plot_item.plot_object.plot_window, 'Error', 'Error while plotting {} !\n{}'.format(self.options_key, e), QtGui.QMessageBox.Ok)

      for line_item in self.lines: self.plot_item.plot_object.addItem(line_item)
      


 ################################################################################

class Plot3DObject(gl.GLViewWidget, PlotObject):
  n_rock_frames  = 100
  rock_movements=  np.sin( np.arange(0, 2*np.pi, 2*np.pi/n_rock_frames) )  # precomputing rock orbit deltas
  active_space_size=20.0

  default_options={ 'frame_duration':30, 'gridXY_ticks':20,}
  def __init__(self, plot_window): #x_label='', y_label='', z_label='', options={}):
    gl.GLViewWidget.__init__(self)
    PlotObject.__init__(self)       ## --> sets self.options

    #gx.setSpacing(1, 1, 1)
    s=self.active_space_size
    hs=s/2
    gyz = gl.GLGridItem();  gyz.setSize(s, s, 1.0);  gyz.rotate(90, 0, 1, 0);   gyz.translate(0, hs, hs); 
    gzx = gl.GLGridItem();  gzx.setSize(s, s, 1.0);  gzx.rotate(90, 1, 0, 0);   gzx.translate(hs, 0, hs)
    gxy = gl.GLGridItem();  gxy.setSize(s, s, 1.0);                             gxy.translate(hs, hs, 0)
    gxy.setObjectName('gridXY');   gyz.setObjectName('gridYZ');   gzx.setObjectName('gridZX'); 
    self.addItem(gxy);       self.addItem(gyz);    self.addItem(gzx)
    self.gridXY=gxy;  self.gridYZ=gyz;  self.gridZX=gzx;  
    self.plot_window=plot_window
    self.meshes={}
    self.make_node_meshes()

    #self.axis_labels=
    self.rocking=False
    self.rocking_timer=QtCore.QTimer()
    self.rock_position=0
    self.rocking_timer.timeout.connect(self.rock_move_next)
    self.click_and_moved=None
    self.opts['distance'] = 40
    self.setAutoFillBackground(False)

    self.text_labels={}


  def make_node_meshes(self):
    """ Initialize and store the meshdata to draw nodes (in self.meshes); it also perform a trick to prevent a bug when clicking to select: it adds an invisible instance per mesh type (puppet_balls)"""
    sphere_shape =    gl.MeshData.sphere(rows=10, cols=10)                                   # Sphere
    cone_shape= gl.MeshData.cylinder(rows=10, cols=10, radius=[1.0, 0.1], length=2.0)  # Cone 
    vs=cone_shape.vertexes()
    subt=np.array( [ [0, 0, 1.0] for _ in range(len(vs))] )
    cone_shape.setVertexes( vs-subt )  #centering 
    cylinder_shape=      gl.MeshData.cylinder(rows=10, cols=10, radius=[1.0, 1.0], length=1.5)  # Cylinder
    vs=cylinder_shape.vertexes()
    subt=np.array( [ [0, 0, 0.75] for _ in range(len(vs))] )
    cylinder_shape.setVertexes( vs-subt )       #centering 
    for name, shape in ('sphere', sphere_shape), ('cone', cone_shape), ('cylinder', cylinder_shape):
      first_ball = gl.GLMeshItem(meshdata=shape, smooth=True, color=rgbcolor2glcolor('FFFFFF', 0.0), shader='balloon', glOptions='additive')
      first_ball.df_index=None #setObjectName(':FirstPuppetBall:')
      self.addItem(first_ball)
      self.meshes[name]   =shape


  # def addItem(self, *args, **kargs):
  #   #print 'ADD ITEM DIO CANE', args, kargs
  #   gl.GLViewWidget.addItem(self, *args, **kargs)

  def world2screen(self, item):
    """ input item is one of the gl.items;   or a QtGui.QVector3D().   The function translates its coordinate to that of the view window"""
    view_transform=self.viewMatrix()
    projection_transform=self.projectionMatrix()
    minx,miny,width,height=self.getViewport()
    assert minx==0; assert miny==0    
    if isinstance(item, QtGui.QVector3D):
      p=projection_transform * view_transform * item
    else:
      model_transform=item.transform()
      model_coord=QtGui.QVector3D(0.0, 0.0, 0.0)    
      p=projection_transform * view_transform * model_transform * model_coord    # (some QVector3D with (x, y, ?) with x and y between -1 and 1; -1 is the left/top corner, +1 is the right/bottom one

    xout= rescale(p.x(), minx, width, -1., 1.)
    yout= rescale(p.y(), miny, height, 1., -1.)
    return [xout, yout]


  def add_text(self, plot_item, text, coords, qfont, qpen, ali):
    if not plot_item in self.text_labels: self.text_labels[plot_item]=[]
    self.text_labels[plot_item].append(  [text, coords, qfont, qpen, ali]  )

  def clear_text(self, plot_item): 
    if plot_item in self.text_labels: del self.text_labels[plot_item]  

  def paintEvent(self, *args, **kwds):
    #print 'paintEvent'
    gl.GLViewWidget.paintEvent(self, *args, **kwds)
    if True: #not self.click_and_moved:
      painter=QtGui.QPainter()
      painter.begin(self)
      last_pen=None
      last_font=None
      for plot_item in self.text_labels:
        for text, coords, qfont, qpen, ali in self.text_labels[plot_item]:
          #text, coords, qfont, pen, ali= self.text_labels[plot_item]
          if   len(coords)==2: x,y=coords
          elif len(coords)==3: x,y=map(int, self.world2screen( QtGui.QVector3D(*coords)  ))
          if qpen!=last_pen:       painter.setPen(qpen)
          if qfont!=last_font:     painter.setFont(qfont)
          
          x+=8
          y+=8

          painter.drawText(x, y, text)
          last_pen=qpen
          last_font=qfont
      painter.end()


  def paintGL(self, *args, **kwds):
    """ Decorating this function to add axis labels"""
    gl.GLViewWidget.paintGL(self, *args, **kwds)
    self.qglColor( QtCore.Qt.white ) # rgbcolor2glcolor('#FFFFFF') )
    qfont=QtGui.QFont('Arial', 10)
    #self.renderText(10, 40, '')                

    s=self.active_space_size
    if self.plot_window.axis_labels:
      xlab, ylab, zlab=self.plot_window.axis_labels
      if xlab:     self.renderText(s, 0, 0, xlab, qfont)        
      if ylab:     self.renderText(0, s, 0, ylab, qfont)
      if zlab:     self.renderText(0, 0, s, zlab, qfont)

    ## self.renderText(20, 20, 'test') ## for totally nonsense reasons this fucks up with itemsAt method, thus every click select some ball


  def mousePressEvent(self, e):
    if self.rocking: self.stop_rocking()
    self.click_and_moved=False
    gl.GLViewWidget.mousePressEvent(self, e)

  def mouseReleaseEvent(self, e):
    print 'catch mouse 3d'
    if e.button() == QtCore.Qt.RightButton:        

      pos= e.pos()
      self.show_action_popup()

    elif e.button() == QtCore.Qt.LeftButton:        
      if not self.click_and_moved:
        #if not self.isActiveWindow(): 
        self.activateWindow()

        pos= e.pos()
        items_here=self.itemsAt( region=(pos.x(), pos.y(), 1, 1) )

        if items_here:
          ball_items=[ item   for item in items_here        if isinstance(item, gl.items.GLMeshItem.GLMeshItem) and not item.df_index is None]
          if ball_items:                   
            plotitem2ball_items={}  #let's categorize the clicked objects by their (parent) plot_item
            for b in ball_items: 
              if not b.plot_item in plotitem2ball_items: plotitem2ball_items[b.plot_item]=[]
              plotitem2ball_items[b.plot_item].append(b)

            tree_manager=self.plot_window.master().trees()
            write('highlight or select nodes from 3d click! ', 1)
            ns_to_select=   None  #will contain the list of nodes for which we have to do some 'select' action
            ns_to_highlight=None 
            for plot_item in plotitem2ball_items:
              df=plot_item.dc.out()
              click_effect=plotitem2ball_items[plot_item][0].plot_item.options['on_click']
              if   click_effect=='n': continue
              clicked_nodes=NodeSelector([tree_manager.get_node(    df.at[ s.df_index, 'Node']       )   for s in plotitem2ball_items[plot_item]])
              if click_effect=='s': 
                if ns_to_select is None: ns_to_select=NodeSelector()
                ns_to_select.update(clicked_nodes)
              elif click_effect=='h': 
                if ns_to_highlight is None: ns_to_highlight=NodeSelector()
                ns_to_highlight.update(clicked_nodes)

            action_list=[]
            if not ns_to_select is None:     action_list.append(['Selected nodes',    ns_to_select])
            if not ns_to_highlight is None:  action_list.append(['Highlighted nodes', ns_to_highlight])
            for selname, target_ns in action_list:
              ns=self.plot_window.master().selections().get_node_selection( selname ).copy()
              if   QtGui.QApplication.keyboardModifiers() == QtCore.Qt.ShiftModifier:        ns.update(target_ns)
              elif QtGui.QApplication.keyboardModifiers() == QtCore.Qt.ControlModifier:
                for node in target_ns:
                  if not node in ns:       ns.add(node)                      
                  else:                    ns.remove(node)                      
              else: ## normal behavior: select just these nodes
                ns=target_ns
              self.plot_window.master().selections().edit_node_selection(selname, ns)            
            
    self.click_and_moved=False
    gl.GLViewWidget.mouseReleaseEvent(self, e)

  def mouseMoveEvent(self, e):
    """ """
    if e.buttons() == QtCore.Qt.LeftButton or e.buttons() == QtCore.Qt.MidButton:
      self.click_and_moved=True
    gl.GLViewWidget.mouseMoveEvent(self, e)

  def show_action_popup(self):
    """ Show the right click menu of the 3D plot"""
    menu=QtGui.QMenu()
    menu.addAction('Export...', self.export_dialog  )
    if not self.rocking:     menu.addAction('Start rocking', self.start_rocking  )    
    else:                    menu.addAction('Stop rocking',  self.stop_rocking  )    
    menu.exec_(QtGui.QCursor.pos())

  def export_dialog(self): 
    """ TO BE IMPLEMENTED """
    write('export dialog clicked!', 1, how='yellow')
    #    self.save_to_file('a.png')    

  def start_rocking(self):
    self.rocking=True
    self.rocking_timer.start( self.options['frame_duration'] )

  def stop_rocking(self):
    self.rocking_timer.stop()
    self.rock_position=0
    self.rocking=False

  def rock_move_next(self): 
    self.rock_position+=1
    if self.rock_position>= self.n_rock_frames: self.rock_position=0
    ## ellipsoid motion; change in elevation is half the change in x  ## not: only change in horizontal
    deltax= self.rock_movements[self.rock_position]
    deltay= 0 #self.rock_movements[ (self.rock_position + self.n_rock_frames/4) % self.n_rock_frames     ] / 2.0
    self.orbit( deltax, deltay )

  def save_to_file(self, fileout, quality=-1):
    qi=self.readQImage()
    qi.save(fileout, None, quality) # quality -1 is for default settings;  None is for automatic format detection


################################################################################
class Plot3DWindow(pg.GraphicsView, PlotWindow):
  available_plot_items=[NodePlot3DItem] ### add one
  dimensions=3
  def window_identifier(self): return {'window_name':self.plot_title } #return {'category':'ScatterPlot'}
  def __init__(self, master_link, plot_title=''): 
    self.plot_title=plot_title
    PlotWindow.__init__(self, master_link) #    self.plot_items=[];     self.active_menu=[]     ## plot_item, category, menu, button
    pg.GraphicsView.__init__(self)
    self.setWindowTitle(plot_title)
    self.main_layout= QtGui.QVBoxLayout(); self.main_layout.setContentsMargins(0, 0, 0, 0);     self.main_layout.setSpacing(0)
    self.setLayout(self.main_layout) 
    self.toolbar_layout= QtGui.QVBoxLayout()  
    self.main_layout.addLayout(self.toolbar_layout)
    ### active interactivity menu
    self.menu_layout= QtGui.QVBoxLayout()        ## necessary!
    self.main_layout.addLayout(self.menu_layout) 

    self.plot_layout= QtGui.QVBoxLayout()    #useless really; but just to keep the same structure as scatterplot
    self.plot_layout.setContentsMargins(0, 0, 0, 0);     self.plot_layout.setSpacing(0)

    #self.axes=[]  #first element: QLabel for X;      second element: for Y
    #self.axes.append(self.plot_layout.addLabel('--', col=0, row=1, angle=-90)) #later text is set
    self.plot_object= Plot3DObject(plot_window=self)
    self.plot_layout.addWidget(self.plot_object)
    self.main_layout.addLayout(self.plot_layout)

  #def get_n_dimensions(self): return 2

  def set_axis_label(self, index_dimension, label):    pass 
    #nothing to do here; see Plot3DObject paintGL()
    #self.plot_object
    #print 'trying to set axis labels', index_dimension, label
