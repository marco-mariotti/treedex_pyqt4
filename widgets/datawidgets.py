print 'module datawidgets'
from .base   import *
from ..data  import *
import numpy as np                  #only to check type of entry np.floating and np.integer

class DataChannelWidget(QtGui.QWidget): 
  """ (This is also called DCW) Widget to create, modify and inspect DataChannel instances. It consists in a horizontal succession of 'pipes', each corresponding to a DataChannelOperation. A special such pipe is shown when the DC is empty instead. A classical menu is present at the right end. 
  Init with:    
    -dc:      the DataChannel linked to this widget. This can be modified live by this widget.
    -within:  possible values ['FeatureExplorer', 'Plot']. When the DCW is embedded in these widgets, it affects the entries shown in menus
"""
  style={'base': 'QWidget{ background: #99CCFF; padding: 0px}  \
                  QLineEdit { background: white }  \
                  QComboBox { background: none }  \
                  ToolButton { background: white }',  #selection-background-color: #FFCC66 } \
         'locked':  'QWidget{ background: #a5a5a5 }   QComboBox { background: white }',
#         'post':   'QWidget{ background: #a5a5a5 } QComboBox { background: white }',
         'broken':  'background: #bb1111',}

  def __init__(self, dc, within=None):
    super(DataChannelWidget, self).__init__() #    QtGui.QWidget.__init__(self)  
    self.dc=dc
    self.within=within
    self.editing=None #index of DCO currently being edited
    self.setStyleSheet( self.style['base'] )
    self.layout=QtGui.QHBoxLayout(); self.layout.setContentsMargins(0, 0, 0, 0); self.layout.setSpacing(0)
    self.setLayout(self.layout)   #One widget per DCO here, followed by a vline;  plus last one for menu
    self.setSizePolicy(fixed_size_policy)   #### NOT WORKING PROPERLY
    self.fill()
    self.dc.signal_dc_changed.connect(self.dc_changed)

  def dc_changed(self):
    print 'dcw: -> dc changed ', self.dc.key()
    self.dc.validate()  # this stores the result in self.dc.validated
    self.fill()

  def fill(self):
    print 'fill dc widget ', self.dc.key()
    clear_layout(self.layout)
    if not self.dc.chain:      
      edc=empty_DC(self)
      self.layout.addWidget(edc)      
    else:
      chain_button=ChainButton(lambda s,i=-1: self.open_chain_menu(i))
      if not self.editing is None: chain_button.setEnabled(False)         #we're editing some DCO          
      self.layout.addWidget(chain_button)

    for dco_index, dco in enumerate(self.dc.chain):  # this is also in the else:, conceptually
      w=QtGui.QWidget()    # w is dedicated to this DCO
      #self.layout.itemAt( dco_index*2 ).widget()  --> recovers w
      if self.dc.is_locked(dco_index):        
        w.setStyleSheet( self.style['locked'] )
        w.setToolTip( "This Data Channel is locked" )
      if not self.dc.validated is None and self.dc.validated[0]==dco_index:
        #this came out as the problematic DCO in the last dc.validate()
        w.setStyleSheet( self.style['broken'] )
        w.setToolTip( "Data Channel broken:\n"+ str(self.dc.validated[1])  )
      w.setSizePolicy(fixed_size_policy)
      w.frame_layout=QtGui.QVBoxLayout(); w.frame_layout.setContentsMargins(0, 0, 0, 0); w.frame_layout.setSpacing(0)
      w.setLayout(w.frame_layout)
      w.frame_layout.addWidget(HorizontalLine())
      w.layout=QtGui.QHBoxLayout(); w.layout.setContentsMargins(2, 2, 2, 2); w.layout.setSpacing(0)
      w.frame_layout.addLayout(w.layout)
      w.frame_layout.addWidget(HorizontalLine())

