# Here, the file should scan for Gpi ports. 

import data_acquisition



def write(self, ip_ad, numd):

  group = []
  for x in range(0,self.numd):

    if x <= 9:
      # I hope "x" go all th way
      while x != 9 or x != numd:
        g = "gpib0,0%d" % (x)
        gp = '"' + g + '"'
        k = data_acquisition.vxi_11.vxi_11_connection.__init__(host=ip_ad,device=gp,raise_on_err=0,timeout=500,device_name='nothing')
        error, reason, group[x] = k.transaction('*IDN?')
        #self.group[x] = self.fun(self.str_ip_ad, gp,'*IDN?')

    else:

      while x != numd:
        g = "gpib0,%d" % (x)
        gp = '"' + g + '"'
        k = data_acquisition.vxi_11.vxi_11_connection.__init__(host=ip_ad,device=gp,raise_on_err=0,timeout=500,device_name='nothing')
        error, reason, group[x] = k.transaction('*IDN?')
        #self.group[x] = self.fun(self.str_ip_ad, gp,'*IDN?')

    return 

def ok(self):

  self.write()
  print self.group




















  #    print 'We\'re on time %d' % (x)


    