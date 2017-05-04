from .base   import *
from ..data  import *
import numpy as np                  #only to check type of entry np.floating and np.integer

# class container_of_DCOW(QtGui.QWidget):
#   def __init__(self, dco):
#     self.dco=dco
#     super(container_of_DCOW, self).__init__() #    QtGui.QWidget.__init__(self)  
#     #self.setAutoFillBackground(True)

class DataChannelWidget(QtGui.QWidget): 
  """ (This is also called DCW) Widget to create, modify and inspect DataChannel instances. It consists in a horizontal succession of 'pipes', each corresponding to a DataChannelOperation. A special such pipe is shown when the DC is empty instead. A classical menu is present at the right end. 
  Init with:    
    -dc:      the DataChannel linked to this widget. This can be modified live by this widget.
    deprecated: ## -within:  possible values ['FeatureExplorer', 'Plot']. When the DCW is embedded in these widgets, it affects the entries shown in menus
"""
  style={'base': 'QWidget{ background: #99CCFF; padding: 0px}  \
                  ToolButton { background: white }',  #selection-background-color: #FFCC66 } \
         'editing':'QWidget{background: #4488FF} \
                  QLineEdit { background: white }  \
                  QComboBox { background: none }  \
                  ToolButton { background: white } ',
         'locked':       'QWidget{ background: #909090 }  ', 
         'unremovable':  'QWidget{ background: #c0c0c0 }  ', 
  # QComboBox { background: white }
#         'post':   'QWidget{ background: #a5a5a5 } QComboBox { background: white }',
         'broken':  'background: #bb1111',}

  def __init__(self, dc, within=None):
    super(DataChannelWidget, self).__init__() #    QtGui.QWidget.__init__(self)  
    self.dc=dc
    self.within=within
    self.editing=None #index of DCO currently being edited
    self.setStyleSheet( self.style['base'] )
    self.layout=QtGui.QVBoxLayout(); self.layout.setContentsMargins(0, 0, 0, 0); self.layout.setSpacing(0)
    self.setLayout(self.layout)   #One widget per DCO here, followed by a vline;  plus last one for menu
    self.setSizePolicy(fixed_size_policy)   #### NOT WORKING PROPERLY
    self.containers_of_DCOW=[]   #index of DCO -> widget that contains DCOW (or just text if not being edited)
    self.fill()
    self.dc.signal_dc_changed.connect(self.fill) #dc_changed)
    self.dc.signal_value_changed.connect(self.refresh_components_style) #dc_changed)

  def refresh_components_style(self):
    print 'refresh_components!'
    error_components=set()
    if isinstance(self.dc.memory_unit, ErrorUnit):
      p=self.dc.memory_unit.error[0]  #initially a DCO
      while not p.container is None:  error_components.add(p); p=p.container
      
    for w in self.containers_of_DCOW:
      w.setStyleSheet( self.style['base'] )
      dco_index=w.dco_index

      if self.dc.is_locked(dco_index):        
        if self.dc.is_modifiable(dco_index):   
          w.setStyleSheet( self.style['unremovable'] )
          w.setToolTip( "This component cannot be removed" )
        else:                                  
          w.setStyleSheet( self.style['locked'] )
          w.setToolTip( "This component is locked" )

      if w.dco in error_components:
        #this is the cause of the error in this DC
        w.setStyleSheet( self.style['broken'] )
        w.setToolTip( "Data Channel broken:\n"+ str(self.dc.memory_unit.error[1])  )


      if self.editing==dco_index:        
        w.setStyleSheet( self.style['editing'] )

    
  def fill(self):
    print 'fill dc widget ', self.dc.key()
    while self.containers_of_DCOW: self.containers_of_DCOW.pop()
    clear_layout(self.layout)
    row_layout=QtGui.QHBoxLayout(); row_layout.setContentsMargins(0, 0, 0, 0); row_layout.setSpacing(2)
    try:
      self.layout.addLayout(row_layout)
    except RuntimeError:
      self.layout=QtGui.QVBoxLayout(); self.layout.setContentsMargins(0, 0, 0, 0); self.layout.setSpacing(0)
      self.setLayout(self.layout)   #One widget per DCO here, followed by a vline;  plus last one for menu
      self.layout.addLayout(row_layout)

    found_editing_dco=False

    if not self.dc.chain or self.dc.chain[0].name=='empty':      
      edc=empty_DC(self)
      row_layout.addWidget(edc, alignment=QtCore.Qt.AlignLeft) 
      if not self.editing is None: edc.setEnabled(False)      
    elif not (self.dc.chain and self.dc.chain[0].name=='lockinsert'):
      chain_button=ChainButton(lambda s,i=-1: self.open_chain_menu(i))
      if not self.editing is None: chain_button.setEnabled(False)         #we're editing some DCO          
      row_layout.addWidget(chain_button, alignment=QtCore.Qt.AlignLeft)

    for dco_index, dco in enumerate(self.dc.chain):  # this is also in the else:, conceptually
      if dco.name=='empty' and dco_index==0: continue
      if dco.name=='lockinsert':             continue
      if dco.name=='lockappend':             continue
      w=QtGui.QWidget() #  container_of_DCOW(dco)    # w is dedicated to this DCO
      w.dco=dco
      w.dco_index=dco_index
      self.containers_of_DCOW.append(w)
      #self.layout.itemAt( dco_index*2 ).widget()  --> recovers w
      # if self.dc.is_locked(dco_index):        
      #   w.setStyleSheet( self.style['locked'] )
      #   if self.dc.is_modifiable(dco_index):   w.setToolTip( "This component cannot be removed" )
      #   else:                                  w.setToolTip( "This component is locked" )
      # if isinstance(self.dc.memory_unit, ErrorUnit) and self.dc.memory_unit.error[0]==dco_index:
      #   #not self.dc.validated is None and self.dc.validated[0]==dco_index:
      #   #this came out as the problematic DCO in the last dc.validate()
      #   w.setStyleSheet( self.style['broken'] )
      #   w.setToolTip( "Data Channel broken:\n"+ str(self.dc.memory_unit.error[1])  )
      w.setSizePolicy(fixed_size_policy)
      w.frame_layout=QtGui.QVBoxLayout(); w.frame_layout.setContentsMargins(0, 0, 0, 0); w.frame_layout.setSpacing(0)
      w.setLayout(w.frame_layout)

      w.frame_layout.addWidget(HorizontalLine(), alignment=QtCore.Qt.AlignLeft) 
      w.layout=QtGui.QHBoxLayout(); w.layout.setContentsMargins(2, 2, 2, 2); w.layout.setSpacing(0)
      w.frame_layout.addLayout(w.layout)
      w.frame_layout.addWidget(HorizontalLine(), alignment=QtCore.Qt.AlignLeft) 

      #if not self.dc.is_locked(dco_index):  
      #else:                                 fn=None
      if dco.name=='empty':
        edc=empty_DC(self)
        row_layout.addWidget(edc, alignment=QtCore.Qt.AlignLeft) 
        if not self.editing is None: edc.setEnabled(False) #we're editing another DCO
        continue
      elif dco.name=='newline':
        row_layout.addStretch() #previous row
        row_layout=QtGui.QHBoxLayout(); row_layout.setContentsMargins(0, 0, 0, 0); row_layout.setSpacing(2)
        self.layout.addLayout(row_layout)
        chain_button=ChainButton(lambda s,i=dco_index: self.open_chain_menu(i))
        w.layout.addWidget(chain_button, QtCore.Qt.AlignLeft)
        row_layout.addWidget(w,  alignment=QtCore.Qt.AlignLeft)
        #row_layout.addWidget(VerticalLine())
        continue

      icon_name=dco.name if not hasattr(dco, 'icon_name') else dco.icon_name
      tooltip=  dco.name.capitalize().replace('_', ' ')     if not hasattr(dco, 'tooltip')  else dco.tooltip
      tool_button=ToolButton(icon_name, tooltip)  
      h={'Database':'DB', 'Scatterplot':'Plot', 'Retrieve':'Get', 'Table':'Tab'}
      if tooltip in h: tool_button.setText( h[tooltip] )
      tool_button.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
      w.layout.addWidget(tool_button)

      if self.editing==dco_index:        
        #we're editing this DCO
        #w.setStyleSheet('QWidget {background: yellow} ')
        dcow_class=DCO_name2widget[dco.name]    if dco.DCOW_class is None else dco.DCOW_class
        dcow=dcow_class(self, dco)
        w.layout.addWidget( dcow )
        if self.dc.is_modifiable(dco_index):          tool_button.clicked.connect( lambda  s,dcow=dcow:self.clicked_dco_button_to_save(dcow)  ) 
        else:                                         dcow.setEnabled(False)
        found_editing_dco=True
        #w.setStyleSheet( self.style['editing'] )
        # first trigger:   set self.editing ######### REVISE! Looks redundant after new edit (DCO->notify parent DC)
        # if dco has been modified:
        #  --> this will call self.dc.notify_modification        #  --> triggers self.dc.signal_dc_changed
        #   --> self.dc_changed -->  self.fill()  ## on any DCW with this DC
        # else:  self.fill()

      else:
        if self.dc.is_modifiable(dco_index):     tool_button.clicked.connect( lambda s,i=dco_index:self.clicked_dco_button_to_edit(i) )
        dco_short=dco.short()    #label with dco parameters 
        if not dco_short: dco_short='(None)'
        qlabel=QtGui.QLabel( dco_short ) 
        qlabel.setSizePolicy(fixed_size_policy)
        w.layout.addWidget(qlabel)
        if not self.editing is None:         #we're editing another DCO
          w.setEnabled(False)
        #else:           #we're not editing any DCO

        if not ( len(self.dc.chain)>dco_index+1 and self.dc.chain[dco_index+1].name=='lockappend' ):
          chain_button=ChainButton(lambda s,i=dco_index: self.open_chain_menu(i))
          w.layout.addWidget(chain_button)

      row_layout.addWidget(w, alignment=QtCore.Qt.AlignLeft)
      row_layout.addWidget(VerticalLine(), alignment=QtCore.Qt.AlignLeft)

    if not self.editing is None and not found_editing_dco:  #rare case when you're editing something but it gets deleted by some other effect
      self.editing=None
      self.fill()
    menu_button=ToolButton('menu', 'DataChannel Menu...', self.open_menu)
    menu_button.setSizePolicy(fixed_size_policy)
    if not self.editing is None:  menu_button.setEnabled(False)
    row_layout.addWidget(menu_button, alignment=QtCore.Qt.AlignLeft)
    row_layout.addStretch()
    self.refresh_components_style()

  def edit_dco(self, index):              self.editing=index
  def clicked_dco_button_to_edit(self, index):    
    print 'clicked_dco_button_to_edit', index, self.dc.key()
    self.edit_dco(index); self.fill()
  def clicked_dco_button_to_save(self, dcow):     
    print 'clicked_dco_button_to_save', dcow, '(container)', self.dc.key()
    self.editing=None;    dcow.save()  # this calls self.fill() one way or another
    print '--> saved', self.dc.key()

  def add_table(self, index):
    wm=self.dc.master().windows()
    i=1
    potential_title='table{}'.format(i)
    write(wm.windows, 1, how='green')
    while wm.has_window('Table: '+potential_title):
      i+=1
      potential_title='table{}'.format(i) 
    dco=DCO_table(potential_title)
    self.dc.insert(index, dco)

  def add_scatterplot(self, index):
    wm=self.dc.master().windows()
    i=1
    potential_title='plot{}'.format(i)
    while wm.has_window('Scatterplot: '+potential_title):
      i+=1
      potential_title='plot{}'.format(i) 
    dco=DCO_scatterplot(potential_title)
    self.dc.insert(index, dco)

  def add_plot3D(self, index):
    wm=self.dc.master().windows()
    i=1
    potential_title='3D.{}'.format(i)
    while wm.has_window('Plot3D: '+potential_title):
      i+=1
      potential_title='3D.{}'.format(i) 
    dco=DCO_plot3D(potential_title)
    self.dc.insert(index, dco)

  def send_to_plot(self, index):   self.add_dco('send_to_plot', index)
    # dco=DCO_add_to_plot()
    # self.dc.insert(index, dco)

  def add_dco(self, dco_name, index=None, edit_it=True):
    print 'add_dco', dco_name, index
    if index==0 and self.dc.chain and self.dc.chain[0].name=='empty': 
      self.dc.pop(0, no_emit=True)
    dco=  DCO_name2class[dco_name] ()  #default parameters
    if edit_it: self.edit_dco(index)   #preparing for when, just below, append/insert triggers the signal that forces self.fill
    if index is None:   self.dc.append(dco)
    else:               self.dc.insert(index, dco)
    #self.dc.notify_modification()

  def remove_dco(self, index=None): 
    self.dc.pop(index) #when None, the last one is removed
    #self.fill()
    #self.dc.notify_modification()

  def open_menu(self):      
    qmenu=QtGui.QMenu()
    #qmenu.addAction('Edit', self.edit_data_channel  )
    #dc_broken=not self.dc.chain   or   not self.dc.validated is None
    # if self.within!='FeatureExplorer':      
    #   a=qmenu.addAction('Inspect data', self.inspect_data)
    #   if dc_broken: a.setEnabled(False)
    # if self.within!='Plot':                 
    #   a=qmenu.addAction('Open scatterplot', self.open_scatterplot)     
    #   if dc_broken: a.setEnabled(False)
    # qmenu.addSeparator()
    # submenu_add_component=QtGui.QMenu('Add component')
    # for dco_name in available_DCOs:
    #   submenu_add_component.addAction( get_icon(dco_name), dco_name.capitalize(), lambda n=dco_name:self.add_dco(n) )
    # qmenu.addMenu(submenu_add_component)
    # qmenu.addAction('Remove last component', self.remove_dco)
    # qmenu.addSeparator()
    qmenu.addAction('Copy Data Channel', self.copy_data_channel)
    #qmenu.addAction('Save Data Channel', self.save_data_channel)
    clipboard_text=str(QtGui.QApplication.clipboard().text())
    dc_key=clipboard_text[4:]   if clipboard_text.startswith('#DC#')   else None
    a=qmenu.addAction('Paste/Replace Data Channel', lambda k=dc_key:self.paste_replace_dc(k)  )
    if dc_key is None: a.setEnabled(False)      
    qmenu.addAction('Force output', self.force_output)
    qmenu.exec_(QtGui.QCursor.pos())

  # def open_scatterplot(self):
  #   win=ScatterPlotWindow(self.dc.master())
  #   win.add_plot_item(piclass=NodeScatterPlotItem, options={'dc':self.dc.copy()})
  #   win.show()
  # def inspect_data(self, dco_index=None):
  #   """ The dco_index can be provided to get partial (e.g. intermediate dc) data tables. 
  #   This 0-based index refers to the last DCO in the DC which is actually used"""
  #   if dco_index is None or dco_index==len(self.dc)-1:
  #     window_name='FeatExplorerDC.'+str(id(self.dc))
  #     if self.dc.master().windows().has_window( window_name ): 
  #       self.dc.master().windows().get_window( window_name ).activateWindow()
  #     else:
  #       win=TreedexFeatureExplorer(self.dc)
  #       win.show()
  #   else:
  #     partial_dc=self.dc.copy(index_end=dco_index)
  #     print 'partial_dc', partial_dc, dco_index
  #     win=TreedexFeatureExplorer(partial_dc)
  #     win.show()

  def force_output(self):    return self.dc.force_out()

  def open_chain_menu(self, dco_index):
    """corresponding to the button right after the dco number dco_index (0based) """
    #print 'open chain menu', dco_index
    qmenu=QtGui.QMenu()

    # if dco_index!=-1 and not (self.within=='FeatureExplorer' and dco_index== len(self.dc)-1):
    #   qmenu.addAction('Inspect data', lambda i=dco_index:self.inspect_data(i))
    #   #qmenu.addAction('Edit', self.edit_data_channel  )
    #   qmenu.addSeparator()

    qmenu.addAction('Add component...',     lambda i=dco_index:self.open_add_component_menu(i+1) )
    qmenu.addAction('Add newline',          lambda i=dco_index:self.add_dco('newline', i+1, edit_it=False) )
    qmenu.addSeparator()
    qmenu.addAction('Open table',           lambda i=dco_index:self.add_table(i+1) )
    qmenu.addAction('Open scatterplot',     lambda i=dco_index:self.add_scatterplot(i+1) )
    qmenu.addAction('Open plot3D',          lambda i=dco_index:self.add_plot3D(i+1) )    
    a=qmenu.addAction('Send to existing plot', lambda i=dco_index:self.send_to_plot(i+1) )
    if not self.dc.master().windows().plot_window_list():      a.setEnabled(False)
    qmenu.addSeparator()   

    clipboard_text=str(QtGui.QApplication.clipboard().text())
    dc_key=clipboard_text[4:]   if clipboard_text.startswith('#DC#')   else None   
    a=qmenu.addAction('Paste/Concatenate Data Channel', lambda i=dco_index,k=dc_key:self.paste_concatenate_dc(k,i+1)  )
    if dc_key is None: a.setEnabled(False)     

    if dco_index!=-1: 
      a=qmenu.addAction('Remove component: {}'.format(self.dc.chain[dco_index].name), lambda i=dco_index:self.remove_dco(i))
      if self.dc.is_locked(dco_index):  a.setEnabled(False)
    qmenu.exec_(QtGui.QCursor.pos())

  def open_add_component_menu(self, dco_index):
    w=ExtendDataChannelWidget(self, dco_index)
    self.add_menu=w #### cleaner please

  def copy_data_channel(self):  
    k="#DC#"+self.dc.key()
    QtGui.QApplication.clipboard().setText(k)
    print 'copy DC! '+k

  def paste_concatenate_dc(self, dc_key, index=None):    
    print 'paste_dc', dc_key, index
    pasted_dc=DataChannel(self.dc.master(), from_key=dc_key)
    #if index==1 and self.dc.chain[0].summary()=='database:None':      self.dc.pop(0)
    self.dc.concatenate(pasted_dc, index) #when index is none, append
    #self.dc.notify_modification()
  
  def paste_replace_dc(self, dc_key):
    print 'paste_replace_dc', dc_key
    if len(self.dc.chain)>1:
      pressed_button=QtGui.QMessageBox.warning(self, 'Warning', 'This will delete the current content of the Data Channel. Are you sure?', QtGui.QMessageBox.Cancel, QtGui.QMessageBox.Ok)
      #confirm_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
      if pressed_button==QtGui.QMessageBox.Cancel: 
        print 'cancel! not saving'
        return 
    pasted_dc=DataChannel(self.dc.master(), from_key=dc_key)
    self.dc.chain=[]
    self.dc.concatenate(pasted_dc) 
    #self.dc.notify_modification()

  def save_data_channel(self):      print 'save DC! well not today'
     