#      if not self.dc.is_locked(dco_index):  
#      else:                                 fn=None
      tool_button=ToolButton(dco.name, dco.name.capitalize())  
      w.layout.addWidget(tool_button)

      if self.editing==dco_index:        
        #we're editing this DCO
        #w.setStyleSheet('QWidget {background: yellow} ')
        dcow_class=DCO_name2widget[dco.name]    if dco.DCOW_class is None else dco.DCOW_class
        dcow=dcow_class(self, dco)
        w.layout.addWidget( dcow )
        if not self.dc.is_locked(dco_index):          tool_button.clicked.connect( lambda  s,dcow=dcow:self.clicked_dco_button_to_save(dcow)  ) 
        else:                                         dcow.setEnabled(False)
        # first trigger:   set self.editing ######### REVISE! Looks redundant after new edit (DCO->notify parent DC)
        # if dco has been modified:
        #  --> this will call self.dc.notify_modification        #  --> triggers self.dc.signal_dc_changed
        #   --> self.dc_changed --> self.dc.validate() and self.fill()  ## on any DCW with this DC
        # else:  self.fill()

      else:
        tool_button.clicked.connect( lambda s,i=dco_index:self.clicked_dco_button_to_edit(i) )
        dco_short=dco.short()    #label with dco parameters 
        if not dco_short: dco_short='(None)'
        qlabel=QtGui.QLabel( dco_short ) 
        qlabel.setSizePolicy(fixed_size_policy)
        w.layout.addWidget(qlabel)
        if not self.editing is None:         #we're editing another DCO
          w.setEnabled(False)
        #else:           #we're not editing any DCO

        if 1: #not self.dc.is_locked(dco_index+1) and not self.dc.is_post(dco_index):
          # vline= QtGui.QFrame()            #vertical line to separate from previous dco
          # vline.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Expanding)
          # vline.setFrameStyle(QtGui.QFrame.VLine)
          # self.layout.addWidget(vline)
          chain_button=ChainButton(lambda s,i=dco_index: self.open_chain_menu(i))
          w.layout.addWidget(chain_button)

      self.layout.addWidget(w)
      self.layout.addWidget(VerticalLine())

    menu_button=ToolButton('menu', 'DataChannel Menu...', self.open_menu)
    menu_button.setSizePolicy(fixed_size_policy)
    if not self.editing is None:  menu_button.setEnabled(False)
    self.layout.addWidget(menu_button)

  def edit_dco(self, index):              self.editing=index
  def clicked_dco_button_to_edit(self, index):    
    print 'clicked_dco_button_to_edit', index, self.dc.key()
    self.edit_dco(index); self.fill()
  def clicked_dco_button_to_save(self, dcow):     
    print 'clicked_dco_button_to_save', dcow, '(container)', self.dc.key()
    self.editing=None;    dcow.save()  # this calls self.fill() one way or another
    print '--> saved', self.dc.key()

  def add_dco(self, dco_name, index=None):
    print 'add_dco', dco_name, index
    dco=  DCO_name2class[dco_name] ()  #default parameters
    self.edit_dco(index)   #preparing for when, just below, append/insert triggers the signal that forces self.fill
    if index is None:   self.dc.append(dco)
    else:               self.dc.insert(index, dco)
    #self.dc.notify_modification()

  def remove_dco(self, index=None): 
    self.dc.pop(index) #when None, the last one is removed
    self.fill()
    #self.dc.notify_modification()

  def open_menu(self):      
    qmenu=QtGui.QMenu()
    #qmenu.addAction('Edit', self.edit_data_channel  )
    dc_broken=not self.dc.chain   or   not self.dc.validated is None
    if self.within!='FeatureExplorer':      
      a=qmenu.addAction('Inspect data', self.inspect_data)
      if dc_broken: a.setEnabled(False)
    if self.within!='Plot':                 
      a=qmenu.addAction('Open scatterplot', self.open_scatterplot)     
      if dc_broken: a.setEnabled(False)
    qmenu.addSeparator()
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
    qmenu.exec_(QtGui.QCursor.pos())

  def open_scatterplot(self):
    win=ScatterPlotWindow(self.dc.master())
    win.add_plot_item(piclass=NodeScatterPlotItem, options={'dc':self.dc.copy()})
    win.show()

  def open_chain_menu(self, dco_index):
    """corresponding to the button right after the dco number dco_index (0based) """
    #print 'open chain menu', dco_index
    qmenu=QtGui.QMenu()
    if dco_index!=-1 and not (self.within=='FeatureExplorer' and dco_index== len(self.dc)-1):
      qmenu.addAction('Inspect data', lambda i=dco_index:self.inspect_data(i))
      #qmenu.addAction('Edit', self.edit_data_channel  )
      qmenu.addSeparator()
    qmenu.addAction('Add component...', lambda i=dco_index:self.open_add_component_menu(i+1) )
    clipboard_text=str(QtGui.QApplication.clipboard().text())
    dc_key=clipboard_text[4:]   if clipboard_text.startswith('#DC#')   else None
    a=qmenu.addAction('Paste/Concatenate Data Channel', lambda i=dco_index,k=dc_key:self.paste_concatenate_dc(k,i+1)  )
    if dc_key is None: a.setEnabled(False)     

    if dco_index!=-1: a=qmenu.addAction('Remove component', lambda i=dco_index:self.remove_dco(i))
    #if (self.dc.is_pre(dco_index) or self.dc.is_post(dco_index)): a.setEnabled(False)
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
     
  def inspect_data(self, dco_index=None):
    """ The dco_index can be provided to get partial (e.g. intermediate dc) data tables. 
    This 0-based index refers to the last DCO in the DC which is actually used"""
    if dco_index is None or dco_index==len(self.dc)-1:
      window_name='FeatExplorerDC.'+str(id(self.dc))
      if self.dc.master().windows().has_window( window_name ): 
        self.dc.master().windows().get_window( window_name ).activateWindow()
      else:
        win=TreedexFeatureExplorer(self.dc)
        win.show()
    else:
      partial_dc=self.dc.copy(index_end=dco_index)
      print 'partial_dc', partial_dc, dco_index
      win=TreedexFeatureExplorer(partial_dc)
      win.show()


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
    print 'update dco', self.__class__, [text, self.dco.parameters]
    if text!=self.dco.parameters:
      self.dco.update(text) #--> self.dco.dc.notify_modification()   
    else: self.dcw.fill() #if modification happened, the fill() will be triggered by signals

