# Name: Return coupled device 
# Made by: Nadiah Zainol Abidin
# Date: 02/15/12  (MM/DD/YY)
# Goal: to query which output is coupled
# Devices:  1) "hpe3631a"
# Modifiers:  None 
# SCPI command: INST:COUP?
# Result: One string. It is the currently coupled output.

import libgpib

class CoupOutput:		
  """
  This class returns the currently coupled output. Returns 'ALL', 'NONE', or a list. If any output is not coupled, 
  'NONE' is returned. If all of three outputs are coupled, 'ALL' is returned. If a list of outputs is coupled,
  the list is returned.
  """

  def __init__(self, IPad, Gpibad, namdev): 

    self.ip_id = IPad
    self.gpib_id = Gpibad
    self.name_of_device = namdev
    self.rightDevice = ['hpe3631a']

  def check(self):
    """
    To check if the given device will work with CvoltageDC function (to avoid module from crashing).
    """
    if self.name_of_device not in self.rightDevice:
      return False


    return True
  


  def get(self):		
    """
    The main SCPI command
    """
    m = eval('libgpib.'+ self.name_of_device+'(host="'+self.ip_id+'", device="'+self.gpib_id+'")')   
    z , c , coupdevice = m.transaction('INST:COUP?')
    m.disconnect()
    return (string(coupdevice))


# INSTrument:COUPle[:TRIGger]?
# This query returns the currently coupled output.
# Returns 'ALL', 'NONE', or a list. If any output is not coupled, 
# 'NONE' is returned. If all of three outputs are coupled, 'ALL' is returned.
# If a list of outputs is coupled, the list is returned.