class empty_DC(QtGui.QWidget):
  def __init__(self, dcw):
    super(empty_DC, self).__init__(parent=dcw) #    QtGui.QWidget.__init__(self)  
    self.dcw=dcw
    self.frame_layout=QtGui.QVBoxLayout(); self.frame_layout.setContentsMargins(0, 0, 0, 0); self.frame_layout.setSpacing(0)
    self.setLayout(self.frame_layout)
    self.layout=QtGui.QHBoxLayout(); self.layout.setContentsMargins(2, 2, 2, 2); self.layout.setSpacing(0)
    self.frame_layout.addWidget(HorizontalLine())
    self.frame_layout.addLayout(self.layout)
    self.frame_layout.addWidget(HorizontalLine())
    tool_button=ToolButton('empty', "Empty Data Channel", self.open_menu)
    chain_button=ChainButton(self.open_menu)
    self.setSizePolicy(fixed_size_policy)
    self.layout.addWidget(tool_button)
    label=QtGui.QLabel('(Empty)')
    label.setStyleSheet('background:none')
    self.layout.addWidget(label)    
    self.layout.addWidget(chain_button)

  def open_menu(self):
    qmenu=QtGui.QMenu()
    qmenu.addAction('Add component...',  lambda :self.dcw.open_add_component_menu(0) )
    clipboard_text=str(QtGui.QApplication.clipboard().text())
    dc_key=clipboard_text[4:]   if clipboard_text.startswith('#DC#')   else None
    a=qmenu.addAction('Paste Data Channel', lambda k=dc_key:self.dcw.paste_replace_dc(k)  )
    if dc_key is None: a.setEnabled(False)
    qmenu.exec_(QtGui.QCursor.pos())

  # def add_db_dco(self):
  #   self.dcw.dc.append(DCO_database())  
  #   self.dcw.edit_dco(0)

########################################################################################
class DCOW(QtGui.QWidget):
  def __init__(self, dcw, dco):
    super(DCOW, self).__init__() #    QtGui.QWidget.__init__(self)  
    self.dcw=dcw
    self.dco=dco
  #def dco(self): return self.dco_link #self.dc.chain[self.dco_index]
  def save(self): raise Exception, "ERROR no save function for this DCO_widget!"
  def update_dco(self, text):
    print 'update dco (from dcow) ?'
    # if text!=self.dco.parameters :  
    #   print 'update dco!', self.__class__, [text, self.dco.parameters]
    notified=self.dco.update(text) #--> self.dco.dc.notify_modification()   
    if notified: print 'update dco: YES'
    if not notified:  self.dcw.fill() #if modification happened, the fill() will be triggered by signals

class DCOW_join(DCOW):
  """ """
  def __init__(self, dcw, dco):
    super(DCOW_join, self).__init__(dcw, dco) #    QtGui.QWidget.__init__(self)  
    self.layout=QtGui.QVBoxLayout(); self.layout.setContentsMargins(0,0,0,0); self.layout.setSpacing(0)
    self.setLayout(self.layout)
    dbname, field, target, join_type=self.get_values_from_dco()

    row1=QtGui.QHBoxLayout(); row1.setContentsMargins(0,0,0,0); row1.setSpacing(0)
    row1.addWidget(QtGui.QLabel('with'))
    self.type_combobox=QtGui.QComboBox()
    self.type_combobox.possible_values=['database','cache','antenna']
    for i, possible_target in enumerate(self.type_combobox.possible_values): 
      self.type_combobox.addItem(possible_target)
      if possible_target==target: self.type_combobox.setCurrentIndex(i)
    self.type_combobox.activated[int].connect( self.activated_type_combobox )
    row1.addWidget(self.type_combobox)
    self.layout.addLayout(row1)

    self.database_combobox=QtGui.QComboBox() 
    self.fill_database_combobox()
    self.database_combobox.activated[int].connect( self.activated_database_combobox )
    self.dcw.dc.master().data().signal_database_list_changed.connect(  self.fill_database_combobox  )  
    self.layout.addWidget(self.database_combobox)

    self.cache_combobox=QtGui.QComboBox()
    self.available_cache_names=None #init in fill_combobox
    self.fill_cache_combobox()
    self.layout.addWidget(self.cache_combobox)

    self.antenna_combobox=QtGui.QComboBox() 
    self.fill_antenna_combobox()
    self.dcw.dc.master().selections().signal_selection_list_changed.connect(  self.fill_antenna_combobox  )  
    self.layout.addWidget(self.antenna_combobox)

    self.on_field_textbox=QtGui.QLineEdit()
    self.on_field_textbox.setText(field)
    self.layout.addWidget(self.on_field_textbox)      
    
    self.join_type_combobox=QtGui.QComboBox()
    for jt in self.dco.possible_types:      self.join_type_combobox.addItem(jt)
    self.join_type_combobox.setCurrentIndex( self.dco.possible_types.index(join_type) )
    self.layout.addWidget(self.join_type_combobox) 

    self.activated_type_combobox(  self.type_combobox.possible_values.index(target)  )  #this shows/hide the right stuff, sets text of self.

  def get_values_from_dco(self):
    """Useful to compute all necessary. 
    Returns dbname, field, target, join_type  extracted from current self.dco.parameters
    """
    x=self.dco.parameters if not self.dco.parameters is None else ''
    splt=x.split('@')   
    if   len(splt)==1:  join_type='left'
    elif len(splt)==2:  x,join_type=splt
    splt=x.split('&')
    if   len(splt)==1:   field='Node'; dbname=splt[0]
    elif len(splt)==2:   dbname,field=splt
    else:                raise Exception, "ERROR initiating DCOW_join!"
    if   dbname.startswith(':'): target='cache'   
    elif dbname.startswith('^'): target='antenna'
    else:                        target='database'; dbname='?'+dbname
    return     dbname[1:], field, target, join_type

  def save(self):
    field=str(self.on_field_textbox.text()).strip()
    if field: field='&'+field
    join_type=self.dco.possible_types[ self.join_type_combobox.currentIndex() ]

    if self.type_combobox.currentIndex()==1:  #cache
      db_name=':'+self.available_cache_names[ self.cache_combobox.currentIndex() ]
    elif self.type_combobox.currentIndex()==2:  #antenna      
      db_name='^'+self.dcw.dc.master().selections().get_available_node_selections()[ self.antenna_combobox.currentIndex() ]
    else: #database
      av_dfs=self.dcw.dc.get_available_databases()
      db_name=av_dfs[self.database_selection_index] if av_dfs else 'None'

    new_text=db_name+field
    if join_type!='left':  new_text+='@'+join_type   
    self.update_dco(new_text)

  def fill_database_combobox(self):  #slight modification of same method for DCOW_database
    dbname, _, _, _=self.get_values_from_dco()
    self.database_combobox.clear()
    available_dfs=self.dcw.dc.get_available_databases()
    self.database_selection_index=None
    for avdf_i, avdf in enumerate(available_dfs):  
      self.database_combobox.addItem(avdf)
      if avdf == dbname: self.database_selection_index=avdf_i
    if not available_dfs:     
      self.database_combobox.addItem('(No databases available)')
      self.database_combobox.model().item(0).setEnabled(False)
    if self.database_selection_index is None: self.database_selection_index=0
    self.database_combobox.insertSeparator(self.database_combobox.count())
    self.database_combobox.addItem('Load new data ...')
    self.database_combobox.setCurrentIndex(self.database_selection_index)

  def fill_cache_combobox(self):
    """This should be activated when the user clicks. Would need another model with a button, whose click trigger this on a invisible combobox """
    dbname, _, _, _=self.get_values_from_dco()
    self.cache_combobox.clear()
    available_cache_names=set()
    container=self.dco.container
    while not container is None:
      available_cache_names.update( container.caches )
      container=container.container
    self.available_cache_names=['None']+sorted(available_cache_names)
    for i, cache_name in enumerate(self.available_cache_names): 
      self.cache_combobox.addItem(cache_name)      
      if cache_name==dbname: self.cache_combobox.setCurrentIndex(i)

  def fill_antenna_combobox(self):
    """This should be activated when the user clicks. Would need another model with a button, whose click trigger this on a invisible combobox """
    dbname, _, _, _=self.get_values_from_dco()
    self.antenna_combobox.clear()
    possible_values=self.dcw.dc.master().selections().get_available_node_selections()
    #write(('FILL COMBOBOX', possible_values), 1, how='red')
    for i, antenna_name in enumerate(possible_values):      
      self.antenna_combobox.addItem(antenna_name)
      if antenna_name==dbname: self.antenna_combobox.setCurrentIndex(i)
 
  #totally copied same method for DCOW_database
  def activated_database_combobox(self, selection_index):   #dco_index should be always 0 for database
    av_dfs=self.dcw.dc.get_available_databases()
    if selection_index<len(av_dfs):  
      self.database_selection_index=selection_index # nothing to do until self.save() is called
    else:                            
      self.open_feature_loader()
      self.database_combobox.setCurrentIndex(self.database_selection_index)  #going back to previous item selected

  def activated_type_combobox(self, index):
    if   index==0: #db type selected
      self.database_combobox.setVisible(True)
      self.cache_combobox.setVisible(False)
      self.antenna_combobox.setVisible(False)
    elif index==1:        #cache 
      self.database_combobox.setVisible(False)
      self.cache_combobox.setVisible(True)
      self.antenna_combobox.setVisible(False)
    elif index==2:        #antenna
      self.database_combobox.setVisible(False)
      self.cache_combobox.setVisible(False)
      self.antenna_combobox.setVisible(True)
        
  def open_feature_loader(self):
    print 'Load new features!'  
    if self.dcw.dc.master().windows().has_window('FeatureLoader'): 
      self.dcw.dc.master().windows().get_window('FeatureLoader').activateWindow()
    else:
      loader=FeatureLoader(self.dcw.dc.master())
      loader.show()

class DCOW_append(DCOW):
  """ """
  def __init__(self, dcw, dco):
    super(DCOW_append, self).__init__(dcw, dco) #    QtGui.QWidget.__init__(self)  
    self.layout=QtGui.QVBoxLayout(); self.layout.setContentsMargins(0,0,0,0); self.layout.setSpacing(0)
    self.setLayout(self.layout)
    dbname, target, append_type=self.get_values_from_dco()

    row1=QtGui.QHBoxLayout(); row1.setContentsMargins(0,0,0,0); row1.setSpacing(0)
    row1.addWidget(QtGui.QLabel('append '))
    self.type_combobox=QtGui.QComboBox()
    self.type_combobox.possible_values=['database','cache','antenna']
    for i, possible_target in enumerate(self.type_combobox.possible_values): 
      self.type_combobox.addItem(possible_target)
      if possible_target==target: self.type_combobox.setCurrentIndex(i)
    self.type_combobox.activated[int].connect( self.activated_type_combobox )
    row1.addWidget(self.type_combobox)
    self.layout.addLayout(row1)

    self.database_combobox=QtGui.QComboBox() 
    self.fill_database_combobox()
    self.database_combobox.activated[int].connect( self.activated_database_combobox )
    self.dcw.dc.master().data().signal_database_list_changed.connect(  self.fill_database_combobox  )  
    self.layout.addWidget(self.database_combobox)

    self.cache_combobox=QtGui.QComboBox()
    self.available_cache_names=None #init in fill_combobox
    self.fill_cache_combobox()
    self.layout.addWidget(self.cache_combobox)

    self.antenna_combobox=QtGui.QComboBox() 
    self.fill_antenna_combobox()
    self.dcw.dc.master().selections().signal_selection_list_changed.connect(  self.fill_antenna_combobox  )  
    self.layout.addWidget(self.antenna_combobox)
   
    self.append_type_combobox=QtGui.QComboBox()
    for at in self.dco.possible_types:      self.append_type_combobox.addItem(at)
    self.append_type_combobox.setCurrentIndex( self.dco.possible_types.index(append_type) )
    self.layout.addWidget(self.append_type_combobox) 

    self.activated_type_combobox(  self.type_combobox.possible_values.index(target)  )  #this shows/hide the right stuff, sets text of self.

  def get_values_from_dco(self):
    """Useful to compute all necessary. 
    Returns dbname, target, append_type  extracted from current self.dco.parameters
    """
    dbname=self.dco.parameters if not self.dco.parameters is None else ''
    if dbname.endswith('@'):     append_type='bottom'
    else:                        append_type='top'; dbname=dbname+'?'
    if   dbname.startswith(':'): target='cache'   
    elif dbname.startswith('^'): target='antenna'
    else:                        target='database'; dbname='?'+dbname
    return     dbname[1:-1], target, append_type

  def save(self):
    append_type=self.dco.possible_types[ self.append_type_combobox.currentIndex() ]

    if self.type_combobox.currentIndex()==1:  #cache
      db_name=':'+self.available_cache_names[ self.cache_combobox.currentIndex() ]
    elif self.type_combobox.currentIndex()==2:  #antenna      
      db_name='^'+self.dcw.dc.master().selections().get_available_node_selections()[ self.antenna_combobox.currentIndex() ]
    else: #database
      av_dfs=self.dcw.dc.get_available_databases()
      db_name=av_dfs[self.database_selection_index] if av_dfs else 'None'

    new_text=db_name
    if append_type=='top':  new_text+='@'
    self.update_dco(new_text)

  def fill_database_combobox(self):  #slight modification of same method for DCOW_database
    dbname, _, _=self.get_values_from_dco()
    self.database_combobox.clear()
    available_dfs=self.dcw.dc.get_available_databases()
    self.database_selection_index=None
    for avdf_i, avdf in enumerate(available_dfs):  
      self.database_combobox.addItem(avdf)
      if avdf == dbname: self.database_selection_index=avdf_i
    if not available_dfs:     
      self.database_combobox.addItem('(No databases available)')
      self.database_combobox.model().item(0).setEnabled(False)
    if self.database_selection_index is None: self.database_selection_index=0
    self.database_combobox.insertSeparator(self.database_combobox.count())
    self.database_combobox.addItem('Load new data ...')
    self.database_combobox.setCurrentIndex(self.database_selection_index)

  def fill_cache_combobox(self):
    """This should be activated when the user clicks. Would need another model with a button, whose click trigger this on a invisible combobox """
    dbname, _, _=self.get_values_from_dco()
    self.cache_combobox.clear()
    available_cache_names=set()
    container=self.dco.container
    while not container is None:
      available_cache_names.update( container.caches )
      container=container.container
    self.available_cache_names=['None']+sorted(available_cache_names)
    for i, cache_name in enumerate(self.available_cache_names): 
      self.cache_combobox.addItem(cache_name)      
      if cache_name==dbname: self.cache_combobox.setCurrentIndex(i)

  def fill_antenna_combobox(self):
    """This should be activated when the user clicks. Would need another model with a button, whose click trigger this on a invisible combobox """
    dbname, _, _=self.get_values_from_dco()
    self.antenna_combobox.clear()
    possible_values=self.dcw.dc.master().selections().get_available_node_selections()
    #write(('FILL COMBOBOX', possible_values), 1, how='red')
    for i, antenna_name in enumerate(possible_values):      
      self.antenna_combobox.addItem(antenna_name)
      if antenna_name==dbname: self.antenna_combobox.setCurrentIndex(i)
 
  #totally copied same method for DCOW_database
  def activated_database_combobox(self, selection_index):   #dco_index should be always 0 for database
    av_dfs=self.dcw.dc.get_available_databases()
    if selection_index<len(av_dfs):  
      self.selection_index=selection_index # nothing to do until self.save() is called
    else:                            
      self.open_feature_loader()
      self.database_combobox.setCurrentIndex(self.selection_index)  #going back to previous item selected

  def activated_type_combobox(self, index):
    if   index==0: #db type selected
      self.database_combobox.setVisible(True)
      self.cache_combobox.setVisible(False)
      self.antenna_combobox.setVisible(False)
    elif index==1:        #cache 
      self.database_combobox.setVisible(False)
      self.cache_combobox.setVisible(True)
      self.antenna_combobox.setVisible(False)
    elif index==2:        #antenna
      self.database_combobox.setVisible(False)
      self.cache_combobox.setVisible(False)
      self.antenna_combobox.setVisible(True)
        
  def open_feature_loader(self):
    print 'Load new features!'  
    if self.dcw.dc.master().windows().has_window('FeatureLoader'): 
      self.dcw.dc.master().windows().get_window('FeatureLoader').activateWindow()
    else:
      loader=FeatureLoader(self.dcw.dc.master())
      loader.show()


