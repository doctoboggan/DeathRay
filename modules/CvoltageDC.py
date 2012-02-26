# Name: Set DC voltage for given channels of given devices.
# Made by: Nadiah Zainol Abidin
# Date: 02/15/12  (MM/DD/YY)
# Goal: set a DC voltage to a specific channel.
# Devices:  1) "hpe3631a"
# Modifiers:  None 
# SCPI command: 
# 1) hpe3631a: --> Select channel ==> inst:sel <channnel>
#              --> Set DC voltage ==> volt:lev:imm:ampl <value>
# ------------- <channel>: ---------------
# <channel> ::= {P6V | P25V | N25V}
# ----------------------------------------
# -------------- <value>: ----------------
# Becarefule, values are limited by the channel. Please see table #4-1 on page# 72 of "hpe3631a" manaule (in the manual folder).
# ----------------------------------------
# Result: One string. it notifies output has been changed to the new voltage.  

import data_acquisition

class CvoltageDC(data_acquisition.vxi_11.vxi_11_connection,data_acquisition.gpib_utilities.gpib_device):		
  """
  This class set DC voltage for given channels of the given device. 
  This class provides the DC current value of the given devices (to know the devices, please use
  'rightdevice' function.
  We are feeding the class with vxi_11.vxi_11_connection and gpib_utilities.gpib_device from data_acquisition library.
  """

  def __init__(self, IPad, Gpibad, namdev, Input, channel='', timeout = 2000): 
    """
    Requiremnt: ( IPad, Gpibad, namdev, input, channel='', timeout=2000)
    Ex of requirement: '129.59.93.179', 'gpib0,22', 'hpe3631a', '3' , channel='P25v', timeout=3000)
    ____________________________
    To store the given values from the user. 
    Note:
      --> IPad is the number of ip-address with quotation mark. 
      --> Gpibad is the number of Gpib address with quotation mark.
      --> namdev is the name of the device.
      --> input is the value of wanted DC voltage. 
      --> channel is a channel number for some devices. If the device do not have channels,
          the channel number will be ignored. 
      --> timeout is time duration of the operation. 
    Ex (for non-channel device) :  -----CvoltageDC('129.59.93.27', 'gpib0,10', 'hp34401a', 3).get()-----
    Ex (for channel device) :   -----CvoltageDC('129.59.93.27', 'gpib0,10', 'hp34401a', '5', channel='p25v').get()
    Also, the definition has the devices list (hard-coded).
    Besdies that, you can control the time-out duration. The dafult time-out duration is 2500 msec. To change the time-out to 3000msec:
    Ex (for channel device with different time-out): ----- CvoltageDC('129.59.93.27', 'gpib0,10', 'hp34401a', '15', channel='p25v', timeout=3000).get()
    Becareful with time-out, it will cause crazy issues if the time-out is small (ex: 100msec).
    """

    self.ip_id = IPad
    self.gpib_id = Gpibad
    self.name_of_device = namdev.lower()    #lower case the input
    self.rightDevice = ['hpe3631a']
    self.channels_for_hpe3631a = ['P6V', 'p6v', 'P25V', 'p25v', 'N25V', 'n25v']
    self.channel = channel.lower()    #lower case the input
    self.value = Input
    self.timeout = timeout
    rise_on_error = 0
    data_acquisition.vxi_11.vxi_11_connection.__init__(self,host=IPad,device=Gpibad,raise_on_err=rise_on_error,timeout=timeout,device_name=namdev)  #here we are feeding the data_acquisition library

  def check(self):
    """
    To check if the given device will work with CvoltageDC function (to avoid module from crashing).
    Also, it check if the specified channel of certain device matchs the data base of the names of channels in that device.
    For ex: hpe3631a has only these channels: P25V, N25V, and P6V. If the user inputs anything unlike these names, the function will not work. to aviod that, we have a check method for that.   
    To check if the given device will work with CvoltagetDC function (avoiding issues).
    Also, it makes sure that the input channels do exist (to aviod conflicts). 
    ALso, we take care of time-out minimum duration (to aviod run out of time).
    Also, we rmind the user if the input channel is not required for the given device.  
    """
    if self.name_of_device in self.rightDevice:
      print "0"
      if self.timeout >= 2000:      # hardcoded. Also, the number was choosen after several testing.
        print "1"
        if self.value is int or float:
          print "2"
          if self.name_of_device == 'hpe3631a':

            if self.channel not in ['p6v', 'P6V', 'p25v', 'P25V', 'n25v', 'N25V', '']:      # cor channel checking. Wehave to do this with each and every channelly device!!
              print "choosen channel does not exist !!"     # For debug purpose
              return False, 'c'
            else:
              return True

          else:
            if self.channel != '':
              print "The device does not have any channel. So, your input channel will be ignored."     # To remind the user about his/her mistake of entering channel, where the device does not have (for future devices). 
              return True
            else:
              return True

        else:
          print "The input voltage is not a number !!"  # For debug purpose
          return False, 'n'

      else:
        print "The time-out is too short"   # For debug purpose
        return False, 'o'

    else:
      print "the device is not in data base"    # For debug purpose
      return False, 'x'


  def get(self):		
    """
    The main SCPI command. It has two steps,
    First step:
    select the channel of the device. this is done using the SCPI command 'INST:SEL '
    followed by the channel <P6V|p6v|P25V|p25v|N25V|n25v> feeded in the __init__ (for the hpe3631a device)
    Second step: 
    sets the value of the DC voltage wanted on the channel selected in step 1. 
    This is done using the SCPI command volt:lev:imm:ampl ' followed by the input value 
    feeded in the _init_
    """

    if self.check() is True:

      print "PASS check test"         # For debug purpose

      if self.name_of_device == 'hpe3631a':

        set_channel = self.transaction('INST:SEL '+self.channel)      #First step
        set_voltageDC = self.transaction('volt:lev:imm:ampl '+self.value)   #second step
        print "DC voltage is "+set_voltageDC[2]    # For debug reasons.

        if set_voltageDC[2] == '':             #check if it times out.

          print "For some reasons, it times out. Maybe: \n 1- The gpib address is not right (Double check it). \n 2- The hard coded time-out duration is not enouph (if so, please modify the module 'currentDC' to the right time out[by hard coding it in check() and __init__() defs). \n 3- The hard coded SCPI command is not right (if so, please modify the module 'currentDC' by hard coded to the right SCPI command in get() command). \n 4- For other unknown reaosns !!.....Good luck :O"               # For debug reasons. 
          return False, 'e'               # I have to considre this test here because I need to know the result. 

        else:
          return self.channel +' has been selected. And, the DC voltage has been set to '+ self.value

      
      else: 
        print "you should not be here at all. HOW DiD YOU PASS THE CHECK TEST !!"       # here , we add new devices with new commands (using "elif" command). The user should not get here at all (hopefully).
        


    else:
      return self.check()


#example: "INST:SEL P25V" Select the +25V output
# Note:   ---> 'o' means time-out is too short.
#         ---> 'e' means empty string
#         ---> 'n' means input voltage is not number.
#         ---> 'c' means wrong channel input. 
#         ---> 'x' wrong name of device. 
# CvoltageDC.CvoltageDC('129.59.93.179', 'gpib0,22', 'hpe3631a').get()
# I could not test it because there is a bug in the data_acquisition
