from ..base import *
from ...data  import *
from ...common import *
from ..datawidgets import *

def set_black_theme():
  """Set the black theme for scatterplots; all those opened after this is called will be affected """
  pg.setConfigOption('background', 'k')
  pg.setConfigOption('foreground', 'w')

def set_white_theme():
  """Set the white theme for scatterplots; all those opened after this is called will be affected """
  pg.setConfigOption('background', 'w')
  pg.setConfigOption('foreground', 'k')
set_white_theme()

NoDefault=object()
def smart_get(what, local_options, df, row_i, default=NoDefault):
  fallback_value=local_options[what] if default is NoDefault else default
  if not what in df.columns:   return fallback_value
  x=df.at[row_i, what]
  try:
    if pd.isnull(x):                   return fallback_value   #falls on default if no value for this row # is None or np.isnan(x)
  except ValueError:
    write( 'array given to isnull! df={}\n\nrow_i={} what={}\nx={}'.format(df, row_i, what, x), 1, how='red,reverse')
    return fallback_value
  return x

coordinate_names=['x', 'y', 'z']
######################################################################
############################################# Base class #############
class PlotWindow(TreedexWindow): 
  """ Motherclass for all windows of plots. Every subclass must define:
Class attributes:
  -available_plot_items    list of PlotItem subclasses that be added with self.add_plot_item
  -dimensions              integer. Used for high-level manipulation of axis labels
Instance attributes:
  -menu_layout             here the active menus will be added
Methods:
  -set_axis_label(self, index_dimension, label)     set this label as axis for the plot
  """
  available_plot_items=[]
  dimensions=None
  #default_plot_options={'auto_axis_labels':True}
  def __init__(self, dco_link): 
    self.dco_link=dco_link   
    c=self.dco_link
    while not c.container is None: c=c.container
    self.master_link=c
    #self.container=master_link

    TreedexWindow.__init__(self)
    self.plot_items=[]
    self.active_menu=[]     ## plot_item, category, menu, button
    self.axis_labels=[]
    #self.plot_options=deepcopy(self.default_plot_options)
 
  def master(self): return self.master_link
  def window_identifier(self): return {'category': self.__class__.__name__}
  def delete_data_channels(self):
     for pi in self.plot_items:       pi.delete_item() #this will flush all DCs
  def add_plot_item(self, piclass, options=None, cache_name='PlotInput'):
    """ Init a plotitem class with options and add it to the plot_object of this window. 
       No need to reimplement this for window subclasses. The majority of the job is done actually in the __init__ of the plotitems"""
    if options is None: options={}
    if not 'name' in options:
      #for pi in self.plot_items:
      #  print pi.plot_type, piclass.plot_type, pi.plot_type==piclass.plot_type
      index=len([1 for pi in self.plot_items if pi.plot_type==piclass.plot_type])+1
      name='{}.{}'.format(piclass.plot_type, index)
      options['name']=name
    pi=piclass(self.plot_object, cache_name=cache_name, options=options)
    self.plot_items.append(pi)
    tb=pi.toolbar_class(pi)
    tb.setAutoFillBackground(True)
    pi.toolbar=tb
    self.toolbar_layout.addWidget(tb)
    self.update_axis()
    return pi
    
  def remove_plot_item(self, pi):
    pi.delete_item()
    index=self.plot_items.index(pi)
    self.plot_items.pop(index)
    clear_layout(self.toolbar_layout, index=index)
    self.update_axis()

  def hide_menu(self):
    #write('hide menu!', 1)
    if self.active_menu:
      #self.active_menu[2].setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
      self.active_menu[3].setStyleSheet( self.active_menu[3].stylesheet  ) # back to basic style
      clear_layout(self.menu_layout)
      #for i in reversed(range(self.menu_layout.count())):      self.menu_layout.itemAt(i).widget().deleteLater()
      self.active_menu[0].toolbar.active_label.setText('')
    self.active_menu=[]

  def update_axis(self):
    print 'updating axis'
    self.axis_labels=[]
    for dim in range(self.dimensions):
      # coord_name=coordinate_names[dim]
      label_pieces=[]
      for pi in self.plot_items:
        header=pi.headers[dim]
        if not header in label_pieces: label_pieces.append(header)
      label=' | '.join(label_pieces)      
      self.axis_labels.append(label)

    for dim, label  in enumerate(self.axis_labels):      
      self.set_axis_label(dim, label)  #class specific method

  # def get_plot_items(self): return self.plot_items

  # def update_axis(self):
  #   axis_labels=[] 
  #   for item_index, plot_item in enumerate(self.get_plot_items()):
  #     for index_dimension, label in enumerate(plot_item.get_axis_labels()): 
  #       if not item_index: axis_labels.append(label)
  #       else:              axis_labels[index_dimension]+=' / '+label
  #   for index_dimension, axis_label in enumerate(axis_labels):      self.set_axis_label(index_dimension, axis_label)
  #   boundaries=[plot_item.get_boundaries() for item_index, plot_item in enumerate(self.get_plot_items())   ]

  #   for index_dimension in range(len(axis_labels)):   #axis_labels as excuse
  #     min_this_dimension=min( [b[index_dimension][0] for b in boundaries]  )  #)
  #     max_this_dimension=max( [b[index_dimension][1] for b in boundaries]  )  #)
  #     #adding a 4% per side
  #     add=(max_this_dimension-min_this_dimension)/25.0
  #     self.set_axis_range(index_dimension, min_this_dimension-add, max_this_dimension+add )
      
  # def set_axis_label(self, index_dimension, label):     raise Exception, "ERROR this function must be defined in subclasses!"
  # def set_axis_range(self, index_dimension, min_this_dimension, max_this_dimension): raise Exception, "ERROR this function must be defined in subclasses!" 

  # def update_toolbar_looks(self):
  #   if self.toolbar_layout.count()==1:
  #     toolbar=self.toolbar_layout.itemAt(0).widget()
  #     toolbar.set_label('  ')
  #     #toolbar.hide_plot_button(show=True)
  #     toolbar.hide_remove_button()
  #     toolbar.hide_align_button()
  #     return 

  #   for index in range(self.toolbar_layout.count()):
  #     toolbar=self.toolbar_layout.itemAt(index).widget()
  #     print index, toolbar, type(toolbar)
  #     if not isinstance(toolbar, TreedexPlotItemToolbar):
  #       continue
  #     toolbar.set_label('#'+str(index+1))
  #     toolbar.hide_remove_button(show=True)
  #     toolbar.hide_align_button(show=True)
  #     #if index: toolbar.hide_plot_button()