class DCOW_select(DCOW):
  """ """
  def __init__(self, dcw, dco):
    super(DCOW_select, self).__init__(dcw, dco) #    QtGui.QWidget.__init__(self)  
    self.layout=QtGui.QVBoxLayout(); self.layout.setContentsMargins(0,0,0,0); self.layout.setSpacing(0)
    self.setLayout(self.layout)
    text=str(self.dco.parameters) if not self.dco.parameters is None else ''

    self.textbox= QtGui.QLineEdit(self)
    self.checkbox=QtGui.QCheckBox(self)
    self.checkbox.setText('include Node')

    self.invert_checkbox=QtGui.QCheckBox(self)
    self.invert_checkbox.setText('exclude these instead of select')
    if text.startswith('Node,'):  
      text=text[5:]
      self.checkbox.setChecked(True)
    if text.startswith('@'):  
      self.invert_checkbox.setChecked(True)
      text=text[1:]
    self.layout.addWidget(self.textbox)
    self.layout.addWidget(self.checkbox)
    self.layout.addWidget(self.invert_checkbox)

    self.textbox.setText(text)

  def save(self):
    new_text=str(self.textbox.text()).strip().strip(',').strip()
    new_text= ','.join([s.strip()   for s in new_text.split(',')])
    if self.checkbox.isChecked():         new_text='Node,'+new_text
    if self.invert_checkbox.isChecked():  new_text='@'+new_text
    if not new_text:    new_text=None
    self.update_dco(new_text)

class DCOW_simple_text_input(DCOW):
  """ """
  def __init__(self, dcw, dco):
    super(DCOW_simple_text_input, self).__init__(dcw, dco) #    QtGui.QWidget.__init__(self)  
    self.layout=QtGui.QVBoxLayout(); self.layout.setContentsMargins(0,0,0,0); self.layout.setSpacing(0)
    self.setLayout(self.layout)
    text=str(self.dco.parameters) if not self.dco.parameters is None else ''
    self.textbox= QtGui.QLineEdit(text, self)
    self.layout.addWidget(self.textbox)

  def save(self):
    new_text= str(self.textbox.text()).strip()
    if not new_text: new_text=None
    self.update_dco(new_text)

class DCOW_filter(DCOW_simple_text_input):   """ """
class DCOW_process(DCOW_simple_text_input):  """ """
class DCOW_compute(DCOW_simple_text_input):  """ """

class DCOW_pgls(DCOW): #_simple_text_input):     """ """  ## to be finished!
  def __init__(self, dcw, dco):
    super(DCOW_pgls, self).__init__(dcw, dco) #    QtGui.QWidget.__init__(self)  
    self.layout=QtGui.QVBoxLayout(); self.layout.setContentsMargins(0,0,0,0); self.layout.setSpacing(0)    
    self.setLayout(self.layout)
    p=self.dco.parameters if not self.dco.parameters is None else self.dco.default_dcow_parameters
    current_mode=p.split('mode=')[1]
    self.model_combobox=QtGui.QComboBox()
    for i, m in enumerate(self.dco.possible_values['mode']):
      desc=self.dco.descriptions['mode'][m]
      self.model_combobox.addItem(desc)
      if current_mode==m: self.model_combobox.setCurrentIndex(i)
    self.layout.addWidget(QtGui.QLabel("Evol. model:"))
    self.layout.addWidget(self.model_combobox)
    
  def save(self):
    new_text='mode='+self.dco.possible_values['mode'][ self.model_combobox.currentIndex() ]
    self.update_dco(new_text)   


class DCOW_trace(DCOW):
  """ """
  def __init__(self, dcw, dco):
    super(DCOW_trace, self).__init__(dcw, dco) #    QtGui.QWidget.__init__(self)  
    self.layout=QtGui.QVBoxLayout(); self.layout.setContentsMargins(0,0,0,0); self.layout.setSpacing(0)
    self.setLayout(self.layout)
    self.trace_procedure_combobox=QtGui.QComboBox()
    self.trace_procedure_combobox.possible_values=['None']+sorted(trace_procedures.keys())
    x=str(self.dco.parameters).split(':')[0]
    current_trace_procedure=x.rstrip('@') 
    for index, trace_procedure in enumerate(self.trace_procedure_combobox.possible_values):
      self.trace_procedure_combobox.addItem(trace_procedure)
      if trace_procedure==current_trace_procedure: self.trace_procedure_combobox.setCurrentIndex(index)
    self.layout.addWidget(self.trace_procedure_combobox)
    ### for multiple trees, need to add another box here
    self.append_checkbox=QtGui.QCheckBox()
    self.append_checkbox.setText('append to input')
    if not x.endswith('@'): self.append_checkbox.setChecked(True)
    self.layout.addWidget(self.append_checkbox)   
    
  def save(self):
    new_text=self.trace_procedure_combobox.possible_values[ self.trace_procedure_combobox.currentIndex() ]
    if not self.append_checkbox.isChecked(): new_text+='@'
    self.update_dco(new_text)   

class DCOW_rename(DCOW):
  """ """
  def __init__(self, dcw, dco):
    super(DCOW_rename, self).__init__(dcw, dco) #    QtGui.QWidget.__init__(self)  
    self.layout=QtGui.QVBoxLayout(); self.layout.setContentsMargins(0,0,0,0); self.layout.setSpacing(0)
    self.setLayout(self.layout)
    self.pairs=[]  # list of tuples of len 2; each object is a textbox
    input_text=self.dco.parameters or '='
    add_button=ToolButton('plus', 'Add a renaming item', lambda s:self.add_pair())
    self.layout.addWidget(add_button)
    for row_index, pair in enumerate(input_text.split(',')):
      newK,oldK= pair.split('=')
      self.add_pair(newK,oldK)

  def add_pair(self, newK='', oldK=''):
    #print 'add pair', oldK, newK, len(self.pairs)
    row_layout=QtGui.QHBoxLayout(); row_layout.setContentsMargins(0,0,0,0); row_layout.setSpacing(0)
    textbox1=QtGui.QLineEdit(oldK, self)
    label=QtGui.QLabel(' to ')
    textbox2=QtGui.QLineEdit(newK, self)
    row_layout.addWidget(textbox1);     row_layout.addWidget(label);     row_layout.addWidget(textbox2)
    self.pairs.append( [textbox1, textbox2] )
    if len(self.pairs)>1: #adding a button to remove a pair
      remove_button=ToolButton('remove', 'Remove this renaming item', lambda s,index=len(self.pairs)-1:self.remove_pair(index=index) )
      row_layout.addWidget(remove_button)
    self.layout.insertLayout( self.layout.count()-1, row_layout )

  def remove_pair(self, index):
    self.pairs.pop(index)
    clear_layout(self.layout, index=index)

  def save(self):
    tot_text=''
    for textbox1, textbox2 in self.pairs: 
      oldK= str(textbox1.text()).strip()
      newK= str(textbox2.text()).strip()
      if not oldK and not newK : continue
      if not oldK or not newK : raise Exception, "ERROR renaming fields cannot be left empty!"
      if not check_forbidden_characters(oldK) or not check_forbidden_characters(newK): 
          raise Exception, "ERROR one or more forbidden character detected in renaming fields!"
      tot_text+=newK+'='+oldK+','
    final=tot_text[:-1] if tot_text else None
    self.update_dco(final)

class DCOW_var(DCOW):
  """ """
  def __init__(self, dcw, dco):
    super(DCOW_var, self).__init__(dcw, dco) #    QtGui.QWidget.__init__(self)  
    self.layout=QtGui.QHBoxLayout(); self.layout.setContentsMargins(0,0,0,0); self.layout.setSpacing(2)
    self.setLayout(self.layout)
    x=self.dco.parameters    
    if not x:   var_name, value='', ''
    else:
      splt=x.split('=')
      var_name=splt[0]
      value=x[len(var_name)+1:]
    self.textbox1=QtGui.QLineEdit(var_name, self)
    self.textbox1.setMaximumWidth(60)
    self.textbox2=QtGui.QLineEdit(value, self)   
    self.textbox2.setMaximumWidth(120)
    self.layout.addWidget(QtGui.QLabel('$'))
    self.layout.addWidget(self.textbox1)
    self.layout.addWidget(QtGui.QLabel('='))
    self.layout.addWidget(self.textbox2)

  def save(self):
    new_text=  '{}={}'.format(  str(self.textbox1.text()).strip(),   str(self.textbox2.text()).strip()  )
    if len(new_text)==1: new_text=None
    self.update_dco(new_text)

class DCOW_aggregate(DCOW):
  """ """
  def __init__(self, dcw, dco):
    super(DCOW_aggregate, self).__init__(dcw, dco) #    QtGui.QWidget.__init__(self)  
    self.layout=QtGui.QVBoxLayout(); self.layout.setContentsMargins(0,0,0,0); self.layout.setSpacing(0)
    self.setLayout(self.layout)
    input_text=self.dco.parameters or '&'
    s, operation=input_text.split('&')
    fields=s.split(',')
    self.field_textboxes=[]
    self.field_layout=QtGui.QHBoxLayout(); self.field_layout.setContentsMargins(0,0,0,0); self.field_layout.setSpacing(0)
    self.field_layout.addWidget(QtGui.QLabel('Group by'))

    self.remove_button=ToolButton('remove', 'Remove last grouping field', self.remove_field)
    self.field_layout.addWidget(self.remove_button)
    self.remove_button.setVisible(False)

    self.add_button=ToolButton('plus', 'Add a grouping field', lambda s:self.add_field())
    self.field_layout.addWidget(self.add_button)

    for f in fields: self.add_field(f)
    self.operation_layout=QtGui.QHBoxLayout(); self.operation_layout.setContentsMargins(0,0,0,0); self.operation_layout.setSpacing(0)
    self.operation_layout.addWidget(QtGui.QLabel('& aggregate with'))
    self.operation_textbox=QtGui.QLineEdit(operation, self)
    self.operation_layout.addWidget(self.operation_textbox)
    self.layout.addLayout(self.field_layout)
    self.layout.addLayout(self.operation_layout)
    
  def add_field(self, field=''):
    nfields_already=len(self.field_textboxes)
    if nfields_already==1:       self.remove_button.setVisible(True)
    if nfields_already>0:
      comma=QtGui.QLabel(',')
      self.field_layout.insertWidget(self.field_layout.count()-2, comma)
    textbox=QtGui.QLineEdit(field, self)
    self.field_textboxes.append(textbox)
    self.field_layout.insertWidget(self.field_layout.count()-2, textbox)
    
  def remove_field(self):
    self.field_textboxes.pop()
    clear_layout(self.field_layout, index=self.field_layout.count()-3)  #textbox
    clear_layout(self.field_layout, index=self.field_layout.count()-3)  #comma
    if len(self.field_textboxes)==1: self.remove_button.setVisible(False)
    
  def save(self):
    text_fields=','.join([str(tb.text()).strip() for tb in self.field_textboxes])
    operation= str(self.operation_textbox.text()).strip()
    if( not text_fields and operation) or (text_fields and not operation):
      raise Exception, "ERROR group/aggregate fields cannot be left empty!"
    new_text=text_fields+'&'+operation if (text_fields and operation) else None
    self.update_dco(new_text)

class DCOW_database(DCOW):
  """ """
  def __init__(self, dcw, dco):
    super(DCOW_database, self).__init__(dcw, dco) #    QtGui.QWidget.__init__(self)  
    self.layout=QtGui.QVBoxLayout(); self.layout.setContentsMargins(0,0,0,0); self.layout.setSpacing(0)
    self.setLayout(self.layout)
    self.combobox=QtGui.QComboBox() ## !
    self.fill_combobox()
    self.layout.addWidget(self.combobox)
    self.combobox.activated[int].connect( lambda selection_index:self.activated_combobox(selection_index) )
    self.dcw.dc.master().data().signal_database_list_changed.connect(  self.fill_combobox  )  

  def fill_combobox(self):
    self.combobox.clear()
    available_dfs=self.dcw.dc.get_available_databases()
    self.selection_index=None
    for avdf_i, avdf in enumerate(available_dfs):  
      self.combobox.addItem(avdf)
      if avdf == self.dco.parameters: self.selection_index=avdf_i
    if not available_dfs:     
      self.combobox.addItem('(No databases available)')
      self.combobox.model().item(0).setEnabled(False)
    if self.selection_index is None: self.selection_index=0
    self.combobox.insertSeparator(self.combobox.count())
    self.combobox.addItem('Load new data ...')
    self.combobox.setCurrentIndex(self.selection_index)

  def activated_combobox(self, selection_index):   #dco_index should be always 0 for database
    av_dfs=self.dcw.dc.get_available_databases()
    if selection_index<len(av_dfs):  
      self.selection_index=selection_index # nothing to do until self.save() is called
    else:                            
      self.open_feature_loader()
      self.combobox.setCurrentIndex(self.selection_index)  #going back to previous item selected

  def open_feature_loader(self):
    print 'Load new features!'  
    if self.dcw.dc.master().windows().has_window('FeatureLoader'): 
      self.dcw.dc.master().windows().get_window('FeatureLoader').activateWindow()
    else:
      loader=FeatureLoader(self.dcw.dc.master())
      loader.show()

  def save(self):
    selection_index=self.selection_index
    av_dfs=self.dcw.dc.get_available_databases()
    dataframe_name=av_dfs[selection_index] if av_dfs else None
    self.update_dco(dataframe_name)


class DCOW_cache(DCOW):
  """ """
  def __init__(self, dcw, dco):
    super(DCOW_cache, self).__init__(dcw, dco) #    QtGui.QWidget.__init__(self)  
    self.layout=QtGui.QVBoxLayout(); self.layout.setContentsMargins(0,0,0,0); self.layout.setSpacing(0)
    self.setLayout(self.layout)
    text=str(self.dco.parameters) if not self.dco.parameters is None else ''
    self.textbox= QtGui.QLineEdit(text, self)
    self.layout.addWidget(self.textbox)

  def save(self):
    new_text= str(self.textbox.text()).strip()
    if not new_text: new_text=None
    #else:    new_text+='@master' ### debug
    self.update_dco(new_text)


class DCOW_retrieve(DCOW):
  """ """
  def __init__(self, dcw, dco):
    super(DCOW_retrieve, self).__init__(dcw, dco) #    QtGui.QWidget.__init__(self)  
    self.layout=QtGui.QVBoxLayout(); self.layout.setContentsMargins(0,0,0,0); self.layout.setSpacing(0)
    self.setLayout(self.layout)
    self.combobox=QtGui.QComboBox()
    self.layout.addWidget(self.combobox)
    self.available_cache_names=None #init in fill_combobox
    self.fill_combobox()

  def fill_combobox(self):
    """This should be activated when the user clicks. Would need another model with a button, whose click trigger this on a invisible combobox """
    self.combobox.clear()
    available_cache_names=set()
    container=self.dco.container
    while not container is None:
      available_cache_names.update( container.caches )
      container=container.container
    self.available_cache_names=['None']+sorted(available_cache_names)
    for i, cache_name in enumerate(self.available_cache_names): 
      self.combobox.addItem(cache_name)      
      if cache_name==str(self.dco.parameters): self.combobox.setCurrentIndex(i)

  def save(self):
    cache_name=self.available_cache_names[self.combobox.currentIndex()]  #may be 'None'
    self.update_dco(cache_name)

class DCOW_antenna(DCOW):
  """ """
  def __init__(self, dcw, dco):
    super(DCOW_antenna, self).__init__(dcw, dco) #    QtGui.QWidget.__init__(self)  
    self.layout=QtGui.QVBoxLayout(); self.layout.setContentsMargins(0,0,0,0); self.layout.setSpacing(0)
    self.setLayout(self.layout)
    self.combobox=QtGui.QComboBox() 
    self.fill_combobox()
    self.layout.addWidget(self.combobox)
    #self.combobox.activated[int].connect( lambda selection_index:self.activated_combobox(selection_index) )  ## no connection and no function since there's nothing to do until the DCO is saved
    self.dcw.dc.master().selections().signal_selection_list_changed.connect(   self.fill_combobox   )      

  def fill_combobox(self):
    self.combobox.clear()
    possible_values=self.dcw.dc.master().selections().get_available_node_selections()
    #write(('FILL COMBOBOX', possible_values), 1, how='red')
    for item in possible_values:      self.combobox.addItem(item)
    self.combobox.setCurrentIndex(  possible_values.index(self.dco.parameters)  )

  def save(self):
    selection_index=self.combobox.currentIndex()
    possible_values=self.dcw.dc.master().selections().get_available_node_selections()
    value=possible_values[selection_index]
    self.update_dco(value)

