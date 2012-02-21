# Name: DC current reader
# Made by: Anas Alfuntukh
# Date: 06/02/12  (MM/DD/YY)
# Goal: This moduel suppose to be able to return the DC current value from the given devices.
# Devcies:  1) "hp34401a" 2) 2) "hpe3631a"
# Modifiers:  None (for now)  
# SCPI command: 1) hpe3631a: ----> get DC current Value ===>  meas:curr:dc? <channel>
# ----------- <channel>" --------------
# <channel> ::= {p6v | p25v | n25v}
# Note: The dafult channel is the last active channel.
# -------------------------------------
#               2) hp34401a: -----> get DC curent value ===> meas:curr:dc?
# Result: One float. It is the DC current value.

import data_acquisition

class currentDC(data_acquisition.vxi_11.vxi_11_connection,data_acquisition.gpib_utilities.gpib_device):		
  """
  This class provides the DC current value of the given devices (to know the devices, please use
  'rightdevice' function.
  We are feeding the class with vxi_11.vxi_11_connection and gpib_utilities.gpib_device from data_acquisition library.
  """

  def __init__(self, IPad, Gpibad, namdev, channel='', timeout=2500): 
    """
    Requiremnt: ( IPad, Gpibad, namdev, channel='', timeout=2500)
    Ex of requirement: '129.59.93.179', 'gpib0,22', 'hpe3631a', channel='P25v', timeout=3000)
    __________________
    To store the given values from the user. 
    Note:
      --> IPad is the number of ip-address with quotation mark. 
      --> Gpibad is the number of Gpib address with quotation mark.
      --> namdev is the name of the device.
      --> channel is a channel number for some devices. If the device do not have channels,
          the channel number will be ignored. 
    Ex (for non-channel device) :  -----currentDC('129.59.93.27', 'gpib0,10', 'hp34401a').get()-----
    Ex (for channel device) :   -----currentDC('129.59.93.27', 'gpib0,10', 'hp34401a', channel='p25v').get()
    Also, the definition has the devices list (hard-coded).
    Besdies that, you can control the time-out duration. The dafult time-out duration is 2500 msec. To change the time-out to 3000msec:
    Ex (for channel device with different time-out): ----- currentDC('129.59.93.27', 'gpib0,10', 'hp34401a', channel='p25v', timeout=3000).get()
    Becareful with time-out, it will cause crazy issues if the time-out is small (ex: 1000msec).
    """
    self.ip_id = IPad
    self.gpib_id = Gpibad
    self.name_of_device = namdev.lower()    #lower case the input
    self.channel = channel.lower()          #lower case the input
    self.rightDevice = ['hp34401a', 'hpe3631a']
    rise_on_error = 0
    data_acquisition.vxi_11.vxi_11_connection.__init__(self,host=IPad,device=Gpibad,raise_on_err=rise_on_error,timeout=timeout,device_name=namdev)  #here we are feeding the data_acquisition library

  def check(self):
    """
    To check if the given device will work with currentDC function (avoiding issues).
    Also, it makes sure that the input channels do exist (to aviod conflicts). 
    ALso, we take care of time-out minimum duration (to aviod run out of time).
    Aslo, we rmind the user if the input channel is not required for the given device. 
    """
    if self.name_of_device in self.rightDevice:

      if self.timeout >= 2500:      # hardcoded. Also, the number was choosen after several testing.

        if self.name_of_device == 'hpe3631a':

          if self.channel not in ['p6v', 'P6V', 'p25v', 'P25V', 'n25v', 'N25V', '']:      # cor channel checking. Wehave to do this with each and every channelly device!!
            print "choosen channel does not exist !!"     # For debug purpose
            return False, 'c'
          else:
            return True

        else:
          if self.channel != '':
            print "The device does not have any channel. So, your input channel will be ignored."     # To remind the user about his/her mistake of entering channel, where the device does not have. 
            return True
          else:
            return True

      else:
        print "The time-out is too short"   # For debug purpose
        return False, 'o'

    else:
      print "the device is not in data base"    # For debug purpose
      return False, 'x'

  


  def get(self):		
    """
    The main SCPI commands, where the DC current value is !!
    """
    if self.check() is True:

      print "PASS check test"         # For debug purpose

      if self.name_of_device == 'hpe3631a':

        currDC = self.transaction('meas:curr:dc? '+self.channel)
        self.disconnect
        print "DC current is "+currDC[2]    # For debug reasons.

        if currDC[2] == '':             #check if it times out.

          print "For some reasons, it times out. Maybe the hard coded time-out duration is not enouph (if so, please modify the module 'currentDC' to the right time out[by hard coding it in check() and __init__() defs). Or, the hard coded SCPI command is not right (if so, please modify the module 'currentDC' by hard coded to the right SCPI command in get() command). Or, for other unknown reaosns !!.....Good luck :O"               # For debug reasons. 
          return False, 'e'               # I have to considre this test here because I need to know the result. 

        else:

          return float(currDC[2])
 
      elif self.name_of_device == 'hp34401a':

        currDC = self.transaction('meas:curr:dc?')
        self.disconnect
        print "DC current is "+currDC[2]      # For debug reasons.

        if currDC[2] == '':             #check if it times out.

          print "For some reasons, it times out. Maybe the hard coded time-out duration is not enouph (if so, please modify the module 'currentDC' to the right time out[by hard coding it in check() and __init__() defs). Or, the hard coded SCPI command is not right (if so, please modify the module 'currentDC' by hard coded to the right SCPI command in get() command). Or, for other unknown reaosns !!.....Good luck :O"               # For debug reasons. 
          return False, 'e'               # I have to considre this test here because I need to know the result. 

        else:

          return float(currDC[2])
      
      else: 
        print "you should not be here at all. HOW DiD YOU PASS THE CHECK TEST !!"       # here , we add new devices with new commands. The user should not get here at all (hopefully)
        


    else:
      return self.check()


#print main('129.59.93.27', 'gpib0,10', 'hp34401a').check()
#print main('129.59.93.27', 'gpib0,10', 'hp34401a').main()
# Modify the manual. 
# discuss about the control modules.
# I have to know what rise_on_error means? I think I need to ask profossoe Meh...
# We are taking the third value in the range because it is the current value
# Note: hp34401a has the ability to control channel (it has multiple channels). hp34401a has onlt one channel to read from. 
# Note:   ---> 'o' means time-out is too short.
#         ---> 'e' means empty string
#         ---> 'c' means wrong channel input. 
#         ---> 'x' wrong name of device. 
# currentDC.currentDC('129.59.93.179', 'gpib0,22', 'hp34401a').get()




