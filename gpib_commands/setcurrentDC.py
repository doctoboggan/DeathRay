# Name: Set DC current for given channel of given devices.
# Made by: Nadiah Zainol Abidin
# Date: 02/15/12  (MM/DD/YY)
# Goal: set a DC current to a specific channel.
# Devices:  1) "hpe3631a"
# Modifiers:  None 
# SCPI command:
# 1) hpe3631a: ---> Select channel  ==> inst:sel <channel>
#              ---> set the DC current  ==>  curr:lev:imm:ampl  <value>
# -------------- <channel>: --------------
# <channel> ::= {P6V | P25V | N25V}
# ----------------------------------------
# -------------- <value>: ----------------
# Becarefule, values are limited by the channel. Please see table #4-1 on page# 72 of "hpe3631a" manaule (in the manual folder).
# Also, note that, the current stay in that value until the time out is over. So, please feed it the right amount of time out duration. 
#-----------------------------------------
# Result: One string. it notifies output has been changed to the new DC current.  
# User input: voltage,float
# User input: channel,str

import data_acquisition

class setcurrentDC(data_acquisition.vxi_11.vxi_11_connection,data_acquisition.gpib_utilities.gpib_device,data_acquisition.vxi_11.VXI_11_Error):		
  """
  This class sets the DC current for the selected channel of the given device. 
  This class provides the DC current value of the given devices (to know the devices, please use
  'rightdevice' function.
  We are feeding the class with vxi_11.vxi_11_connection and gpib_utilities.gpib_device from data_acquisition library.
  """

  def __init__(self, IPad ='127.0.0.1' , Gpibad ="inst0" , namdev = "Network Device", current = '0.5', channel='p25v', Duration = '5000',  timeout = 2000): 

    """
    Requiremnt: ( IPad, Gpibad, namdev, input, channel='', timeout=2000)
    Ex of requirement: '129.59.93.179', 'gpib0,22', 'hpe3631a', 0.5 , 'P25v', 3000)
    ____________________________
    To store the given values from the user. 
    Note:
      --> IPad is the number of ip-address with quotation mark. 
      --> Gpibad is the number of Gpib address with quotation mark.
      --> namdev is the name of the device.
      --> input is the value of wanted DC current. 
      --> channel is a channel number for some devices. If the device do not have channels,
          the channel number will be ignored. 
      --> timeout is time duration of the operation. 
    Ex (for non-channel device) :  -----CcurrentDC('129.59.93.27', 'gpib0,10', 'hp34401a', '1').get()-----
    Ex (for channel device) :   -----CcurrentDC('129.59.93.27', 'gpib0,10', 'hp34401a', '0.5', channel='p25v').get()
    Also, the definition has the devices list (hard-coded).
    Besdies that, you can control the time-out duration. The dafult time-out duration is 2500 msec. To change the time-out to 3000msec:
    Ex (for channel device with different time-out): ----- CvoltageDC('129.59.93.27', 'gpib0,10', 'hp34401a', '1', channel='p25v', timeout=3000).get()
    Becareful with time-out, it will cause crazy issues if the time-out is small (ex: 100msec).
    """

    self.ip_id = IPad
    self.gpib_id = Gpibad
    self.name_of_device = namdev.lower()    #lower case the input
    self.rightDevice = ['e3631a']
    self.channels_for_e3631a = ['P6V', 'p6v', 'P25V', 'p25v', 'N25V', 'n25v']
    self.channel = channel.lower()    #lower case the input
    self.value = current
    self.timeout = timeout
    self.duration = int(Duration)
    rise_on_error = 0
    data_acquisition.vxi_11.vxi_11_connection.__init__(self,host=IPad,device=Gpibad,raise_on_err=rise_on_error,timeout=self.duration,device_name=namdev)  #here we are feeding the data_acquisition library

  def check(self):
    """
    To check if the given device will work with CCurrentDC function (to avoid module from crashing).
    It also checks if the specified channel of certain device matchs the data base of the names of channels in that device.
    For ex: hpe3631a has only these channels: P25V, N25V, and P6V. If the user inputs anything other than these names, 
    the function will not work. to avoid that, we have a check method to check the user's input. 
    To check if the given device will work with CcurrentDC function (avoiding issues).
    Also, it makes sure that the input channels do exist (to aviod conflicts). 
    ALso, we take care of time-out minimum duration (to aviod run out of time).
    Also, we rmind the user if the input channel is not required for the given device.
    Note: Some devices have its own characteristics. For that: 
    1) hpe3631a: There is current limitation in each channel (take a look at table #4-1 on page# 72 of "hpe3631a" manaule) 
    """
    
    if self.name_of_device in self.rightDevice:

      if self.timeout >= 10:      # hardcoded. Also, the number was choosen after several testing.

        if type(self.timeout) is int or type(self.timeout) is float:

          if type(self.value) is str:

            try:    # making sure that the input is a number.

              self.value = float(self.value)
            
              if self.name_of_device == 'e3631a':

                # start configure "e3631a".     [START]

                if type(self.channel) is str:

                  if self.channel not in self.channels_for_e3631a:      # cor channel checking. Wehave to do this with each and every channelly device!!

                    print "choosen channel does not exist for e3631a !!"     # For debug purpose
                    return False, 'c'

                  else:
                    

                        if self.channel in ['p6v']:

                          if self.value <= 5.15 and self.value >= 0:
                            
                            self.value = str(self.value)
                            return True
      
                          else: 

                            print "The imput DC current is not right (out of range)"    #debug
                            return False, 'z'

                        elif self.channel in ['p25v']:

                          if self.value <= 1.03 and self.value >= 0:

                            self.value = str(self.value)
                            return True

                          else: 
                            print "The imput DC current is not right (out of range)"    #debug
                            return False, 'z'

                        elif self.channel in ['n25v']:

                          if self.value <= 1.03 and self.value >= 0:

                            self.value = str(self.value)
                            return True

                          else: 

                            print "The imput DC current is not right (out of range)"    #debug
                            return False, 'z'

                        else:   # the user can not be here because we considre all posiblities...!

                          print "you should NOT BE HERE. HOW DID you DO ThAt!!! ;/ "    #debug
                          return False, 'w'


                else:

                  print "the channel input is not string"
                  return False, 's'

                  # End of characteristics of "e3631a". [END]

              else:   #if we have another device, add elif argument here
                print "The device does exist in the data base. However, it does not have any 'check' method configuration, which is not good thing. Anyway, we can not continuse until we have the check method for this device."
                return False, 'c'

            except ValueError:

              print "The current input value is not number (can not be converted to number)."
              return False, 'n'

          else:
            print "The input current type is not a string. I know the input is a number. However, it hasto be string type....sorry"  # For debug purpose
            return False, 's'

        else:

          print "timeout input is not acceptable"
          return False, 'q'

      else:
        print "The time-out is too short"   # For debug purpose
        return False, 'o'

    else:
      print "the device is not in data base"    # For debug purpose
      return False, 'x'
  


  def do(self):		
    """
    The main SCPI command. It has two steps,
    First step:
    select the channel of the device. this is done using the SCPI command 'INST:SEL '
    followed by the channel number: <P6V|p6v|P25V|p25v|N25V|n25v> feeded in the __init__ (for the hpe3631a device)
    Second step: 
    sets the value of the DC current wanted on the channel selected in step 1. 
    This is done using the SCPI command curr:lev:imm:ampl ' followed by the input value 
    feeded in the _init_
    Note: between each transaction, we have to disconnect the connection to avoid time-out errors. This also allows other 
    connections to take place. 
    """
    if self.check() is True:

      print "PASS check test"         # For debug purpose

      if self.name_of_device == 'e3631a':

        set_channel = self.write('INST:SEL '+self.channel)      #First step
        set_currentDC = self.write('curr:lev:imm:ampl '+self.value)   #second step. I have to convert 

        if set_currentDC[0] == 0:             #check if it times out.

          print "It works, the current has been set !!"               # For debug reasons. 
          return True               # I have to considre this test here because I need to know the result. 

        else:
          print self.identify_vxi_11_error(set_currentDC[0])      #print the error information.
          return False, set_currentDC[0]   # return the error number.

      
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
#         ---> 'q' timeout input is not number.
#         ---> 'w' something wrong with code.
#         ---> 'z' out of range 
# CcurrentDC.CcurrentDC('129.59.93.179', 'gpib0,22', 'hpe3631a').get()
# I have to considre when it the input is more than the limit ...!! I do not know. Still, the control modules are not rupest enouph. 
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