class DCOW_nodeFilter(DCOW):  
  """ """
  def __init__(self, dcw, dco):
    super(DCOW_nodeFilter, self).__init__(dcw, dco) #    QtGui.QWidget.__init__(self)  
    self.layout=QtGui.QVBoxLayout(); self.layout.setContentsMargins(0,0,0,0); self.layout.setSpacing(0)
    self.setLayout(self.layout)
    self.combobox=QtGui.QComboBox() 
    self.fill_combobox()
    self.layout.addWidget(self.combobox)
    self.ancestors_checkbox=QtGui.QCheckBox()
    self.ancestors_checkbox.setText('Use ancestors')
    btp=self.dco.backtrace_parameters(self.dco.parameters)
    if btp.startswith('@'):     self.ancestors_checkbox.setChecked(True)     
    if btp.endswith('^'):       self.ancestors_checkbox.setEnabled(False)
    self.layout.addWidget(self.ancestors_checkbox)

    #self.combobox.activated[int].connect( lambda selection_index:self.activated_combobox(selection_index) )  ## no connection and no function since there's nothing to do until the DCO is saved
    self.dcw.dc.master().selections().signal_selection_list_changed.connect(   self.fill_combobox   )      

  def fill_combobox(self):
    self.combobox.clear()
    possible_values=self.dcw.dc.master().selections().get_available_node_selections()
    #write(('FILL COMBOBOX', possible_values), 1, how='red')
    for item in possible_values:      self.combobox.addItem(item)
    current_selection_name=self.dco.backtrace_parameters(self.dco.parameters)
    if current_selection_name.startswith('@'):   current_selection_name=current_selection_name[1:]
    if current_selection_name.endswith('^'):     current_selection_name=current_selection_name[:-1]
    self.combobox.setCurrentIndex( possible_values.index(current_selection_name)  )

  def save(self):
    selection_index=self.combobox.currentIndex()
    possible_values=self.dcw.dc.master().selections().get_available_node_selections()
    value=possible_values[selection_index]
    if self.ancestors_checkbox.isChecked():     value='@'+value
    if not self.ancestors_checkbox.isEnabled(): value=value+'^'
    self.update_dco(value)


class DCOW_generator(DCOW):
  """ """
  def __init__(self, dcw, dco):
    super(DCOW_generator, self).__init__(dcw, dco) #    QtGui.QWidget.__init__(self)  
    self.layout=QtGui.QVBoxLayout(); self.layout.setContentsMargins(0,0,0,0); self.layout.setSpacing(0)
    self.setLayout(self.layout)
    row1=QtGui.QHBoxLayout(); row1.setContentsMargins(0,0,0,0); row1.setSpacing(2)
    row1.addWidget(QtGui.QLabel('N.rows'))
    self.nrows_textbox=QtGui.QLineEdit()
    row1.addWidget(self.nrows_textbox)
    self.layout.addLayout(row1)

    row2=QtGui.QHBoxLayout(); row2.setContentsMargins(0,0,0,0); row2.setSpacing(2)
    row2.addWidget(QtGui.QLabel('Columns'))
    self.cols_textbox=QtGui.QLineEdit()
    row2.addWidget(self.cols_textbox)
    self.layout.addLayout(row2)

    row3=QtGui.QHBoxLayout(); row3.setContentsMargins(0,0,0,0); row3.setSpacing(2)
    row3.addWidget(QtGui.QLabel('Fill'))
    self.fill_textbox=QtGui.QLineEdit()
    row3.addWidget(self.fill_textbox)
    self.fill_combobox=QtGui.QComboBox()
    self.fill_combobox.addItem('(float)')
    self.fill_combobox.addItem('(integer)')
    self.fill_combobox.addItem('(string)')
    row3.addWidget(self.fill_combobox)
    self.layout.addLayout(row3)

    if not self.dco.parameters is None:
      splt=self.dco.parameters.split('&')
      self.nrows_textbox.setText( splt[0] )
      self.cols_textbox.setText(  splt[1].lstrip('^')   )
      if len(splt)==3:
        f=splt[2]     
        if   f.startswith('^'): 
          f=f[1:]
          self.fill_combobox.setCurrentIndex(1)
        elif f.startswith('@'): 
          f=f[1:]
          self.fill_combobox.setCurrentIndex(2)         
        self.fill_textbox.setText(f)

  def save(self):    
    r=str(self.nrows_textbox.text()).strip()
    c=str(self.cols_textbox.text()).strip()
    try:    int(c); c='^'+c
    except: pass
    f=str(self.fill_textbox.text()).strip()
    if   f and self.fill_combobox.currentIndex()==1: f='^'+f #int
    elif f and self.fill_combobox.currentIndex()==2: f='@'+f #string     #else: float
    if f: f='&'+f
    new_text='{r}&{c}{f}'.format( r=r, c=c, f=f )
    self.update_dco(new_text)

class DCOW_add_column(DCOW):
  """ """
  def __init__(self, dcw, dco):
    super(DCOW_add_column, self).__init__(dcw, dco) #    QtGui.QWidget.__init__(self)  
    self.layout=QtGui.QVBoxLayout(); self.layout.setContentsMargins(0,0,0,0); self.layout.setSpacing(0)
    self.setLayout(self.layout)
    row1=QtGui.QHBoxLayout(); row1.setContentsMargins(0,0,0,0); row1.setSpacing(2)
    row1.addWidget(QtGui.QLabel('Column name'))
    self.colname_textbox=QtGui.QLineEdit()
    row1.addWidget(self.colname_textbox)
    self.layout.addLayout(row1)

    row2=QtGui.QHBoxLayout(); row2.setContentsMargins(0,0,0,0); row2.setSpacing(2)
    row2.addWidget(QtGui.QLabel('Value'))
    self.value_textbox=QtGui.QLineEdit()
    row2.addWidget(self.value_textbox)
    self.type_combobox=QtGui.QComboBox()
    self.type_combobox.addItem('(float)')
    self.type_combobox.addItem('(integer)')
    self.type_combobox.addItem('(string)')
    row2.addWidget(self.type_combobox)
    self.layout.addLayout(row2)

    if not self.dco.parameters is None:
      splt=self.dco.parameters.split('=')
      self.colname_textbox.setText( splt[0] )
      f=splt[1]     
      if   f.startswith('^'): 
        f=f[1:]
        self.type_combobox.setCurrentIndex(1)
      elif f.startswith('@'): 
        f=f[1:]
        self.type_combobox.setCurrentIndex(2)         
      self.value_textbox.setText(f)

  def save(self):    
    c=str(self.colname_textbox.text()).strip()
    f=str(self.value_textbox.text()).strip()
    if   f and self.type_combobox.currentIndex()==1: f='^'+f #int
    elif f and self.type_combobox.currentIndex()==2: f='@'+f #string     #else: float
    if not c: new_text=None
    else:     new_text='{c}={f}'.format( c=c, f=f )
    self.update_dco(new_text)


class DCOW_column_transform(DCOW):
  """ Mother class for DCOW implementing any DCOs that are subclasses of DCO_column_transform"""
  def __init__(self, dcw, dco):
    super(DCOW_column_transform, self).__init__(dcw, dco) #    QtGui.QWidget.__init__(self)  
    self.layout=QtGui.QVBoxLayout(); self.layout.setContentsMargins(0,0,0,0); self.layout.setSpacing(0)
    self.setLayout(self.layout)

  def add_fixed_part(self):
    subclass_params, colspec, prefix, suffix, r_or_a = self.split_parameters()
    row1=QtGui.QHBoxLayout(); row1.setContentsMargins(0,0,0,0); row1.setSpacing(0)
    self.column_selector_combobox=QtGui.QComboBox()
    self.column_selector_combobox.possible_values=[ [typeflag, 'All '+DCO_typecheck.type_descriptions[typeflag]+' columns' ]        for typeflag in self.dco.accepted_types ]    
    self.column_selector_combobox.possible_values.insert(0, ['!', 'Specify columns: '])
    self.column_selector_textbox=QtGui.QLineEdit()
    if colspec.endswith('^'):  
      colspec=colspec.rstrip('^')
      self.column_selector_combobox.setEnabled(False)
      self.column_selector_textbox.setEnabled(False)
    for i, (flag,desc) in enumerate(self.column_selector_combobox.possible_values): 
      self.column_selector_combobox.addItem(desc)
      if '@'+flag==colspec: self.column_selector_combobox.setCurrentIndex(i)
    self.column_selector_combobox.activated[int].connect(self.activated_column_selector_combobox)
    row1.addWidget(self.column_selector_combobox)
    row1.addWidget(self.column_selector_textbox)
    self.column_selector_textbox.setVisible(False)
    if not colspec.startswith('@'): 
      self.column_selector_textbox.setText(colspec)  
      self.column_selector_textbox.setVisible(True)    
    row1.addStretch()
    self.layout.addLayout(row1)

    row2=QtGui.QHBoxLayout(); row2.setContentsMargins(0,0,0,0); row2.setSpacing(0)
    if prefix.endswith('^') and suffix.endswith('^'): row2.setEnabled(False)
    row2.addWidget(QtGui.QLabel('Rename to '))
    self.prefix_texbox=QtGui.QLineEdit()
    if prefix.endswith('^'):  
      prefix=prefix.rstrip('^')
      self.prefix_texbox.setEnabled(False)
    self.prefix_texbox.setText(prefix)
    self.prefix_texbox.setMaximumWidth(45)
    row2.addWidget(self.prefix_texbox)
    row2.addWidget(QtGui.QLabel('<name>'))

    self.suffix_texbox=QtGui.QLineEdit()
    if suffix.endswith('^'):  
      suffix=suffix.rstrip('^')
      self.suffix_texbox.setEnabled(False)
    self.suffix_texbox.setText(suffix)
    self.suffix_texbox.setMaximumWidth(45)
    row2.addWidget(self.suffix_texbox)
    row2.addStretch()
    self.layout.addLayout(row2)

    row3=QtGui.QHBoxLayout(); row3.setContentsMargins(0,0,0,0); row3.setSpacing(0)
    row3.addWidget(QtGui.QLabel('Columns are '))
    self.replace_combobox=QtGui.QComboBox()
    self.replace_combobox.possible_values=[['r', 'replaced'], ['a', 'added']]
    if r_or_a.endswith('^'):  
      r_or_a=r_or_a.rstrip('^')
      self.replace_combobox.setEnabled(False)
      row3.setEnabled(False)
    for i, (flag,desc) in enumerate(self.replace_combobox.possible_values): 
      self.replace_combobox.addItem(desc)
      if flag==r_or_a: self.replace_combobox.setCurrentIndex(i)
    row3.addWidget(self.replace_combobox)
    row3.addStretch()
    self.layout.addLayout(row3)

  def activated_column_selector_combobox(self, index):
    if index==0:   self.column_selector_textbox.setVisible(True)
    else:          self.column_selector_textbox.setVisible(False)

  def split_parameters(self):
    """ returns  subclass_params, col_spec, prefix, suffix, r_or_a   """
    p=self.dco.parameters     if not self.dco.parameters is None else self.dco.default_dcow_parameters
    subclass_params, col_spec, rename_specs, r_or_a= p.split('|')
    prefix, suffix=rename_specs.split('@')
    return  subclass_params, col_spec, prefix, suffix, r_or_a

  def save(self):
    new_text='{sp}|{cols}|{pre}@{suff}|{r}'.format(sp=self.get_subclass_params(),  \
      cols=','.join([i.strip() for i in str(self.column_selector_textbox.text()).strip().split(',')]) +('' if self.column_selector_textbox.isEnabled() else '^')\
      if self.column_selector_combobox.currentIndex()==0 else '@'+self.column_selector_combobox.possible_values[self.column_selector_combobox.currentIndex()][0],
      pre=str(self.prefix_texbox.text())                                                 + ('' if self.prefix_texbox.isEnabled() else '^'),
      suff=str(self.suffix_texbox.text())                                                + ('' if self.suffix_texbox.isEnabled() else '^'),
      r=self.replace_combobox.possible_values[self.replace_combobox.currentIndex()][0]   + ('' if self.replace_combobox.isEnabled() else '^')   )
    self.update_dco(new_text)

  def get_subclass_params(self): return ''

class DCOW_log(DCOW_column_transform):
  def __init__(self, dcw, dco):
    super(DCOW_log, self).__init__(dcw, dco) 
    my_params, _, _, _, _ = self.split_parameters()
    row0=QtGui.QHBoxLayout(); row0.setContentsMargins(0,0,0,0); row0.setSpacing(0)
    row0.addWidget(QtGui.QLabel('Logarithm base:'))
    self.logbase_textbox=QtGui.QLineEdit(my_params)
    row0.addWidget(self.logbase_textbox)
    self.logbase_textbox.setMaximumWidth(25)
    row0.addStretch()
    self.layout.addLayout(row0)
    self.add_fixed_part()    

  def get_subclass_params(self): return str(self.logbase_textbox.text()).strip()

class DCOW_scale(DCOW_column_transform):
  def __init__(self, dcw, dco):
    super(DCOW_scale, self).__init__(dcw, dco) 
    my_params, _, _, _, _ = self.split_parameters()
    min_in, max_in, min_out, max_out=my_params.split(':')

    row0a=QtGui.QHBoxLayout(); row0a.setContentsMargins(0,0,0,0); row0a.setSpacing(0)
    row0a.addWidget(QtGui.QLabel('minimum'))
    self.layout.addLayout(row0a)
    rowa=QtGui.QHBoxLayout(); rowa.setContentsMargins(0,0,0,0); rowa.setSpacing(0)
    rowa.addWidget(QtGui.QLabel('   In:'))
    self.min_in_checkbox=QtGui.QCheckBox()
    self.min_in_checkbox.setText('auto')
    rowa.addWidget(self.min_in_checkbox)
    self.min_in_textbox=QtGui.QLineEdit()
    rowa.addWidget(self.min_in_textbox)
    self.min_in_textbox.setMaximumWidth(25)
    if min_in.endswith('^'): 
      min_in=min_in.rstrip('^')
      self.min_in_textbox.setEnabled(False)
      self.min_in_checkbox.setEnabled(False)
    if min_in=='@': 
      self.min_in_checkbox.setChecked(True)
      self.min_in_textbox.setVisible(False)
    else: 
      self.min_in_textbox.setText(min_in)
    self.min_in_checkbox.stateChanged.connect(self.clicked_min_in_checkbox)

    rowa.addSpacing(12)
    rowa.addWidget(QtGui.QLabel('Out:'))
    self.min_out_textbox=QtGui.QLineEdit()
    self.min_out_textbox.setMaximumWidth(25)
    if min_out.endswith('^'): 
      min_out=min_out.rstrip('^')
      self.min_out_textbox.setEnabled(False)
    self.min_out_textbox.setText(min_out)
    rowa.addWidget(self.min_out_textbox)
    rowa.addStretch()
    self.layout.addLayout(rowa)


    row0b=QtGui.QHBoxLayout(); row0b.setContentsMargins(0,0,0,0); row0b.setSpacing(0)
    row0b.addWidget(QtGui.QLabel('maximum'))
    self.layout.addLayout(row0b)
    rowb=QtGui.QHBoxLayout(); rowb.setContentsMargins(0,0,0,0); rowb.setSpacing(0)
    rowb.addWidget(QtGui.QLabel('   In:'))
    self.max_in_checkbox=QtGui.QCheckBox()
    self.max_in_checkbox.setText('auto')
    rowb.addWidget(self.max_in_checkbox)
    self.max_in_textbox=QtGui.QLineEdit()
    rowb.addWidget(self.max_in_textbox)
    self.max_in_textbox.setMaximumWidth(25)
    if max_in.endswith('^'): 
      max_in=max_in.rstrip('^')
      self.max_in_textbox.setEnabled(False)
      self.max_in_checkbox.setEnabled(False)
    if max_in=='@': 
      self.max_in_checkbox.setChecked(True)
      self.max_in_textbox.setVisible(False)
    else: 
      self.max_in_textbox.setText(max_in)
    self.max_in_checkbox.stateChanged.connect(self.clicked_max_in_checkbox)

    rowb.addSpacing(12)
    rowb.addWidget(QtGui.QLabel('Out:'))
    self.max_out_textbox=QtGui.QLineEdit()
    self.max_out_textbox.setMaximumWidth(25)
    if max_out.endswith('^'): 
      max_out=max_out.rstrip('^')
      self.max_out_textbox.setEnabled(False)
    self.max_out_textbox.setText(max_out)
    rowb.addWidget(self.max_out_textbox)
    rowb.addStretch()
    self.layout.addLayout(rowb)

    self.add_fixed_part()    


  def clicked_min_in_checkbox(self, s):    self.min_in_textbox.setVisible(not s)
  def clicked_max_in_checkbox(self, s):    self.max_in_textbox.setVisible(not s)

  def get_subclass_params(self): 
    min_in=('@' if self.min_in_checkbox.isChecked() else str(self.min_in_textbox.text()).strip()) + ('' if self.min_in_textbox.isEnabled() else '^')
    max_in=('@' if self.max_in_checkbox.isChecked() else str(self.max_in_textbox.text()).strip()) + ('' if self.max_in_textbox.isEnabled() else '^')
    min_out=str(self.min_out_textbox.text()).strip()   + ('' if self.min_out_textbox.isEnabled() else '^')
    max_out=str(self.max_out_textbox.text()).strip()   + ('' if self.max_out_textbox.isEnabled() else '^')
    return '{}:{}:{}:{}'.format(min_in, max_in, min_out, max_out)

