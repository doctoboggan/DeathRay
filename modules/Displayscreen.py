# Name: Voltage AC Reader
# Made by: Anas Alfuntukh
# Date: 12/02/12  (MM/DD/YY)
# Goal: This moduel suppose will write a string (of 12 character) in the interface panel.
# Devcies:  1) "hpe3631a" 2) "hp34401a"
# Modifiers: 
# SCPI command: disp:text "example"
# ---------------- <example>: -------------
# Note: example has to be around 12 characters (include the space). 
# Note: the sentence will be shown in the panel as far as timeout has not run out of time. 
# -----------------------------------------
# Result: Nothing

import data_acquisition

class Displayscreen(data_acquisition.vxi_11.vxi_11_connection,data_acquisition.gpib_utilities.gpib_device):		
  """
  This class will show a sentence in the user interface panel.

  """

  def __init__(self, IPad, Gpibad, namdev, text_here='text here', timeout = 500):  
    """
    Requiremnt: ( IPad, Gpibad, namdev, input, channel='', timeout=500)
    Ex of requirement: '129.59.93.179', 'gpib0,22', 'hpe3631a', 0.5 , channel='P25v', timeout=3000)
    ____________________________
    To store the given values from the user. 
    Note:
      --> IPad is the number of ip-address with quotation mark. 
      --> Gpibad is the number of Gpib address with quotation mark.
      --> namdev is the name of the device.
      --> text_here is the input text. 
      --> timeout is time duration of the operation. 
    Ex (for device) :  -----Displayscreen('129.59.93.27', 'gpib0,10', 'hp34401a', 'yes').get()-----
    Also, the definition has the devices list (hard-coded).
    Besdies that, you can control the time-out duration. The dafult time-out duration is 500 msec. To change the time-out to 3000msec:
    Ex (for channel device with different time-out): ----- CvoltageDC('129.59.93.27', 'gpib0,10', 'hp34401a', 15, channel='p25v', timeout=3000).get()
    Becareful with time-out, it will cause crazy issues if the time-out is small (ex: 100msec).
    """

    self.ip_id = IPad
    self.gpib_id = Gpibad
    self.name_of_device = namdev
    self.text = text_here
    self.timeout = timeout
    self.rightDevice = ['hpe3631a','hp34401a']
    rise_on_error = 0
    data_acquisition.vxi_11.vxi_11_connection.__init__(self,host=IPad,device=Gpibad,raise_on_err=rise_on_error,timeout=timeout,device_name=namdev)  #here we are feeding the data_acquisition library

  def check(self):
    """
    To check if the given device will work with Display string function (avoiding issues). 
    ALso, we take care of time-out minimum duration (to aviod run out of time).
    """
    if self.name_of_device in self.rightDevice:

      if self.timeout >= 500:      # hardcoded. Also, the number was choosen after several testing.

        if len(self.text) <= 12:

          return True

        else:
          print "The entered text is too long"    # For debug purpose
          return False, 't' 


      else:
        print "The time-out is too short"   # For debug purpose
        return False, 'o'

    else:
      print "the device is not in data base"    # For debug purpose
      return False, 'x'
  


  def get(self):		
    """
    The main SCPI commands, where the text string will be sent !!
    """

    if self.check() is True:
      
      self.transaction('disp:text "'+self.text+'"')
      self.disconnect
      print "It should print now. If not, check \n 1- The gpib address (double check). \n 2- I do not know....good luck... :p"
      return None

    else: 

      return self.check()

# Note: the string will be in the panel until the time out is over. 
# Note:   ---> 'o' means time-out is too short.
#         ---> 'e' means empty string
#         ---> 't' means the input text is not 
#         ---> 'x' wrong name of device. 
# CcurrentDC.CcurrentDC('129.59.93.179', 'gpib0,22', 'hpe3631a').get()
# I am wondering what is different between -- self.disconnect() --- and --- self.disconnect --- ?




