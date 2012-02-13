# Name: Voltage AC Reader
# Made by: Jack Minardi
# Date: 12/02/12  (MM/DD/YY)
# Goal: This moduel suppose to be able to return the voltage AC (with frequency) value from the given devices.
# Devcies:  1) "hp34401a" 
# Modifiers: 
# SCPI command: meas:volt:ac?
# Result: two floats 

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
    To check if the given device will work with voltageAC function (avoiding issues).
    """
    if self.name_of_device not in self.rightDevice:
      return False


    return True
  


  def get(self):		
    """
    The main SCPI commands, where the voltage AC value is !!
    """
    m = eval('libgpib.'+ self.name_of_device+'(host="'+self.ip_id+'", device="'+self.gpib_id+'")')   
    z , c , voltfix = m.transaction('meas:volt:ac?')
    z , c , freqfix = m.transaction('meas:freq?')
    m.disconnect()
    return (float(voltfix), float(freqfix))



