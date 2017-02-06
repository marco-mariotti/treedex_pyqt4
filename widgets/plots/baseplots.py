from ..base import *
from ...data  import *
from ...common import *
import pyqtgraph as pg

def set_black_theme():
  """Set the black theme for scatterplots; all those opened after this is called will be affected """
  pg.setConfigOption('background', 'k')
  pg.setConfigOption('foreground', 'w')

def set_white_theme():
  """Set the white theme for scatterplots; all those opened after this is called will be affected """
  pg.setConfigOption('background', 'w')
  pg.setConfigOption('foreground', 'k')
set_white_theme()

######################################################################
############################################# Base class #############
class PlotWindow(TreedexWindow): 
  """ Motherclass for all windows of plots  """
  def Master(self): return self.master_link
  def update_axis(self): pass
  def add_toolbar(self, tb):    self.toolbar_layout.addWidget(tb)

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
  defaults={ 'main_dc':None }
  name=None
  toolbar_class=None
  ## key:  value         or   key:  {subkey: subvalue, subkey2: subvalue2}
  def __init__(self, plot_object, options):
    self.plot_object=plot_object
    self.options=dict(self.defaults)
    for k in self.options: 
      if k in options: self.options[k]=options[k]

  def update_options(self, options):
    for k in options:
      v=options[k]
      if isinstance(v, dict):
        for subk in v.keys():
          subv=d[subk]
          self.options[k][subk]= subv
      else:
        self.options[k]=v

  def make_toolbar(self):    #raise Exception, "ERROR make_toolbar should be defined in subclasses"
    tb=self.toolbar_class(self)
    tb.setAutoFillBackground(True)
    return tb

#####################################################################################
class PlotObject(object):
  #default_options= { 'click_action':'Highlight', 'show_highlight':True, 'show_select':False } 
  def __init__(self, options={}):    pass
    #self.options=dict(self.default_options);  self.options.update(options)  #plot options
  def Master(self): return self.plot_window.Master()
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

class ToolbarDataMenu(ToolbarMenu):
  """ """
  def __init__(self, plot_item):
    super(ToolbarDataMenu, self).__init__(plot_item=plot_item)
    self.layout=QtGui.QVBoxLayout()
    self.setLayout(self.layout)
    self.layout.addWidget(  QtGui.QLabel('fanfara')   )

####################################################################################
class PlotItemToolbar(QtGui.QWidget):
  """Mother class for plot toolbars """
  data_menu=ToolbarDataMenu

  def __init__(self, plot_item): 
    super(PlotItemToolbar, self).__init__() #    QtGui.QWidget.__init__(self)  
    self.plot_item=plot_item
    self.active_menu=[]   # category, menu, button
    #self.plot_title=plot_title
    sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
    self.setSizePolicy(sizePolicy)
    self.main_layout=QtGui.QVBoxLayout();    self.main_layout.setContentsMargins(0, 0, 0, 0);     self.main_layout.setSpacing(0)
    self.setLayout(self.main_layout)
    self.layout=QtGui.QHBoxLayout();         self.layout.setContentsMargins(0, 0, 0, 0);          self.layout.setSpacing(0)
    self.label=QtGui.QLabel('  ')
    self.layout.addWidget(self.label)
    self.menu_layout=QtGui.QVBoxLayout();    self.menu_layout.setContentsMargins(0, 0, 0, 0);     self.menu_layout.setSpacing(0)
    self.main_layout.addLayout(self.layout)
    self.main_layout.addLayout(self.menu_layout)
    self.main_layout.addWidget(HorizontalLine())
    
    #buttons:
    self.plotitem_button=ToolbarToolButton(self.plot_item.name, 'Plot item', self.plotitem_button_was_clicked)
    self.layout.addWidget(self.plotitem_button)
    self.layout.addWidget(VerticalLine())

    self.data_button=ToolbarToolButton('targetdata', 'Input', self.data_button_was_clicked)
    self.layout.addWidget(self.data_button)
    # self.view_button=TreedexToolButton('view.icon.png', 'View', self.view_button_was_clicked)
    # self.layout.addWidget(self.view_button)
    # self.ancestors_button=TreedexToolButton('ancestors.icon.png', 'Ancestors', self.ancestors_button_was_clicked)
    # self.layout.addWidget(self.ancestors_button)

    # self.layout.addWidget(VerticalLine())

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

  def hide_menu(self):
    write('hide menu!', 1)
    if self.active_menu:
      #self.active_menu[2].setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
      self.active_menu[2].setStyleSheet( self.active_menu[2].stylesheet  ) # back to basic style
      for i in reversed(range(self.menu_layout.count())):      self.menu_layout.itemAt(i).widget().deleteLater()
      self.active_label.setText('')
    self.active_menu=[]

  def button_was_clicked(self, key, menu_class, button):
    """ Prototype for any of the buttons being clicked """
    if self.active_menu:
      if self.active_menu[0]==key: return self.hide_menu()  #second click; just hide existing menu
      else:                               self.hide_menu()
    self.active_label.setText(key.capitalize())
    menu=menu_class(self.plot_item)
    hline= HorizontalLine()
    hline.setStyleSheet('QFrame {color:lightgrey }')
    self.menu_layout.addWidget(hline)
    self.menu_layout.addWidget(menu)
    button.setStyleSheet(button.stylesheet_active)
    self.active_menu=[key, menu, button]

  def data_button_was_clicked(self):           self.button_was_clicked('data',      self.data_menu,      self.data_button)
  # def view_button_was_clicked(self):           self.button_was_clicked('view',      ScatterplotItemViewMenu,      self.view_button)
  # def ancestors_button_was_clicked(self):      self.button_was_clicked('ancestors', PlotItemAncestorsMenu, self.ancestors_button)
  def plotitem_button_was_clicked(self):       
    pass
    #self.button_was_clicked('plotitem',  PlotItemPlotMenu,      self.plotitem_button)
  # def tables_button_was_clicked(self):         self.button_was_clicked('tables',    PlotItemTablesMenu,    self.tables_button)
  # def stats_button_was_clicked(self):          self.button_was_clicked('stats',     PlotItemStatsMenu,     self.stats_button)


