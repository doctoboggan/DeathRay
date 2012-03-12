# it works


import os

class list(): # do not forget, if you are going to change the name of class, change too in the checkinit.py file.!!

  def __init__(self, direct):

    self.direct = direct
    self.lis = [] 
    
    self.lise = []
    self.lisee = []
    self.finallist = []
    self.tolist = []
    self.rightDevice = ['']

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

          if self.lise[count] == '__init__':    # to make sure that, it does not read its self. Also, we can any unwanted file hereto be unscanned (for future purpose)

            pass

          else:
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

  def get(self):        # this is the oneto run (do not worry about the others)

    self.clee()
    print self.finallist
    return self.finallist
        

  def together(self):

    self.sep()
    ncount = 0
    for count in range(len(self.lis)):

        if self.lisee[count] == '.py':
          self.tolist.append(ncount)
          self.tolist[ncount] = self.lise[count] + self.lisee[count]
          print ncount    #debug
          print count     #debug
          ncount = ncount + 1

        else:
          print "refused are here:"   #debug
          print count    #debug 
          print "next"    #debug

    return  self.tolist

#  def impor(self):

#    self.together()
#    count = 0
#    for count in range(len(self.tolist)):

#      print count
#      print self.tolist[count]
#      print "------------------------------------"
#      g = self.finallist[count]
#      from self.direct import g


# fullname , extensions = os.path.splitext(fulllname)

#Andrew Sternburg 

#Jeff kawppiln 
#listgood.list('/home/computer/DeathRay/modules').get()