class DCOW_treeInfo(DCOW):
  """ """
  def __init__(self, dcw, dco):
    super(DCOW_treeInfo, self).__init__(dcw, dco) #    QtGui.QWidget.__init__(self)  
    self.layout=QtGui.QVBoxLayout(); self.layout.setContentsMargins(0,0,0,0); self.layout.setSpacing(0)
    self.setLayout(self.layout)
    self.tree_combobox=QtGui.QComboBox()
    self.fill_tree_combobox()
    self.dcw.dc.master().trees().signal_tree_list_changed.connect(self.fill_tree_combobox)    
    self.layout.addWidget(self.tree_combobox)
    self.what_combobox=QtGui.QComboBox()
    current_what=self.dco.parameters.split(':')[0]  if not self.dco.parameters is None else  None
    for i,what in enumerate(self.dco.possible_values):
      self.what_combobox.addItem(what)
      if what==current_what:           self.what_combobox.setCurrentIndex(i)      
    self.layout.addWidget(self.what_combobox)    

  def fill_tree_combobox(self):
    if self.dco.parameters is None or not self.dco.parameters.count(':'):    current_tree_name=self.dcw.dc.master().trees().default_tree.tree_name
    else:                                                                    current_tree_name=self.dco.parameters.split(':')[-1]
    for i, tree_name in enumerate(self.dcw.dc.master().trees().get_available_trees()):
      self.tree_combobox.addItem(tree_name)
      if tree_name==current_tree_name: self.tree_combobox.setCurrentIndex(i)
    self.tree_combobox.setEnabled(False) ### to be removed when multiple trees will be supported

  def save(self):
    what=self.dco.possible_values[ self.what_combobox.currentIndex() ]
    tree_name=self.dcw.dc.master().trees().get_available_trees()[ self.tree_combobox.currentIndex() ]
    if tree_name==self.dcw.dc.master().trees().default_tree.tree_name:   tree_name=''
    else:   tree_name=':'+tree_name
    new_text=what+tree_name
    self.update_dco(new_text)


class DCOW_call(DCOW):
  """ """
  def __init__(self, dcw, dco):
    super(DCOW_call, self).__init__(dcw, dco) #    QtGui.QWidget.__init__(self)  
    self.layout=QtGui.QVBoxLayout(); self.layout.setContentsMargins(0,0,0,0); self.layout.setSpacing(0)
    self.setLayout(self.layout)
    self.combobox=QtGui.QComboBox()
    self.layout.addWidget(self.combobox)
    self.available_define_names=None #init in fill_combobox
    self.fill_combobox()

  def fill_combobox(self):
    """This should be activated when the user clicks. Would need another model with a button, whose click trigger this on a invisible combobox """
    self.combobox.clear()
    available_define_names=set()
    container=self.dco.container
    while not container is None:
      available_define_names.update( container.defines )
      container=container.container
    self.available_define_names=['None']+sorted(available_define_names)
    for i, define_name in enumerate(self.available_define_names): 
      self.combobox.addItem(define_name)      
      if define_name==str(self.dco.parameters): self.combobox.setCurrentIndex(i)

  def save(self):
    define_name=self.available_define_names[self.combobox.currentIndex()]  #may be 'None'
    self.update_dco(define_name)


class DCOW_group(DCOW):
  def __init__(self, dcw, dco):
    super(DCOW_group, self).__init__(dcw, dco) #    QtGui.QWidget.__init__(self)  
    self.layout=QtGui.QHBoxLayout(); self.layout.setContentsMargins(1,1,1,1); self.layout.setSpacing(5)
    self.setLayout(self.layout)
    write('INIT dcow_{} "{}"'.format(self.dco.name, self.dco.parameters), 1, how='magenta')
    group_name=self.dco.group_name   #self.dco.parameters[ : self.dco.parameters.index('[') ] if self.dco.parameters else ''
    if not self.dco.group_name_in_progress is None:
      group_name=self.dco.group_name_in_progress
    self.textbox=QtGui.QLineEdit(group_name, self)
    self.textbox.editingFinished.connect(self.edited_textbox)
    self.textbox.setMaximumWidth(100)
    self.layout.addWidget(self.textbox)
    dcw=DataChannelWidget(self.dco) #self.clipboard_dc)
    self.layout.addWidget(dcw)

  def edited_textbox(self): 
    print 'edited textbox'
    txt=str(self.textbox.text()).strip()
    self.dco.group_name_in_progress=txt     

  def save(self):
    self.dco.group_name_in_progress=None
    name= str(self.textbox.text()).strip()
    k=self.dco.key()  # key of the DC internal to this group 
    k_no_name=k[k.index('['):]   #this includes [ and ]
    new_text='{n}{k}'.format(k=k_no_name, n=name)
    if not new_text:      new_text=None
    self.update_dco(new_text)

class DCOW_define(DCOW_group):
  """ """

class DCOW_color(DCOW):
  """ """
  def __init__(self, dcw, dco):
    super(DCOW_color, self).__init__(dcw, dco) #    QtGui.QWidget.__init__(self)  
    self.layout=QtGui.QVBoxLayout(); self.layout.setContentsMargins(0,0,0,0); self.layout.setSpacing(0)
    self.setLayout(self.layout)
    
    self.type_combobox=QtGui.QComboBox()
    self.type_combobox.possible_values=[('f', 'fixed'), ('g', 'gradient'), ('m', 'colormap')]
    for i, (code, desc) in enumerate(self.type_combobox.possible_values):  
      self.type_combobox.addItem(desc)
      if not self.dco.parameters is None and self.dco.parameters.startswith(code): 
        self.type_combobox.setCurrentIndex(i)      
    self.type_combobox.activated.connect(self.update_visibles)
    self.layout.addWidget(self.type_combobox)

    # gradient part
    row1=QtGui.QHBoxLayout();     row1.setContentsMargins(0,0,0,0);    row1.setSpacing(0)
    self.column_label=QtGui.QLabel('column:')
    row1.addWidget(self.column_label)
    self.column_textbox=QtGui.QLineEdit()
    self.column_textbox.setMaximumWidth(100)
    row1.addWidget(self.column_textbox)
    row1.addStretch()
    self.layout.addLayout(row1)
    row2=QtGui.QHBoxLayout();     row2.setContentsMargins(0,0,0,0);    row2.setSpacing(0)
    self.gradient_widget=TreedexGradientEditor(parent=self)# , self.edited_gradient)
    row2.addWidget(self.gradient_widget)
    #row2.addStretch()
    self.layout.addLayout(row2)
    row3=QtGui.QHBoxLayout();     row3.setContentsMargins(0,0,0,0);    row3.setSpacing(0)
    self.default_color_label=QtGui.QLabel('missing data:')
    row3.addWidget(self.default_color_label)
    self.default_color_selector=TreedexColorButton()    
    row3.addWidget(self.default_color_selector)
    row3.addStretch()
    self.layout.addLayout(row3)
    
    # fixed color part
    row4=QtGui.QHBoxLayout();     row4.setContentsMargins(0,0,0,0);    row4.setSpacing(0)
    self.fixed_label=QtGui.QLabel('color:')
    row4.addWidget(self.fixed_label)
    self.fixed_color_selector=TreedexColorButton()    
    row4.addWidget(self.fixed_color_selector)
    self.layout.addLayout(row4)

    # colormap part
    row5=QtGui.QHBoxLayout();     row5.setContentsMargins(0,0,0,0);    row5.setSpacing(0) 
    self.colormap_label=QtGui.QLabel('name:')
    row5.addWidget(self.colormap_label)
    self.colormap_combobox=QtGui.QComboBox()
    self.dcw.dc.master().colors().signal_colormap_list_changed.connect(self.fill_colormap_combobox)
    self.fill_colormap_combobox()
    row5.addWidget(self.colormap_combobox)
    self.layout.addLayout(row5)    
  
    #update to current values of self.dco, both visible state and colors and knobs etc
    self.update_visibles()
    if not self.dco.parameters is None:
      pam=self.dco.backtrace_parameters(self.dco.parameters)
      if   pam.startswith('g'):
          cs=pam[2:]
          splt=cs.split('@')
          if len(splt)==2:     column=splt[0];        s=splt[1]
          else:                column='';             s=splt[0]
          splt=s.split(';')
          s=splt[0]    
          if len(splt)==2:     default_color=splt[1]
          else:                default_color=self.dcw.dc.master().colors().get_default_color()
          self.column_textbox.setText(column)
          self.gradient_widget.load_colorspace(s)
          self.default_color_selector.load_color(default_color)
      elif pam.startswith('f'):
          c=pam[2:]
          self.fixed_color_selector.load_color(c)
      else:  pass # nothing to do here since fill_colormap_combobox already took care of this

  def fill_colormap_combobox(self):
    self.colormap_combobox.clear()
    current_colormap=None if (self.dco.parameters is None or not self.dco.parameters.startswith('m')) else self.dco.parameters[2:]
    for i, colormap_name in enumerate(self.dcw.dc.master().colors().get_available_colormaps()):
      self.colormap_combobox.addItem(colormap_name)
      if colormap_name==current_colormap:  self.colormap_combobox.setCurrentIndex(i)

  def update_visibles(self):
    """ Note: reads self.type_combobox.currentIndex()  ; it will restore values in self.dco.parameters if they match the current type"""
    if   self.type_combobox.currentIndex()==0:
        self.column_textbox.setVisible(False)
        self.gradient_widget.setVisible(False)
        self.default_color_label.setVisible(False)
        self.default_color_selector.setVisible(False)
        self.column_label.setVisible(False)
        self.fixed_label.setVisible(True)
        self.fixed_color_selector.setVisible(True)
        self.colormap_label.setVisible(False)
        self.colormap_combobox.setVisible(False)

    elif self.type_combobox.currentIndex()==1:
        self.column_textbox.setVisible(True)
        self.gradient_widget.setVisible(True)
        self.default_color_label.setVisible(True)
        self.default_color_selector.setVisible(True)
        self.column_label.setVisible(True)
        self.fixed_label.setVisible(False)
        self.fixed_color_selector.setVisible(False)
        self.colormap_label.setVisible(False)
        self.colormap_combobox.setVisible(False)

    elif self.type_combobox.currentIndex()==2:        
        self.column_textbox.setVisible(False)
        self.gradient_widget.setVisible(False)
        self.default_color_label.setVisible(False)
        self.default_color_selector.setVisible(False)
        self.column_label.setVisible(False)
        self.fixed_label.setVisible(False)
        self.fixed_color_selector.setVisible(False)
        self.colormap_label.setVisible(True)
        self.colormap_combobox.setVisible(True)

      
  def save(self):
    if   self.type_combobox.currentIndex()==0:
      new_text='f|{c}'.format(c=self.fixed_color_selector.get_color())
    elif self.type_combobox.currentIndex()==1:
      colorspace=self.gradient_widget.get_colorspace()
      column_name=str(self.column_textbox.text()).strip()
      if column_name: column_name+='@'
      default_color=self.default_color_selector.get_color()
      new_text='g|{column}{colorspace};{defcolor}'.format(column=column_name, colorspace=colorspace, defcolor=default_color)
    elif self.type_combobox.currentIndex()==2:
      new_text='m|{}'.format( self.dcw.dc.master().colors().get_available_colormaps() [self.colormap_combobox.currentIndex()] ) 
    self.update_dco(new_text)


class TreedexColorButton(pg.ColorButton):
  """ Simply a colored box; upon click, it opens a window with a nice color picker palette (colorDialog)
    You can use its sigColorChanged signal; then use get_color() ;  similarly there's a load_color('RRGGBB')
"""
  def __init__(self): #, *args, **kargs):
    super(TreedexColorButton, self).__init__() #*args, **kargs)
    self.colorDialog.setOption(QtGui.QColorDialog.ShowAlphaChannel, False)
    self.setMinimumHeight(20);    self.setMaximumHeight(20)
    self.setMinimumWidth(28);     self.setMaximumWidth(28)
    self.setSizePolicy(fixed_size_policy)


  def get_color(self):
    r,g,b,_=self.color(mode='byte')
    return '{r:02X}{g:02X}{b:02X}'.format(r=r, g=g, b=b)

  def load_color(self,c): 
    r=int(c[:2],  16)
    g=int(c[2:4], 16)
    b=int(c[4:],  16)
    self.setColor( (r,g,b,255) )

class TreedexGradientEditor(pg.GradientWidget):
  def __init__(self, parent, fn_triggered=None): #, *args, **kargs):
    #h=40; 
    w=320
    super(TreedexGradientEditor, self).__init__() #*args, **kargs)
    self.parent=parent
    self.item.colorDialog.setOption(QtGui.QColorDialog.ShowAlphaChannel, False)
    #self.setMinimumHeight(h);    self.setMaximumHeight(h)
    self.setMinimumWidth(w);     self.setMaximumWidth(w)
    self.setSizePolicy(fixed_size_policy)

    if not fn_triggered is None:
      self.sigGradientChangeFinished.connect(fn_triggered)
      self.rgbAction.triggered.connect(      fn_triggered) 
      self.hsvAction.triggered.connect(      fn_triggered) 

  def get_colorspace(self):
    """Input is what is returned by pyqtgraph.graphicsItems.GradientEditorItem.GradientEditorItem.saveState()
      that is to say something like:   {'ticks': [(0, (0, 0, 0, 255)), (0.13563402889245585, (9, 39, 34, 255)), 
                                          (0.3635634028892456, (39, 33, 33, 255)), (0.884430176565008, (255, 0, 0, 255))], 'mode': 'hsv'}
     Output is colorspace: r0.0:rrggbb,0.556:rrggbb,1.000:rrggbb
     Note that input contain alpha, but this is dropped""" 
    s=self.item.saveState()
    s['ticks'].sort(key=lambda x:x[0]) 
    return ('r' if s['mode']=='rgb' else 'h') + \
      ','.join(   ['{p}:{r:02X}{g:02X}{b:02X}'.format(p=round(p,3),r=r,g=g,b=b)  for p,(r,g,b,_) in s['ticks']]    )

  def load_colorspace(self, cs):
    mode={'r':'rgb', 'h':'hsv'}[cs[0]]
    state={'mode':mode, 'ticks':[]}
    for block in cs[1:].split(','):
      splt=block.split(':')
      pos=float(splt[0])
      r=int(splt[1][:2],  16)
      g=int(splt[1][2:4], 16)
      b=int(splt[1][4:],  16)
      state['ticks'].append([pos, [r,g,b,255]])  #255 is for alpha   
    self.restoreState(state)

    
class DCOW_window(DCOW):
  def __init__(self, dcw, dco):
    super(DCOW_window, self).__init__(dcw, dco) #    QtGui.QWidget.__init__(self)  
    self.layout=QtGui.QVBoxLayout(); self.layout.setContentsMargins(0,0,0,0); self.layout.setSpacing(0)
    self.setLayout(self.layout)
    text=    self.dco.backtrace_parameters(   str(self.dco.parameters) if not self.dco.parameters is None else '' )
    self.textbox= QtGui.QLineEdit(text, self)
    self.layout.addWidget(self.textbox)
    activate_window_button=QtGui.QPushButton('Show window')
    activate_window_button.clicked.connect(  lambda s:self.dco.window_link.activateWindow()  )
    row_layout=QtGui.QHBoxLayout(); row_layout.setContentsMargins(0,0,0,0); row_layout.setSpacing(0)
    row_layout.addStretch()
    row_layout.addWidget(activate_window_button)
    row_layout.addStretch()   
    self.layout.addLayout(row_layout)

  def save(self):
    new_text= str(self.textbox.text()).strip()
    if not new_text: new_text=None
    self.update_dco(new_text)

class DCOW_table(DCOW_window): 
  """ """
class DCOW_scatterplot(DCOW_window): 
  """ """
class DCOW_plot3D(DCOW_window): 
  """ """

