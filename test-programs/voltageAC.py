# Name:  AC voltage Reader
# Made by: Jack Minardi
# Date: 12/02/12  (MM/DD/YY)
# Goal: This moduel suppose to be able to return the AC voltage (with frequency) value from the given devices.
# Devcies:  1) "hp34401a" 
# Modifiers: 
# SCPI command: meas:volt:ac?
# Result: Two floats. One of them is the AC voltage value. And, the other one is frequency.

import libgpib

class voltageAC:		
  """
  This class provides the peak to peak AC voltage and the frequency in a tuple
  like this: (VPP, Freq)
  """

  def __init__(self, IPad, Gpibad, namdev): 

    self.ip_id = IPad
    self.gpib_id = Gpibad
    self.name_of_device = namdev
    self.rightDevice = ['hp34401a']

  def check(self):
    """
    To check if the given device will work with voltageAC function (avoiding issues).
    Also, it makes sure that the input channels do exist (to aviod conflicts). 
    """
    if self.name_of_device not in self.rightDevice:
      return False


    return True
  


  def get(self):		
    """
    The main SCPI commands, where the AC voltage value is !!
    """
    m = eval('libgpib.'+ self.name_of_device+'(host="'+self.ip_id+'", device="'+self.gpib_id+'")')   
    z , c , voltfix = m.transaction('meas:volt:ac?')
    z , c , freqfix = m.transaction('meas:freq?')
    m.disconnect()
    return (float(voltfix), float(freqfix))



