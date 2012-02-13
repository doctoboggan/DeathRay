# Name: Current AC Reader
# Made by: Anas Alfuntukh
# Date: 12/02/12  (MM/DD/YY)
# Goal: This moduel suppose to be able to return the Current AC (with frequency) value from the given devices.
# Devcies:  1) "hp34401a" 
# Modifiers: 
# SCPI command: meas:curr:ac?
# Result: two floats. One of them is current. And, the other one is the frequency. 

import libgpib

class currentAC:		
  """
  This class provides the peak to peak current and the frequency in a tuple
  like this: (VPP, Freq)
  """

  def __init__(self, IPad, Gpibad, namdev): 

    self.ip_id = IPad
    self.gpib_id = Gpibad
    self.name_of_device = namdev
    self.rightDevice = ['hp34401a']

  def check(self):
    """
    To check if the given device will work with currentAC function (avoiding issues).
    """
    if self.name_of_device not in self.rightDevice:
      return False


    return True
  


  def get(self):		
    """
    The main SCPI commands, where the current AC value is !!
    """
    m = eval('libgpib.'+ self.name_of_device+'(host="'+self.ip_id+'", device="'+self.gpib_id+'")')   
    z , c , currfix = m.transaction('meas:curr:ac?')
    z , c , freqfix = m.transaction('meas:freq?')
    m.disconnect()
    return (float(currfix), float(freqfix))