class DCOW_send_to_plot(DCOW):
  """ """
  def __init__(self, dcw, dco):
    super(DCOW_send_to_plot, self).__init__(dcw, dco) #    QtGui.QWidget.__init__(self)  
    self.layout=QtGui.QVBoxLayout(); self.layout.setContentsMargins(0,0,0,0); self.layout.setSpacing(0)
    self.setLayout(self.layout)
    var_name, _=self.dco.parameters.split('@') if self.dco.parameters else ('','')
    text=var_name
    row1=QtGui.QHBoxLayout(); row1.setContentsMargins(0,0,0,0); row1.setSpacing(0)
    row1.addWidget(QtGui.QLabel('send as '))
    self.cache_name_textbox=QtGui.QLineEdit(text, self)
    self.cache_name_textbox.ever_edited=False
    self.cache_name_textbox.textEdited.connect( lambda s: self.cache_name_textbox_was_edited )
    row1.addWidget(self.cache_name_textbox)
    self.layout.addLayout(row1)
    row2=QtGui.QHBoxLayout(); row2.setContentsMargins(0,0,0,0); row2.setSpacing(0)
    row2.addWidget(QtGui.QLabel('to '))
    self.window_combobox=QtGui.QComboBox()
    self.window_combobox.activated.connect(self.auto_set_var_name)
    self.fill_combobox()
    row2.addWidget(self.window_combobox)
    self.layout.addLayout(row2)
    self.auto_set_var_name()
    self.dcw.dc.master().windows().signal_window_list_changed.connect(self.fill_combobox)

  def cache_name_textbox_was_edited(self, s):    self.cache_name_textbox.ever_edited=True

  def fill_combobox(self):
    _, window_name=self.dco.parameters.split('@') if self.dco.parameters else ('','')
    for i, avail_win_name in enumerate(self.dcw.dc.master().windows().plot_window_list()):
      self.window_combobox.addItem(avail_win_name)
      if avail_win_name==window_name: self.window_combobox.setCurrentIndex(i)
    if not self.window_combobox.count(): 
      self.window_combobox.addItem('No plot available')
      self.window_combobox.setEnabled(False)
    else:       self.window_combobox.setEnabled(True)


  def auto_set_var_name(self):
    if not self.cache_name_textbox.ever_edited: 
      windows=self.dcw.dc.master().windows().plot_window_list()
      if not windows: return 
      win_name=windows[ self.window_combobox.currentIndex() ]
      win=self.dcw.dc.master().windows().get_window(win_name)
      container=win.dco_link
      index=1
      var_name='Input{}'.format(index)
      while container.has_cache(var_name):
        index+=1
        var_name='Input{}'.format(index)
      self.cache_name_textbox.setText(var_name)

  def save(self):
    windows=self.dcw.dc.master().windows().plot_window_list()      
    if not windows:  new_text=None
    else:            new_text= '{v}@{w}'.format(v=str(self.cache_name_textbox.text()).strip(), w=windows[ self.window_combobox.currentIndex() ])
    self.update_dco(new_text)


DCO_categories=[ ['Start', ['database', 'antenna', 'generator']],\
                 ['Row operations', ['filter', 'append', 'aggregate', 'transform', 'nodeFilter']],\
                 ['Column operations', ['select', 'rename', 'process', 'compute', 'join', 'add_column', 'log', 'scale' ]],\
                 ['Colors', ['color']],\
                 ['Tree', ['trace', 'treeInfo', 'pgls']],\
                 ['DC management', ['cache', 'retrieve','call', 'var']],\
                 #, 'group', # 'define', 
               ]
DCO_descriptions={'database':   'Start with a dataframe table from a file', 
                  'retrieve':   'Resume from a dataframe previously cached', 
                  'antenna':    'Get current selection, dynamically updated', 
                  'generator':  'Create a dataframe with arbitrary shape',
                  'filter':     'Keep only the rows that pass a certain condition',
                  'nodeFilter': 'Filter only the rows included in a node selection',
                  'append':     'Stack rows to an existing dataframe',
                  'add_column': 'Add a column to an existing dataframe',
                  'aggregate':  'Group and merge rows (e.g. by averaging)',
                  'transform':  'Rank rows or fit them to a distribution',
                  'log':        'Apply a logarithmic function on columns',
                  'scale':      'Rescale one or more columns',
                  'select':     'Select or reorder one or more columns',
                  'rename':     'Change the name of one or more columns',
                  'process':    'Create or modify any existing columns',
                  'compute':    'Create or modify existing numerical columns',
                  'join':       'Join with an existing dataframe',
                  'cache':      'Store current dataframe for later retrieval',
                  'define':     'Define a custom routine',
                  'var':        'Declare a variable, then available in next components',
                  'call':       'Use a previously defined routine',
                  'group':      'Assemble multiple components into one',
                  'trace':      'Perform ancestral state reconstruction',      
                  'pgls':       'Test for correlation taking into account the tree',
                  'treeInfo':   'Given a list of nodes, fetch some info from the tree',
                  'color':      'Add a column with a color to be used in plot items',
}
DCO_name2widget={'database':DCOW_database, 'antenna':DCOW_antenna, 'generator':DCOW_generator,
                 'cache':DCOW_cache, 'retrieve':DCOW_retrieve, 'define':DCOW_define, 'call':DCOW_call, 'var':DCOW_var, 
                 'select':DCOW_select, 'filter':DCOW_filter, 'nodeFilter':DCOW_nodeFilter,
                 'process':DCOW_process, 'compute':DCOW_compute, 'rename':DCOW_rename, 
                 'aggregate':DCOW_aggregate, 'join':DCOW_join, 'append':DCOW_append,
                 'add_column':DCOW_add_column,
                 'group':DCOW_group, 'trace':DCOW_trace, 'treeInfo':DCOW_treeInfo,
                 'table':DCOW_table,  'scatterplot':DCOW_scatterplot, 'plot3D':DCOW_plot3D,  'send_to_plot':DCOW_send_to_plot,
                 'color':DCOW_color,
                 'log':DCOW_log,   'scale':DCOW_scale, 
                 'pgls':DCOW_pgls}


class ExtendDataChannelWidget(QtGui.QWidget):
  class SearchBox(QtGui.QLineEdit): 
    def focusOutEvent(self, e): return self.parent().focusOutEvent(e)
  class ScrollArea(QtGui.QScrollArea): 
    def focusOutEvent(self, e): return self.parent().focusOutEvent(e)

  def focusOutEvent(self, e):
    """ To make sure this widget cease to exists when you click somewhere else, like a qmenu"""
    super(ExtendDataChannelWidget, self).focusOutEvent(e)
    #print 'focus out!', e, e.gotFocus(), e.lostFocus(), e.reason()
    if e.lostFocus() and e.reason()==QtCore.Qt.ActiveWindowFocusReason: self.close()

  def __init__(self, dcw, dco_index):
    a_size_policy= QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
    super(ExtendDataChannelWidget, self).__init__() #    QtGui.QWidget.__init__(self)  
    self.dcw=dcw; self.dco_index=dco_index
    vlayout=QtGui.QVBoxLayout(); vlayout.setContentsMargins(1, 1, 1, 1);     vlayout.setSpacing(2)    
    self.setLayout(vlayout)
    self.setWindowTitle('Add Data Channel component...')
    self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
    self.search_layout=QtGui.QHBoxLayout()
    #self.dashboard_layout=QtGui.QVBoxLayout()
    self.all_dcos_layout=QtGui.QVBoxLayout(); self.all_dcos_layout.setContentsMargins(1, 1, 1, 1); self.all_dcos_layout.setSpacing(1)
    vlayout.addLayout(self.search_layout); 
    #vlayout.addLayout(self.dashboard_layout); 
    ## vlayout.addLayout(self.all_dcos_layout)
    scrollarea=self.ScrollArea(parent=self)
    scrollarea.setWidgetResizable(True)
    #scrollarea.setMinimumHeight(800)
    #scrollarea.setMinimumWidth(600)
    w=QtGui.QWidget(scrollarea)
    scrollarea.setWidget(w)
    w.setLayout(self.all_dcos_layout)
    vlayout.addWidget(scrollarea)
    #w.setSizePolicy(a_size_policy)
    #scrollarea.setSizePolicy(a_size_policy)
    self.setSizePolicy(a_size_policy)
    ### search
    self.search_box=self.SearchBox(parent=self)
    self.search_box.textEdited.connect(self.edited_search_box)
    search_button=  ToolButton('searchglass', 'Search for components')    
    self.search_layout.addWidget(self.search_box); self.search_layout.addWidget(search_button)
    self.fill()
    self.show()    
    wsh=w.sizeHint()
    w_width_hint=wsh.width(); w_height_hint=wsh.height()
    self.resize( w_width_hint+20, w_height_hint+40   )  #making decent looking starting size
    # write( ('scrollarea',   scrollarea.sizeHint(), scrollarea.size())  , 1, how='blue')
    # write( ('w',        w.sizeHint(), w.size())  , 1, how='magenta')
    self.place()
    #self.make_reasonable_size()
    self.setFocus(True)
    self.search_box.setFocus(True)

  def place(self):   self.move(QtGui.QCursor.pos())
  # def make_reasonable_size(self): return 
  #   w,h= self.width(), self.height()
  #   g=QtGui.QDesktopWidget().screenGeometry(self)
  #   screen_w,screen_h= g.width(), g.height()
  #   w=min([screen_w,tab_w]); h=min([screen_h,tab_h])
  #   self.resize(w,h)

  def clear_layouts(self):
    #clear_layout(self.dashboard_layout)
    clear_layout(self.all_dcos_layout)

  def fill(self):
    dco_size_policy= QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
    self.clear_layouts()
    ### dashboard
    # dashrow=QtGui.QHBoxLayout()
    # dashrow.addStretch(); dashrow.addWidget(QtGui.QLabel('Dashboard')); dashrow.addStretch()
    # dashboard_layout.addLayout(dashrow)
    searched=str(    self.search_box.text()   )
    ### all DCOs
    #dcosrow=QtGui.QHBoxLayout()
    #dcosrow.addStretch(); dcosrow.addWidget(QtGui.QLabel('All components')); dcosrow.addStretch()
    #self.all_dcos_layout.addLayout(dcosrow)
    some_hit=False
    for category, dco_names in DCO_categories:
      filtered_dco_names=[dco_name for dco_name in dco_names  \
                          if not searched or dco_name.find(searched)!=-1 or (dco_name in DCO_descriptions and DCO_descriptions[dco_name].find(searched)!=-1)]
      if not filtered_dco_names: continue
      some_hit=True
      self.all_dcos_layout.addWidget(HorizontalLine())
      row_title=QtGui.QHBoxLayout()
      label=QtGui.QLabel(category)
      label.setSizePolicy(dco_size_policy)
      row_title.addWidget(label); row_title.addStretch()
      self.all_dcos_layout.addLayout(row_title)

      for dco_name in filtered_dco_names:
        row=QtGui.QHBoxLayout()
        button=ToolButton(dco_name, dco_name[0].upper()+dco_name[1:].replace('_', ' '))
        button.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        button.clicked.connect( lambda s,n=dco_name:self.add_dco(n) )
        row.addWidget(button) #        row.addWidget(QtGui.QLabel(dco_name.capitalize()))
        desc='' if not dco_name in DCO_descriptions else DCO_descriptions[dco_name]
        desc_label=QtGui.QLabel(desc)
        desc_label.setStyleSheet('color:#666666')
        desc_label.setSizePolicy(dco_size_policy)
        button.setSizePolicy(dco_size_policy)
        row.addWidget(desc_label)
        row.addStretch()
        self.all_dcos_layout.addLayout(row)
    if not some_hit:
      row=QtGui.QHBoxLayout()
      row.addWidget(QtGui.QLabel('No components match your query'))
      row.addStretch()
      self.all_dcos_layout.addLayout(row)
    self.all_dcos_layout.addStretch()
   
  def edited_search_box(self, text):
    text=str(text)
    print 'edited search box', text
    self.fill()

  def add_dco(self, name):
    self.dcw.add_dco(name, self.dco_index)
    self.close()


#################################################

class FeatureLoader(TreedexWindow):
  def window_identifier(self): return {'window_name':'FeatureLoader'}
  def master(self):            return self.master_link
  def __init__(self, master_link, origin=None):
    self.master_link=master_link
    super(FeatureLoader, self).__init__() #    QtGui.QWidget.__init__(self)  
    self.setWindowTitle('Treedex - Load feature file')
    self.layout = QtGui.QVBoxLayout()
    self.setLayout(self.layout)
    
    # load file box
    filelayout=QtGui.QHBoxLayout()
    filelayout.addWidget(QtGui.QLabel('File:'))
    self.filename_box=QtGui.QLineEdit('', self);  self.filename_box.setMinimumSize(300, 30)
    self.filename_box.editingFinished.connect(self.load_file_box_editing_finished)
    filelayout.addWidget(self.filename_box)
    openfile_button=QtGui.QPushButton('Browse ...')
    openfile_button.clicked.connect(self.clicked_browse_file_button)
    filelayout.addWidget(openfile_button)
    self.layout.addLayout(filelayout)

    # field separator
    self.layout.addWidget(HorizontalLine())
    #    self.layout.addWidget(QtGui.QLabel('Settings for importing'))
    separatorlayout=QtGui.QHBoxLayout()
    separatorlayout.addWidget(QtGui.QLabel('Field separator: '))
    self.separatorcombobox=QtGui.QComboBox()
    self.separatorcombobox.possible_values=[('\t', 'Tab'), (',', 'Comma'), (' ', 'Space')]
    for _,txt in self.separatorcombobox.possible_values: self.separatorcombobox.addItem(txt)
    separatorlayout.addWidget(self.separatorcombobox)
    separatorlayout.addStretch()
    self.layout.addLayout(separatorlayout)

    indexlayout=QtGui.QHBoxLayout()
    self.useindex_checkbox=QtGui.QCheckBox(self) #, checked=True)
    self.useindex_checkbox.setText('Treat first column as index')
    indexlayout.addWidget(self.useindex_checkbox)
    self.layout.addLayout(indexlayout)

    ### Species determination
    speciesidlayout=QtGui.QHBoxLayout()
    label=QtGui.QLabel('Species is indicated in the ')
    speciesidlayout.addWidget(label)
    self.speciesid_rc_combobox=QtGui.QComboBox()
    self.speciesid_rc_combobox.possible_values=[('c', 'column'), ('r', 'row')]
    for _,txt in self.speciesid_rc_combobox.possible_values: self.speciesid_rc_combobox.addItem(txt)
    speciesidlayout.addWidget(self.speciesid_rc_combobox)
    label=QtGui.QLabel(' with ')
    speciesidlayout.addWidget(label)
    self.speciesid_in_combobox=QtGui.QComboBox()
    self.speciesid_in_combobox.possible_values=[('i', 'index'), ('n', 'name') ]
    for _,txt in self.speciesid_in_combobox.possible_values: self.speciesid_in_combobox.addItem(txt)
    speciesidlayout.addWidget(self.speciesid_in_combobox)
    speciesidlayout.addWidget(QtGui.QLabel(': '))
    self.speciesid_v_textbox = QtGui.QLineEdit('1', self)
    speciesidlayout.addWidget(self.speciesid_v_textbox)
    speciesidlayout.addStretch()
    self.layout.addLayout(speciesidlayout) 

    self.layout.addWidget(HorizontalLine())
    namelayout=QtGui.QHBoxLayout()
    namelayout.addWidget( QtGui.QLabel('Choose a name for your database:') )
    self.name_box=QtGui.QLineEdit('NewDatabase')  
    self.name_box.setMaximumWidth(200)
    self.name_box.editingFinished.connect(self.check_overwrite_need)
    namelayout.addWidget(self.name_box)
    namelayout.addStretch()
    self.layout.addLayout(namelayout)    
  
    self.overwrite_layout=QtGui.QHBoxLayout()
    self.overwrite_label=QtGui.QLabel('A database with this name already exists! ')
    self.overwrite_layout.addWidget(self.overwrite_label)
    self.overwrite_label.setStyleSheet('color:#bb0000')
    self.overwrite_checkbox=QtGui.QCheckBox(self)
    self.overwrite_checkbox.setText('Overwrite')
    self.overwrite_layout.addWidget(self.overwrite_checkbox)
    self.overwrite_layout.addStretch()
    self.layout.addLayout(self.overwrite_layout)

    buttonlayout=QtGui.QHBoxLayout()
    buttonlayout.addStretch()
    # hidden buttons first
    self.button_load_another=QtGui.QPushButton('Load another database ...')
    self.button_load_another.setVisible(False)
    self.button_load_another.clicked.connect(self.clicked_load_another_button)
    buttonlayout.addWidget(self.button_load_another)
    self.button_close=QtGui.QPushButton('Close window')
    self.button_close.setVisible(False)
    self.button_close.clicked.connect(self.close)
    buttonlayout.addWidget(self.button_close)
    # visible:
    self.button_load=QtGui.QPushButton('Load database')
    buttonlayout.addWidget(self.button_load)
    self.button_load.clicked.connect(self.clicked_load_file_button)
    self.layout.addLayout(buttonlayout)
    
    self.log_box=QtGui.QTextBrowser(self)
    self.log_box.setFontFamily("Monospace")  #to be able to see DataFrame.head() correctly aligned
    self.layout.addWidget(self.log_box)

    self.check_overwrite_need()

  def clicked_load_another_button(self):
    self.button_load.setEnabled(True)
    self.button_load_another.setVisible(False)
    self.button_close.setVisible(False)
    self.log_box.setText('')
    self.filename_box.setText('')
    self.name_box.setText('NewDatabase')

  def clicked_browse_file_button(self):
    fname = QtGui.QFileDialog.getOpenFileName(self) #, 'Open file', '/home')
    print 'dialog finished:', [fname]
    if fname:
      self.filename_box.setText(fname)
      self.load_file_box_editing_finished()  

  def load_file_box_editing_finished(self):
    filename=str(self.filename_box.text())
    current_df_name=str(self.name_box.text()).strip()
    #print 'load_file_box_editing_finished', filename, current_df_name
    if filename and current_df_name=='NewDatabase': 
      suggested_name='.'.join(str(os.path.basename(filename)).split('.')[:-1]).capitalize()
      self.name_box.setText(suggested_name)    
      self.check_overwrite_need()

  def check_overwrite_need(self):
    df_name=str(self.name_box.text()).strip()
    if self.master().data().has_database(df_name):
      self.overwrite_checkbox.setChecked(False)
      self.overwrite_checkbox.setVisible(True)
      self.overwrite_label.setVisible(True)
    else: 
      self.overwrite_checkbox.setChecked(False)
      self.overwrite_checkbox.setVisible(False)
      self.overwrite_label.setVisible(False)

  def clicked_load_file_button(self):
    try:
      filename=str(self.filename_box.text())
      field_separator=self.separatorcombobox.possible_values[self.separatorcombobox.currentIndex()][0] 
      # regarding species identification
      row_or_col=   self.speciesid_rc_combobox.possible_values[self.speciesid_rc_combobox.currentIndex()][0] # 'c' or 'r'
      index_or_name=self.speciesid_in_combobox.possible_values[self.speciesid_in_combobox.currentIndex()][0] # 'i' or 'n'
      with_value=   str(self.speciesid_v_textbox.text())

      index_col={True:0, False:False}[self.useindex_checkbox.isChecked()]
      pd_df=pd.read_csv(filename, sep=field_separator, index_col=index_col) #pandas dataframe
      if  row_or_col=='r':      pd_df=pd_df.T
      if    index_or_name=='i':      node_field=str(pd_df.columns[  int(with_value)-1  ])
      elif  index_or_name=='n':      node_field=with_value
      #if    index_or_name=='i':      node_field=str(pd_df.columns[  int(with_value)-1  ])
      #elif  index_or_name=='n':      node_field=with_value    
  
      df_name=str(self.name_box.text()).strip()
      if not df_name: raise Exception, "ERROR cannot save a database with no name"
      overwrite=self.overwrite_checkbox.isChecked()

      #df= pd.DataFrame(data=pd_df, name=df_name, node_field=node_field)  #treedex dataframe
      self.master().data().add_database(df, overwrite=overwrite, name=df_name, node_field=node_field)
      r,c=df.shape
      msg='Success!\nLoaded database "{n}" with {r} rows and {c} columns.\nExample lines:\n\n{h}'.format(n=df_name, r=r, c=c, h=df.head())
      self.log_box.setText(msg)
      self.button_load_another.setVisible(True)
      self.button_close.setVisible(True)
      self.button_load.setEnabled(False)

    except Exception as e:
      msg='Load database FAILED!\nPlease see the error traceback below:\n{e}'.format(e=e)
      self.log_box.setText(msg)  
               

