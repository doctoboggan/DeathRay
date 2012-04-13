# This file for checking __init__ file

import listgood

class check(listgood.list):

  def __init__(self, direct, dirr ):

    self.file = open(direct, 'a+')
    self.linelist = []
    self.lineelist = []
    listgood.list.__init__(self, dirr)
    self.rightDevice = ['']

  def read(self):



    self.linelist = self.file.readlines()
    print "real list is "
    print self.linelist
    print "done"
    print "file is here:"
    print ":)"
    print "_______________________over_______________"

  #  return linelist

  def scann(self):

    self.read()
    print "first time"
    print "the length of linelist is "
    print len(self.linelist)
    print "yesssssssssssssssssssssss"
     
    for count in range(0,len(self.linelist)):

      self.lineelist.append(self.linelist[count].split()[1]) 

    print "lineelist from the scan method is "
    print self.lineelist
    print "_-_-_-_-[___--__--__----_-"


  def decide(self):

    self.scann()
    print "It just scan"
    lll = self.get()
    print "length of the scaned list:"
    print len(lll)
    print "++++++over++++++"
    print "the imported list is "
    print lll
    print "**************"
    for n in range(len(lll)):
      print "we just started for!!"
      print "It is comaprung to :"
      print lll[n]
      print "ok"
      print "lineelist is:"
      print self.lineelist
      print "^^^^^^^^^^^^^^^^^^^^"
      if lll[n] in self.lineelist:
        print "the canceled one is:"
        print lll[n]
        print "done for cancel"
        print "pass"
        pass

      else: 
        print "the new one is:"
        print lll[n]
        print "done adding"
        self.file.write('import ')
        self.file.write(lll[n]+'\n')

    #self.file.close()


  def extra(self):

    self.scann()
    print "It just scan"
    ttt = self.get()
    print "length of the scaned list:"
    print len(ttt)
    print "++++++over++++++"
    print "the imported list is "
    print ttt
    print "**************"
    print "Here is what inside the init file:"
    print self.lineelist
    print "&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&"
    for n in range(len(ttt)):
      if self.lineelist[n] not in ttt:
          print "the removed one is:"
          print self.lineelist[n]
          print "removing is over"
          print "line number :"
          print self.linelist[n]
          print "is going to be removed"
          del line[self.linelist[n]]
          self.file.writelines(self.linelist)   # an issue here
          #self.file.del(self.linelist[n])
          print "line number :"
          print self.linelist[n]
          print "has been removed"

      else: 
          print "we will keep this:"
          print self.lineelist[n]
          print "from removing ----------------------"
          print "This one:"
          print self.linelist[n]
          print "will not be removed ++++++++++++++++++++++++++"
          pass

  
#checkinit.check('/home/computer/DeathRay/modules/__init__.py','/home/computer/DeathRay/modules/').decide()

# later, I should make sure that, there is no empty line nor unknown ones.