class DCOW_join(DCOW):
  """ """
  def __init__(self, dcw, dco):
    super(DCOW_join, self).__init__(dcw, dco) #    QtGui.QWidget.__init__(self)  
    self.layout=QtGui.QVBoxLayout(); self.layout.setContentsMargins(0,0,0,0); self.layout.setSpacing(0)
    self.setLayout(self.layout)
    splt=(self.dco.parameters if not self.dco.parameters is None else '').split('&')
    if len(splt)<2: field='Node'
    else:           _,field=splt
    self.combobox=QtGui.QComboBox() ## !
    self.fill_combobox()
    self.combobox.activated[int].connect( lambda selection_index:self.activated_combobox(selection_index) )
    self.dcw.dc.master().features().signal_dataframe_list_changed.connect(  self.fill_combobox  )  
    self.layout.addWidget(self.combobox)
    self.on_field_textbox=QtGui.QLineEdit()
    self.on_field_textbox.setText(field)
    self.layout.addWidget(self.on_field_textbox)   

  def save(self):
    field=str(self.on_field_textbox.text()).strip()
    if field: field='&'+field
    selection_index=self.selection_index
    av_dfs=self.dcw.dc.get_available_dataframes()
    db_name=av_dfs[selection_index] if av_dfs else None
    new_text=db_name+field
    self.update_dco(new_text)

  def fill_combobox(self):  #slight modification of same method for DCOW_database
    db_name=(self.dco.parameters if not self.dco.parameters is None else '').split('&')[0]
    self.combobox.clear()
    available_dfs=self.dcw.dc.get_available_dataframes()
    self.selection_index=None
    for avdf_i, avdf in enumerate(available_dfs):  
      self.combobox.addItem(avdf)
      if avdf == db_name: self.selection_index=avdf_i
    if not available_dfs:     
      self.combobox.addItem('(No databases available)')
      self.combobox.model().item(0).setEnabled(False)
    if self.selection_index is None: self.selection_index=0
    self.combobox.insertSeparator(self.combobox.count())
    self.combobox.addItem('Load new data ...')
    self.combobox.setCurrentIndex(self.selection_index)

  #totally copied same method for DCOW_database
  def activated_combobox(self, selection_index):   #dco_index should be always 0 for database
    av_dfs=self.dcw.dc.get_available_dataframes()
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