#####################################################################################
class PlotItem(object):
  """A PlotItem corresponds to a bunch of graphical items ('components') with the same basic source data. For example, you have the scatterplot dots and their labels.
  Init with the parent plot_object and options, which contain all input/parameters/options. This is stored in self.options.
  Node coordinate input is of course a DataChannel. There's a main one which act as root for all others (dc); this can be then further enriched for specific PlotItem components.
 """
  defaults={'name':None}
  plot_type=None 
  toolbar_class=None
  ## key:  value         or   key:  {subkey: subvalue, subkey2: subvalue2}
  def __init__(self, plot_object, cache_name, options):
    self.plot_object=plot_object
    self.options=deepcopy(self.defaults)  #this stores the current options of the plot
    # copying from dict 
    self.store_options(options, self.options) #updating self.options
    self.init_data_channel(cache_name) #this will create a self.dc
    self.options_drawn={}              #this stores the options used when the graphics were constructed
    self.init_item()
    self.store_plot_options()

  def store_headers(self, n):    
    """ Keeps the column names of plot_item.dc when plotted. Function connected to be run when necessary. Useful to store for axis labels"""
    df=self.dc.out()
    self.headers=[str(df.columns[i])  if not df is None else ''    for i in range(n)]

  def copy_options(self):
    out={}
    self.store_options(self.options, out, copy=True)  #dc_as_keys=True, 
    return out
    
  def store_options(self, options, target, copy=False): #dc_as_keys=False, 
    #self.stored_options={}
    for k in options:
      v=options[k]   
      #if dc_as_keys and isinstance(v, DataChannel): v=v.key(non_redundant=True) 
      if isinstance(v, dict):
        for subk in v.keys():
          subv=v[subk]      
          #if dc_as_keys and isinstance(subv, DataChannel): subv=subv.key(non_redundant=True)
          if copy:        subv=deepcopy(subv)
          if not k in target: target[k]={}
          target[k][subk]= subv
      else:
        if copy:        v=deepcopy(v)
        target[k]=v
  def store_plot_options(self): self.store_options(self.options, self.options_drawn, copy=True)   #dc_as_keys=True, 

  def delta_options(self):
    """ Return a set of the primary keys for which their corresponding values changed between self.options_drawn and self.options """
    def different_values(a, b):
      #if isinstance(a, DataChannel):          a=a.key(non_redundant=True)
      #if isinstance(b, DataChannel):          b=b.key(non_redundant=True)        
      return a!=b
    out=set()
    for k in self.options:
      is_different=False
      v=self.options[k]
      if isinstance(v, dict):
        for subk in v.keys():
          subv=v[subk]
          if different_values(self.options_drawn[k][subk], subv):  
            is_different=True
            break          
      else:        
        if different_values(self.options_drawn[k], v):            is_different=True
      if is_different: out.add(k)
    return out

  def update_options(self, options):
    for k in options:
      v=options[k]  #manually writing copy methods for total control
      if isinstance(v, dict):
        for subk in v.keys():
          subv=v[subk]
          self.options[k][subk]= subv
      else:                         self.options[k]=v

  def init_data_channel(self, cache_name): """Create self.dc based on cache_name """; raise Exception
  def init_item(self):                     """Start up the plotItem; implemented in subclasses""";     raise Exception
  def update_item(self):                   """Update the whole plotItem; implemented in subclasses"""; raise Exception   

  # def make_toolbar(self):    #raise Exception, "ERROR make_toolbar should be defined in subclasses"
  #   tb=self.toolbar_class(self)
  #   tb.setAutoFillBackground(True)
  #   return tb

