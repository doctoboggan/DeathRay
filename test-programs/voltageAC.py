# Name: Voltage Setter
# Made by: Anas Alfuntukh
# Date: 06/02/12  (MM/DD/YY)
# Goal: This moduel suppose to be able to return the voltage value from the given devices.
# Devcies:  1) "hp34401a"  2) "hpe3631a"
# Modifiers:  None (for now)  <----  Here the name of a developer, who may modify the code in the future, with the date.
# SCPI command: meas:volt:dc?
# Result: float

import libgpib

class voltageAC:		
  """
  This class provides the peak to peak voltage and the frequency in a tuple
  like this: (VPP, Freq)
  """

  def __init__(self, IPad, Gpibad, namdev): 

    self.ip_id = IPad
    self.gpib_id = Gpibad
    self.name_of_device = namdev
    self.rightDevice = ['hp34401a']

  def check(self):
    """
    To check if the given device will work with voltageDC function (avoiding issues).
    """
    if self.name_of_device not in self.rightDevice:
      return False


    return True
  


  def get(self):		
    """
    The main SCPI commands, where the voltage value is !!
    """
    m = eval('libgpib.'+ self.name_of_device+'(host="'+self.ip_id+'", device="'+self.gpib_id+'")')   
    z , c , voltfix = m.transaction('meas:volt:ac?')
    z , c , freqfix = m.transaction('meas:freq?')
    m.disconnect()
    return (float(voltfix), float(freqfix))



