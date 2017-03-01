from .baseplots import *  

def smart_get(what, local_options, df, row_i):
  if not what in df.columns:   return local_options[what]
  x=df.at[row_i, what]
  if x is None or np.isnan(x): return local_options[what]   #falls on default if no value for this row
  return x

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
    ls_checkbox.setText('Points for leaf nodes')
    ls_checkbox.stateChanged.connect(self.clicked_leaf_spots_visible_checkbox)
    row1_layout.addWidget(ls_checkbox)
    #row1_layout.addSpacing(30)
    row1_layout.addWidget(VerticalLine('lightgrey'))
    row1_layout.addWidget(QtGui.QLabel('Node filter:'))
    temp_button=QtGui.QToolButton(); temp_button.setEnabled(False)
    row1_layout.addWidget(temp_button)
    row1_layout.addWidget(VerticalLine('lightgrey'))
    row1_layout.addWidget(QtGui.QLabel('Color:'))
    temp_button=QtGui.QToolButton(); temp_button.setEnabled(False)
    row1_layout.addWidget(temp_button)
    temp_label=QtGui.QLabel('(default)'); temp_label.setEnabled(False)
    row1_layout.addWidget(temp_label)

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
    row1_layout.addWidget(QtGui.QLabel('Node filter:'))
    temp_button=QtGui.QToolButton(); temp_button.setEnabled(False)
    row1_layout.addWidget(temp_button)
    row1_layout.addWidget(VerticalLine('lightgrey'))
    row1_layout.addWidget(QtGui.QLabel('Color:'))
    temp_button=QtGui.QToolButton(); temp_button.setEnabled(False)
    row1_layout.addWidget(temp_button)
    temp_label=QtGui.QLabel('(default)'); temp_label.setEnabled(False)
    row1_layout.addWidget(temp_label)
    row1_layout.addWidget(VerticalLine('lightgrey'))
    label_field=ll_options['label_field']
    self.ll_label_field_textbox=QtGui.QLineEdit()
    self.ll_label_field_textbox.setText(label_field)
    self.ll_label_field_textbox.setMaximumWidth(75) 
    self.ll_label_field_textbox.editingFinished.connect(self.edited_leaf_labels_label_field_textbox)   
    row1_layout.addWidget(QtGui.QLabel('Display:'))
    row1_layout.addWidget(self.ll_label_field_textbox)

    row1_layout.addStretch()  

    row2_layout=QtGui.QHBoxLayout()
    row2_layout.addSpacing(30) #30 non stretchable pixels at the left end

    fontsize=ll_options['fontsize']
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
    row2_layout.addWidget(QtGui.QLabel('Anchor:'))
    row2_layout.addSpacing(5)
    row2_layout.addWidget(QtGui.QLabel('horizontal'))
    hanchor, vanchor= ll_options['anchor']
    self.ll_anchor_h_combobox=QtGui.QComboBox()
    self.ll_anchor_h_combobox.possible_values=[(0.0,'left'), (0.5,'center'),(1.0,'right')]
    for _,desc in self.ll_anchor_h_combobox.possible_values: self.ll_anchor_h_combobox.addItem(desc)
    self.ll_anchor_h_combobox.setCurrentIndex(  [s for s,_ in self.ll_anchor_h_combobox.possible_values].index(hanchor)   )
    self.ll_anchor_h_combobox.currentIndexChanged[int].connect(self.activated_leaf_labels_anchor_h_combobox)
    row2_layout.addWidget(self.ll_anchor_h_combobox)
    row2_layout.addSpacing(5)
    row2_layout.addWidget(QtGui.QLabel('vertical'))
    self.ll_anchor_v_combobox=QtGui.QComboBox()
    self.ll_anchor_v_combobox.possible_values=[(0.0,'above'), (0.5,'center'),(1.0,'below')]
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
    try:     value=int(text.strip())
    except ValueError:
      QtGui.QMessageBox.warning(self, 'Error', 'Invalid value! Please enter a number', QtGui.QMessageBox.Ok)
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
    try:     alpha=float(text.rstrip('%'))/100  # 1-100%   (or without % )   --> 0.01 - 1.0 
    except ValueError:
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
    self.plot_item.options['LeafLabels']['fontsize']=value
    self.ll_size_textbox.setText(str(value))
    self.plot_item.update_item()
  def edited_leaf_labels_size_textbox(self):
    text=str(self.ll_size_textbox.text())
    try:     value=int(text.strip())
    except ValueError:
      QtGui.QMessageBox.warning(self, 'Error', 'Invalid value! Please enter a number', QtGui.QMessageBox.Ok)
      self.ll_size_textbox.setText(str(self.plot_item.options['LeafLabels']['fontsize']))
      return 
    self.plot_item.options['LeafLabels']['fontsize']=value
    self.ll_size_slider.setValue( max([value, self.ll_size_slider.maximum()]) )
    self.plot_item.update_item()
  def activated_leaf_labels_anchor_h_combobox(self, index):
    self.plot_item.options['LeafLabels']['anchor'][0]=self.ll_anchor_h_combobox.possible_values[index][0]
    self.plot_item.update_item()
  def activated_leaf_labels_anchor_v_combobox(self, index):
    self.plot_item.options['LeafLabels']['anchor'][1]=self.ll_anchor_v_combobox.possible_values[index][0]
    self.plot_item.update_item()



