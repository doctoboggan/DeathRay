import os

class list():

  def __init__(self, direct):

    self.direct = direct
    self.lis = []
    
    self.lise = []
    self.lisee = []
    self.finallist = []

  def scan(self):

    for count in range(len(os.listdir(self.direct))):
      
      self.lis.append(count)
      print count       #debug
      self.lis[count] = os.listdir(self.direct)[count]
      print self.lis[count]   #debug

  def sep(self):
    
    self.scan()
    for count in range(len(self.lis)):
      print count
      self.lise.append(count)
      self.lisee.append(count)
      self.lise[count], self.lisee[count] = os.path.splitext(self.lis[count])
      print self.lise[count]    #debug
      print self.lisee[count]   #debug
      

  def clee(self):

    self.sep()
    ncount = 0
    for count in range(len(self.lis)):

        if self.lisee[count] == '.py':
          self.finallist.append(ncount)
          self.finallist[ncount] = self.lise[count]
          print ncount    #debug
          print count     #debug
          print self.finallist[ncount]   #debug
          ncount = ncount + 1

        else:
          print "refused are here:"   #debug
          print count    #debug 
          print "next"    #debug
          pass

  def get(self):

    self.clee()
    print self.finallist
    return self.finallist
        



# fullname , extensions = os.path.splitext(fulllname)

#Andrew Sternburg 

#Jeff kawppiln 
#listgood.list('/home/computer/DeathRay/modules').get()
