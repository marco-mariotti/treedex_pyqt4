from .base   import *
from ..data  import *
from .plots import *
import numpy as np                  #only to check type of entry np.floating and np.integer

fixed_size_policy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
class DataChannelWidget(QtGui.QWidget): 
  """ Widget to create, modify and inspect DataChannel instances"""
  style={'base': 'QWidget{ background: #d6d6d6; padding: 0px; selection-background-color: #4444DD } \
                  QLineEdit { background: white }  QComboBox { background: white }', 
         'pre':  'QWidget{ background: #a5a5a5 }   QComboBox { background: white }',
         'post':   'QWidget{ background: #a5a5a5 } QComboBox { background: white }',
         'broken':  'background: #bb1111',}

  def __init__(self, dc, within=None):
    super(DataChannelWidget, self).__init__() #    QtGui.QWidget.__init__(self)  
    self.dc=dc
    self.within=within
    self.editing=None #index of DCO currently being edited
    self.setStyleSheet( self.style['base'] )
    self.layout=QtGui.QHBoxLayout(); self.layout.setContentsMargins(0, 0, 0, 0); self.layout.setSpacing(2)
    self.setLayout(self.layout)   #One widget per DCO here, followed by a vline;  plus last one for menu
    self.setSizePolicy(fixed_size_policy)   #### NOT WORKING PROPERLY
    self.fill()
    self.dc.signal_dc_changed.connect(self.dc_changed)

  def fill(self):
    clear_layout(self.layout)
    if not self.dc.chain:      self.layout.addWidget(empty_DC(self))      
    for dco_index, dco in enumerate(self.dc.chain):
      w=QtGui.QWidget()    # w is dedicated to this DCO
      #self.layout.itemAt( dco_index*2 ).widget()  --> recovers w
      # if self.dc.is_pre(dco_index):        w.setStyleSheet( self.style['pre'] )
      # if self.dc.is_post(dco_index):       w.setStyleSheet( self.style['post'] )      
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

      tool_button=ToolButton(dco.name, dco.name.capitalize(), lambda s,i=dco_index:self.edit_dco(i) )  
      w.layout.addWidget(tool_button)

      if self.editing==dco_index:        
        #we're editing this DCO
        #w.setStyleSheet('QWidget {background: yellow} ')
        dcow= DCO_name2widget[dco.name] (self, dco)
        w.layout.addWidget( dcow )
        tool_button.clicked.connect( dcow.save ) 
        # first trigger:   set self.editing 
        # if dco has been modified:
        #  --> this will call self.dc.notify_modification        #  --> triggers self.dc.signal_dc_changed
        #   --> self.dc_changed --> self.dc.validate() and self.fill()  ## on any DCW with this DC
        # else:  self.fill()

      else:
        dco_key=dco.short()    #label with dco parameters
        if not dco_key: dco_key='(None)'
        qlabel=QtGui.QLabel( dco_key ) 
        qlabel.setSizePolicy(fixed_size_policy)
        w.layout.addWidget(qlabel)
        if not self.editing is None:         #we're editing another DCO
          w.setEnabled(False)
        #else:           #we're not editing any DCO

        if 1: #not self.dc.is_pre(dco_index+1) and not self.dc.is_post(dco_index):
          # vline= QtGui.QFrame()            #vertical line to separate from previous dco
          # vline.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Expanding)
          # vline.setFrameStyle(QtGui.QFrame.VLine)
          # self.layout.addWidget(vline)
          chain_button=QtGui.QPushButton(">") 
          chain_button.setStyleSheet('padding: 0px')
          chain_button.setFixedSize(10, 20)  
          #action=QtGui.QAction(get_icon('chain'), 'Chain Menu...', chain_button)
          #chain_button.setDefaultAction(action)
          chain_button.setSizePolicy(fixed_size_policy)
          chain_button.clicked.connect(   lambda s,i=dco_index: self.open_chain_menu(i)    )
          w.layout.addWidget(chain_button)

      self.layout.addWidget(w)
      self.layout.addWidget(VerticalLine())

    menu_button=ToolButton('menu', 'DataChannel Menu...', self.open_menu)
    menu_button.setSizePolicy(fixed_size_policy)
    if not self.editing is None:  menu_button.setEnabled(False)
    self.layout.addWidget(menu_button)

  def open_menu(self):      
    qmenu=QtGui.QMenu()
    #qmenu.addAction('Edit', self.edit_data_channel  )
    if self.within!='FeatureExplorer':
      qmenu.addAction('Inspect data', self.inspect_data)
    if self.within!='Plot':      
      qmenu.addAction('Open scatterplot', self.open_scatterplot)     
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
    win=ScatterPlotWindow(self.dc.master_link)
    win.add_plot_item( {'main_dc':self.dc} )
    win.show()

  def open_chain_menu(self, dco_index):
    print 'open chain menu', dco_index
    qmenu=QtGui.QMenu()
    if not (self.within=='FeatureExplorer' and dco_index== len(self.dc)-1):
      qmenu.addAction('Inspect data', lambda i=dco_index:self.inspect_data(i))
      #qmenu.addAction('Edit', self.edit_data_channel  )
      qmenu.addSeparator()
    if 1: #not (self.dc.is_pre(dco_index+1) or self.dc.is_post(dco_index)) : 
      submenu_add_component=QtGui.QMenu('Add component')
      for dco_name in available_DCOs:
        if (dco_name =='database' and not len(self.dc.chain)==0): continue            
        submenu_add_component.addAction(dco_name.capitalize(),          # get_icon(dco_name), ### icon not working why???
                                        lambda i=dco_index,n=dco_name:self.add_dco(n,i+1) )
      submenu_add_component.addSeparator()
      clipboard_text=str(QtGui.QApplication.clipboard().text())
      dc_key=clipboard_text[4:]   if clipboard_text.startswith('#DC#')   else None
      a=submenu_add_component.addAction('Paste/Concatenate Data Channel', lambda i=dco_index,k=dc_key:self.paste_concatenate_dc(k,i+1)  )
      if dc_key is None: a.setEnabled(False)
      
      qmenu.addMenu(submenu_add_component)
    a=qmenu.addAction('Remove component', lambda i=dco_index:self.remove_dco(i))
    #if (self.dc.is_pre(dco_index) or self.dc.is_post(dco_index)): a.setEnabled(False)
    qmenu.exec_(QtGui.QCursor.pos())

  def edit_dco(self, index):
    if self.editing==index: 
      self.editing=None
    else:                   
      self.editing=index
      self.fill()

  def add_dco(self, dco_name, index=None):
    print 'add_dco', dco_name, index
    dco=  DCO_name2class[dco_name] ()  #default parameters
    if index is None:   self.dc.append(dco)
    else:               self.dc.insert(index, dco)
    self.edit_dco(index)
    self.dc.notify_modification()
    #self.fill()
    #self.dc.dc_was_modified()   #not doing this just becase: new DCO are initialized empty, thus neutral

  def remove_dco(self, index=None): 
    self.dc.pop(index) #when None, the last one is removed
    self.fill()
    self.dc.notify_modification()

  def copy_data_channel(self):  
    k="#DC#"+self.dc.key()
    QtGui.QApplication.clipboard().setText(k)
    print 'copy DC! '+k

  def paste_concatenate_dc(self, dc_key, index=None):    
    print 'paste_dc', dc_key, index
    pasted_dc=DataChannel(self.dc.master_link, from_key=dc_key)
    if index==1 and self.dc.chain[0].summary()=='database:None':      self.dc.pop(0)
    self.dc.concatenate(pasted_dc, index) #when index is none, append
    self.dc.notify_modification()
  
  def paste_replace_dc(self, dc_key):
    print 'paste_replace_dc', dc_key
    if len(self.dc.chain)>1:
      pressed_button=QtGui.QMessageBox.warning(self, 'Warning', 'This will delete the current content of the Data Channel. Are you sure?', QtGui.QMessageBox.Cancel, QtGui.QMessageBox.Ok)
      #confirm_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
      if pressed_button==QtGui.QMessageBox.Cancel: 
        print 'cancel! not saving'
        return 
    pasted_dc=DataChannel(self.dc.master_link, from_key=dc_key)
    self.dc.chain=[]
    self.dc.concatenate(pasted_dc) 
    self.dc.notify_modification()

  def save_data_channel(self):      print 'save DC! well not today'
     
  def inspect_data(self, dco_index=None):
    """ The dco_index can be provided to get partial (e.g. intermediate dc) data tables. 
    This 0-based index refers to the last DCO in the DC which is actually used"""
    if dco_index is None or dco_index==len(self.dc)-1:
      window_name='FeatExplorerDC.'+str(id(self.dc))
      if self.dc.master_link.windows().has_window( window_name ): 
        self.dc.master_link.windows().get_window( window_name ).activateWindow()
      else:
        win=TreedexFeatureExplorer(self.dc)
        win.show()
    else:
      partial_dc=self.dc.copy(index_end=dco_index)
      win=TreedexFeatureExplorer(partial_dc)
      win.show()

  def dc_changed(self):
    self.dc.validate()  # this stores the result in self.dc.validated
    self.fill()

