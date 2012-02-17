# Name: Set DC voltage for given channels of given devices.
# Made by: Nadiah Zainol Abidin
# Date: 02/15/12  (MM/DD/YY)
# Goal: set a DC voltage to a specific channel.
# Devices:  1) "hpe3631a"
# Modifiers:  None 
# SCPI command: 
# 1) hpe3631a: --> Select channel ==> inst:sel <channnel>
#              --> Set DC voltage ==> volt:lev:imm:ampl <value>
# Result: One string. it notifies output has been changed to the new voltage.  

import libgpib

class CvoltageDC:		
  """
  This class set DC voltage for given channels of the given device. 
  """

  def __init__(self, IPad, Gpibad, namdev, Input, channel=''): 

    self.ip_id = IPad
    self.gpib_id = Gpibad
    self.name_of_device = namdev
    self.rightDevice = ['hpe3631a']
    self.channels_for_hpe3631a = ['P6V', 'p6v', 'P25V', 'p25v', 'N25V', 'n25v']
    self.Channel = channel
    self.value = Input

  def check(self):
    """
    To check if the given device will work with CvoltageDC function (to avoid module from crashing).
    Also, it check if the specified channel of certain device matchs the data base of the names of channels in that device.
    For ex: hpe3631a has only these channels: P25V, N25V, and P6V. If the user inputs anything unlike these names, the function will not work. to aviod that, we have a check method for that.     
    """
    if self.name_of_device not in self.rightDevice:
      return False
    if self.name_of_device is 'hpe3631a':
      if self.Channel not in self.channels_for_hpe3631a:
        return False

    return True
  


  def get(self):		
     """
    The main SCPI command. It has two steps,
    First step:
    select the channel of the device. this is done using the SCPI command 'INST:SEL '
    followed by the channel <P6V|p6v|P25V|p25v|N25V|n25v> feeded in the __init__ (for the hpe3631a device)
    Second step: 
    sets the value of the DC voltage wanted on the channel selected in step 1. 
    This is done using the SCPI command volt:lev:imm:ampl ' followed by the input value 
    feeded in the _init_
    Note: between each transmation, we have to disconnect the connection to aviod time-out errors. Also, to allow other connection to be established. 
    """
    m = eval('libgpib.'+ self.name_of_device+'(host="'+self.ip_id+'", device="'+self.gpib_id+'")')   
    z , c , x = m.transaction('INST:SEL'+self.outputSelected)
    m.disconnect()
    z , c , l = m.transaction('volt:lev:imm:ampl '+self.value)
    m.disconnect()
    return self.outputSelected+' has been selected. And, the voltage has been set to '+ self.value


#example: "INST:SEL P25V" Select the +25V output
