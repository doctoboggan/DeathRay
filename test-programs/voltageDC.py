# Name: Voltage reader
# Made by: Anas Alfuntukh
# Date: 06/02/12  (MM/DD/YY)
# Goal: This moduel suppose to be able to return the voltage value from the given devices.
# Devcies:  1) "hp34401a"  2) "hpe3631a"
# Modifiers:  None (for now)  <----  Here the name of a developer, who may modify the code in the future, with the date.
# SCPI command: meas:volt:dc?
# Result: float

import libgpib

class voltageDC:		
  """
  This class provides the Voltage value of the given devices (to know the devices, please use 'rightdevice' function.
  """

  def __init__(self, IPad, Gpibad, namdev, channel=None): 
    """
    To store the given values from the user. 
    Note:
      -->IPad is the number of ip-address with quotation mark. 
      --> Gpibad is the number of Gpib address with quotation mark.
      --> namdev is the name of the device
    Ex:  -----main('129.59.93.27', 'gpib0,10', 'hp34401a')-----
    """
    self.ip_id = IPad
    self.gpib_id = Gpibad
    self.name_of_device = namdev
    self.rightDevice = ['hp34401a', 'hpe3631a']

  def check(self):
    """
    To check if the given device will work with Voltage_dc function (avioding cause issues).
    """
    if self.name_of_device not in self.rightDevice:
      return False
    else:
      return True

  def get(self):		
    """
    The main command, where the voltage value is !!
    """
    m = eval('libgpib.'+ self.name_of_device+'(host="'+self.ip_id+'", device="'+self.gpib_id+'")')   
    z , c , voltfix = m.transaction('meas:volt:dc?')
    volt = float(voltfix)  
    return volt

#print main('129.59.93.27', 'gpib0,10', 'hp34401a').check()
#print main('129.59.93.27', 'gpib0,10', 'hp34401a').main()
#add meas:vpp? <source> for the oscope (dso)