########
class NodeScatterPlotToolbar(PlotItemToolbar):
  """ """
  #plotitem_menu is default of PlotItemToolbar
  #data_menu is default of PlotItemToolbar
  view_menu=ToolbarViewMenu


  
####################################################################################
class NodeScatterPlotItem(PlotItem):
  plot_type='NodeScatter'
  defaults={ 'dc':None, 'name':None,
             'LeafSpots': {'point_visible':True, 'size':6,  'symbol':'o', 'alpha':0.5}, 
             'LeafLabels':{'label_visible':False, 'fontsize':7, 'anchor':[0.5, 1.0], 'label_field':'Node'}} 
  #'fixed_size':True, ## pg bug when pxMode != True
  toolbar_class=NodeScatterPlotToolbar

  def init_data_channel(self):
    if   self.options['dc'] is None: 
      self.options['dc']=DataChannel(self.plot_object.plot_window)      
    elif type(self.options['dc']) == str:  #a DC key was provided
      self.options['dc']=DataChannel(self.plot_object.plot_window, from_key=self.options['dc'])           
    dc=self.options['dc']
    if dc.chain and dc.chain[-1].name=='group' and dc.chain[-1].parameters[:dc.chain[-1].parameters.index('[')]=='adapter' :      
      dco_adapter_w_base_type=dc.pop()   # this is a basic group type, instead of DCO_adapter
      dc.append( self.DCO_adapter(dco_adapter_w_base_type.parameters) )
    else:
      dc.append( self.DCO_adapter() )   
    dc.signal_dc_changed.connect(self.update_item) 
    dc.signal_value_changed.connect(self.update_item) 

  def init_item(self):
    print 'init scatterplot, ', self.options['name'], id(self.options)
    dc=self.options['dc'] #; x_dc=self.options['x']; y_dc=self.options['y']
    df=dc.out();              # xdf=x_dc.out();         ydf=y_dc.out()   
    self.leaf_spots= self.LeafSpots( self, df, self.options['LeafSpots']) 
    self.leaf_labels=self.LeafLabels(self, df, self.options['LeafLabels']) 
    self.store_headers(df, 2)
    ### add other components

  def update_item(self):
    # write('update called for '+self.options['name'], 1, how='red')
    # for pi in self.plot_object.plot_window.plot_items:
    #   write( (pi.options['name'], pi.options, id(pi.options['LeafSpots'])), 1)
    FLAG='this is a flag'
    self.computed_data=FLAG  #flag for: something was updated
    
    def get_data(self): 
      if self.computed_data is FLAG:
        dc=self.options['dc'] 
        df=dc.out();          
        self.computed_data=df
      return self.computed_data

    delta=self.delta_options()
    print 'updating scatterplot? n={n} delta={d}'.format(n=self.options['name'], d=delta)
    if 'name' in delta:   self.toolbar.plotitem_label.setText(self.options['name'])
    if 'dc' in delta: 
      for k in ['LeafSpots','LeafLabels']:    delta.add(k)

    if 'LeafSpots' in delta:
      print '  -update leafspots'
      df=get_data(self) 
      self.leaf_spots.update_plot(df, self.options['LeafSpots'])
    if 'LeafLabels' in delta:
      print '  -update leaflabels'
      df=get_data(self) 
      self.leaf_labels.update_plot(df, self.options['LeafLabels'])
    # update other components..

    if not self.computed_data is FLAG:   
      self.store_plot_options()
      self.store_headers(self.computed_data, 2)
      self.plot_object.plot_window.update_axis()
 
  def delete_item(self):
    self.leaf_labels.update_plot(None, {})
    self.leaf_spots.update_plot( None, {})
    print 'delete item!'
         
  ########################  
  ### PlotItem Components
  class LeafSpots(pg.ScatterPlotItem):
    """Dots, each one linked to a leaf node in the tree. Init with df """
    def __init__(self, plot_item, df, local_options):      
      self.plot_item=plot_item
      pg.ScatterPlotItem.__init__(self, pxMode=True) #local_options['fixed_size'])
      self.update_plot(df, local_options)
      self.plot_item.plot_object.addItem(self)
      self.sigClicked.connect(self.spots_were_clicked)

    def update_plot(self, df, local_options): 
      #self.setPxMode( local_options['fixed_size'] )  #buggy
      spot_data=[]
      if df is None: pass
      else:
        if local_options['point_visible']: 
          for i, row_i in enumerate(df.index):
            is_visible=smart_get('point_visible', local_options, df, row_i)
            if not is_visible: continue
            node_name=df.at[row_i, 'Node']        
            xcoord=float(df.iat[i,0])     #    df.at[row_i,xdf.columns[0]])  #better way?
            ycoord=float(df.iat[i,1])            #df.at[row_i,ydf.columns[0]])
            symbol=smart_get('symbol', local_options, df, row_i )
            size=  smart_get('size', local_options, df, row_i )
            alpha= smart_get('alpha', local_options, df, row_i ) 
            alphahex=int(rescale( alpha, ymin=0, ymax=255, xmin=0.0, xmax=1.0 )) #from 0 to 255
            alphahex_pen=int(min([alphahex*1.1, 255])) #alpha for pen is a little more than for body
            alphastring=format(alphahex, 'x'); alphastring_pen=format(alphahex_pen, 'x')
            color=  self.plot_item.plot_object.plot_window.master().colors().node_color_maps['default'][node_name]             #temp
            brush=color+alphastring; pen=color+alphastring_pen;   
            spot_data.append({'pos': [xcoord,ycoord], 'data': node_name, 'symbol':symbol, 'size':size, 'pen':pen, 'brush':brush})
        #print spot_data
      self.setPoints(spot_data)  

    def spots_were_clicked(self,  plot, spots): 
      tree_manager= self.plot_item.plot_object.plot_window.master().trees()
      clicked_nodes=NodeSelector([tree_manager.get_node( s.data() )   for s in spots])
      ns=self.plot_item.plot_object.plot_window.master().selections().get_node_selection( 'Selected nodes' ).copy()
      if   QtGui.QApplication.keyboardModifiers() == QtCore.Qt.ShiftModifier:        ns.update(clicked_nodes)
      elif QtGui.QApplication.keyboardModifiers() == QtCore.Qt.ControlModifier:
        for node in clicked_nodes:
          if not node in ns:       ns.add(node)                      
          else:                    ns.remove(node)                      
      else: ## normal behavior: select this node
        ns=clicked_nodes
      self.plot_item.plot_object.plot_window.master().selections().edit_node_selection('Selected nodes', ns)            


  class LeafLabels(object):
    """ labels in pyqtgraph scatterplot"""
    def __init__(self, plot_item, df, local_options):
      self.plot_item=plot_item
      self.labels=[] #list of pg.TextItem, which is QtGui.QGraphicsTextItem really
      self.update_plot(df, local_options)

    def update_plot(self, df, local_options):
      for label in self.labels: self.plot_item.plot_object.removeItem(label)
      self.labels=[]       
      if df is None: return       
      if local_options['label_visible']: 
        for i, row_i in enumerate(df.index):
          is_visible=smart_get('label_visible', local_options, df, row_i)
          if not is_visible: continue
          label_field=local_options['label_field']
          text='{}'.format(df.at[row_i,label_field])
          xcoord=float(df.iat[i,0])     #    df.at[row_i,xdf.columns[0]])  #better way?
          ycoord=float(df.iat[i,1])            #df.at[row_i,ydf.columns[0]])
          size=  smart_get('fontsize', local_options, df, row_i)
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
      #color = pg.functions.mkColor(color)
      #self.textItem.setDefaultTextColor(color)
  ########################  

  ############## The DCO adapter used by this PlotItem
  #
  class DCO_adapter(DCO_group):
    """ """
    icon_name='NodeScatter'
    def __init__(self, parameters=None):           #### trying to unify... start over is better idea
      if parameters is None: parameters='$2;$3'
      else:  #initialized with the resulting DC key. let's backtrack to get the essential
        parameters=self.backtrace_parameters(parameters)
      DCO_group.__init__(self, parameters=parameters) #'test[select:$2]')     
      #cache:input |>select:$2,$3 |>rename:x=$2,y=$3'

    def update(self, parameters):
      """ Overriding DCO_group.update to change parameters (expand it)"""
      parameters=self.expand_parameters(parameters)
      DCO_group.update(self, parameters)
      #self.parameters=parameters
      # k=self.parameters[ self.parameters.index('[')+1:-1 ]  #if not self.parameters is None else None
      # self.dc=DataChannel(self, from_key=k  ) #passing DC key only
      # if not self.parent is None: self.parent.notify_modification()

    def short(self): return 'ScatterPlotItem'
    def expand_parameters(self, parameters):
      x_selector,y_selector=parameters.split(';')
      p='adapter[var:xfield={x}{sep}var:yfield={y}{sep}select:$xfield,$yfield,Node,:{sep}cache:PlotData]'.format(sep=DataChannel.dco_separator_char, x=x_selector, y=y_selector)
      return p  #{sep}process:label=Node
    def backtrace_parameters(self, parameters):
      splt=parameters.split(DataChannel.dco_separator_char)
      x_selector=splt[0][splt[0].index('=')+1:]
      y_selector=splt[1][splt[1].index('=')+1:]
      p='{};{}'.format(x_selector, y_selector)
      return p
   
   ############# the widget of this DCO:
    class DCOW_class(DCOW):
      def __init__(self, dcw, dco):
        DCOW.__init__(self, dcw, dco)   #super(DCOW_class, self).__init__(dcw, dco) 
        self.layout=QtGui.QHBoxLayout(); self.layout.setContentsMargins(1,1,1,1); self.layout.setSpacing(5)
        self.setLayout(self.layout)
        x_selector,y_selector=self.dco.backtrace_parameters( self.dco.parameters ).split(';')

        self.textbox_x=QtGui.QLineEdit(x_selector, self)
        self.textbox_x.setMaximumWidth(100)
        self.textbox_y=QtGui.QLineEdit(y_selector, self)
        self.textbox_y.setMaximumWidth(100)
        self.layout.addWidget(QtGui.QLabel('x='))
        self.layout.addWidget(self.textbox_x)
        self.layout.addWidget(QtGui.QLabel('y='))
        self.layout.addWidget(self.textbox_y)

      def save(self):
        new_text='{};{}'.format(str(self.textbox_x.text()).strip(), str(self.textbox_y.text()).strip())
        self.update_dco(new_text)  #expand_parameters happening under the hood
   #############
  #
  ####################

####################################################################################
class ScatterPlotObject(pg.PlotItem, PlotObject):
  def __init__(self, plot_window, options={}):
    pg.PlotItem.__init__(self)
    PlotObject.__init__(self, options=options)
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
  def window_identifier(self): return {'category':'ScatterPlot'}
  def __init__(self, master_link, plot_title='ScatterPlot'): 
    PlotWindow.__init__(self, master_link) #    self.plot_items=[];     self.active_menu=[]     ## plot_item, category, menu, button
    pg.GraphicsView.__init__(self)
    self.setWindowTitle(plot_title)
    self.main_layout= QtGui.QVBoxLayout(); self.main_layout.setContentsMargins(0, 0, 0, 0);     self.main_layout.setSpacing(0)
    self.setLayout(self.main_layout) 
    self.toolbar_layout= QtGui.QVBoxLayout()  
    self.main_layout.addLayout(self.toolbar_layout)
    ### active feedback menu
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

