# Name: Set DC current for given channel of given devices.
# Made by: Nadiah Zainol Abidin
# Date: 02/15/12  (MM/DD/YY)
# Goal: set a DC current to a specific channel.
# Devices:  1) "hpe3631a"
# Modifiers:  None 
# SCPI command:
# 1) hpe3631a: ---> Select channel  ==> inst:sel <channel>
#              ---> set the DC current  ==>  curr:lev:imm:ampl  <value>
# -------------- <channel>: --------------
# <channel> ::= {P6V | P25V | N25V}
# ----------------------------------------
# -------------- <value>: ----------------
# Becarefule, values are limited by the channel. Please see table #4-1 on page# 72 of "hpe3631a" manaule (in the manual folder).
# Also, note that, the current stay in that value until the time out is over. So, please feed it the right amount of time out duration. 
#-----------------------------------------
# Result: One string. it notifies output has been changed to the new DC current.  

import libgpib

class CcurrentDC:		
  """
  This class sets the DC current for the selected channel of the given device. 
  """

  def __init__(self, IPad, Gpibad, namdev, Input, channel=''): 

    self.ip_id = IPad
    self.gpib_id = Gpibad
    self.name_of_device = namdev
    self.rightDevice = ['hpe3631a']
    self.channels_for_hpe3631a = ['P6V', 'p6v', 'P25V', 'p25v', 'N25V', 'n25v']
    upperchannel = upper(channel) # To upper case the input channel (just in case). I do not know what will be the result with the numbers?!
    self.Channel = upperchannel
    self.value = Input

  def check(self):
    """
    To check if the given device will work with CCurrentDC function (to avoid module from crashing).
    It also checks if the specified channel of certain device matchs the data base of the names of channels in that device.
    For ex: hpe3631a has only these channels: P25V, N25V, and P6V. If the user inputs anything other than these names, 
    the function will not work. to avoid that, we have a check method to check the user's input. 
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
    followed by the channel number: <P6V|p6v|P25V|p25v|N25V|n25v> feeded in the __init__ (for the hpe3631a device)
    Second step: 
    sets the value of the DC current wanted on the channel selected in step 1. 
    This is done using the SCPI command curr:lev:imm:ampl ' followed by the input value 
    feeded in the _init_
    Note: between each transaction, we have to disconnect the connection to avoid time-out errors. This also allows other 
    connections to take place. 
    """
    m = eval('libgpib.'+ self.name_of_device+'(host="'+self.ip_id+'", device="'+self.gpib_id+'")')
    z , c , x = m.transaction('INST:SEL '+self.Channel)
    m.disconnect() #nadia: Are you sure we disconnect here? or after we select the value? <--- #Anas: Answer: I think we should disconnect twice (after each transmation)
    z , c , l = m.transaction('curr:lev:imm:ampl '+self.value)
    m.disconnect()
    return self.outputSelected+' has been selected. And, its current has been set to '+ self.value


# example: "INST:SEL P25V" Select the +25V output
# (nadia: not sure how? please explain in class about how you want me to describe it) <---- #Anas: It is very good now.
# nadia: I added some docstring for the get function work, does that look okay? <------ #Anas: Actually, It is very good. I added the name of the device (for future purpose)
