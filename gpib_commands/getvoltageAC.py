# Name:  AC voltage Reader
# Made by: Jack Minardi
# Date: 12/02/12  (MM/DD/YY)
# Goal: This moduel suppose to be able to return the AC voltage (with frequency) value from the given devices.
# Devcies:  1) "hp34401a" 
# Modifiers: 
# SCPI command: 1) hp34401a: ---> getting the AC voltage ==> meas:volt:ac? 
#                            ---> getting the frequancy ==> meas:freq?
# Result: Two floats. One of them is the AC voltage value. And, the other one is frequency.

import data_acquisition

class getvoltageAC(data_acquisition.vxi_11.vxi_11_connection,data_acquisition.gpib_utilities.gpib_device,data_acquisition.vxi_11.VXI_11_Error):		
  """
  This class provides the peak to peak AC voltage and the frequency in a tuple
  like this: (VPP, Freq)
  We are feeding the class with vxi_11.vxi_11_connection and gpib_utilities.gpib_device from data_acquisition library. 
  """

  def __init__(self, IPad ='127.0.0.1' , Gpibad ="inst0" , namdev ="Network Device", timeout=2000): 
    '''
    Requiremnt: ( IPad, Gpibad, namdev, timeout=2000)
    Ex of requirement: '129.59.93.179', 'gpib0,22', 'hp34401a', timeout=2000)
    ________________________________
    /\ To store the given values from the user. 
    /\ Note:
      --> IPad is the number of ip-address with quotation mark. 
      --> Gpibad is the number of Gpib address with quotation mark.
      --> namdev is the name of the device.
    
    /\ Besdies that, you can control the time-out duration. The dafult time-out duration is 2500 msec  (and, it is the minimum time, where command can run) (please, do not lower it than that. It will cause an issue). To change the time-out to 500msec:
    /\ Ex (different time-out): ----- voltageAC('129.59.93.27', 'gpib0,10', 'hp34401a', timeout=500).get()
    /\ Becareful with time-out, it will cause crazy issues if the time-out is small (ex: 100msec).
    /\ Note: there is no channel input because "hp34401a" (which is the only device on this module for now) has only one channel to read AC voltage. In the future, if there is another device (which has multiple channel to read AC voltage, you (as developer) should add channel input (see voltageDC.py as an example) 
    '''

    self.ip_id = IPad
    self.gpib_id = Gpibad
    self.name_of_device = namdev.lower()
    self.timeout = timeout
    self.rightDevice = ['34401a']
    rise_on_error = 0
    data_acquisition.vxi_11.vxi_11_connection.__init__(self,host=IPad,device=Gpibad,raise_on_err=rise_on_error,timeout=timeout,device_name=namdev)  #here we are feeding the data_acquisition library

  def check(self):
    """
    To check if the given device will work with voltageAC function (avoiding issues).
    Also, it makes sure that the input channels do exist (to aviod conflicts). 
    ALso, we take care of time-out minimum duration (to aviod run out of time).
    """
    if self.name_of_device in self.rightDevice:

      if self.timeout >= 2000:      # hardcoded. Also, the number was choosen after several testing.

        return True 

      else:
        print "The time-out is too short"   # For debug purpose
        return False, 'o'

    else:
      print "the device is not in data base"    # For debug purpose
      return False, 'x'





  def do(self):		
    """
    The main SCPI commands, where the AC voltage value is !!
    Note: we are taking the third return value because it is the one, which we are looking for.
    Note: we are checking before running the command.  
    """   

    if self.check() is True:

      print "PASS check test"         # For debug purpose

      if self.name_of_device == '34401a':           # the device was specified to make the program more ropust and easy to expand in the future.

        voltAC = self.transaction('meas:volt:ac?')
        print "AC voltage is "+voltAC[2]    # For debug reasons.

        if voltAC[0] == 0:             #check if it times out.

          return float(voltAC[2])

        else:

          print  self.identify_vxi_11_error(voltAC[0])      #print the error information.
          return False, voltAC[0]   # return the error number.   

      
      else: 
        print "you should not be here at all. HOW DiD YOU PASS THE CHECK TEST !!"       # here , we add new devices with new commands. The user should not get here at all (hopefully)
        


    else:
      return self.check()

# we have some series issues here:
# 1) the timeout effect the result. If the timeout is too short, the reult will be empty string (which means time-out occurred). So depends on the operation, we have to make dafult time out is at right duration. In this case, timout = 1000 msec is not enough. I changed the dafult timeout to 2300 msec (after several testing).
# 2) In case of timeout occurre (in any situation) the "get" command will return empty string. In that case, we can not convert the result (which will be empty string)  to a number (float) because if we do, it will crash the module. The solution for this complex issue in few steps: 
# A) call the "check" command in the "get" command. So, if it returns true, continue the operation. if it return false, break and send wrong input warning. (will cover 65% of the issue)
# B) make sure the dafult time-out is right.. Also, make sure the input time-out is reasonable (equal or higher than the dafult). (will cover 15%)
# C) check the return value of get. If it is an empty string, return a symbol verible (which means time out occure). (will cover 20%) 


# x means is not in the data base. o means time-out is too short.
# I choose to name it "o" or "x" for a reason. To defind them to the computer. So that, the computer can tell the user via GUI it is time-out or wrong input (for now). 
# to test the file, run (after import it): tesvoltageAC.voltageAC('129.59.93.179', 'gpib0,22', 'hp  34401a', timeout=5000).get()
# Note: yo can play with the name of device or with the time-out value. The program us smart enough to know ifit should run the command or not. Moreover, you do not need to enter time-out value as following: 
# getvoltageAC.getvoltageAC('129.59.93.179', 'gpib0,22', 'hp34401a').do()
