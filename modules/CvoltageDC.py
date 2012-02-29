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
# Note: the negative channel only accept negative values. 
# ----------------------------------------
# Result: One string. it notifies output has been changed to the new voltage.  

import data_acquisition

class setvoltageDC(data_acquisition.vxi_11.vxi_11_connection,data_acquisition.gpib_utilities.gpib_device,data_acquisition.vxi_11.identify_vxi_11_error):		
  """
  This class set DC voltage for given channels of the given device. 
  This class provides the DC current value of the given devices (to know the devices, please use
  'rightdevice' function.
  We are feeding the class with vxi_11.vxi_11_connection and gpib_utilities.gpib_device from data_acquisition library.
  """

  def __init__(self, IPad, Gpibad, namdev, Input, channel='p25v', timeout = 500): 
    """
    Requiremnt: ( IPad, Gpibad, namdev, input, channel='p25v', timeout=500)
    Ex of requirement: '129.59.93.179', 'gpib0,22', 'hpe3631a', '3' , channel='n25v', timeout=3000)
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
    Also, we remind the user if the input channel is not required for the given device. 
    Note: Some devices have its own characteristics. For that: 
    1) hpe3631a: There is voltage limitation in each channel (take a look at table #4-1 on page# 72 of "hpe3631a" manaule)
    """
    if self.name_of_device in self.rightDevice:

      if type(self.timeout) is int or float:

        if self.timeout >= 500:      # hardcoded. Also, the number was choosen after several testing.

          if type(self.value) is int or float:

            if self.name_of_device == 'hpe3631a':

              if self.channel not in ['p6v', 'P6V', 'p25v', 'P25V', 'n25v', 'N25V']: # for channel checking. Wehave to do this with each and every channelly device!! (we can not accept unknow channel any more).
                print "choosen channel does not exist !!"     # For debug purpose
                return False, 'c'
              else:
                # from here, we are entering characteristics of hpe3631a. [START]
                if self.channel in ['p6v']:

                  if self.value <= 6.18 and self.value >= 0:

                    return True

                  else: 

                    print "The imput DC voltage is not right (out of range)"    #debug
                    return False, 'z'

                elif self.channel in ['p25v']:

                  if self.value <= 25.75 and self.value >= 0:

                    return True

                  else: 
                    print type(self.value)   #debug
                    print self.value  #debug
                    print "The imput DC voltage is not right (out of range)"    #debug
                    return False, 'z'

                elif self.channel in ['n25v']:

                  if self.value <= 0 and self.value >= -25.75:

                    return True

                  else: 

                    print "The imput DC voltage is not right (out of range)"    #debug
                    return False, 'z'

                else:

                  print "you should NOT BE HERE. HOW DID you DO ThAt!!! ;/ "    #debug
                  return False, 'w'

                # End of characteristics of hpe3631a. [END]

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

        print "timeout input is not acceptable"
        return False, 'q'

    else:
      print "the device is not in data base"    # For debug purpose
      return False, 'x'


  def do(self):		
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

        # we can add a new check for making sure the psoitive nad negative values. 

          set_channel = self.transaction('INST:SEL '+self.channel)      #First step
          interger_value = str(self.value)      #convert to string
          set_voltageDC = self.transaction('volt:lev:imm:ampl '+interger_value)   #second step

          print "DC voltage is "+set_voltageDC[2]    # For debug reasons.

          if set_voltageDC[0] == 0:             #check if it times out.

            print "It works !!"               # For debug reasons. 
            return True                # I have to considre this test here because I need to know the result. 

          else:
            print self.identify_vxi_11_error(set_voltageDC[0])      #print the error information.
            return False, set_voltageDC[0]  # It is going to return the error number. 

      
      else: 
        print "you should not be here at all. HOW DiD YOU PASS THE CHECK TEST !!"       # here , we add new devices with new commands (using "elif" command). The user should not get here at all (hopefully).
        return False, 'w'


    else:
      return self.check()


#example: "INST:SEL P25V" Select the +25V output
# Note:   ---> 'o' means time-out is too short.
#         ---> 'e' means empty string
#         ---> 'n' means input voltage is not number.
#         ---> 'c' means wrong channel input. 
#         ---> 'x' wrong name of device. 
#         ---> 'w' wired error (something wrong with code)
#         ---> 'z' out of range 
#         ---> 'q' timeout input is not number.
# CvoltageDC.CvoltageDC('129.59.93.179', 'gpib0,22', 'hpe3631a').get()
# check if input is negative or not for the negative or positive channels. 
# we have another douple check in the GUI level (the user input)
#--------------------------------------
# For error number, THe meaning is: 
#       1:"Syntax error", 3:"Device not accessible",
# 			4:"Invalid link identifier", 5:"Parameter error", 6:"Channel not established",
#				8:"Operation not supported", 9:"Out of resources", 11:"Device locked by another link",
#				12:"No lock held by this link", 15:"IO Timeout", 17:"IO Error",  21:"Invalid Address",
# 			23:"Abort", 29:"Channel already established" ,
#				"eof": "Cut off packet received in rpc.recvfrag()",
#				"sync":"stream sync lost",
#				"notconnected": "Device not connected"}
#---------------------------------------
