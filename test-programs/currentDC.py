# Name: DC current reader
# Made by: Anas Alfuntukh
# Date: 06/02/12  (MM/DD/YY)
# Goal: This moduel suppose to be able to return the DC current value from the given devices.
# Devcies:  1) "hp34401a" 2) 2) "hpe3631a"
# Modifiers:  None (for now)  
# SCPI command: meas:volt:ac?
# Result: One float. It is the DC current value.

import libgpib

class currentDC:		
  """
  This class provides the DC current value of the given devices (to know the devices, please use
  'rightdevice' function.
  """

  def __init__(self, IPad, Gpibad, namdev, channel=''): 
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
    """
    self.ip_id = IPad
    self.gpib_id = Gpibad
    self.name_of_device = namdev
    self.channel = channel
    self.rightDevice = ['hp34401a', 'hpe3631a']

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
    m = eval('libgpib.'+ self.name_of_device+'(host="'+self.ip_id+'", device="'+self.gpib_id+'")')   
    z , c , currfix = m.transaction('meas:curr:dc? '+self.channel)
    m.disconnect()  
    return float(currfix)

#print main('129.59.93.27', 'gpib0,10', 'hp34401a').check()
#print main('129.59.93.27', 'gpib0,10', 'hp34401a').main()
#add meas:vpp? <source> for the oscope (dso)
# Modify the manual. 
# discuss about the control modules.
# Add voltage read from the oscope
# compelte an example of channels (or multi-channel)
# Modify the docstring of the class.




