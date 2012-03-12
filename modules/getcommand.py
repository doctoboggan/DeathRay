# Here, we should be able to get the right commands for given device

import checkinit
import __init__

class check(checkinit.check):

  def __init__(self, IPad, Gpibad, namdev, direct, dirr):    

    # namdev is the name of choosen device (by the user). The program will search of any match commands for this device. 
    # direct is the path of __init__ file (include the name of the file)
    # dirr is the path of module folder (where, the system will check the modules avalibilty)
    # both input have to be string (they have to have [""]to be string.

    self.ip_id = IPad
    self.gpib_id = Gpibad
    self.look = namdev.lower()
    checkinit.check.__init__(self, direct, dirr)
    self.rightDevice = ['']
    self.wow = []



  def do(self):        # there is two ways. 1) feed the function the right gpib address from "getdevice or make excaption (I will  go with the first one. Ot os more clean)

    self.scann()
    qqq = self.lineelist
    num = 0
    print "the qqq is: "
    print qqq
    print "-over-"
    print "number in qqq is: "
    print len(qqq)
    print "--over--"
    for u in range(0,len(qqq)): 
      qqq.append(u)
      print "the u number is: "
      print u
      print "----over---"
      print "the turn is: " + qqq[u] + " to be"
      aa = str(qqq[u])
      print "in the command, it is going to be: "+ aa +" ....!. Also, the type is: " 
      print type(aa) 
      print  " ....ok"
      cc = "__init__." + aa + '.' + aa + '("' +self.ip_id + '","' + self.gpib_id+'").rightDevice'
      print "the command is --> " + cc + " <--- !"
      a = eval(cc)
      print a
      if self.look in a:
        self.wow.append(num)
        self.wow[num] = qqq[u]
        num = num + 1
      else:
        pass

    return self.wow
        


# in the information place, the developer must defind which input will from the user and which input is from the program. 

# way to write the GUI:
'''
1) ask the user the IP address
2) run "getdevice" to get the avialble devices and their gpib addresses. 
3) run "checkinit" to check __init__ file in the module folder. 
4) run "getcommand"
'''
# getcommand.check('129.59.93.179','gpib0,10','hp34401a','/home/computer/DeathRay/modules/__init__.py','/home/computer/DeathRay/modules/').do()

# every single module must have "rightDevice" list even if it is empty. (by saying empty, it is going to be like this : {self.rightDevice = ['']} )
# all inputs for any module has to optional (for no reason !!)