class DCOW_select(DCOW):
  """ """
  def __init__(self, dcw, dco):
    super(DCOW_select, self).__init__(dcw, dco) #    QtGui.QWidget.__init__(self)  
    self.layout=QtGui.QVBoxLayout(); self.layout.setContentsMargins(0,0,0,0); self.layout.setSpacing(0)
    self.setLayout(self.layout)
    text=str(self.dco.parameters) if not self.dco.parameters is None else ''
    self.textbox= QtGui.QLineEdit(text, self)
    self.checkbox=QtGui.QCheckBox(self)
    self.checkbox.setText('include Node')
    if self.dco.parameters and self.dco.parameters.startswith('Node,'):  
      self.textbox.setText(self.dco.parameters[5:])
      self.checkbox.setChecked(True)
    self.layout.addWidget(self.textbox)
    self.layout.addWidget(self.checkbox)

  def save(self):
    new_text= str(self.textbox.text()).strip().strip(',').strip()
    if self.checkbox.isChecked(): new_text='Node,'+new_text
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
    self.dcw.dc.master().features().signal_dataframe_list_changed.connect(  self.fill_combobox  )  

  def fill_combobox(self):
    self.combobox.clear()
    available_dfs=self.dcw.dc.get_available_dataframes()
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
    av_dfs=self.dcw.dc.get_available_dataframes()
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
    av_dfs=self.dcw.dc.get_available_dataframes()
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
    text=str(self.dco.parameters) if not self.dco.parameters is None else ''
    self.textbox= QtGui.QLineEdit(text, self)
    self.layout.addWidget(self.textbox)

  def save(self):
    new_text= str(self.textbox.text()).strip()
    if not new_text: new_text=None
    #else:    new_text+='@master' ### debug
    self.update_dco(new_text)

class DCOW_antenna(DCOW):
  """ """
  possible_values=['Selected nodes', 'Highlighted nodes']

  def __init__(self, dcw, dco):
    super(DCOW_antenna, self).__init__(dcw, dco) #    QtGui.QWidget.__init__(self)  
    self.layout=QtGui.QVBoxLayout(); self.layout.setContentsMargins(0,0,0,0); self.layout.setSpacing(0)
    self.setLayout(self.layout)
    self.combobox=QtGui.QComboBox() 
    self.fill_combobox()
    self.layout.addWidget(self.combobox)
    #self.combobox.activated[int].connect( lambda selection_index:self.activated_combobox(selection_index) )  ## no connection and no function since there's nothing to do until the DCO is saved

  def fill_combobox(self):
    self.combobox.clear()
    for item in self.possible_values:      self.combobox.addItem(item)
    self.combobox.setCurrentIndex(  self.possible_values.index(self.dco.parameters)  )

  def save(self):
    selection_index=self.combobox.currentIndex()
    value=self.possible_values[selection_index]
    self.update_dco(value)

class DCOW_generator(DCOW):
  """ STILL TO IMPLEMENT"""
  def __init__(self, dcw, dco):
    super(DCOW_generator, self).__init__(dcw, dco) #    QtGui.QWidget.__init__(self)  
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


class DCOW_define(DCOW):
  """ """
  def __init__(self, dcw, dco):
    super(DCOW_define, self).__init__(dcw, dco) #    QtGui.QWidget.__init__(self)  
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


class DCOW_call(DCOW):
  """ """
  def __init__(self, dcw, dco):
    super(DCOW_call, self).__init__(dcw, dco) #    QtGui.QWidget.__init__(self)  
    self.layout=QtGui.QVBoxLayout(); self.layout.setContentsMargins(0,0,0,0); self.layout.setSpacing(0)
    self.setLayout(self.layout)
    text=str(self.dco.parameters) if not self.dco.parameters is None else ''
    self.textbox= QtGui.QLineEdit(text, self)
    self.layout.addWidget(self.textbox)

  def save(self):
    new_text= str(self.textbox.text()).strip()
    if not new_text: new_text=None
    self.update_dco(new_text)

