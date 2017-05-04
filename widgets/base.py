import os
from PyQt4   import QtCore, QtGui
from ..common import *
import pyqtgraph as pg

fixed_size_policy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)

def clear_layout(layout, widget=None, index=None):
  """Clears completely a PyQt layout; or, if item is not None, clears only that item.
  Defining a function for this since the standard way to do this causes a crash on mac. Will try to remedy and save memory at some point (in current implementation the widgets don't quite really disappear"""
  if not widget is None:   
    layout.removeWidget(widget)
    widget.setVisible(False)
    widget.setParent(None)
  else:
    try: 
      indices=reversed(range(layout.count())) if index is None else [index]
      items=[layout.itemAt(i)  for i in indices]
      for i in items:
        w=i.widget()
        if w is None:        
          if i.layout(): clear_layout(i.layout())    ### recursively removing layouts
          layout.removeItem(i)
        else:                
          layout.removeWidget(w)
          #w.setVisible(False)
          w.setParent(None)
          w.deleteLater()    # this would cause the crash
    except RuntimeError:
      print 'runtime error blablab'

def icons_folder():  return os.path.dirname(os.path.abspath(__file__))+'/../icons/'

stored_icons={}
def get_icon(label):
  filename='{path}{tag}.png'.format(path=icons_folder(), tag=label)
  if not os.path.isfile(filename): printerr('WARNING icon not found: {f}'.format(f=filename), 1)
  if not label in stored_icons: stored_icons[label]=QtGui.QIcon(filename)
  return stored_icons[label]

stored_pixmap={}
def get_pixmap(label):
  filename='{path}{tag}.png'.format(path=icons_folder(), tag=label)
  if not os.path.isfile(filename): printerr('WARNING pixmap not found: {f}'.format(f=filename), 1)
  if not label in stored_pixmap: stored_pixmap[label]=QtGui.QPixmap(filename)
  return stored_pixmap[label]

####################################################################################
class TreedexWindow(QtGui.QWidget):
  def __init__(self):
    super(TreedexWindow, self).__init__() 
    self.master().windows().add_window( self, **(self.window_identifier()) )    
    # now self.window_name is available

  def delete_data_channels(self): return
  def window_identifier(self):
    """ must return either {'window_name': something}   or {'category':something} """
    raise Exception, "ERROR TreedexWindow window_identifier must be defined in subclasses!"

  def closeEvent(self, e):
    write('catch: window closed {n}'.format(n=self.window_name), 1)
    if hasattr(self, 'dco_link') and not self.dco_link is None: # if is None, the closeEvent was actually triggered from the dco being deleted.
      print 'plot window closed! removing linked DCO'
      self.dco_link.window_link=None    #avoiding second activation
      self.dco_link.container.pop(    self.dco_link.container.chain.index(self.dco_link)     ) 
    self.delete_data_channels()
    self.master().windows().remove_window(self)
    QtGui.QWidget.closeEvent(self, e)

####################################################################################
class HorizontalLine(QtGui.QFrame):
  def __init__(self, color=None):
    super(HorizontalLine, self).__init__()
    self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
    self.setFrameStyle(QtGui.QFrame.HLine)    
    if not color is None: self.setStyleSheet('color:{}'.format(color))

class VerticalLine(QtGui.QFrame):
  def __init__(self, color=None):
    super(VerticalLine, self).__init__()
    self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Expanding)
    self.setFrameStyle(QtGui.QFrame.VLine)    
    if not color is None: self.setStyleSheet('color:{}'.format(color))

####################################################################################
class ToolButton(QtGui.QToolButton):
  stylesheet='' 
  def __init__(self, icon, text, fn=None):
    super(ToolButton, self).__init__()
    icon=get_icon(icon)
    action= QtGui.QAction(icon, text, self)
    self.setDefaultAction(action)
    if not fn is None:        self.clicked.connect(fn)
    if self.stylesheet: self.setStyleSheet(self.stylesheet)

class ChainButton(QtGui.QPushButton):
  def __init__(self, fn=None):
    super(ChainButton, self).__init__(">") 
    self.setStyleSheet('padding: 0px')
    self.setFixedSize(10, 20)  
    self.setSizePolicy(fixed_size_policy)    
    if not fn is None:        self.clicked.connect(fn)
