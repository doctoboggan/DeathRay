# Here, the file should scan for Gpi ports. 

import getIDN

class check():

  def __init__(self,IPad, numberofdevices = 0):

    self.ip_ad = IPad
    self.gpib_id = 'gpib0,00'
    self.numd = numberofdevices
    self.group = []
    self.gg = []
    self.gb = []
    #data_acquisition.vxi_11.vxi_11_connection.__init__(self,host=IPad,device=self.gpib_id,raise_on_err=0,timeout=500,device_name='nothing')
    self.rightDevice = ['']

  def write(self):

    for x in range(0,self.numd-1):

      self.group.append(x)

      if x <= 9:
        # I hope "x" go all th way
          g = "gpib0,0%d" % (x)
          print g
          #gp = '"' + g + '"'
          k = getIDN.name(self.ip_ad,g)
          a, b, self.group[x] = k.transaction('*IDN?')
          print "it is here"
          print self.group[x]
          print "over"
          #self.group[x] = self.fun(self.str_ip_ad, gp,'*IDN?')

      else:

          g = "gpib0,%d" % (x)
          print g
          #gp = '"' + g + '"'
          k = getIDN.name(self.ip_ad,g)
          a , b, self.group[x] = k.transaction('*IDN?')
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


#getdevice.check('129.59.93.179',25).fix()
# It returns the the name of avalible devices and their gpib address.










# getdevice.check('129.59.93.179', 25).fix()
# It is kind of slow for now.
#    print 'We\'re on time %d' % (x)


    
