from .baseplots import *  

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
    symbol=as_options['symbol']
    self.as_symbol_combobox=QtGui.QComboBox()
    self.as_symbol_combobox.possible_values=[('o','circle'), ('s','square'), ('t','triangle'), ('d','diamond'),('+','plus')]
    for _,desc in self.as_symbol_combobox.possible_values: self.as_symbol_combobox.addItem(desc)
    self.as_symbol_combobox.setCurrentIndex(  [s for s,_ in self.as_symbol_combobox.possible_values].index(symbol)   )
    self.as_symbol_combobox.currentIndexChanged[int].connect(self.activated_ancestral_spots_symbol_combobox)
    row2_layout.addWidget(self.as_symbol_combobox)
    row2_layout.addWidget(VerticalLine('lightgrey'))

    size=as_options['size']
    row2_layout.addWidget(QtGui.QLabel('Size:'))
    self.as_size_slider= QtGui.QSlider(QtCore.Qt.Horizontal)
    self.as_size_slider.setMinimum(1);      self.as_size_slider.setMaximum(20);    self.as_size_slider.setValue(size)
    self.as_size_slider.setTickInterval(1)
    self.as_size_slider.valueChanged.connect( self.moved_ancestral_spots_size_slider )
    self.as_size_slider.resize(10,10)  #it's actually hitting below the minimum width limit, but that's fine
    self.as_size_slider.setSizePolicy(fixed_size_policy)
    row2_layout.addWidget(self.as_size_slider)
    self.as_size_textbox=QtGui.QLineEdit()
    self.as_size_textbox.setText(str(size))
    self.as_size_textbox.setMaximumWidth(25) 
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
    row2_layout.addWidget(QtGui.QLabel('Placed:'))
    horiz_label=QtGui.QLabel();    horiz_label.setPixmap( get_pixmap('horizontal')  )
    row2_layout.addWidget(horiz_label)#  QtGui.QLabel('horizontal'))
    hanchor, vanchor= al_options['anchor']
    self.al_anchor_h_combobox=QtGui.QComboBox()
    self.al_anchor_h_combobox.possible_values=[(1.0,'left'), (0.5,'center'),(0.0,'right')]
    for _,desc in self.al_anchor_h_combobox.possible_values: self.al_anchor_h_combobox.addItem(desc)
    self.al_anchor_h_combobox.setCurrentIndex(  [s for s,_ in self.al_anchor_h_combobox.possible_values].index(hanchor)   )
    self.al_anchor_h_combobox.currentIndexChanged[int].connect(self.activated_ancestral_labels_anchor_h_combobox)
    row2_layout.addWidget(self.al_anchor_h_combobox)
    row2_layout.addSpacing(5)
    vert_label=QtGui.QLabel();    vert_label.setPixmap( get_pixmap('vertical')  )
    row2_layout.addWidget(vert_label)#  QtGui.QLabel('horizontal'))
    self.al_anchor_v_combobox=QtGui.QComboBox()
    self.al_anchor_v_combobox.possible_values=[(1.0,'above'), (0.5,'center'),(0.0,'below')]
    for _,desc in self.al_anchor_v_combobox.possible_values: self.al_anchor_v_combobox.addItem(desc)
    self.al_anchor_v_combobox.setCurrentIndex(  [s for s,_ in self.al_anchor_v_combobox.possible_values].index(vanchor)   )
    self.al_anchor_v_combobox.currentIndexChanged[int].connect(self.activated_ancestral_labels_anchor_v_combobox)
    row2_layout.addWidget(self.al_anchor_v_combobox)
    row2_layout.addWidget(VerticalLine('lightgrey'))
    row2_layout.addStretch()  

    al_layout.addLayout(row1_layout)
    al_layout.addLayout(row2_layout)
    self.layout.addLayout(al_layout)
    self.layout.addWidget(HorizontalLine('grey'))

    ### AncestralPaths
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
  def activated_ancestral_spots_symbol_combobox(self, index):    #index=self.ls_symbol_combobox.currentIndex()
    self.plot_item.options['AncestralSpots']['symbol']=self.as_symbol_combobox.possible_values[index][0]
    self.plot_item.update_item()

  def moved_ancestral_spots_size_slider(self, value):
    self.plot_item.options['AncestralSpots']['size']=value
    self.as_size_textbox.setText(str(value))
    self.plot_item.update_item()
  def edited_ancestral_spots_size_textbox(self):
    text=str(self.as_size_textbox.text())
    try:     value=int(text.strip()); assert value>0 and value <=20
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
  def activated_ancestral_labels_anchor_h_combobox(self, index):
    self.plot_item.options['AncestralLabels']['anchor'][0]=self.al_anchor_h_combobox.possible_values[index][0]
    self.plot_item.update_item()
  def activated_ancestral_labels_anchor_v_combobox(self, index):
    self.plot_item.options['AncestralLabels']['anchor'][1]=self.al_anchor_v_combobox.possible_values[index][0]
    self.plot_item.update_item()

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