class DCOW_group(DCOW):
  def __init__(self, dcw, dco):
    super(DCOW_group, self).__init__(dcw, dco) #    QtGui.QWidget.__init__(self)  
    self.layout=QtGui.QHBoxLayout(); self.layout.setContentsMargins(1,1,1,1); self.layout.setSpacing(5)
    self.setLayout(self.layout)
    text=self.dco.parameters[ : self.dco.parameters.index('[') ] if self.dco.parameters else ''
    self.textbox=QtGui.QLineEdit(text, self)
    self.textbox.setMaximumWidth(100)
    self.layout.addWidget(self.textbox)
    dcw=DataChannelWidget(self.dco.dc) #self.clipboard_dc)
    self.layout.addWidget(dcw)

  def save(self):
    name= str(self.textbox.text()).strip()
    new_text='{n}[{k}]'.format(k=self.dco.dc.key(), n=name)
    if not new_text:      new_text=None
    self.update_dco(new_text)
    


DCO_categories=[ ['Start', ['database', 'retrieve', 'antenna', 'generator']],\
                 ['Row operations', ['filter', 'append', 'aggregate', 'transform']],\
                 ['Column operations', ['select', 'rename', 'process', 'compute', 'join']],\
                 ['DC management', ['cache', 'define', 'var', 'call', 'group']],\
                 ['Tree', ['trace']],\
               ]
DCO_descriptions={'database':'Start with a data-frame table', 
                  'select':'Select one or more columns',}
DCO_name2widget={'database':DCOW_database, 'select':DCOW_select, 'filter':DCOW_filter, 'process':DCOW_process, 'compute':DCOW_compute, 'rename':DCOW_rename, 'aggregate':DCOW_aggregate, 'join':DCOW_join, 'cache':DCOW_cache, 'retrieve':DCOW_retrieve, 'define':DCOW_define, 'call':DCOW_call, 'antenna':DCOW_antenna, 'generator':DCOW_generator, 'group':DCOW_group, 'var':DCOW_var}


class ExtendDataChannelWidget(QtGui.QWidget):
  class SearchBox(QtGui.QLineEdit): 
    def focusOutEvent(self, e): return self.parent().focusOutEvent(e)

  def __init__(self, dcw, dco_index):
    super(ExtendDataChannelWidget, self).__init__() #    QtGui.QWidget.__init__(self)  
    self.dcw=dcw; self.dco_index=dco_index
    vlayout=QtGui.QVBoxLayout()
    self.setLayout(vlayout)
    self.setWindowTitle('Add Data Channel component...')
    self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
    self.search_layout=QtGui.QHBoxLayout()
    self.dashboard_layout=QtGui.QVBoxLayout()
    self.all_dcos_layout=QtGui.QVBoxLayout()
    vlayout.addLayout(self.search_layout); vlayout.addLayout(self.dashboard_layout); vlayout.addLayout(self.all_dcos_layout)
    ### search
    self.search_box=self.SearchBox(parent=self)
    self.search_box.textEdited.connect(self.edited_search_box)
    search_button=  ToolButton('searchglass', 'Search for components')    
    self.search_layout.addWidget(self.search_box); self.search_layout.addWidget(search_button)
    self.fill()
    self.show()
    self.place()
    self.setFocus(True)
    self.search_box.setFocus(True)

  def clear_layouts(self):
    clear_layout(self.dashboard_layout)
    clear_layout(self.all_dcos_layout)

  def fill(self):
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
                          if not searched or dco_name.find(searched)!=-1 or (dco_name in DCO_descriptions and DCO_descriptions[dco_name].find(dco_name)!=-1)]
      if not filtered_dco_names: continue
      some_hit=True
      self.all_dcos_layout.addWidget(HorizontalLine())
      row_title=QtGui.QHBoxLayout()
      row_title.addWidget(QtGui.QLabel(category)); row_title.addStretch()
      self.all_dcos_layout.addLayout(row_title)

      for dco_name in filtered_dco_names:
        row=QtGui.QHBoxLayout()
        button=ToolButton(dco_name, dco_name.capitalize())
        button.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        button.clicked.connect( lambda s,n=dco_name:self.add_dco(n) )
        row.addWidget(button) #        row.addWidget(QtGui.QLabel(dco_name.capitalize()))
        desc='' if not dco_name in DCO_descriptions else DCO_descriptions[dco_name]
        desc_label=QtGui.QLabel(desc)
        desc_label.setStyleSheet('color:darkgrey')
        row.addWidget(desc_label)
        row.addStretch()
        self.all_dcos_layout.addLayout(row)
    if not some_hit:
      row=QtGui.QHBoxLayout()
      row.addWidget(QtGui.QLabel('No components match your query'))
      row.addStretch()
      self.all_dcos_layout.addLayout(row)
    self.all_dcos_layout.addStretch()

    
  def place(self):   self.move(QtGui.QCursor.pos())

  def edited_search_box(self, text):
    text=str(text)
    print 'edited search box', text
    self.fill()

  def add_dco(self, name):
    self.dcw.add_dco(name, self.dco_index)
    self.close()

  def focusOutEvent(self, e):
    """ To make sure this widget cease to exists when you click somewhere else, like a qmenu"""
    super(ExtendDataChannelWidget, self).focusOutEvent(e)
    #print 'focus out!', e, e.gotFocus(), e.lostFocus(), e.reason()
    if e.lostFocus() and e.reason()==QtCore.Qt.ActiveWindowFocusReason: self.close()

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
    if self.master().features().has_dataframe(df_name):
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

      df= DataFrame(data=pd_df, name=df_name, node_field=node_field)  #treedex dataframe
      self.master().features().add_dataframe(df, overwrite=overwrite)
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
class TreedexTableWidget(QtGui.QTableWidget):
  default_options={'display_index':None, 'max_column_width':220} #display_index forces showing index in column '0'  #Node -> auto; False/True -> forced
  def __init__(self, data=None):
    super(TreedexTableWidget, self).__init__() 
    self.setSelectionBehavior(QtGui.QAbstractItemView.SelectItems) #QAbstractItemView.SelectRows)   
    self.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)   #disabling editing
    self.options=dict(self.default_options) 
    self.setSortingEnabled(True)
    self.data=None
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
    self.table_index2data_index={}
    for tab_index, data_index in enumerate(self.data.index):
      self.table_index2data_index[ tab_index ]=data_index

  def fill(self):
    self.clear()
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
      self.horizontalHeaderItem(col_i).setToolTip(column_name)
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
        try:                    text+=str(self.item(i,c).text()) + "\t"
        except AttributeError:  text+="\t"
      if text: text=text[:-1]+'\n'
    return text

  ##### copy
  def copy_selected(self):
    """ Copy the text of the cells currently selected in the system clipboard. Sparse selections are not permitted: if you select some column, that will be selected in every row with at least one cell selected. This is thought to copy paste the selection to an excel file"""
    text=self.get_selected_text(include_headers=True)
    if text: QtGui.QApplication.clipboard().setText(text)  

  def add_menu_actions(self,  menu): 
    pass


   
