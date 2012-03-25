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

class setdisplayscreen(data_acquisition.vxi_11.vxi_11_connection,data_acquisition.gpib_utilities.gpib_device,data_acquisition.vxi_11.VXI_11_Error):		
  """
  This class will show a sentence in the user interface panel.

  """

  def __init__(self, IPad = '127.0.0.1', Gpibad ="inst0" , namdev = "Network Device" , text_here='text here', timeout = 2000):  
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
    self.rightDevice = ['e3631a','34401a']
    rise_on_error = 0
    data_acquisition.vxi_11.vxi_11_connection.__init__(self,host=IPad,device=Gpibad,raise_on_err=rise_on_error,timeout=timeout,device_name=namdev)  #here we are feeding the data_acquisition library

  def check(self):
    """
    To check if the given device will work with Display string function (avoiding issues). 
    ALso, we take care of time-out minimum duration (to aviod run out of time).
    """
    if self.name_of_device in self.rightDevice:

      if self.time is not int or float:

        if self.timeout >= 500:      # hardcoded. Also, the number was choosen after several testing.

          if type(self.text) is str:    # Making sure that the input text is string to aviod issue in the SCPI command level.

            if self.name_of_device == 'e3631a' or '34401a':

              # Start configuration for 'e3631a' and '34401a'.     [START]

              if len(self.text) <= 12:

                return True

              else:
                print "The entered text is too long"    # For debug purpose
                return False, 'z' 

              # end of configuration for 'e3631a' and '34401a'.    [END]

            else: #if we have another device, add elif argument here
              print "The device does exist in the data base. However, it does not have any 'check' method configuration, which is not good thing. Anyway, we can not continuse until we have the check method for this device."
              return False, 'c'

          else:

            print "The input text is not string (can not be converted to string)."
            return False, 's'


        else:
          print "The time-out is too short"   # For debug purpose
          return False, 'o'

      else:
        print "timeout input is not acceptable"
        return False, 'q'

    else:
      print "the device is not in data base"    # For debug purpose
      return False, 'x'
  


  def do(self):		
    """
    The main SCPI commands, where the text string will be sent !!
    """

    if self.check() is True:

      print "PASS check test"
      
      m = self.transaction('disp:text "'+self.text+'"')
      
      if m[0] == 0:             #check if it times out.

          print "The text has been sent"
          return True

      else:

          print  self.identify_vxi_11_error(m[0])      #print the error information.
          return False, m[0]   # return the error number.   

    else: 

      return self.check()

# Note: the string will be in the panel until the time out is over. 
# Note:   ---> 'o' means time-out is too short.
#         ---> 'e' means empty string
#         ---> 'x' wrong name of device. 
# CcurrentDC.CcurrentDC('129.59.93.179', 'gpib0,22', 'hpe3631a').get()
# I am wondering what is different between -- self.disconnect() --- and --- self.disconnect --- ?