####################################################################################
class ToolbarViewMenu(ToolbarMenu):
  """ """
  def __init__(self, plot_item):
    super(ToolbarViewMenu, self).__init__(plot_item=plot_item)
    self.layout=QtGui.QVBoxLayout()
    self.setLayout(self.layout)

    ########     leafSpots section   #######
    # [v] Points for leaf nodes       Node filter:[NSW]      Color: [cm]
    #      Symbol: [cb]/or dc/     Size: |___|[n]/or dc/    Alpha: |___|[n]/or dc/
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
    symbol=ls_options['symbol']
    self.ls_symbol_combobox=QtGui.QComboBox()
    self.ls_symbol_combobox.possible_values=[('o','circle'), ('s','square'), ('t','triangle'), ('d','diamond'),('+','plus')]
    for _,desc in self.ls_symbol_combobox.possible_values: self.ls_symbol_combobox.addItem(desc)
    self.ls_symbol_combobox.setCurrentIndex(  [s for s,_ in self.ls_symbol_combobox.possible_values].index(symbol)   )
    self.ls_symbol_combobox.currentIndexChanged[int].connect(self.activated_leaf_spots_symbol_combobox)
    row2_layout.addWidget(self.ls_symbol_combobox)
    row2_layout.addWidget(VerticalLine('lightgrey'))

    size=ls_options['size']
    row2_layout.addWidget(QtGui.QLabel('Size:'))
    self.ls_size_slider= QtGui.QSlider(QtCore.Qt.Horizontal)
    self.ls_size_slider.setMinimum(1);      self.ls_size_slider.setMaximum(20);    self.ls_size_slider.setValue(size)
    self.ls_size_slider.setTickInterval(1)
    self.ls_size_slider.valueChanged.connect( self.moved_leaf_spots_size_slider )
    self.ls_size_slider.resize(10,10)  #it's actually hitting below the minimum width limit, but that's fine
    self.ls_size_slider.setSizePolicy(fixed_size_policy)
    row2_layout.addWidget(self.ls_size_slider)
    self.ls_size_textbox=QtGui.QLineEdit()
    self.ls_size_textbox.setText(str(size))
    self.ls_size_textbox.setMaximumWidth(25) 
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
    row2_layout.addWidget(QtGui.QLabel('Placed:'))
    horiz_label=QtGui.QLabel();    horiz_label.setPixmap( get_pixmap('horizontal')  )
    row2_layout.addWidget(horiz_label)#  QtGui.QLabel('horizontal'))
    hanchor, vanchor= ll_options['anchor']
    self.ll_anchor_h_combobox=QtGui.QComboBox()
    self.ll_anchor_h_combobox.possible_values=[(1.0,'left'), (0.5,'center'),(0.0,'right')]
    for _,desc in self.ll_anchor_h_combobox.possible_values: self.ll_anchor_h_combobox.addItem(desc)
    self.ll_anchor_h_combobox.setCurrentIndex(  [s for s,_ in self.ll_anchor_h_combobox.possible_values].index(hanchor)   )
    self.ll_anchor_h_combobox.currentIndexChanged[int].connect(self.activated_leaf_labels_anchor_h_combobox)
    row2_layout.addWidget(self.ll_anchor_h_combobox)
    row2_layout.addSpacing(5)
    vert_label=QtGui.QLabel();    vert_label.setPixmap( get_pixmap('vertical')  )
    row2_layout.addWidget(vert_label)#  QtGui.QLabel('horizontal'))
    self.ll_anchor_v_combobox=QtGui.QComboBox()
    self.ll_anchor_v_combobox.possible_values=[(1.0,'above'), (0.5,'center'),(0.0,'below')]
    for _,desc in self.ll_anchor_v_combobox.possible_values: self.ll_anchor_v_combobox.addItem(desc)
    self.ll_anchor_v_combobox.setCurrentIndex(  [s for s,_ in self.ll_anchor_v_combobox.possible_values].index(vanchor)   )
    self.ll_anchor_v_combobox.currentIndexChanged[int].connect(self.activated_leaf_labels_anchor_v_combobox)
    row2_layout.addWidget(self.ll_anchor_v_combobox)
    row2_layout.addWidget(VerticalLine('lightgrey'))

    row2_layout.addStretch()  

    ll_layout.addLayout(row1_layout)
    ll_layout.addLayout(row2_layout)
    self.layout.addLayout(ll_layout)


  #############
  ## active feedback
  def clicked_leaf_spots_visible_checkbox(self, boxstate):
    self.plot_item.options['LeafSpots']['point_visible']=boxstate
    self.plot_item.update_item()
  def activated_leaf_spots_symbol_combobox(self, index):    #index=self.ls_symbol_combobox.currentIndex()
    self.plot_item.options['LeafSpots']['symbol']=self.ls_symbol_combobox.possible_values[index][0]
    self.plot_item.update_item()

  def moved_leaf_spots_size_slider(self, value):
    self.plot_item.options['LeafSpots']['size']=value
    self.ls_size_textbox.setText(str(value))
    self.plot_item.update_item()
  def edited_leaf_spots_size_textbox(self):
    text=str(self.ls_size_textbox.text())
    try:     value=int(text.strip()); assert value>0 and value <=20
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
  def activated_leaf_labels_anchor_h_combobox(self, index):
    self.plot_item.options['LeafLabels']['anchor'][0]=self.ll_anchor_h_combobox.possible_values[index][0]
    self.plot_item.update_item()
  def activated_leaf_labels_anchor_v_combobox(self, index):
    self.plot_item.options['LeafLabels']['anchor'][1]=self.ll_anchor_v_combobox.possible_values[index][0]
    self.plot_item.update_item()