###############################################################################
## TODO: update TreedexFeatureExplorer to use DataChannelTable instead of more generic TreedexTableWidget
# class DataChannelTable(TreedexTableWidget):
#   """ Init with any DataChannel to open an interactive table window (non-editable)"""
#   def __init__(self, dc):
#     super(DataChannelTable, self).__init__()
#     self.master_link=None
#     self.update(dc)

  # def update(self, dc):
  #   self.master_link=dc.master()
  #   self.set_data(dc.out())
  #   #title=dc.summary();    self.setWindowTitle(title)
  #   self.fill()

  # def add_menu_actions(self, menu):    
  #   print 'aio'
  #   if self.node_info_available():
  #     menu.addSeparator()
  #     menu.addAction('Select these nodes', self.select_nodes)

  # #### nodes
  # def node_info_available(self):
  #   if self.data is None: return 0
  #   if   'Node' in self.data.columns:   return 1
  #   elif self.data.index.name=='Node':  return 2
  #   else: return 0

  # def select_nodes(self):   
  #   all_row_indexes=set()
  #   for r in self.selectedRanges():  
  #     for index in range(r.topRow(), r.bottomRow()+1):            all_row_indexes.add(index)
  #   node_data_type=self.node_info_available #1-> Node is a column;  2-> Node is the index
  #   if node_data_type==2:
  #     ns=NodeSelector( [ self.table_index2data_index[i]  for i in all_row_indexes ] )    
  #   elif node_data_type==1:
  #     col_index=self.data.columns.index('Node')
  #     ns=NodeSelector() 
  #     for i in all_row_indexes:
  #       di=self.table_index2data_index[i]
  #       node=self.data.at[di,col_index]
  #       ns.add(node)
  #   self.master_link.selections().edit_node_selection('Selected nodes', ns)

###############################################################################

