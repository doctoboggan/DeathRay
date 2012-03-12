# Here, the file should scan for Gpi ports. 

import fun
import data_acquisition

class check(data_acquisition.vxi_11.vxi_11_connection,data_acquisition.gpib_utilities.gpib_device):

  def __init__(self,IPad, numberofdevices = 0):

    self.ip_ad = IPad
    self.gpib_id = 'gpib0,00'
    self.numd = numberofdevices
    self.group = []
    #data_acquisition.vxi_11.vxi_11_connection.__init__(self,host=IPad,device=Gpibad,raise_on_err=0,timeout=500,device_name='nothing')

  def write(self):

    for x in range(0,self.numd):

      if x <= 9:
        # I hope "x" go all th way
        while x != 9 or x != self.numd:
          g = "gpib0,0%d" % (x)
          gp = '"' + g + '"'
          self.group[x] = self.fun(self.str_ip_ad, gp,'*IDN?')

      else:

        while x != self.numd:
          g = "gpib0,%d" % (x)
          gp = '"' + g + '"'
          self.group[x] = self.fun(self.str_ip_ad, gp,'*IDN?')

  def ok(self):

    self.write()
    print self.group




# check2.check('129.59.93.179', numberofdevices= 5).ok()













  #    print 'We\'re on time %d' % (x)


    