class empty_DC(QtGui.QWidget):
  def __init__(self, dcw):
    super(empty_DC, self).__init__() #    QtGui.QWidget.__init__(self)  
    self.dcw=dcw
    self.frame_layout=QtGui.QVBoxLayout(); self.frame_layout.setContentsMargins(0, 0, 0, 0); self.frame_layout.setSpacing(0)
    self.setLayout(self.frame_layout)
    self.layout=QtGui.QHBoxLayout(); self.layout.setContentsMargins(2, 2, 2, 2); self.layout.setSpacing(0)
    self.frame_layout.addWidget(HorizontalLine())
    self.frame_layout.addLayout(self.layout)
    self.frame_layout.addWidget(HorizontalLine())
    tool_button=ToolButton('empty_data_channel', "Empty Data Channel", self.open_menu)
    tool_button.setSizePolicy(fixed_size_policy)
    self.layout.addWidget(tool_button)
    self.layout.addWidget(QtGui.QLabel('(Empty)'))    

  def open_menu(self):
    qmenu=QtGui.QMenu()
    qmenu.addAction('Add database component',  lambda dc=self.dcw.dc: dc.append(DCO_database()) )  
    clipboard_text=str(QtGui.QApplication.clipboard().text())
    dc_key=clipboard_text[4:]   if clipboard_text.startswith('#DC#')   else None
    a=qmenu.addAction('Paste Data Channel', lambda k=dc_key:self.dcw.paste_replace_dc(k)  )
    if dc_key is None: a.setEnabled(False)
    qmenu.exec_(QtGui.QCursor.pos())


