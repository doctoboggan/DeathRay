# Name: Sets the trigger mode of the oscilloscope.
# Made by: Nadiah Zainol Abidin
# Date: 02/17/12  (MM/DD/YY)
# Goal: sets the trigger mode of the oscilloscope, 
# Devices:  1) dso6032a
# Modifiers:  None 
# SCPI command: 1) dso6032a: ---> Command Syntax ==> :TRIGger:MODE <mode>
# -------------- <mode>: -----------------
# <mode> ::= {EDGE | GLITch | PATTern | CAN | DURation | I2S |IIC
# | EBURst | LIN | M1553| SEQuence | SPI | TV | UART| USB | FLEXray}
# ----------------------------------------
# Result: One string. it notifies the osc is set to the trigger mode requested  

import data_acquisition

class getTrigMode(data_acquisition.vxi_11.vxi_11_connection,data_acquisition.gpib_utilities.gpib_device,data_acquisition.vxi_11.VXI_11_Error):		
  """
  This class sets the type of mode for the trigger
  """

  def __init__(self, IPad = '127.0.0.1', Gpibad = "inst0", namdev = "Network Device", timeout = 2000): 
    """
    Requiremnt: ( IPad, Gpibad, namdev, timeout)
    Ex of requirement: '129.59.93.179', 'gpib0,07', 'dso6032a', '3' , channel='1', timeout=3000)
    ____________________________
    To store the given values from the user. 
    Note:
      --> IPad is the number of ip-address with quotation mark. 
      --> Gpibad is the number of Gpib address with quotation mark.
      --> namdev is the name of the device.
      --> timeout is time duration of the operation. 
    """

    self.ip_id = IPad
    self.gpib_id = Gpibad
    self.name_of_device = namdev.lower()
    self.rightDevice = ['dso6032a'] 
    self.timeout = timeout
    rise_on_error = 0
    data_acquisition.vxi_11.vxi_11_connection.__init__(self,host=IPad,device=Gpibad,raise_on_err=rise_on_error,timeout=timeout,device_name=namdev)  
                                            #here we are feeding the data_acquisition library


  def check(self):
    """
    To check if the given device will work with getTrigMode function
    it also checks to make sure the setmode entered by the user is valid for the device
    ALso, we take care of time-out minimum duration (to aviod run out of time).
    Also, we remind the user if the input channel is not required for the given device. 
    """
    if self.name_of_device in self.rightDevice:

      if type(self.timeout) is int or type(self.timeout) is float:

        if self.timeout >= 500:      # hardcoded. Also, the number was choosen after several testing.

          if self.name_of_device == 'dso6032a':

            # start configuration for "dso6032a".   [START]

            return True
           
            # End of "dso6023a" configuration.   [END]

          else:   # You add new devices configuration here (by using "elif" function).
            print "The device does exist in the data base. However, it does not have any 'check' method configuration, which is not good thing. Anyway, we can not continuse until we have the check method for this device."
            return False, 'c'                                                                #the user may add elif here if there exist another device that works with the comman

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
    The main SCPI command. 
    First step:
    select the mode of the device. this is done using the SCPI command 
    TRIGger:MODE <mode>
    the type of mode can be selected from the following option:
    <mode> ::= {EDGE | GLITch | PATTern | CAN | DURation | I2S |IIC | EBURst | LIN | M1553| SEQuence | SPI | TV | UART| USB | FLEXray}
    """

    re = self.check()

    if re is True:

      print "PASS check test"         # For debug purpose

      if self.name_of_device == 'dso6032a':

          trig_mode = self.transaction('TRIG:MODE?')

          if trig_mode[0] == 0:             #check if it times out.

            print "It works !!"               # For debug reasons. 
            return trig_mode[2].strip()                # I have to consider this test here because I need to know the result. 

          else:
            print self.identify_vxi_11_error(trig_mode[0])      #print the error information.
            return False, trig_mode[0]  # It is going to return the error number. 

      
      else: 
        print "you should not be here at all. HOW DiD YOU PASS THE CHECK TEST !!"       
        # here , we add new devices with new commands (using "elif" command). The user should not get here at all 
        return False, 'w'


    else:

      return re

# ------------ Information : -----------
# page 485
# :TRIGger:MODE
# (see page 798)
# Command Syntax :TRIGger:MODE <mode>
# <mode> ::= {EDGE | GLITch | PATTern | CAN | DURation | I2S |IIC
# | EBURst | LIN | M1553| SEQuence | SPI | TV | UART
# | USB | FLEXray}
# The :TRIGger:MODE command selects the trigger mode (trigger type).
# Query Syntax :TRIGger:MODE?
# The :TRIGger:MODE? query returns the current trigger mode. If the
# :TIMebase:MODE is ROLL or XY, the query returns "NONE".
# --------------------------------------