#################################################
class PandasTableWidget(QtGui.QTableWidget):
  """ Generic Table Widget that can display a pd.DataFrame, or pd.Series, or anything usable to init a dataframe (like a list)"""
  default_options={'display_index':None, 'max_column_width':220} #display_index forces showing index in column '0'  #Node -> auto; False/True -> forced
  def __init__(self, data=None):
    super(PandasTableWidget, self).__init__() 
    self.setSelectionBehavior(QtGui.QAbstractItemView.SelectItems) #QAbstractItemView.SelectRows)   
    self.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)   #disabling editing
    self.options=dict(self.default_options) 
    self.setSortingEnabled(True)
    self.data=None
    self.data_index2table_index=None 
    self.table_index2data_index=None 
    if not data is None: self.set_data(data)
    hheader=self.horizontalHeader()
    hheader.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
    hheader.customContextMenuRequested.connect(self.open_horizontal_header_menu) #right click
    hheader.sectionClicked.connect(self.clicked_horizontal_header)       #left click

  def set_data(self, data):
    """ Thought for pandas objects, but generic enough (DataFrame, Series), list etc) """
    if not hasattr(data, 'shape'): data=pd.DataFrame(data) #if not DataFrame or Series
    self.data=data
    self.data_index2table_index={ i:i for i in range(len(self.data.index))  }   #updated when sorting by column is activated (see clicked_horizontal_header)
    self.table_index2data_index={ i:i for i in range(len(self.data.index))  }   #updated when sorting by column is activated (see clicked_horizontal_header)

  def fill(self):
    self.clear()
    self.setSortingEnabled(False)
    #print 'fill table!', self.data.shape
    if    len(self.data.shape)==2:        n_rows, n_cols=self.data.shape   #dataframe
    elif  len(self.data.shape)==1:        n_rows=self.data.shape; n_cols=1 #series  

    if self.options['display_index'] is None: #auto show index pandas.indexes.range.RangeIndex
      ind=self.data.index
      
      index_col_present=  not ind is None and ( ( ind.name ) or \
                          ( type(ind) != pd.indexes.range.RangeIndex and not pd.indexes.numeric.is_integer_dtype(ind) )   )
      #print 'display index', ind, type(ind), ind.name, index_col_present
    else:  index_col_present= int( self.options['display_index'] ) #keeping it as int (0/1) 

    self.setColumnCount(n_cols+1)  #extra field to keep an index for original order
    self.setRowCount(n_rows)   
    # vertical headers, if shown 
    if not index_col_present:                self.verticalHeader().setVisible(False)
    else:
      self.verticalHeader().setVisible(True)
      for row_i in range(n_rows):
        index_value=self.data.index[row_i]
        vheader_item=QtGui.QTableWidgetItem()
        if   isinstance(index_value, np.floating): index_value=float(index_value)
        elif isinstance(index_value, np.integer):  index_value=int(index_value)
        vheader_item.setData(QtCore.Qt.DisplayRole, index_value)
        self.setVerticalHeaderItem(row_i, vheader_item)
        self.verticalHeaderItem(row_i).setToolTip(str(index_value))

    # (horizontal) headers
    for col_i in range(n_cols):
      column_name=self.data.columns[col_i]
      self.setHorizontalHeaderItem(col_i, QtGui.QTableWidgetItem(column_name))
      try:    tooltip='{}\ntype: {}'.format(column_name, self.data[column_name].dtype)
      except: tooltip='{}'.format(column_name)
      self.horizontalHeaderItem(col_i).setToolTip( tooltip )
    self.setHorizontalHeaderItem(n_cols, QtGui.QTableWidgetItem('(order)'))   
    #items
    for row_i in range(n_rows):
      for col_i in range(n_cols):
        value=  self.data.iat[row_i, col_i]
        if   isinstance(value, np.floating): value=float(value)
        elif isinstance(value, np.integer):  value=int(value)
        item=QtGui.QTableWidgetItem() 
        item.setData(QtCore.Qt.DisplayRole, value)    #in this way, the actual value (float if necessary) is used; this is required for appropriate sorting
        self.setItem(row_i, col_i, item)
      ## storing order index
      item=QtGui.QTableWidgetItem() 
      item.setData(QtCore.Qt.DisplayRole, row_i+1)
      self.setItem(row_i, n_cols, item)

    self.setSortingEnabled(True)
    #resizing
    self.resizeColumnsToContents()
    for col_i in range(self.columnCount()):
      if self.columnWidth(col_i)>self.options['max_column_width']: 
        self.setColumnWidth(col_i, self.options['max_column_width'])
    #setting an attribute to keep track of sorting and hidden columns
    self.visible_fields={i:True for i in range(n_cols+1)}
    hheader=self.horizontalHeader()
    hheader.setSortIndicator(n_cols, 0) #setting sort based on invisible order column
    self.sorting=(hheader.sortIndicatorOrder(), hheader.sortIndicatorSection())
    #print 'sorting', self.sorting
    for c in range(n_cols):     self.toggle_column(c, True)
    self.toggle_column(n_cols)

  def toggle_column(self, index, value=None):
    """ Show or hide the column index. """
    if value is None: value=not self.visible_fields[index]
    self.visible_fields[index]=value
    if self.visible_fields[index]:    self.horizontalHeader().showSection(index)
    else:                             self.horizontalHeader().hideSection(index)  

  def sizeHint(self):   
    height = QtGui.QTableWidget.sizeHint(self).height()
    width= sum([self.horizontalHeader().sectionSize(col_i) for col_i in range(self.columnCount()) ]) #for the hidden ones this is zero
    width += self.verticalHeader().width()        
    width += self.verticalScrollBar().sizeHint().width()    
    margins = self.contentsMargins()
    width += margins.left() + margins.right()   
    width += 5   #dunno why, still missing something in width
    return QtCore.QSize(width, height)

  ###### mouse
  def mouseReleaseEvent(self, e):
    """ To catch clicks on the cells. Left click remains default, but we customize the right click menu """
    QtGui.QTableWidget.mouseReleaseEvent(self, e) # letting it select or not as it normally does
    if e.button() == QtCore.Qt.RightButton:        
      menu=QtGui.QMenu()
      menu.addAction('Copy selected cell(s)', self.copy_selected  )
      menu.addSeparator()
      menu.addAction('Select all cells', self.select_all  )
      menu.addAction('Select entire row(s)', self.select_rows  )
      menu.addAction('Select entire column(s)', self.select_columns  )
      self.add_menu_actions(menu)
      #menu.addAction('echo', self.echo  )
      menu.exec_(QtGui.QCursor.pos())

  def clicked_horizontal_header(self, col_index):
    """ To catch any left click on the header. Function connected to self.horizontalHeader().sectionClicked """
    hheader=self.horizontalHeader()
    order, section = hheader.sortIndicatorOrder(), hheader.sortIndicatorSection()
    #self.sorting  has the old sorting
    previous_order, previous_section = self.sorting
    if previous_section == section and previous_order==1: 
      #modifying default behavior so that, at the third click on a column, it goes back to 'no ordering' (which really is sorting on a hidden column
      order, section =   self.columnCount()-1, 0
      hheader.setSortIndicator(order, section)
    self.sorting = (order, section)
    self.data_index2table_index={}
    self.table_index2data_index={}
    for table_index in range(len(self.data.index)):
      data_index=self.item(   table_index,   self.columnCount()-1  ).data(QtCore.Qt.DisplayRole).toInt()[0]-1
      self.data_index2table_index[data_index]=table_index
      self.table_index2data_index[table_index]=data_index

  def open_horizontal_header_menu(self, point):
    col_index=self.horizontalHeader().logicalIndexAt(point.x())
    col_name=self.horizontalHeaderItem(col_index).text()
    menu=QtGui.QMenu()
    menu.addAction('Copy column title', lambda text=col_name:QtGui.QApplication.clipboard().setText(text))
    menu.addSeparator()
    a=QtGui.QAction('Visible columns:', self); a.setEnabled(False)
    menu.addAction(a)
    for c in range(self.columnCount()):
      field=self.horizontalHeaderItem(c).text()
      action=QtGui.QAction( field, self,  checkable=True, checked=self.visible_fields[c]) 
      action.triggered.connect(lambda s,x=c:self.toggle_column(x))
      menu.addAction(action)
    menu.exec_(QtGui.QCursor.pos())

  ##### keyboard
  def keyPressEvent(self, e):
    if (e.modifiers() & QtCore.Qt.ControlModifier ):
      if   e.key() == QtCore.Qt.Key_C:         self.copy_selected()
      elif e.key() == QtCore.Qt.Key_A:         self.select_all()   
    elif e.key() == QtCore.Qt.Key_Escape:    self.clearSelection()

  ### selections
  def select_all(self):    
    self.setRangeSelected(QtGui.QTableWidgetSelectionRange(0, 0,  self.rowCount()-1, self.columnCount()-1), True)

  def select_rows(self):
    all_row_indexes=set()
    for r in self.selectedRanges():  
      for index in range(r.topRow(), r.bottomRow()+1):            all_row_indexes.add(index)
    for index in all_row_indexes:
      self.setRangeSelected(QtGui.QTableWidgetSelectionRange(index, 0, index, self.columnCount()-1), True)

  def select_columns(self):
    all_column_indexes=set()
    for r in self.selectedRanges():  
      for index in range(r.leftColumn(), r.rightColumn()+1):      all_column_indexes.add(index)
    for index in all_column_indexes:
      self.setRangeSelected(QtGui.QTableWidgetSelectionRange(0, index, self.rowCount()-1, index), True)

  def get_selected_text(self, include_headers=True):    
    all_column_indexes=set();     all_row_indexes=set()
    for r in self.selectedRanges():  
      for index in range(r.leftColumn(), r.rightColumn()+1):      all_column_indexes.add(index)
      for index in range(r.topRow(), r.bottomRow()+1):            all_row_indexes.add(index)
    all_column_indexes=sorted(all_column_indexes)
    all_row_indexes=sorted(all_row_indexes)
    if not include_headers: text=''
    else:     text = '\t'.join([str(self.horizontalHeaderItem(c).text()) for c in all_column_indexes])
    if text: text+='\n'
    for i in all_row_indexes:
      for c in all_column_indexes:
        if not self.visible_fields[c]: continue
        try:                    text+=str(self.item(i,c).text()) + "\t"
        except AttributeError:  text+="\t"
      if text: text=text[:-1]+'\n'
    return text

  ##### copy
  def copy_selected(self):
    """ Copy the text of the cells currently selected in the system clipboard. Sparse selections are not permitted: if you select some column, that will be selected in every row with at least one cell selected. This is thought to copy paste the selection to an excel file"""
    text=self.get_selected_text(include_headers=True)
    if text: QtGui.QApplication.clipboard().setText(text)  

  def get_key_column(self, key): 
    """ Return the index of a column with a certain name, if present;  
               -1 if that is the index name;      
             None otherwise """
    if len(self.data.shape)<2:       return  
    if self.data.index.name==key: return -1
    if key in self.data.columns:  return self.data.columns.get_loc(key)   

  def add_menu_actions(self,  menu):     pass

### Table for DataChannels, to be included in TreedexFeatureExplorer
class TreedexTableWidget(PandasTableWidget):
  """ """
  def __init__(self, feature_explorer):
    self.feature_explorer=feature_explorer
    super(TreedexTableWidget, self).__init__() 

  def get_node_column(self): return self.get_key_column('Node')
  def add_menu_actions(self, menu):    
    node_col=self.get_node_column()
    if not node_col is None: 
      menu.addSeparator()
      menu.addAction('These nodes: select',    self.select_these_nodes  )      
      menu.addAction('These nodes: highlight', self.highlight_these_nodes  )    
      menu.addAction('Copy column titles', self.copy_column_titles)

  def copy_column_titles(self):
    QtGui.QApplication.clipboard().setText(  ','.join([ ','.join(self.data.columns[r.leftColumn():r.rightColumn()+1])   for r in self.selectedRanges()])  )
    
  def get_nodes_selected_in_table(self):
    node_col=self.get_node_column()
    ns=NodeSelector()
    tm=self.feature_explorer.master_link.trees()                     
    if   node_col is None: pass #giving empty NS
    elif node_col ==-1:   #node is data.index
      for r in self.selectedRanges(): 
        for table_row_index in range(r.topRow(), r.bottomRow()+1):
          node_name=self.data.index[  self.table_index2data_index[table_row_index]  ]
          ns.add( tm.get_node(node_name) )          
    else:
      for r in self.selectedRanges(): 
        for table_row_index in range(r.topRow(), r.bottomRow()+1):
          node_name=self.data.iat[ self.table_index2data_index[table_row_index] , node_col]   #data_index=self.tabl         
          ns.add( tm.get_node(node_name) )
      #this would work only when no sorting was activated for table:
      #for r in self.selectedRanges(): ns.update([ tm.get_node(node_name)     for node_name in self.data.iloc[r.topRow() : r.bottomRow()+1, node_col] ])
    return ns.walk_tree(down=True, only_leaves=True)

  def select_these_nodes(self): 
    ns=self.get_nodes_selected_in_table()
    self.feature_explorer.master_link.selections().edit_node_selection('Selected nodes', ns)

  def highlight_these_nodes(self): 
    ns=self.get_nodes_selected_in_table()
    self.feature_explorer.master_link.selections().edit_node_selection('Highlighted nodes', ns)
    
###############################################################################

