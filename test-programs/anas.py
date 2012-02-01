import libgpib

Class devices:

  def  __init__(self):
    self.realnum = len(dir(libgpib))
    self.counter = 0
    self.devicee = []


  def  __itisme__(self):
    for x in range(self.realnum)
      xx = dir(libgpib)[x]
      devicess = libgpib.xx.__module__
      

