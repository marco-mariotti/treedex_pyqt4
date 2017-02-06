from .baseplots import *

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
  def window_identifier(self): return {'category':'ScatterPlot'}
  def __init__(self, master_link, plot_title='ScatterPlot'): 
    self.master_link=master_link
    PlotWindow.__init__(self)
    pg.GraphicsView.__init__(self)
    self.plot_items=[]
    self.axes=[]  #first element: QLabel for X;      second element: for Y
    self.setWindowTitle(plot_title)
    self.main_layout= QtGui.QVBoxLayout(); self.main_layout.setContentsMargins(0, 0, 0, 0);     self.main_layout.setSpacing(0)
    self.setLayout(self.main_layout) 
    self.toolbar_layout= QtGui.QVBoxLayout()  
    self.main_layout.addLayout(self.toolbar_layout)
    self.plot_layout=pg.GraphicsLayoutWidget()
    self.plot_layout.ci.layout.setContentsMargins(0, 0, 0, 0);     self.plot_layout.ci.layout.setSpacing(0)
    self.axes.append(self.plot_layout.addLabel('--', col=0, row=1, angle=-90)) #later text is set
    self.plot_object= ScatterPlotObject(plot_window=self)
    self.plot_layout.addItem(self.plot_object, col=2, row=1)
    self.axes.insert(0, self.plot_layout.addLabel('--', col=2, row=2))
    self.main_layout.addWidget(self.plot_layout)

  #def get_n_dimensions(self): return 2

  # def add_data_series(self, ds, color_control=None): #,  make_toolbar=True):
  #   """ add plot_item to self.plot_items and returns it"""
  #   write('adding data_series!', 1, how='yellow')
  #   scatter_plot_item = ScatterPlotItem( plot_object=self.plot_object, data_series=ds, color_control=color_control) # , make_toolbar=make_toolbar )
  #   #if make_toolbar:  
  #   self.toolbar_layout.addWidget(scatter_plot_item.get_toolbar())
  #   self.plot_items.append(scatter_plot_item)
  #   self.plot_object.addItem(scatter_plot_item)
  #   #scatter_plot_item.get_toolbar().update_view_to_settings()
  #   #if make_toolbar: 
  #   scatter_plot_item.get_toolbar().setAutoFillBackground(True)
  #   self.plot_object.plot_window.update_axis()
  #   return scatter_plot_item

  # def remove_data_series(self, index):
  #   plot_item=self.plot_items.pop(index)
  #   plot_item.delete()

  def set_axis_label(self, index_dimension, label):     
    self.axes[index_dimension].setText(label)

  def set_axis_range(self, index_dimension, min_this_dimension, max_this_dimension):
    if    index_dimension==0:      self.plot_object.setXRange( min_this_dimension, max_this_dimension, padding=0)
    elif  index_dimension==1:      self.plot_object.setYRange( min_this_dimension, max_this_dimension, padding=0)
    else: raise Exception

  def add_plot_item(self, options={}): #, pitype=):
    pi=NodeScatterPlotItem(self.plot_object, options=options)
    self.plot_items.append(pi)
    self.add_toolbar( pi.make_toolbar() )

####################################################################################
class NodeScatterPlotToolbar(PlotItemToolbar):
  """ """

####################################################################################
class NodeScatterPlotItem(PlotItem):
  name='scatterplot'
  defaults={ 'main_dc':None, 'LeafSpots':{'size':6, 'symbol':'o'} }
  toolbar_class=NodeScatterPlotToolbar

  def __init__(self, plot_object, options={}):
    PlotItem.__init__(self, plot_object, options)
    main_dc=self.options['main_dc']
    df=main_dc.out()
    self.leaf_spots=self.LeafSpots(df, self.options['LeafSpots'] ) 
    self.plot_object.addItem(self.leaf_spots)
    ### add other components
         
  class LeafSpots(pg.ScatterPlotItem):
    """Dots, each one linked to a leaf node in the tree """
    def __init__(self, df, local_options):      
      pg.ScatterPlotItem.__init__(self, pxMode=True)
      self.update_plot(df, local_options)

    def update_plot(self, df, local_options): 
      nrows=len(df)
      spot_data=[]
      for row_i in range(nrows):
        node_name=df.at[row_i,'Node']
        x=float(df.at[row_i,'x'])
        y=float(df.at[row_i,'y'])
        symbol=local_options['symbol']
        size=  local_options['size']       
        spot_data.append({'pos': [x,y], 'data': node_name, 'symbol':symbol,'size':size}) #, 'pen':pen, 'brush':brush
      #print spot_data
      self.setPoints(spot_data)  

####################################################################################
class ScatterPlotObject(pg.PlotItem, PlotObject):
  def __init__(self, plot_window, options={}):
    pg.PlotItem.__init__(self)
    PlotObject.__init__(self, options=options)
    self.plot_window=plot_window
    self.showGrid(x=True, y=True, alpha=0.1)

