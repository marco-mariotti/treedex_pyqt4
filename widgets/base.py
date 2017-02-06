import os
from PyQt4   import QtCore, QtGui
from ..common import *

def clear_layout(layout, widget=None, index=None):
  """Clears completely a PyQt layout; or, if item is not None, clears only that item.
  Defining a function for this since the standard way to do this causes a crash on mac. Will try to remedy and save memory at some point (in current implementation the widgets don't quite really disappear"""
  if not widget is None:   
    layout.removeWidget(widget)
    widget.setVisible(False)
    widget.setParent(None)
  else:
    indices=reversed(range(layout.count())) if index is None else [index]
    items=[layout.itemAt(i)  for i in indices]
    for i in items:
      w=i.widget()
      if w is None:        layout.removeItem(i)
      else:                
        layout.removeWidget(w)
        w.setVisible(False)
        w.setParent(None)
      #w.deleteLater()    # this would cause the crash

def icons_folder():  return os.path.dirname(os.path.abspath(__file__))+'/../icons/'

stored_icons={}
def get_icon(label):
  filename='{path}{tag}.png'.format(path=icons_folder(), tag=label)
  if not os.path.isfile(filename): printerr('WARNING icon not found: {f}'.format(f=filename), 1)
  if not label in stored_icons: stored_icons[label]=QtGui.QIcon(filename)
  return stored_icons[label]

####################################################################################
class TreedexWindow(QtGui.QWidget):
  def __init__(self):
    super(TreedexWindow, self).__init__() 
    self.Master().windows().add_window( self, **(self.window_identifier()) )    
    # now self.window_name is available
    
  def window_identifier(self):
    """ must return either {'window_name': something}   or {'category':something} """
    raise Exception, "ERROR TreedexWindow window_identifier must be defined in subclasses!"

  def closeEvent(self, e):
    write('catch: window closed {n}'.format(n=self.window_name), 1)
    self.Master().windows().remove_window(self)
    QtGui.QWidget.closeEvent(self, e)

####################################################################################
class HorizontalLine(QtGui.QFrame):
  def __init__(self):
    super(HorizontalLine, self).__init__()
    self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
    self.setFrameStyle(QtGui.QFrame.HLine)    

class VerticalLine(QtGui.QFrame):
  def __init__(self):
    super(VerticalLine, self).__init__()
    self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Expanding)
    self.setFrameStyle(QtGui.QFrame.VLine)    

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
