# Name: DC current reader
# Made by: Anas Alfuntukh
# Date: 06/02/12  (MM/DD/YY)
# Goal: This moduel suppose to be able to return the DC current value from the given devices.
# Devcies:  1) "hp34401a" 2) 2) "hpe3631a"
# Modifiers:  None (for now)  
# SCPI command: meas:volt:ac?
# Result: One float. It is the DC current value.

import data_acquisition

class currentDC(data_acquisition.vxi_11.vxi_11_connection,data_acquisition.gpib_utilities.gpib_device):		
  """
  This class provides the DC current value of the given devices (to know the devices, please use
  'rightdevice' function.
  We are feeding the class with vxi_11.vxi_11_connection and gpib_utilities.gpib_device from data_acquisition library.
  """

  def __init__(self, IPad, Gpibad, namdev, channel='', timeout=1000): 
    """
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
    Besdies that, you can control the time-out duration. The dafult time-out duration is 1000 msec. To change the time-out to 500msec:
    Ex (for channel device with different time-out): ----- voltageDC('129.59.93.27', 'gpib0,10', 'hp34401a', channel='p25v', timeout=500).get()
    Becareful with time-out, it will cause crazy issues if the time-out is small (ex: 100msec).
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
    """
    if self.name_of_device not in self.rightDevice:
      return False

    if self.name_of_device == 'hpe3631a':
      if self.channel not in ['p6v', 'P6V', 'p25v', 'P25V', 'n25v', 'N25V', '']:
        return False

    return True
  


  def get(self):		
    """
    The main SCPI commands, where the DC current value is !!
    """
    crr = self.transaction('meas:curr:dc? '+self.channel)
    self.disconnect()
    return float(crr[2])

#print main('129.59.93.27', 'gpib0,10', 'hp34401a').check()
#print main('129.59.93.27', 'gpib0,10', 'hp34401a').main()
# Modify the manual. 
# discuss about the control modules.
# I have to know what rise_on_error means? I think I need to ask profossoe Meh...
# We are taking the third value in the range because it is the current value




