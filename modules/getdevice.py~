# Name: Device checker.
# Made by: Anas Alfuntukh
# Date: 3/4/12
# Goal: Check all devices in the network and bring their names and their Gpin adresses.
# Device: all gpib devices. 
# Modifiers:  None (for now) 
# Dependancy: 1) QT GUI
# Result: a list of names of all avalible devices in the network and another list of their Gpib addressses.
 

import getIDN   # This method is going to be used later.

class getdevice():

  '''
  --> THis class is for scanning Gpib network for devices. 
  --> It requires "getIDN" module.
  --> This is kind of module.
  '''

  def __init__(self,IPad, numberofdevices = 30):

    '''
    Requirement: (ip address, number of devices)
    Ex: getIDN.getIDN('129.59.93.179', 30)
    ____________________
    --> IPad is the number of ip-address with quotation mark.
    --> number of devices means the number of ports, which will be scanned. 
    --> Makes some lists global to be used in other files.
    --> The rightDevice list has to be there. It responsibles for flexibility of this file. Because this module is not related to devices directly, The list is going to be empty.
    '''

    self.ip_ad = IPad
    # self.gpib_id = 'gpib0,00' # it is useless
    self.numd = numberofdevices
    self.group = []
    self.gg = []
    self.gb = []
    #data_acquisition.vxi_11.vxi_11_connection.__init__(self,host=IPad,device=self.gpib_id,raise_on_err=0,timeout=500,device_name='nothing') # is not needed any more.
    self.rightDevice = ['']

  def write(self):

    for x in range(0,self.numd-1):

      self.group.append(x)

      if x <= 9:
        # I hope "x" go all th way
          g = "gpib0,0%d" % (x)
          print g
          #gp = '"' + g + '"'
          self.group[x] = getIDN.getIDN(self.ip_ad,g).do()
          #a, b, self.group[x] = k.transaction('*IDN?')
          print "it is here"
          print self.group[x]
          print "over"
          #self.group[x] = self.fun(self.str_ip_ad, gp,'*IDN?')

      else:

          g = "gpib0,%d" % (x)
          print g
          #gp = '"' + g + '"'
          self.group[x] = getIDN.getIDN(self.ip_ad,g).do()
          #a , b, self.group[x] = k.transaction('*IDN?')
          print "it is here"
          print self.group[x]
          print "over"
          #self.group[x] = self.fun(self.str_ip_ad, gp,'*IDN?')

    return self.group 

  def ok(self):

    m = []
    m = self.write()
    print m




  def fix(self):


    self.write()
    count = 0

    for y in range(0,len(self.group)-1):

      

      if self.group[y] == None:

        print self.group[y]
        pass

      else:
  
         
         print self.group[y]
         self.gg.append(self.group[y].split(',')[1])
         print "gg is "
         print self.gg[count]
         print "over"

         if y <= 9:
            gc = "gpib0,0%d" % (y)
            print gc
            self.gb.append(gc)


          #self.group[x] = self.fun(self.str_ip_ad, gp,'*IDN?')

         else:

            gc = "gpib0,%d" % (y)
            print gc
            self.gb.append(gc)


         count = count +1

    return  self.gg, self.gb


#getdevice.getdevice('129.59.93.179',25).fix()
# It returns the the name of avalible devices and their gpib address.



# It is kind of slow for now. To speed it up, I have to modify "getIDN" module (read end comments in that file).
#    print 'We\'re on time %d' % (x)


    