class TreedexFeatureExplorer(TreedexWindow):
  """ An extension of TreedexTableWidget with a useful toolbar that includes a DC"""
  default_options={'auto_resize':False, 'action_out':'h', 'action_in':'n'}
  default_table_options={'display_index':None,}
  def window_identifier(self):    return {'window_name':self.title }
  def master(self): return self.master_link
  def delete_data_channels(self):     
    self.dc.delete()
    self.auto_select_cells_dc.delete()

  def __init__(self, dco_link, options={}, title=''):
    self.title=title
    #self.dc=dc  #.Master() must be available when init is called
    self.dco_link=dco_link #this is a DCO_table that acts as a container for this window
    c=self.dco_link
    while not c.container is None: c=c.container
    self.master_link=c
    self.dc=DataChannel(self.dco_link)
    self.dc.muted=True
    self.dc.append(DCO_lockinsert())
    self.dc.append(DCO_retrieve('TableInput'))
    self.dc.muted=False
    self.dc.set_lock(1)
    ## self.update_auto_select_cells_dc() # this will create self.auto_select_cells_dc   ### doing this below for correct order of connect() signals

    super(TreedexFeatureExplorer, self).__init__()  
    self.setWindowTitle(title)
    self.layout=QtGui.QVBoxLayout();     self.layout.setContentsMargins(1, 1, 1, 1);     self.layout.setSpacing(2)    
    self.dc_layout=QtGui.QHBoxLayout();            #self.dc_layout.setContentsMargins(0, 0, 0, 0);  self.dc_layout.setSpacing(0)
    self.opt_layout=QtGui.QHBoxLayout();           #self.opt_layout.setContentsMargins(0, 0, 0, 0); self.opt_layout.setSpacing(0)
    #self.interactivity_layout=QtGui.QHBoxLayout(); #self.opt_layout.setContentsMargins(0, 0, 0, 0); self.opt_layout.setSpacing(0)
    self.tab_layout=QtGui.QHBoxLayout(); self.tab_layout.setContentsMargins(0, 0, 0, 0); self.tab_layout.setSpacing(0)
    self.setLayout(self.layout)
    self.layout.addLayout(self.dc_layout)
    self.layout.addLayout(self.opt_layout)
    #self.layout.addLayout(self.interactivity_layout)  ##multiple present, see below

    self.options=dict(self.default_options)
    self.options.update(options)
    
    self.opt_layout.addWidget(QtGui.QLabel('Index column:'))
    self.display_index_combobox=QtGui.QComboBox()
    self.display_index_combobox.possible_values=[(None, 'Auto'), (False,'No'), (True,'Yes')]
    for _, i in self.display_index_combobox.possible_values: self.display_index_combobox.addItem(i)
    self.display_index_combobox.activated[int].connect(self.activated_display_index_combobox)
    self.opt_layout.addWidget(self.display_index_combobox)
    self.opt_layout.addWidget(QtGui.QLabel(' Auto-resize:'))
    self.opt_layout.addWidget(VerticalLine())

    self.auto_resize_combobox=QtGui.QComboBox()
    self.auto_resize_combobox.possible_values=[(True, 'Yes'), (False, 'No')]
    for _, i in self.auto_resize_combobox.possible_values: self.auto_resize_combobox.addItem(i)
    self.auto_resize_combobox.activated[int].connect(self.activated_auto_resize_combobox)    
    self.opt_layout.addWidget(self.auto_resize_combobox)
    self.opt_layout.addWidget(VerticalLine())

    self.interactivity_button=ToolButton('interactivity', 'Show/hide interactivity menu', self.clicked_interactivity_button) 
    self.interactivity_button.setText('Interactivity...') 
    self.interactivity_button.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
    self.opt_layout.addWidget(self.interactivity_button)

    self.opt_layout.addStretch()
    for i in range(self.opt_layout.count()): 
      w=self.opt_layout.itemAt(i).widget()
      if w: w.setSizePolicy(fixed_size_policy)

    self.interactivity_layouts=[]

    interactivity_layout=QtGui.QHBoxLayout()  #first line
    interactivity_layout.addWidget(QtGui.QLabel('When table cells are selected: '))
    self.action_out_combobox=QtGui.QComboBox()
    self.action_out_combobox.possible_values=[('h','Highlight nodes'), ('s','Select nodes'), ('n','No other effect')]
    for _, i in self.action_out_combobox.possible_values: self.action_out_combobox.addItem(i)
    self.action_out_combobox.activated[int].connect(self.activated_action_out_combobox)
    interactivity_layout.addWidget(self.action_out_combobox)
    interactivity_layout.addStretch()
    self.layout.addLayout(interactivity_layout)
    self.interactivity_layouts.append(interactivity_layout)

    interactivity_layout=QtGui.QHBoxLayout()  #first line
    interactivity_layout.addWidget(QtGui.QLabel('Automatically select table cells when: '))
    self.action_in_combobox=QtGui.QComboBox()
    self.action_in_combobox.possible_values=[('h','Nodes are highlighted'), ('s','Nodes are selected'), ('n','Never')]
    for _, i in self.action_in_combobox.possible_values: self.action_in_combobox.addItem(i)
    self.action_in_combobox.activated[int].connect(self.activated_action_in_combobox)
    interactivity_layout.addWidget(self.action_in_combobox)
    interactivity_layout.addStretch()
    self.layout.addLayout(interactivity_layout)
    self.interactivity_layouts.append(interactivity_layout)

    self.interactivity_visible=True #actually init with false once we virtually clicked below
    self.clicked_interactivity_button()

    self.indicator_nodata= QtGui.QWidget(); self.indicator_nodata.setStyleSheet('background:white')
    self.indicator_nodata.layout=QtGui.QVBoxLayout(); self.indicator_nodata.setLayout(self.indicator_nodata.layout)
    self.indicator_nodata.label=QtGui.QLabel('No data to display')
    self.indicator_nodata.layout.addWidget(self.indicator_nodata.label)
    self.layout.addWidget(self.indicator_nodata)
    self.layout.addLayout(self.tab_layout)

    self.table=TreedexTableWidget(self)
    self.table.options.update(self.default_table_options)

    self.display_index_combobox.setCurrentIndex(  [i[0] for i in self.display_index_combobox.possible_values].index( self.table.options['display_index'] )  )
    self.auto_resize_combobox.setCurrentIndex(  [i[0] for i in self.auto_resize_combobox.possible_values].index( self.options['auto_resize'] )  )
    j=[i[0] for i in self.action_out_combobox.possible_values].index( self.options['action_out'] )
    self.action_out_combobox.setCurrentIndex(j)
    self.activated_action_out_combobox(j, first_run=True)   #connecting to right function
    j=[i[0] for i in self.action_in_combobox.possible_values].index( self.options['action_in'] )
    self.action_in_combobox.setCurrentIndex(j)
    # self.activated_action_in_combobox(j, first_run=True)   #connecting to right function

    self.tab_layout.addWidget(self.table)
    self.set_dc(self.dc, first_run=True) # a little redundant with prior self.dc=dc but necessary
    self.update_auto_select_cells_dc(first_run=True) # this will create self.auto_select_cells_dc   ### doing this below for correct order of connect() signals
    self.md5_data_last_update=None
    self.update_table()

  def set_dc(self, dc, first_run=False):
    if not first_run:      
      #self.dc.signal_dc_changed.disconnect(self.update_table)
      self.dc.signal_value_changed.disconnect(self.update_table)
    self.dc=dc 
    clear_layout(self.dc_layout)
    label=QtGui.QLabel('Data Channel:')
    label.setSizePolicy(fixed_size_policy)
    self.dc_layout.addWidget(label)
    self.dc_layout.addWidget( DataChannelWidget(self.dc, within='FeatureExplorer'))  
    self.dc_layout.addStretch()
    #self.dc.signal_dc_changed.connect(self.update_table)
    self.dc.signal_value_changed.connect(self.update_table)

  def update_auto_select_cells_dc(self, first_run=False):
    #write( 'create/update auto_select_cells_dc', 1, how='reverse,red')
    if not first_run: self.auto_select_cells_dc.delete()
    if self.options['action_in']=='n':   
      self.auto_select_cells_dc=DataChannel(self.dc.container) # empty, useless
    else: 
      df=self.dc.out()
      if df is None or not ('Node' in df.columns  or df.index.name=='Node'):      #can't really try to NodeFilter this df
        self.auto_select_cells_dc=DataChannel(self.dc.container) # empty, useless
      else:
        selname={'h':'Highlighted nodes', 's':'Selected nodes'}[self.options['action_in']]
        self.auto_select_cells_dc=self.dc.copy()
        self.auto_select_cells_dc.muted=True
        self.auto_select_cells_dc.append(DCO_select('Node')) 
        self.auto_select_cells_dc.append(DCO_index('reset')) 
        self.auto_select_cells_dc.append(DCO_nodeFilter(selname)) 
        self.auto_select_cells_dc.muted=False
        self.auto_select_cells_dc.signal_value_changed.connect(self.update_auto_selected_cells)
        self.dc.signal_dc_changed.connect(self.update_auto_select_cells_dc)
        self.update_auto_selected_cells()
    #write( 'created auto_select_cells_dc: '+str(self.auto_select_cells_dc), 1, how='reverse,red')

  def update_auto_selected_cells(self):
    #write( 'update_auto_selected_cells', 1, how='reverse,red')
    df=self.auto_select_cells_dc.out() #single column: Node, same index as dc.out()
    #write( 'current selected nodes='+str(  self.master_link.selections().get_node_selection_df('Selected nodes')    ), 1, how='red')
    #write( 'update.. df='+str(df), 1, how='reverse,red')
    if df is None:     return 
    ## get currently selected columns to respect those. This list may contain a column multiple times if strange selections
    previous_selected_columns_ranges=[ [r.leftColumn(), r.rightColumn()]  for r in self.table.selectedRanges()]  # list of [left,right] 
    self.table.blockSignals(True)
    self.table.clearSelection()
    for data_index in df.index:
      table_index=self.table.data_index2table_index[data_index]
      if not previous_selected_columns_ranges:
        self.table.setRangeSelected( QtGui.QTableWidgetSelectionRange(table_index, 0, table_index, self.table.columnCount()-1) , True)      
      else:
        for left, right in previous_selected_columns_ranges: 
          self.table.setRangeSelected( QtGui.QTableWidgetSelectionRange(table_index, left, table_index, right) , True)

    self.table.blockSignals(False)
    self.table.itemSelectionChanged.emit()

  def clicked_interactivity_button(self):
    self.interactivity_visible= not self.interactivity_visible
    for layout in self.interactivity_layouts:
      for index in range(layout.count()):
        w=layout.itemAt(index).widget()
        if not w is None:     w.setVisible(self.interactivity_visible)
    if self.interactivity_visible:    self.interactivity_button.setStyleSheet('color:blue')
    else:                             self.interactivity_button.setStyleSheet('color:none')

  def activated_action_out_combobox(self, index, first_run=False):
    previous_value=self.options['action_out'] 
    current_value =self.action_out_combobox.possible_values[self.action_out_combobox.currentIndex()][0]

    # disconnect
    if not first_run:
      if previous_value==current_value: return  #nothing to do
      if   previous_value=='n':  pass
      elif previous_value=='h':  self.table.itemSelectionChanged.disconnect(   self.table.highlight_these_nodes   )
      elif previous_value=='s':  self.table.itemSelectionChanged.disconnect(   self.table.select_these_nodes      )

    # connect
    if   current_value=='n':  pass
    elif current_value=='h':  self.table.itemSelectionChanged.connect(   self.table.highlight_these_nodes   )
    elif current_value=='s':  self.table.itemSelectionChanged.connect(   self.table.select_these_nodes      )

    self.options['action_out']=current_value


  def activated_action_in_combobox(self, index): 
    previous_value=self.options['action_in'] 
    current_value =self.action_in_combobox.possible_values[self.action_in_combobox.currentIndex()][0]    
    if previous_value!=current_value:
      self.options['action_in']=current_value
      self.update_auto_select_cells_dc()
      #self.master_link.selections().signal_selection_changed.connect( f )

    
  def activated_display_index_combobox(self, index):
    flag, label =self.display_index_combobox.possible_values[index]
    if flag!=self.table.options['display_index']: 
      self.table.options['display_index']=flag
      self.update_table(force=True)

  def activated_auto_resize_combobox(self, index):
    flag, label =self.auto_resize_combobox.possible_values[index]
    if flag!=self.options['auto_resize']: 
      self.options['auto_resize']=flag
    
  def update_table(self, force=False):        
    if isinstance(self.dc.memory_unit, ErrorUnit): 
      self.table.clear(); self.table.setRowCount(0); self.table.setColumnCount(0)
      self.indicator_nodata.label.setText('ERROR in Data Channel:\n'+str(self.dc.memory_unit.error[1]))
      self.indicator_nodata.setVisible(True)
      return 

    data=self.dc.out()    

    if data is None: #empty
      self.table.clear(); self.table.setRowCount(0); self.table.setColumnCount(0)
      self.indicator_nodata.label.setText('No data available')
      self.indicator_nodata.setVisible(True)
    else:
      md5_data= md5_of_dataframe(data)
      
      if not force and self.md5_data_last_update ==  md5_data:
        print 'update table: NOPE should be identical to last time'
        return 
      print 'update table: YES'
      self.md5_data_last_update=md5_data 
      self.indicator_nodata.setVisible(False)
      self.table.set_data(data)
      self.table.fill()
      if self.options['auto_resize']:      
        s=self.table.sizeHint()
        tab_w,tab_h= s.width(), s.height()
        g=QtGui.QDesktopWidget().screenGeometry(self)
        screen_w,screen_h= g.width(), g.height()
        w=min([screen_w,tab_w]); h=min([screen_h,tab_h])
        self.resize(w,h)


## late import to avoid namespace problems for circularity in dependencies
from .plots import *
from .colors import *

## extra DCO for graphics

class DCO_window(ManagementDCO):
  """Motherclass for all DCOs linked to a window/frame. Ex: table, plots """
  name='window' 
  def manage_dataframe(self, df, mu, dc):
    win_type=self.parameters #[:i]
    win_id  =self.container.group_name  #self.parameters[i+1:]
    write('executing window! '+win_id, 1, how='red')
    master=self.master()

    if win_type=='table':
      window_name='Table: {v}'.format(v=win_id)
      if master.qapp()  and (   not hasattr(self.container, 'window_link') or not self.container.window_link   ):           
        win=TreedexFeatureExplorer(self.container, title=window_name) 
        self.container.window_link=win
        win.show()
      elif  hasattr(self.container, 'window_link') and  str(self.container.window_link.windowTitle())!=window_name:
        self.container.window_link.setWindowTitle(window_name)

    elif win_type=='scatterplot':
      window_name='Scatterplot: {v}'.format(v=win_id)
      if master.qapp()  and (   not hasattr(self.container, 'window_link') or not self.container.window_link   ):           
        win=ScatterPlotWindow(self.container, plot_title=window_name)
        win.add_plot_item(piclass=NodeScatterPlotItem) 
        self.container.window_link=win
        win.show()
      elif  hasattr(self.container, 'window_link') and  str(self.container.window_link.windowTitle())!=window_name:
        self.container.window_link.setWindowTitle(window_name)

    elif win_type=='plot3D':
      window_name='Plot3D: {v}'.format(v=win_id)
      if master.qapp()  and (   not hasattr(self.container, 'window_link') or not self.container.window_link   ):           
        win=Plot3DWindow(self.container, plot_title=window_name)
        win.add_plot_item(piclass=NodePlot3DItem) 
        self.container.window_link=win
        win.show()
      elif  hasattr(self.container, 'window_link') and  str(self.container.window_link.windowTitle())!=window_name:
        self.container.window_link.setWindowTitle(window_name)

    return df, mu

  
class GuiDCO(DCO_smart):
  copiable=False
  def was_removed_from_dc(self, dc):
    if hasattr(self, 'window_link') and not self.window_link is None:      
      print 'deleted DCO! removing window'
      win=self.window_link
      win.dco_link=None
      win.close()

class DCO_table(GuiDCO):
  """ Parameter: just a name for the table"""
  name='table'
  def expand_parameters(self, parameters):     return '{p}[cache:TableInput{sep}window:table]'.format(p=parameters, sep=DataChannel.dco_separator_char)
  def backtrace_parameters(self, parameters):  return self.group_name #parameters[:parameters.index('[')]

class DCO_scatterplot(GuiDCO):
  """ Parameter: just a name for the plot"""
  name='scatterplot'
  def expand_parameters(self, parameters):     return '{p}[cache:PlotInput{sep}window:scatterplot]'.format(p=parameters, sep=DataChannel.dco_separator_char)
  def backtrace_parameters(self, parameters):  return self.group_name #parameters[:parameters.index('[')]    

class DCO_plot3D(GuiDCO):
  """ Parameter: just a name for the plot"""
  name='plot3D'
  def expand_parameters(self, parameters):     return '{p}[cache:PlotInput{sep}window:plot3D]'.format(p=parameters, sep=DataChannel.dco_separator_char)
  def backtrace_parameters(self, parameters):  return self.group_name #parameters[:parameters.index('[')]    


class DCO_send_to_plot(ManagementDCO):
  """ It basically cache this to the namespace of a target plot window (actually, the dco_link for that), making this data available to create new plot items in that plot
  Parameters:   'var_name@type_of_plot: plot_name' """
  name='send_to_plot'
  def manage_dataframe(self, df, mu, dc):
    var_name, window_name=self.interpreted_params(df).split('@')
    master=self.master()
    if master.qapp():
      if not master.windows().has_window(window_name): raise Exception, "DCO_send_to_plot ERROR plot window not found: '{}'".format(window_name)
      win=master.windows().get_window(window_name)
      container=win.dco_link      
      df, pu=write_cache_fn(df, mu, var_name, container, dc)  # basically the operation that DCO_cache does
    return df, mu

DCO_name2class['window']=DCO_window
DCO_name2class['table']=DCO_table
DCO_name2class['scatterplot']=DCO_scatterplot
DCO_name2class['plot3D']=DCO_plot3D
DCO_name2class['send_to_plot']=DCO_send_to_plot
