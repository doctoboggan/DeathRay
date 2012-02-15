# Name: Select output <P6V, P25V, N25V> 
# Made by: Nadiah Zainol Abidin
# Date: 02/15/12  (MM/DD/YY)
# Goal: to select an output
# Devices:  1) "hpe3631a"
# Modifiers:  None 
# SCPI command: INST:SEL <P6V|P25V|N25V>
# Result: One string. it notifies output has been selected 

import libgpib

class SelOutput:		
  """
  This class 
  """

  def __init__(self, IPad, Gpibad, namdev, output): 

    self.ip_id = IPad
    self.gpib_id = Gpibad
    self.name_of_device = namdev
    self.rightDevice = ['hpe3631a']
    self.outputSelected = output

  def check(self):
    """
    To check if the given device will work with SelOutput function (to avoid module from crashing).
    """
    if self.name_of_device not in self.rightDevice:
      return False


    return True
  


  def get(self):		
    """
    The main SCPI command
    """
    m = eval('libgpib.'+ self.name_of_device+'(host="'+self.ip_id+'", device="'+self.gpib_id+'")')   
    z , c , x = m.transaction('INST:SEL'+self.outputSelected)
    m.disconnect()
    return self.outputSelected+' has been selected'


#example: "INST:SEL P25V" Select the +25V output