########################################################################################
class DCOW(QtGui.QWidget):
  def __init__(self, dcw, dco):
    super(DCOW, self).__init__() #    QtGui.QWidget.__init__(self)  
    self.dcw=dcw
    self.dco=dco
  #def dco(self): return self.dco_link #self.dc.chain[self.dco_index]
  def save(self): raise Exception, "ERROR no save function for this DCO_widget!"
  def update_dco(self, text):
    if text!=self.dco.parameters:
      self.dco.update(text)
      self.dcw.dc.notify_modification()   
    else: self.dcw.fill() #if modification happened, the fill() will be triggered by signals

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
    new_text= str(self.textbox.text()).strip().strip(',')
    if self.checkbox.isChecked(): new_text='Node,'+new_text
    if not new_text.strip():    new_text=None
    self.update_dco(new_text)

class DCOW_filter(DCOW):
  """ """
  def __init__(self, dcw, dco):
    super(DCOW_filter, self).__init__(dcw, dco) #    QtGui.QWidget.__init__(self)  
    self.layout=QtGui.QVBoxLayout(); self.layout.setContentsMargins(0,0,0,0); self.layout.setSpacing(0)
    self.setLayout(self.layout)
    text=str(self.dco.parameters) if not self.dco.parameters is None else ''
    self.textbox= QtGui.QLineEdit(text, self)
    self.layout.addWidget(self.textbox)

  def save(self):
    new_text= str(self.textbox.text()).strip()
    if not new_text.strip(): new_text=None
    self.update_dco(new_text)

