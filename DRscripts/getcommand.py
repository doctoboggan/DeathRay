# Here, we should be able to get the right commands for given device

from DRscripts import checkinit
import DRmodules 

class getcommand(checkinit.checkinit):

  def __init__(self, IPad = '127.0.0.1', Gpibad ="inst0" , namdev = "Network Device"):    

    # namdev is the name of choosen device (by the user). The program will search of any match commands for this device. 
    # direct is the path of __init__ file (include the name of the file)
    # dirr is the path of module folder (where, the system will check the modules avalibilty)
    # both input have to be string (they have to have [""]to be string.

    self.ip_id = IPad
    self.gpib_id = Gpibad
    self.look = namdev.lower()
    checkinit.checkinit.__init__(self)
    self.rightDevice = ['']
    self.wow = []



  def do(self):        # there is two ways. 1) feed the function the right gpib address from "getdevice or make excaption (I will  go with the first one. it is more clean)

    self.scann()
    qqq = self.linefromlist
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
      a = DRmodules.command[aa]('129.59.93.179', 'gpib0,07').rightDevice     # we can aviod eval (ask Jack). (it is special because it using __init__
      if self.look in a:
        self.wow.append(num)
        self.wow[num] = qqq[u]
        num = num + 1
      else:
        pass

    return self.wow
        


# in the information place, the developer must defind which input will from the user and which input is from the program. 
# I need to build a check method for it.
# way to write the GUI:
'''
0) run checkinit. 
0.5) install the DRlibraries in the user system.
1) ask the user the IP address
2) run "getdevice" to get the avialble devices and their gpib addresses.  
3) run "getcommand"
'''
# getcommand.getcommand('129.59.93.179','gpib0,10','hp34401a','/home/computer/DeathRay/modules/__init__.py','/home/computer/DeathRay/modules/').do()

# every single module must have "rightDevice" list even if it is empty. (by saying empty, it is going to be like this : {self.rightDevice = ['']} )
# all inputs for any module has to optional (for no reason !!)