#####################################################################################
class PlotObject(object):
  """Canvas for PlotItem. Every PlotWindow has a single PlotObject, which can contain several PlotItem instances.
  This is initialized in the init of the PlotWindow of every specific plot class. """
  default_options= {} 
  def __init__(self):  self.options=dict(self.default_options)
  def master(self):    return self.plot_window.master()
  # def get_window_options(self): 
  #   return self.plot_window.get_options()
  # def get_options(self):
  #   return self.options

####################################################################################
class ToolbarToolButton(ToolButton):
  stylesheet='QToolButton {border: 4px solid lightgrey; border-radius: 2px; margin: 2px;}'
  stylesheet_active='QToolButton {border: 4px solid blue; border-radius: 2px; margin: 2px; }'

##############
class ToolbarMenu(QtGui.QWidget):
  """ """
  def __init__(self, plot_item):
    super(ToolbarMenu, self).__init__()
    self.plot_item=plot_item
    self.setSizePolicy(  QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed) )
    


class ToolbarDataMenu(ToolbarMenu):
  """ """
  def __init__(self, plot_item):
    super(ToolbarDataMenu, self).__init__(plot_item=plot_item)
    self.layout=QtGui.QVBoxLayout()
    self.setLayout(self.layout)
    dc=self.plot_item.dc
    dcw=DataChannelWidget(dc, within='Plot')
    dc_layout=QtGui.QHBoxLayout()
    dc_layout.addWidget(QtGui.QLabel('Data:'))
    dc_layout.addWidget(dcw)
    dc_layout.addStretch()
    self.layout.addLayout(dc_layout)  