class DCOW_process(DCOW):
  """ """
  def __init__(self, dcw, dco):
    super(DCOW_process, self).__init__(dcw, dco) #    QtGui.QWidget.__init__(self)  
    self.layout=QtGui.QVBoxLayout(); self.layout.setContentsMargins(0,0,0,0); self.layout.setSpacing(0)
    self.setLayout(self.layout)
    text=str(self.dco.parameters) if not self.dco.parameters is None else ''
    self.textbox= QtGui.QLineEdit(text, self)
    self.layout.addWidget(self.textbox)

  def save(self):
    new_text= str(self.textbox.text()).strip()
    if not new_text.strip(): new_text=None
    self.update_dco(new_text)

class DCOW_rename(DCOW):
  """ """
  def __init__(self, dcw, dco):
    super(DCOW_rename, self).__init__(dcw, dco) #    QtGui.QWidget.__init__(self)  
    self.layout=QtGui.QVBoxLayout(); self.layout.setContentsMargins(0,0,0,0); self.layout.setSpacing(0)
    self.setLayout(self.layout)
    self.pairs=[]  # list of tuples of len 2; each object is a textbox
    input_text=self.dco.parameters or '>'
    for row_index, pair in enumerate(input_text.split(',')):
      oldK, newK= pair.split('>')
      self.add_pair(oldK, newK)
    add_button=ToolButton('plus', 'Add a renaming item', lambda s:self.add_pair())
    self.layout.addWidget(add_button)

  def add_pair(self, oldK='', newK=''):
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
      text1= str(textbox1.text()).strip()
      text2= str(textbox2.text()).strip()
      if not text1 and not text2: continue
      if not text1 or not text2: raise Exception, "ERROR renaming fields cannot be left empty!"
      if not check_forbidden_characters(text1) or not check_forbidden_characters(text2): 
          raise Exception, "ERROR one or more forbidden character detected in renaming fields!"
      tot_text+=text1+'>'+text2+','
    final=tot_text[:-1] if tot_text else None
    self.update_dco(final)

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
    self.dcw.dc.master_link.features().signal_dataframe_list_changed.connect(  self.fill_combobox  )  
    self.loader=None  #slot for widget for loading features

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
    if self.dcw.dc.master_link.windows().has_window('FeatureLoader'): 
      self.dcw.dc.master_link.windows().get_window('FeatureLoader').activateWindow()
    else:
      loader=FeatureLoader(self.dcw.dc.master_link)
      loader.show()

  def save(self):
    selection_index=self.selection_index
    av_dfs=self.dcw.dc.get_available_dataframes()
    dataframe_name=av_dfs[selection_index] if av_dfs else None
    self.update_dco(dataframe_name)

DCO_name2widget={'database':DCOW_database, 'select':DCOW_select, 'filter':DCOW_filter, 'process':DCOW_process, 'rename':DCOW_rename, 'aggregate':DCOW_aggregate}

#################################################