########
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
    row2.addWidget(QtGui.QLabel(' are marked with outline of color '))
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
    self.plot_item.leaf_spots.update_marking_dc() #'LeafSpots')

  def picked_mark_color(self):
    self.plot_item.options['mark_color']=self.mark_color_button.get_color()
    self.plot_item.leaf_spots.update_marking() #'LeafSpots')

  


########
class NodeScatterPlotToolbar(PlotItemToolbar):
  """ """
  #plotitem_menu is default of PlotItemToolbar
  data_menu=ToolbarDataMenu
  view_menu=ToolbarViewMenu
  ancestors_menu=ToolbarAncestorsMenu
  interactivity_menu=ToolbarInteractivityMenu

class PlotLine(pg.QtGui.QGraphicsLineItem):
  """ """
  #def __init__(self, x1, y1, x2, y2):
  #def setPen(self, pen):
####################################################################################
class NodeScatterPlotItem(PlotItem):
  plot_type='Scatter'
  defaults={ 'name':None, 
             'mark_color':'000000', 'mark_what':'s',  'on_click':'s',             
             'LeafSpots': {'point_visible':True,  'size':6,      'symbol':'o',        'alpha':0.5,          },
             'LeafLabels':{'label_visible':False, 'font_size':7, 'anchor':[0.5, 1.0], 'label_field':'Node', }, 
             'AncestralSpots': { 'point_visible':False, 'size':6,         'symbol':'t',        'alpha':0.3, }, 
             'AncestralLabels': {'label_visible':False, 'font_size':7,    'anchor':[0.5, 1.0], 'label_field':'Node', },
             'AncestralPaths': { 'line_visible': False, 'line_width':1.0, 'line_alpha':0.3,                          },
} 
  #'fixed_size':True, ## pg bug when pxMode != True
  toolbar_class=NodeScatterPlotToolbar

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
    if dc.chain[-2].key()!='cache:'+cache_name: dc.insert(len(dc.chain)-1,   DCO_cache(cache_name))
    dc.set_lock(len(dc.chain)-2)
    if dc.chain[-3].name!='color:':             dc.insert(len(dc.chain)-2,   DCO_color('m|TreeColor'))  #initializing with parameters None
    dc.set_lock(len(dc.chain)-3, 2)
    if dc.chain[-4].name!='trace:':             dc.insert(len(dc.chain)-3,   DCO_trace())  #initializing with parameters None
    dc.muted=False
    dc.notify_modification()

    store_headers_fn=lambda:self.store_headers(2)
    dc.signal_value_changed.connect(store_headers_fn)
    dc.signal_value_changed.connect(self.plot_object.plot_window.update_axis)
    #dc.signal_dc_changed.connect(   store_headers_fn)
    #dc.signal_dc_changed.connect(   self.plot_object.plot_window.update_axis)


  def init_item(self):
    print 'init scatterplot, ', self.options['name'], id(self.options)
    self.leaf_spots=     self.LeafSpots( self, 'LeafSpots', marking=True) 
    self.leaf_labels=    self.LeafLabels(self, 'LeafLabels') 
    self.store_headers(2)

    self.ancestral_spots= self.AncestralSpots(self,  'AncestralSpots')   
    self.ancestral_labels=self.AncestralLabels(self, 'AncestralLabels') 
    self.ancestral_paths= self.AncestralPaths(self,  'AncestralPaths') 
    ### add other components

  def update_item(self):
    delta=self.delta_options()
    print 'updating scatterplot? n={n} delta={d}'.format(n=self.options['name'], d=delta)
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
      self.leaf_labels.update_plot()   #'LeafLabels')
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
      self.store_plot_options()
 
  def delete_item(self):
    ### add remove DC! # also link close window to run this
    self.dc.delete()
    self.leaf_labels.dc.delete()    
    self.leaf_labels.update_plot() #     'LeafLabels')
    self.leaf_spots.dc.delete()
    self.leaf_spots.marking_dc.delete()    
    self.leaf_spots.update_plot() #       'LeafSpots')
    self.ancestral_labels.dc.delete()
    self.ancestral_labels.update_plot() #'AncestralLabels')
    self.ancestral_spots.dc.delete()
    self.ancestral_spots.update_plot() # 'AncestralSpots') 
    self.ancestral_paths.dc.delete()
    self.ancestral_paths.update_plot() # 'AncestralPaths')
    print 'delete item!'
         
  ########################  
  ### PlotItem Components
  class LeafSpots(pg.ScatterPlotItem):
    """Dots, each one linked to a leaf node in the tree"""
    dc_template_key='lockinsert:None{sep}retrieve:{name}{sep}nodeFilter:All leaves^'
    def __init__(self, plot_item, options_key, marking=False):      
      self.plot_item=plot_item
      self.options_key=options_key
      self.marking=marking
      pg.ScatterPlotItem.__init__(self, pxMode=True) #local_options['fixed_size'])
      piname=self.plot_item.options['name']
      self.dc=DataChannel(plot_item.plot_object.plot_window.dco_link, 
                          from_key=self.dc_template_key.format(sep=DataChannel.dco_separator_char, name=piname))
      self.dc.set_lock(1)     ##### unmodifiable
      self.dc.set_lock(2, state=2)  # unremovable
      #fn_update=lambda options_key=options_key:self.update_plot(options_key)
      self.dc.signal_value_changed.connect(self.update_plot) #fn_update)
      #self.dc.signal_dc_changed.connect(self.update_plot)    # fn_update)
      self.update_plot() #options_key)
      self.plot_item.plot_object.addItem(self)
      self.sigClicked.connect(self.spots_were_clicked)
      if marking: 
        self.dc.signal_dc_changed.connect(self.update_marking_dc) #(options_key)) #lambda :
        self.update_marking_dc(first_run=True) #options_key, 
      
    def update_plot(self): #, options_key): 
      print 'update plot item '+self.options_key
      local_options=self.plot_item.options[self.options_key]
      #self.setPxMode( local_options['fixed_size'] )  #buggy
      self.df_index2spot={}
      spot_data=[]
      df=self.dc.out()
      if df is None: pass
      else:
        if local_options['point_visible']: 
          try: 
            default_color=self.plot_item.plot_object.plot_window.master().colors().get_default_color()
            for i, row_i in enumerate(df.index):
              is_visible=smart_get('point_visible', local_options, df, row_i)
              if not is_visible: continue
              node_name=df.at[row_i, 'Node']        if not df.index.name=='Node' else row_i
              xcoord=float(df.iat[i,0])     #    df.at[row_i,xdf.columns[0]])  
              ycoord=float(df.iat[i,1])            #df.at[row_i,ydf.columns[0]])
              symbol=smart_get('symbol', local_options, df, row_i )
              size=  smart_get('size', local_options, df, row_i )
              alpha= smart_get('alpha', local_options, df, row_i ) 
              alphahex=int(rescale( alpha, ymin=0, ymax=255, xmin=0.0, xmax=1.0 )) #from 0 to 255
              alphahex_pen=int(min([alphahex*1.1, 255])) #alpha for pen is a little more than for body
              alphastring=format(alphahex, 'x'); alphastring_pen=format(alphahex_pen, 'x')
              color= '#'+smart_get('color', local_options, df, row_i, default=default_color)
              #colormap[node_name]             #temp
              brush=color+alphastring; pen=color+alphastring_pen;   
              spot_data.append({'pos': [xcoord,ycoord], 'data': row_i, 'symbol':symbol, 'size':size, 'pen':pen, 'brush':brush})            
          except Exception as e:
            QtGui.QMessageBox.warning(self.plot_item.plot_object.plot_window, 'Error', 'Error while plotting {} !\n{}'.format(self.options_key, e), QtGui.QMessageBox.Ok)
            spot_data=[]
      self.setPoints(spot_data)  
      for spot in self.points():   self.df_index2spot[ spot.data() ] = spot    # so that later you can do get the spot for any given row_i  -- which here is spot.data()

    def spots_were_clicked(self,  plot, spots): 
      click_effect=self.plot_item.options['on_click']
      if   click_effect=='n': return 
      elif click_effect=='s': selname= 'Selected nodes'
      elif click_effect=='h': selname= 'Highlighted nodes'

      df=self.dc.out()
      tree_manager= self.plot_item.plot_object.plot_window.master().trees()
      clicked_nodes=NodeSelector([tree_manager.get_node(    df.at[ s.data(), 'Node']       )   for s in spots])
      clicked_nodes=clicked_nodes.walk_tree(down=True, only_leaves=True)
      ns=self.plot_item.plot_object.plot_window.master().selections().get_node_selection( selname ).copy()
      if   QtGui.QApplication.keyboardModifiers() == QtCore.Qt.ShiftModifier:        ns.update(clicked_nodes)
      elif QtGui.QApplication.keyboardModifiers() == QtCore.Qt.ControlModifier:
        for node in clicked_nodes:
          if not node in ns:       ns.add(node)                      
          else:                    ns.remove(node)                      
      else: ## normal behavior: select just this node
        ns=clicked_nodes
      self.plot_item.plot_object.plot_window.master().selections().edit_node_selection( selname, ns)            

    def update_marking_dc(self, first_run=False):
      ## keeping a single marking_dc; options_key is actually always the same, LeafSpots
      write( '.update marking dc', 1, how='green,reverse')

      if not first_run: 
        self.marking_dc.delete()        
      selname= {'n':None, 's':'Selected nodes', 'h':'Highlighted nodes'} [self.plot_item.options['mark_what']]
      if selname is None:    
        self.marking_dc=self.dc.copy(auto_update=False)
        self.marking_dc.muted=True
        self.marking_dc.append(DCO_add_column('_mark=!0')) 
        self.marking_dc.muted=False     
        self.update_marking() #options_key)               #restoring everything as non marked
      else:
        self.marking_dc=self.dc.copy(auto_update=False)     ##the out of this DC will be with a '_mark' column that is True if this spot needs to be marked, NaN otherwise
        self.marking_dc.muted=True
        #self.marking_dc.append(DCO_nodeFilter(selname))      
        self.marking_dc.append(DCO_select('Node,color'))   
        self.marking_dc.append(DCO_nodeFilter('All leaves'))         
        self.marking_dc.append(DCO_add_column('in_input=!1'))         
        self.marking_dc.append(DCO_cache('_w'))      
        self.marking_dc.append(DCO_antenna(selname))      
        self.marking_dc.append(DCO_add_column('_mark=!1'))      
        self.marking_dc.append(DCO_cache('_n'))      
        self.marking_dc.append(DCO_retrieve('_w'))      
        self.marking_dc.append(DCO_join(':_n@outer'))      
        self.marking_dc.append(DCO_filter('in_input==True'))
        self.marking_dc.muted=False
        write( ('        marking dc ', self.marking_dc) , 1, how='green,reverse')

        self.update_marking() #options_key)
        self.marking_dc.signal_value_changed.connect( self.update_marking )

    def update_marking(self): #, options_key): 
      mdf=self.marking_dc.out()
      write( 'update marking!', 1, how='green,reverse')
      print mdf
      default_color=self.plot_item.plot_object.plot_window.master().colors().get_default_color()
      local_options=self.plot_item.options[self.options_key]
      mark_pen_color=self.plot_item.options['mark_color']

      pens=[]
      if not self.df_index2spot or mdf is None: return  #skipping marking since an error occurred while plotting
      for i, row_i in enumerate(mdf.index):
        spot=self.df_index2spot[row_i]
        #this_row=mdf.iloc[i]
        try:          mark_this=not pd.isnull(mdf.at[row_i,'_mark'])
        except ValueError:
          write('update marking ERROR! mdf={}\n row_i={} mark_this={}\n '.format(mdf, row_i, mdf.at[row_i, '_mark'] ), 1, how='red,reverse')
          raise

        alphahex_pen=spot.pen().color().alpha()
        ## alternative: get from data (would need to removed select:Node,color in marking_dc
        # alpha= smart_get('alpha', local_options, mdf, row_i ) 
        # alphahex=int(rescale( alpha, ymin=0, ymax=255, xmin=0.0, xmax=1.0 )) #from 0 to 255
        # alphahex_pen=int(min([alphahex*1.1, 255])) #alpha for pen is a little more than for body
        alphastring_pen=format(alphahex_pen, 'x')

        if mark_this:                 
          pen=  '#'+ mark_pen_color+ alphastring_pen
          width=2.0
        else:         
          color= '#'+smart_get('color', local_options, mdf, row_i, default=default_color)
          pen=color+alphastring_pen;   
          width=1.0
        pens.append(  pg.mkPen(pen,   width=width)    )
        #spot.setPen(  pen, width=width  )
      self.setPen(pens)      


  class LeafLabels(object):
    """ labels in pyqtgraph scatterplot"""
    dc_template_key='lockinsert:None{sep}retrieve:{name}{sep}nodeFilter:All leaves^'
    def __init__(self, plot_item, options_key): 
      self.plot_item=plot_item
      self.options_key=options_key
      self.labels=[] #list of pg.TextItem, which is QtGui.QGraphicsTextItem really
      piname=self.plot_item.options['name']
      self.dc=DataChannel(plot_item.plot_object.plot_window.dco_link, 
                          from_key=self.dc_template_key.format(sep=DataChannel.dco_separator_char, name=piname))
      self.dc.set_lock(1)     ##### unmodifiable
      self.dc.set_lock(2, state=2)  # unremovable
      #fn_update=lambda options_key=options_key:self.update_plot(options_key)
      self.dc.signal_value_changed.connect(self.update_plot) #   fn_update)
      #self.dc.signal_dc_changed.connect(self.update_plot)    #fn_update)
      self.dc.out() #self.update_plot() #options_key)

    def update_plot(self): #, options_key):
      for label in self.labels: self.plot_item.plot_object.removeItem(label)
      self.labels=[]    
      local_options=self.plot_item.options[self.options_key]
      df=self.dc.out()   
      if df is None: return       
      if local_options['label_visible']: 
        try: 
          default_color=self.plot_item.plot_object.plot_window.master().colors().get_default_color()        
          for i, row_i in enumerate(df.index):
            is_visible=smart_get('label_visible', local_options, df, row_i)
            if not is_visible: continue
            node_name=df.at[row_i, 'Node']        if not df.index.name=='Node' else row_i
            label_field=local_options['label_field']
            text='{}'.format(df.at[row_i,label_field]   if not df.index.name==label_field else row_i ) 
            xcoord=float(df.iat[i,0])     #    df.at[row_i,xdf.columns[0]])  #better way?
            ycoord=float(df.iat[i,1])            #df.at[row_i,ydf.columns[0]])
            size=  smart_get('font_size', local_options, df, row_i)
            anchor=pg.Point( local_options['anchor'] )  #arg: (0.5, 1)

            label_item=pg.TextItem()
            qfont=label_item.textItem.font()
            qfont.setPointSize(size)
            label_item.setPlainText(text)
            label_item.textItem.setFont(qfont)
            label_item.anchor=anchor
            label_item.setPos(xcoord, ycoord)     
            label_item.updateTextPos()
            self.plot_item.plot_object.addItem(label_item)
            self.labels.append(label_item)
            color= '#'+smart_get('color', local_options, df, row_i, default=default_color)
            qcolor = pg.functions.mkColor(color)
            label_item.textItem.setDefaultTextColor(qcolor)
        except Exception as e:
          QtGui.QMessageBox.warning(self.plot_item.plot_object.plot_window, 'Error', 'Error while plotting {} !\n{}'.format(self.options_key, e), QtGui.QMessageBox.Ok)

  class AncestralSpots(LeafSpots):
    dc_template_key='lockinsert:None{sep}retrieve:{name}{sep}nodeFilter:@All leaves^'

  class AncestralLabels(LeafLabels):
    dc_template_key='lockinsert:None{sep}retrieve:{name}{sep}nodeFilter:@All leaves^'

  class AncestralPaths(object):
    dc_template_key='lockinsert:None{sep}retrieve:{name}'
    def __init__(self, plot_item, options_key):
      self.plot_item=plot_item
      self.options_key=options_key
      self.lines=[] #list of pg.TextItem, which is QtGui.QGraphicsTextItem really
      piname=self.plot_item.options['name']
      self.dc=DataChannel(plot_item.plot_object.plot_window.dco_link, 
                          from_key=self.dc_template_key.format(sep=DataChannel.dco_separator_char, name=piname))
      self.dc.set_lock(1)     ##### unmodifiable
      #fn_update=lambda options_key=options_key:self.update_plot(options_key)
      self.dc.signal_value_changed.connect(self.update_plot) #fn_update)
      #self.dc.signal_dc_changed.connect(self.update_plot)    # fn_update)
      self.dc.out() #-> #self.update_plot() #options_key)

    def update_plot(self): #, options_key):      
      local_options=self.plot_item.options[self.options_key]
      for line in self.lines: self.plot_item.plot_object.removeItem(line)
      self.lines=[]       
      df=self.dc.out()   
      if df is None: return   
      if df.index.name!='Node': df=df.set_index('Node')
      if local_options['line_visible']: 
        try: 
          #for i, row_i in enumerate(df.index):
          default_color=self.plot_item.plot_object.plot_window.master().colors().get_default_color()
          tree=self.plot_item.plot_object.plot_window.master().trees().get_tree(None)   ### NOTE! if anc_dc is modified to allow non default tree, this has to be modified
          #for df in ldf, adf:   #first let's start from leaf nodes, then ancestors
          first_column, second_column=df.columns[:2]
          for i, row_i in enumerate(df.index):
            is_visible=smart_get('line_visible', local_options, df, row_i)
            if not is_visible: continue
            node_name=df.at[row_i, 'Node']        if not df.index.name=='Node' else row_i
            x1coord=float(df.at[row_i,first_column])
            y1coord=float(df.at[row_i,second_column])
            parent=tree.get_node(node_name).up
            if parent is None: continue
            if not parent.name in df.index:
              #write('AncestorsPath cannot find this parent in DF: {} df=\n{} ; aborting all lines'.format(parent.name, df), 1, how='blue,reverse')
              self.lines=[]
              return 
            x2coord=float(df.at[parent.name,first_column])
            y2coord=float(df.at[parent.name,second_column])

            line_width=smart_get('line_width', local_options, df, row_i)
            line_item=PlotLine(x1coord, y1coord, x2coord, y2coord)
            color= '#'+smart_get('color', local_options, df, row_i, default=default_color)
            qcolor=pg.QtGui.QColor(color)
            pen=pg.QtGui.QPen(qcolor)
            pen.setCosmetic(True);             pen.setWidthF(line_width)
            line_item.setPen(pen)
            alpha=smart_get('line_alpha', local_options, df, row_i)
            line_item.setOpacity(alpha)
            self.lines.append(line_item)
        except Exception as e: 
          QtGui.QMessageBox.warning(self.plot_item.plot_object.plot_window, 'Error', 'Error while plotting {} !\n{}'.format(self.options_key, e), QtGui.QMessageBox.Ok)

      for line_item in self.lines: self.plot_item.plot_object.addItem(line_item)

 
  ########################  

  ############## The DCO adapter used by this PlotItem
  #
  class DCO_adapter(DCO_smart):
    """ """
    icon_name='Scatter'
    #name='adapter'
    default_parameters='$2;$3;Y'
    tooltip='Scatterplot'
    def short(self): return 'Adapter'    
    def expand_parameters(self, parameters):
      x_selector,y_selector,discard_others=parameters.split(';')
      p='scatterplot_adapter[shapecheck:c>2&Node@c{sep}var:xfield={x}{sep}var:yfield={y}{sep}typecheck:$xfield,$yfield=n{sep}select:$xfield,$yfield,Node{d}]'.format(
        sep=DataChannel.dco_separator_char, x=x_selector, y=y_selector,  d=',:' if discard_others=='N' else '')
      return p  #{sep}process:label=Node
    def backtrace_parameters(self, parameters):
      splt=parameters.split(DataChannel.dco_separator_char)
      x_selector=splt[1][splt[1].index('=')+1:]
      y_selector=splt[2][splt[2].index('=')+1:]
      p='{};{};{}'.format(x_selector, y_selector, 'N' if parameters.endswith(',:]') else 'Y' )
      return p
   
   ############# the widget of this DCO:
    class DCOW_class(DCOW):
      def __init__(self, dcw, dco):
        DCOW.__init__(self, dcw, dco)   #super(DCOW_class, self).__init__(dcw, dco) 
        self.layout=QtGui.QVBoxLayout(); self.layout.setContentsMargins(0,0,0,0); self.layout.setSpacing(2)
        self.setLayout(self.layout)
        x_selector,y_selector,discard_others=self.dco.backtrace_parameters( self.dco.parameters ).split(';')

        row1=QtGui.QHBoxLayout();  row1.setContentsMargins(1,1,1,1); row1.setSpacing(5)
        self.textbox_x=QtGui.QLineEdit(x_selector, self)
        self.textbox_x.setMaximumWidth(60)
        self.textbox_y=QtGui.QLineEdit(y_selector, self)
        self.textbox_y.setMaximumWidth(60)
        row1.addWidget(QtGui.QLabel('x='))
        row1.addWidget(self.textbox_x)
        row1.addWidget(QtGui.QLabel('y='))
        row1.addWidget(self.textbox_y)
        self.layout.addLayout(row1)

        row2=QtGui.QHBoxLayout();  row2.setContentsMargins(1,1,1,1); row2.setSpacing(5)
        self.discard_others_checkbox=QtGui.QCheckBox()
        self.discard_others_checkbox.setText('Discard other columns')
        if discard_others: self.discard_others_checkbox.setChecked(True)
        row2.addWidget(self.discard_others_checkbox)
        self.layout.addLayout(row2)        

      def save(self):
        new_text='{};{};{}'.format(str(self.textbox_x.text()).strip(), str(self.textbox_y.text()).strip(),  {True:'Y',False:'N'}[self.discard_others_checkbox.isChecked()] )
        self.update_dco(new_text)  #expand_parameters happening under the hood

  # class ancestral_DCO_adapter(DCO_smart):
  #   """ """
  #   icon_name='trace'
  #   default_parameters='WA'
  #   def short(self): return self.parameters
  #   def expand_parameters(self, parameters):
  #     trace_procedure=parameters
  #     p='trace4plot[retrieve:PlotData{sep}select:$1,$2,Node{sep}trace:{tp}]'.format(sep=DataChannel.dco_separator_char, tp=trace_procedure)
  #     #p='trace4plot[retrieve:PlotData]'
  #     return p  #{sep}process:label=Node
  #   def backtrace_parameters(self, parameters):
  #     splt=parameters.split(DataChannel.dco_separator_char)
  #     trace_procedure=splt[-1][splt[-1].index(':')+1:-1]
  #     return trace_procedure
  #   def short(self): return self.backtrace_parameters(self.parameters)
   
  #  ############# the widget of this DCO:
  #   class DCOW_class(DCOW_trace):
  #     """ """
  #     # def __init__(self, dcw, dco):
  #     #   DCOW.__init__(self, dcw, dco)   #super(DCOW_class, self).__init__(dcw, dco) 
  #     #   self.layout=QtGui.QHBoxLayout(); self.layout.setContentsMargins(1,1,1,1); self.layout.setSpacing(5)
  #     #   self.setLayout(self.layout)
  #     #   x_selector,y_selector=self.dco.backtrace_parameters( self.dco.parameters ).split(';')

  #     #   self.textbox_x=QtGui.QLineEdit(x_selector, self)
  #     #   self.textbox_x.setMaximumWidth(100)
  #     #   self.textbox_y=QtGui.QLineEdit(y_selector, self)
  #     #   self.textbox_y.setMaximumWidth(100)
  #     #   self.layout.addWidget(QtGui.QLabel('x='))
  #     #   self.layout.addWidget(self.textbox_x)
  #     #   self.layout.addWidget(QtGui.QLabel('y='))
  #     #   self.layout.addWidget(self.textbox_y)

  #     # def save(self):
  #     #   new_text='{};{}'.format(str(self.textbox_x.text()).strip(), str(self.textbox_y.text()).strip())
  #     #   self.update_dco(new_text)  #expand_parameters happening under the hood


  

   #############
  #
  ####################

