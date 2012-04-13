from PyQt4 import QtCore

class Thread(QtCore.QThread):
  '''This class runs the function passed to it in its own QThread.
  '''
  def __init__(self, function, *args, **kwargs):
    QtCore.QThread.__init__(self)
    self.function = function
    self.args = args
    self.kwargs = kwargs

  def __del__(self):
    self.wait()

  def run(self):
    if self.args and self.kwargs:
      self.function(*self.args,**self.kwargs)
    elif self.args and not self.kwargs:
      self.function(*self.args)
    elif not self.args and self.kwargs:
      self.function(**self.kwargs)
    else:
      self.function()
    return