class FeatureLoader(TreedexWindow):
  def window_identifier(self): return {'window_name':'FeatureLoader'}
  def Master(self):            return self.master_link
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
    if self.master_link.features().has_dataframe(df_name):
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
      self.master_link.features().add_dataframe(df, overwrite=overwrite)
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
    if not data is None: self.set_data(data)

  def set_data(self, data):
    """ Thought for pandas objects, but generic enough (DataFrame, Series), list etc) """
    if not hasattr(data, 'shape'): data=pd.DataFrame(data) #if not DataFrame or Series
    self.data=data

  def fill(self):
    if    len(self.data.shape)==2:        n_rows, n_cols=self.data.shape   #dataframe
    elif  len(self.data.shape)==1:        n_rows=self.data.shape; n_cols=1 #series  
    index_col_present= int( not (type(self.data.index) == pd.indexes.range.RangeIndex and not self.data.index.name) 
                            if self.options['display_index'] is None else  self.options['display_index'] ) #keeping it as int (0/1) 
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

    hheader=self.horizontalHeader()
    hheader.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
    hheader.customContextMenuRequested.connect(self.open_horizontal_header_menu) #right click
    hheader.sectionClicked.connect(self.clicked_horizontal_header)       #left click
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
    for col_i in range(self.columnCount()):
      if self.columnWidth(col_i)>self.options['max_column_width']: 
          self.setColumnWidth(col_i, self.options['max_column_width'])
    #setting an attribute to keep track of sorting and hidden columns
    self.visible_fields = self.visible_fields={i:True for i in range(n_cols+1)}
    hheader.setSortIndicator(n_cols, 0) #setting sort based on invisible order column
    self.sorting=(hheader.sortIndicatorOrder(), hheader.sortIndicatorSection())
    #print 'sorting', self.sorting
    self.toggle_column(n_cols)

  def toggle_column(self, index):
    """ Show or hide the column index. """
    self.visible_fields[index]=not self.visible_fields[index]
    if self.visible_fields[index]:    self.horizontalHeader().showSection(index)
    else:                             self.horizontalHeader().hideSection(index)  

  def sizeHint(self):   
    height = QtGui.QTableWidget.sizeHint(self).height()
    width= sum([self.horizontalHeader().sectionSize(col_i) for col_i in range(self.columnCount()) ]) #for the hidden ones is zero
    width += self.verticalHeader().width()        
    width += self.verticalScrollBar().sizeHint().width()    
    margins = self.contentsMargins()
    width += margins.left() + margins.right()   
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
      if self.node_info_available():
        menu.addSeparator()
        menu.addAction('Select these nodes', self.select_nodes)
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

  def select_nodes(self):    print 'select these nodes! well not today'

  ##### copy
  def copy_selected(self):
    """ Copy the text of the cells currently selected in the system clipboard. Sparse selections are not permitted: if you select some column, that will be selected in every row with at least one cell selected. This is thought to copy paste the selection to an excel file"""
    text=self.get_selected_text(include_headers=True)
    if text: QtGui.QApplication.clipboard().setText(text)  

  #### nodes
  def node_info_available(self):
    if self.data is None: return 0
    if   'Node' in self.data.columns:   return 1
    elif self.data.index.name=='Node':  return 2
    else: return 0
  
###############################################################################
class DataChannelTable(TreedexTableWidget):
  """ Init with any DataChannel to open an interactive table window (non-editable)"""
  def __init__(self, dc):
    super(DataChannelTable, self).__init__() #text, color=color, anchor=anchor)
    self.update(dc)

  def update(self, dc):
    self.set_data(dc.out())
    title=dc.summary()
    self.setWindowTitle(title)
    self.fill()
###############################################################################

class TreedexFeatureExplorer(TreedexWindow):
  default_options={'auto_resize':1}
  default_table_options={'display_index':None}
  def window_identifier(self):    return {'window_name':'FeatExplorerDC.'+str(id(self.dc))}
  def Master(self): return self.dc.master_link
  def __init__(self, dc, options={}, title=None):
    self.dc=dc  #.Master() must be available when init is called
    super(TreedexFeatureExplorer, self).__init__()  
    self.layout=QtGui.QVBoxLayout();     self.layout.setContentsMargins(0, 0, 0, 0);     self.layout.setSpacing(2)    
    self.dc_layout=QtGui.QHBoxLayout();  self.dc_layout.setContentsMargins(0, 0, 0, 0);  self.dc_layout.setSpacing(0)
    self.opt_layout=QtGui.QHBoxLayout(); self.opt_layout.setContentsMargins(0, 0, 0, 0); self.opt_layout.setSpacing(0)
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
    self.set_dc(dc) # a little redundant with prior self.dc=dc but necessary
    self.update_table()

  def set_dc(self, dc):
    self.dc=dc 
    clear_layout(self.dc_layout)
    label=QtGui.QLabel('Data Channel:')
    label.setSizePolicy(fixed_size_policy)
    self.dc_layout.addWidget(label)
    self.dc_layout.addWidget( DataChannelWidget(self.dc, within='FeatureExplorer'))  
    self.dc_layout.addStretch()
    self.dc.signal_dc_changed.connect(self.update_table)
    
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
      if self.options['auto_resize']:      self.resize(self.table.sizeHint())