####################################################################################
class ScatterPlotObject(pg.PlotItem, PlotObject):
  default_options={}
  def __init__(self, plot_window):
    pg.PlotItem.__init__(self)
    PlotObject.__init__(self)
    self.plot_window=plot_window
    self.showGrid(x=True, y=True, alpha=0.1)

class ScatterPlotWindow(pg.GraphicsView, PlotWindow):
  """      main_layout: QtGui.QVBoxLayout()  #vertical
     +----------------------------------window-title-------------------------+
     | toolbar_layout: QtGui.QVBoxLayout()  #vertical                        |
     | ____________________________________________________________________  |
     | |------  Toolbar 1 ------------------------------------------------|  |   
     | ____________________________________________________________________  | 
     plot layout:  2 cols 2 row                                              |   plot_layout: pg.GraphicsLayoutWidget()
     |+-------+  +--------------------------------------------------------+  |
     |+-y_lab-+  |                        PLOT OBJECT                     |  |
     |+-------+  +--------------------------------------------------------+  |
     |                                                                       |
     |           +--------------------------------------------------------+  |
     |           |               ----x_label----                          |  |
     |           +--------------------------------------------------------+  |
     +-----------------------------------------------------------------------+
     | +------------------------------------------------------------------+  |
     | +             status bar                                           +  |
     | +------------------------------------------------------------------+  |
     +-----------------------------------------------------------------------+
"""
  available_plot_items=[NodeScatterPlotItem]
  dimensions=2
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
    self.plot_layout=pg.GraphicsLayoutWidget()
    self.plot_layout.ci.layout.setContentsMargins(0, 0, 0, 0);     self.plot_layout.ci.layout.setSpacing(0)
    self.axes=[]  #first element: QLabel for X;      second element: for Y
    self.axes.append(self.plot_layout.addLabel('--', col=0, row=1, angle=-90)) #later text is set
    self.plot_object= ScatterPlotObject(plot_window=self)
    self.plot_layout.addItem(self.plot_object, col=2, row=1)
    self.axes.insert(0, self.plot_layout.addLabel('--', col=2, row=2))
    self.main_layout.addWidget(self.plot_layout)

  #def get_n_dimensions(self): return 2

  def set_axis_label(self, index_dimension, label):     
    self.axes[index_dimension].setText(label)

  # def set_axis_range(self, index_dimension, min_this_dimension, max_this_dimension):
  #   if    index_dimension==0:      self.plot_object.setXRange( min_this_dimension, max_this_dimension, padding=0)
  #   elif  index_dimension==1:      self.plot_object.setYRange( min_this_dimension, max_this_dimension, padding=0)
  #   else: raise Exception

