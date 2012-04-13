# Name: Voltage AC Reader
# Made by: Anas Alfuntukh
# Date: 12/02/12  (MM/DD/YY)
# Goal: This moduel suppose will write a string (of 12 character) in the interface panel.
# Devcies:  1) "hpe3631a" 
# Modifiers: 
# SCPI command: disp:text "example"
# Result: Nothing

import libgpib

class Displayscreen:		
  """
  This class will show a sentence in the user interface panel.

  """

  def __init__(self, IPad, Gpibad, namdev, text_here='text here', timeout=10):  
    """
    The defalult string is "text here".
    """

    self.ip_id = IPad
    self.gpib_id = Gpibad
    self.name_of_device = namdev
    self.text = text_here
    self.time_out = timeout
    self.rightDevice = ['hpe3631a']

  def check(self):
    """
    To check if the given device will work with Display string function (avoiding issues).
    """
    if self.name_of_device not in self.rightDevice:
      return False

    if self.time_out < 10: 
      """
      To aviod vewry small duration, which casue some issue with the device.
      """
      return False

    return True
  


  def get(self):		
    """
    The main SCPI commands, where the text string will be sent !!
    """
    m = eval('libgpib.'+ self.name_of_device+'(host="'+self.ip_id+'", device="'+self.gpib_id+'", timeout='+str(self.time_out)+')')       # Here, we can adjust the duration of string displaying 
    print self.text
    m.transaction('disp:text "'+self.text+'"')      ## There is no need to save the rsult because there will be no result (it is going to be time out)
    m.disconnect()
    return None     # I think I do not need to return any thing (or may just say true, so that, it means the string has been sent)

# Note: the string will be in the panel until the time out is over. 
# How check will really chack??!