class TreedexFeatureExplorer(TreedexWindow):
  default_options={'auto_resize':1}
  default_table_options={'display_index':None}
  def window_identifier(self):    return {'window_name':'FeatExplorerDC.'+str(id(self.dc))}
  def master(self): return self.dc.master()
  def __init__(self, dc, options={}, title=None):
    self.dc=dc  #.Master() must be available when init is called
    super(TreedexFeatureExplorer, self).__init__()  
    self.setWindowTitle('Treedex - feature explorer')
    self.layout=QtGui.QVBoxLayout();     self.layout.setContentsMargins(1, 1, 1, 1);     self.layout.setSpacing(2)    
    self.dc_layout=QtGui.QHBoxLayout();  #self.dc_layout.setContentsMargins(0, 0, 0, 0);  self.dc_layout.setSpacing(0)
    self.opt_layout=QtGui.QHBoxLayout(); #self.opt_layout.setContentsMargins(0, 0, 0, 0); self.opt_layout.setSpacing(0)
    self.tab_layout=QtGui.QHBoxLayout(); self.tab_layout.setContentsMargins(0, 0, 0, 0); self.tab_layout.setSpacing(0)
    self.setLayout(self.layout)
    self.layout.addLayout(self.dc_layout)
    self.layout.addLayout(self.opt_layout)
    self.indicator_nodata= QtGui.QWidget(); self.indicator_nodata.setStyleSheet('background:white')
    self.indicator_nodata.layout=QtGui.QVBoxLayout(); self.indicator_nodata.setLayout(self.indicator_nodata.layout)
    self.indicator_nodata.label=QtGui.QLabel('No data to display')
    self.indicator_nodata.layout.addWidget(self.indicator_nodata.label)
    self.layout.addWidget(self.indicator_nodata)
    self.layout.addLayout(self.tab_layout)

    self.options=dict(self.default_options)
    self.options.update(options)
    
    self.opt_layout.addWidget(QtGui.QLabel('Show index'))
    self.display_index_combobox=QtGui.QComboBox()
    self.display_index_combobox.possible_values=[(None, 'Auto'), (False,'No'), (True,'Yes')]
    for _, i in self.display_index_combobox.possible_values: self.display_index_combobox.addItem(i)
    self.display_index_combobox.activated[int].connect(self.activated_display_index_combobox)
    self.opt_layout.addWidget(self.display_index_combobox)
    self.opt_layout.addStretch()
    for i in range(self.opt_layout.count()): 
      w=self.opt_layout.itemAt(i).widget()
      if w: w.setSizePolicy(fixed_size_policy)

    self.table=TreedexTableWidget()
    self.table.options.update(self.default_table_options)
    self.tab_layout.addWidget(self.table)
    self.set_dc(dc, first_run=True) # a little redundant with prior self.dc=dc but necessary
    self.update_table()

  def set_dc(self, dc, first_run=False):
    if not first_run:      
      self.dc.signal_dc_changed.disconnect(self.update_table)
      self.dc.signal_value_changed.disconnect(self.update_table)

    self.dc=dc 
    clear_layout(self.dc_layout)
    label=QtGui.QLabel('Data Channel:')
    label.setSizePolicy(fixed_size_policy)
    self.dc_layout.addWidget(label)
    self.dc_layout.addWidget( DataChannelWidget(self.dc, within='FeatureExplorer'))  
    self.dc_layout.addStretch()
    self.dc.signal_dc_changed.connect(self.update_table)
    self.dc.signal_value_changed.connect(self.update_table)
    
  def activated_display_index_combobox(self, index):
    flag, label =self.display_index_combobox.possible_values[index]
    if flag!=self.table.options['display_index']: 
      self.table.options['display_index']=flag
      self.update_table()
    
  def update_table(self):
    if not self.dc.validated is None:
      self.table.clear(); self.table.setRowCount(0); self.table.setColumnCount(0)
      self.indicator_nodata.label.setText('ERROR in Data Channel:\n'+str(self.dc.validated[1]))
      self.indicator_nodata.setVisible(True)
      return 
    data=self.dc.out()
    if data is None: #empty
      self.table.clear(); self.table.setRowCount(0); self.table.setColumnCount(0)
      self.indicator_nodata.label.setText('No data available')
      self.indicator_nodata.setVisible(True)
    else:
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
