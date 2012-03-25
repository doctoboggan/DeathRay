# Name: Current AC Reader
# Made by: Anas Alfuntukh
# Date: 12/02/12  (MM/DD/YY)
# Goal: This moduel suppose to be able to return the AC current (with frequency) value from the given devices.
# Devcies:  1) "hp34401a" 
# Modifiers: 
# SCPI command: 1) "hp34401a" -----> get AC curent value ===> meas:curr:ac?
# Result: two floats. One of them is AC current. And, the other one is the frequency. 

import data_acquisition

class getcurrentAC(data_acquisition.vxi_11.vxi_11_connection,data_acquisition.gpib_utilities.gpib_device,data_acquisition.vxi_11.VXI_11_Error):		
  """
  This class provides the peak to peak current and the frequency in a tuple
  like this: (VPP, Freq)
  """

  def __init__(self, IPad = '127.0.0.1', Gpibad ="inst0" , namdev = "Network Device", timeout=2000): 

    """
    Requiremnt: ( IPad, Gpibad, namdev, channel='', timeout=2500)
    Ex of requirement: '129.59.93.179', 'gpib0,22', 'hp34401a', timeout=3000)
    ___________________________________________
        To store the given values from the user. 
    Note:
      --> IPad is the number of ip-address with quotation mark. 
      --> Gpibad is the number of Gpib address with quotation mark.
      --> namdev is the name of the device.
    Also, the definition has the devices list (hard-coded).
    Besdies that, you can control the time-out duration. The dafult time-out duration is 2500 msec. To change the time-out to 3000msec:
    Ex (for channel device with different time-out): ----- currentAC('129.59.93.27', 'gpib0,10', 'hp34401a', timeout=3000).get()
    Becareful with time-out, it will cause crazy issues if the time-out is small (ex: 100msec).
    """

    self.ip_id = IPad
    self.gpib_id = Gpibad
    self.name_of_device = namdev.lower()    #lower case the input
    self.timeout = timeout
    self.rightDevice = ['34401a']
    rise_on_error = 0
    data_acquisition.vxi_11.vxi_11_connection.__init__(self,host=IPad,device=Gpibad,raise_on_err=rise_on_error,timeout=timeout,device_name=namdev)  #here we are feeding the data_acquisition library

  def check(self):
    """
    To check if the given device will work with currentAC function (avoiding issues).
    ALso, we take care of time-out minimum duration (to aviod run out of time).
    """
    if self.name_of_device in self.rightDevice:

      if type(self.timeout) is float or type(self.timeout) is int:

        if self.timeout >= 1300:      # hardcoded. Also, the number was choosen after several testing.

          if self.name_of_device == '34401a':

          # start configuration of '34401a'.    [START]

            return True

          # end configuration of '34401a'.    [END]

          else:   # You add new devices configuration here (by using "elif" function).
            print "The device does exist in the data base. However, it does not have any 'check' method configuration, which is not good thing. Anyway, we can not continuse until we have the check method for this device."
            return False, 'c' 

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
    The main SCPI commands, where the AC current value is !!
    """
    if self.check() is True:

      print "PASS check test"         # For debug purpose

 
      if self.name_of_device == '34401a':

        currAC = self.transaction('meas:curr:ac?')
        self.disconnect
        print "AC current is "+currAC[2]      # For debug reasons.

        if currAC[0] == 0:             #check if it times out.

          return float(currAC[2])

        else:

          print  self.identify_vxi_11_error(currAC[0])      #print the error information.
          return False, currAC[0]   # return the error number.   
      
      else: 
        print "you should not be here at all. HOW DiD YOU PASS THE CHECK TEST !!"       # here , we add new devices with new commands (by adding "elif"). The user should not get here at all (hopefully)
        


    else:
      return self.check()

# Note:   ---> 'o' means time-out is too short.
#         ---> 'e' means empty string
#         ---> 'x' wrong name of device. 
# currentAC.currentAC('129.59.93.179', 'gpib0,22', 'hp34401a').get()
# add level of secure input on GUI level.