class ToolbarPlotitemMenu(ToolbarMenu):
  """ """
  def __init__(self, plot_item):
    super(ToolbarPlotitemMenu, self).__init__(plot_item=plot_item)
    self.layout=QtGui.QVBoxLayout()
    self.setLayout(self.layout)
    sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
    self.setSizePolicy(sizePolicy)
    row1=QtGui.QHBoxLayout()
    row1.addWidget(QtGui.QLabel('Type:'))
    row1.addWidget(QtGui.QLabel(self.plot_item.plot_type))
    row1.addWidget(VerticalLine('lightgrey'))
    row1.addWidget(QtGui.QLabel('Name:'))   
    current_name=self.plot_item.options['name']
    self.name_textbox=QtGui.QLineEdit()
    self.name_textbox.setText(current_name)
    self.name_textbox.setSizePolicy(fixed_size_policy)
    self.name_textbox.editingFinished.connect(self.edited_plot_item_name)
    row1.addWidget(self.name_textbox)
    row1.addWidget(VerticalLine('lightgrey'))
    delete_button=QtGui.QPushButton('Delete this plot item')
    delete_button.clicked.connect(self.clicked_delete_plot_item)
    if len(self.plot_item.plot_object.plot_window.plot_items)<2: delete_button.setVisible(False)
    row1.addWidget(delete_button)
    row1.addStretch()
    self.layout.addLayout(row1)
    self.layout.addWidget(HorizontalLine())
    
    row2=QtGui.QHBoxLayout()
    label=QtGui.QLabel('Plot'); label.setStyleSheet('color:red'); row2.addWidget(label)
    self.layout.addLayout(row2)    
    
    row3=QtGui.QHBoxLayout();  row3.addSpacing(10)
    row3.addWidget(QtGui.QLabel('Add plot item:'))
    duplicate_button=QtGui.QPushButton('duplicate this')
    duplicate_button.clicked.connect(self.clicked_duplicate_plot_item)
    row3.addWidget(duplicate_button)
    row3.addWidget(QtGui.QLabel('  or add empty '))    
    for piclass in self.plot_item.plot_object.plot_window.available_plot_items:
      pi_button=ToolButton(piclass.plot_type, piclass.plot_type, lambda s,piclass=piclass:self.clicked_add_plot_item(piclass))
      pi_button.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
      row3.addWidget(pi_button)
    row3.addStretch()
    self.layout.addLayout(row3)

  def edited_plot_item_name(self):
    text=str(self.name_textbox.text())
    self.plot_item.options['name']=text
    self.plot_item.update_item()
  def clicked_delete_plot_item(self):
    pressed_button=QtGui.QMessageBox.warning(self, 'Warning', 'This will remove all the graphical elements related to the plot item "{}". Are you sure?'.format(self.plot_item.options['name']), QtGui.QMessageBox.Cancel, QtGui.QMessageBox.Ok)
    if pressed_button==QtGui.QMessageBox.Cancel: return
    self.plot_item.plot_object.plot_window.remove_plot_item(self.plot_item)
    self.plot_item.plot_object.plot_window.hide_menu()

  def clicked_duplicate_plot_item(self):    
    piclass=self.plot_item.__class__
    options=self.plot_item.copy_options()
    options['name']+="'"
    self.plot_item.plot_object.plot_window.add_plot_item(piclass, options)

  def clicked_add_plot_item(self, piclass):
    self.plot_item.plot_object.plot_window.add_plot_item(piclass) #empty options => default
    

