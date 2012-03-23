# Name: DC voltage reader
# Made by: Anas Alfuntukh
# Date: 06/02/12  (MM/DD/YY)
# Goal: This moduel suppose to be able to return the DC voltage value from the given devices.
# Devcies:  1) "hp34401a"  2) "hpe3631a"
# Modifiers:  None (for now) 
# Dependancy: 1) QT GUI 
# SCPI command: 1) hpe3631a: ----> get DC voltage Value ===>  meas:volt:dc? <channel>
# ----------- <channel>" --------------
# <channel> ::= {p6v | p25v | n25v}
# Note: The dafult channel is the last active channel.
# -------------------------------------
#               2) hp34401a: -----> get DC voltage ===> meas:volt:dc?
# Result: One float. It is the DC voltage value.

import data_acquisition

class getvoltageDC(data_acquisition.vxi_11.vxi_11_connection,data_acquisition.gpib_utilities.gpib_device,data_acquisition.vxi_11.VXI_11_Error):		
  """
  This class provides the DC voltage value of the given devices (to know the devices, please use
  'rightdevice' function).
  We are feeding the class with vxi_11.vxi_11_connection and gpib_utilities.gpib_device from data_acquisition library. 
  """

  def __init__(self, IPad = '127.0.0.1', Gpibad ="inst0" , namdev = "Network Device", channel='p25v', timeout=600): 
    """
    Requiremnt: ( IPad, Gpibad, namdev, channel='p25v', timeout=300)
    Ex of requirement: '129.59.93.179', 'gpib0,22', 'hpe3631a', channel='n25v', timeout=2000)
    __________________
    To store the given values from the user. 
    Note:
      --> IPad is the number of ip-address with quotation mark. 
      --> Gpibad is the number of Gpib address with quotation mark.
      --> namdev is the name of the device.
      --> channel is a channel number for some devices. If the device do not have channels,
          the channel number will be ignored. 
    Ex (for non-channel device) :  -----voltageDC('129.59.93.27', 'gpib0,10', 'hp34401a').get()-----
    Ex (for channel device) :   -----voltageDC('129.59.93.27', 'gpib0,10', 'hp34401a', channel='p25v').get()-----
    Also, the definition has the devices list (hard-coded).
    Besdies that, you can control the time-out duration. The dafult time-out duration is 1000 msec. To change the time-out to 500msec:
    Ex (for channel device with different time-out): ----- voltageDC('129.59.93.27', 'gpib0,10', 'hp34401a', channel='p25v', timeout=500).get()
    Becareful with time-out, it will cause crazy issues if the time-out is small (ex: 100msec). 
    """
    self.ip_id = IPad
    self.gpib_id = Gpibad
    self.name_of_device = namdev.lower()    #lower case the input 
    self.channel = channel.lower()          #lower case the input
    self.rightDevice = ['34401a', 'e3631a']
    rise_on_error = 0
    data_acquisition.vxi_11.vxi_11_connection.__init__(self,host=IPad,device=Gpibad,raise_on_err=rise_on_error,timeout=timeout,device_name=namdev)  #here we are feeding the data_acquisition library

  def check(self):
    """
    To check if the given device will work with voltageDC function (avoiding issues). 
    Also, it makes sure that the input channels do exist (to aviod conflicts). 
    ALso, we take care of time-out minimum duration (to aviod run out of time).
    Aslo, we rmind the user if the input channel is not required for the given device. 
    """
    if self.name_of_device in self.rightDevice:

      if self.timeout is float or int:

        if self.timeout >= 300:      # hardcoded. Also, the number was choosen after several testing.

          if self.name_of_device == 'e3631a':

            # start configure "33631a".     [START]

            if self.channel is str:

              if self.channel not in ['p6v', 'P6V', 'p25v', 'P25V', 'n25v', 'N25V']:      # cor channel checking. Wehave to do this with each and every channelly device!!
                print "choosen channel does not exist !!"     # For debug purpose
                return False, 'c'
              else:
                return True

            else:
              print "the input channel is not string."
              return False, 's'

            # End of characteristics of "e3631a". [END]

          elif self.name_of_device == '34401a':

            # start configure "34401a".     [START]

            if self.channel is str:   # I check it to follow the rules !!.

              if self.channel != '':
                print " '34401a' device does not have channels.Your input channel will be ignored."
                return True
              else:
                return True   # the right case for this device.


            else:
              print "the input channel is not string."
              return False, 's'

            # End of characteristics of "34401a". [END]


          else:    #if we have another device, add elif argument here
            print "The device does exist in the data base. However, it does not have any 'check' method configuration, which is not good thing. Anyway, we can not continuse until we have the check method for this device."
            return False, 'c'

        else:
          print "The time-out is too short"   # For debug purpose
          return False, 'o'

      else:
        print "timeout input is not acceptable"
        return False, 'q'

    else:
      print "the device is not in data base"    # For debug purpose
      return False, 'x'
  


  def do(self):		
    """
    The main SCPI commands, where the DC voltage value is !!
    """  
    if self.check() is True:

      print "PASS check test"         # For debug purpose

      if self.name_of_device == 'e3631a':

        voltDC = self.transaction('meas:volt:dc? '+self.channel)
        #self.disconnect                   
        print "DC voltage is "  # For debug reasons
        print voltDC[2]    # For debug reasons.
        print "Done"    # For debug reasons

        if voltDC[0] == 0:             #check if it times out.

          return float(voltDC[2])

        else:

          print  self.identify_vxi_11_error(voltDC[0])      #print the error information.
          return False, voltDC[0]   # return the error number. 


 
      elif self.name_of_device == '34401a':

        #import time #debug                             [clean]
        voltDC = self.transaction('meas:volt:dc?')
        #self.disconnect
        print "DC voltage is "  # For debug reasons
        print voltDC[2]      # For debug reasons.
        print "Done"    # For debug reasons
        #time.sleep(0.2)            [clean]
        #print "done sleeping"        [clean]

        if voltDC[0] == 0:             #check if it times out.

          return float(voltDC[2])

        else:

          print  self.identify_vxi_11_error(voltDC[0])      #print the error information.
          return False, voltDC[0]   # return the error number.   
      
      else: 
        print "you should not be here at all. HOW DiD YOU PASS THE CHECK TEST !!"       # here , we add new devices with new commands. The user should not get here at all (hopefully)
        


    else:
      return self.check()

#print voltageDC.voltageDC('129.59.93.27', 'gpib0,10', 'hp34401a').check()
#print voltageDC.voltageDC('129.59.93.27', 'gpib0,10', 'hp34401a').get()
#add meas:vpp? <source> for the oscope (dso)
# Modify the manual. 
# Add voltage read from the oscope
# I have to know what rise_on_error means? I think I need to ask profossoe Meh...
# We are taking the third value in the range because it is the voltage value
# Note: hp34401a has the ability to control channel (it has multiple channels). hp34401a has onlt one channel to read from. 
# Note:   ---> 'o' means time-out is too short.
#         ---> 'e' means empty string
#         ---> 'c' means wrong channel input. 
#         ---> 'x' wrong name of device. 
# voltageDC.voltageDC('129.59.93.179', 'gpib0,22', 'hp34401a').get()
# WE HAVE TO disconnect the transaction or we will not recive any signal back!!