####################################################################################
class PlotItemToolbar(QtGui.QWidget):
  """Mother class for plot toolbars """
  plotitem_menu=ToolbarPlotitemMenu
  data_menu=ToolbarDataMenu
  view_menu=None   #must be defined in subclasses
  ancestors_menu=None
  interactivity_menu=None

  def __init__(self, plot_item): 
    super(PlotItemToolbar, self).__init__() #    QtGui.QWidget.__init__(self)  
    self.plot_item=plot_item
    #self.active_menu=[]   # category, menu, button
    #self.plot_title=plot_title
    sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
    self.setSizePolicy(sizePolicy)
    self.main_layout=QtGui.QVBoxLayout();    self.main_layout.setContentsMargins(0, 0, 0, 0);     self.main_layout.setSpacing(0)
    self.setLayout(self.main_layout)
    self.layout=QtGui.QHBoxLayout();         self.layout.setContentsMargins(0, 0, 0, 0);          self.layout.setSpacing(0)
    self.label=QtGui.QLabel('  ')
    self.layout.addWidget(self.label)
    #self.menu_layout=QtGui.QVBoxLayout();    self.menu_layout.setContentsMargins(0, 0, 0, 0);     self.menu_layout.setSpacing(0)
    self.main_layout.addLayout(self.layout)
    #self.main_layout.addLayout(self.menu_layout)
    self.main_layout.addWidget(HorizontalLine('grey'))
    
    #buttons:
    self.plotitem_label=QtGui.QLabel(self.plot_item.options['name'])
    self.plotitem_button=ToolbarToolButton(self.plot_item.plot_type, 'Plot item', self.plotitem_button_was_clicked)
    self.layout.addWidget(self.plotitem_label)
    self.layout.addWidget(self.plotitem_button)
    self.layout.addWidget(VerticalLine())

    self.data_button=ToolbarToolButton('targetdata', 'Input', self.data_button_was_clicked)
    self.layout.addWidget(self.data_button)
    self.view_button=ToolbarToolButton('view', 'View', self.view_button_was_clicked)
    self.layout.addWidget(self.view_button)
    self.ancestors_button=ToolbarToolButton('ancestors', 'Ancestors', self.ancestors_button_was_clicked)
    self.layout.addWidget(self.ancestors_button)
    self.layout.addWidget(VerticalLine())
    self.interactivity_button=ToolbarToolButton('interactivity', 'Interactivity', self.interactivity_button_was_clicked)
    self.layout.addWidget(self.interactivity_button)

    # self.tables_button=TreedexToolButton('tables.icon.png', 'Tables', self.tables_button_was_clicked)
    # self.layout.addWidget(self.tables_button)
    # self.stats_button=TreedexToolButton('stats.icon.png', 'Stats', self.stats_button_was_clicked)
    # self.layout.addWidget(self.stats_button)

    self.layout.addStretch()    
    self.active_label=QtGui.QLabel()
    self.active_label.setText('')
    self.active_label.setStyleSheet('color: blue')
    self.active_label.setAlignment(QtCore.Qt.AlignCenter)
    self.layout.addWidget(self.active_label)
    self.layout.addStretch()    

  def set_label(self, label):    self.label.setText(label)

  # def get_plot_item(self):    return self.plot_item
  # def get_plot_window(self):  return self.get_plot_item().get_plot_window()
  # def get_plot_object(self):  return self.get_plot_item().get_plot_object()

  def button_was_clicked(self, key, menu_class, button):
    """ Prototype for any of the buttons being clicked """
    win=self.plot_item.plot_object.plot_window
    if win.active_menu:
      if win.active_menu[1]==key and self.plot_item==win.active_menu[0]: return win.hide_menu()  #second click; just hide existing menu
      else:                                                                     win.hide_menu()
    self.active_label.setText(key.capitalize())
    menu=menu_class(self.plot_item)
    menu.setAutoFillBackground(True)
    win.menu_layout.addWidget(HorizontalLine('lightgrey'))
    win.menu_layout.addWidget(menu)
    button.setStyleSheet(button.stylesheet_active)
    win.active_menu=[self.plot_item, key, menu, button]

  def plotitem_button_was_clicked(self):       self.button_was_clicked('plotitem',  self.plotitem_menu,  self.plotitem_button)
  def data_button_was_clicked(self):           self.button_was_clicked('data',      self.data_menu,      self.data_button)
  def view_button_was_clicked(self):           self.button_was_clicked('view',      self.view_menu,      self.view_button)
  def ancestors_button_was_clicked(self):      self.button_was_clicked('ancestors', self.ancestors_menu, self.ancestors_button)
  def interactivity_button_was_clicked(self):  self.button_was_clicked('interactivity',  self.interactivity_menu,  self.interactivity_button)
    #self.button_was_clicked('plotitem',  PlotItemPlotMenu,      self.plotitem_button)
  # def tables_button_was_clicked(self):         self.button_was_clicked('tables',    PlotItemTablesMenu,    self.tables_button)
  # def stats_button_was_clicked(self):          self.button_was_clicked('stats',     PlotItemStatsMenu,     self.stats_button)

