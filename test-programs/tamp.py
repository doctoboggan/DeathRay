# Name: module_name
# Made by: module_person  Using add module function
# Date: module_date  (MM/DD/YY)
# Goal: module_goal
# Devcies:  1) module_device_one 2) module_device_two 3) module_device_three 4) module_device_four 5) module_device_five    #if they are more than five, creat with five. Than use edit module to add more devices. mention that in GUI.Also, do not forget '""'
# Modifiers:  None (for now) 
# Dependancy: 1) QT GUI 
# SCPI command: 1) module_device_one : ----> scpi_goal ===>  module_device_one_scpi
#               2) module_device_two : ----> scpi_goal ===> module_device_two_scpi
#               3) module_device_three: ----> scpi_goal ===> module_device_three_scpi
#               4) module_device_four: ----> scpi_goal ===> module_device_four_scpi
#               5) module_device_five: ----> scpi_goal ===> module_device_five_scpi
# Result: module_result

import data_acquisition

class getvoltageDC(data_acquisition.vxi_11.vxi_11_connection,data_acquisition.gpib_utilities.gpib_device,data_acquisition.vxi_11.VXI_11_Error):

  '''
  class_info
  '''
  def __init__(self, IPad = '127.0.0.1', Gpibad ="inst0" , namdev = "Network Device", timeout=2000): 

    '''
    init_info
    '''

    self.ip_id = IPad
    self.gpib_id = Gpibad
    self.name_of_device = namdev.lower()    #lower case the input 
    self.rightDevice = [module_device_one, module_device_two, module_device_three, module_device_four, module_device_five]
    rise_on_error = 0
    data_acquisition.vxi_11.vxi_11_connection.__init__(self,host=IPad,device=Gpibad,raise_on_err=rise_on_error,timeout=timeout,device_name=namdev)  #here we are feeding the data_acquisition library

  def check(self):
    """
    check_info
    """
    if self.name_of_device in self.rightDevice:

      if type(self.timeout) is float or type(self.timeout) is int:

        if self.timeout >= 300:      # hardcoded. Also, the number was choosen after several testing.

          if self.name_of_device == module_device_one :

            # start configure module_device_one .     [START]

            return True

            # End of characteristics of module_device_one . [END]

          elif self.name_of_device ==  module_device_two :

            # start configure module_device_two .     [START]

            return True

            # End of characteristics of module_device_two . [END]

          elif self.name_of_device ==  module_device_three :

            # start configure module_device_three .     [START]

            return True

            # End of characteristics of module_device_three . [END]

          elif self.name_of_device ==  module_device_four :

            # start configure module_device_four .     [START]

            return True

            # End of characteristics of module_device_four . [END]

          elif self.name_of_device ==  module_device_five :

            # start configure module_device_five .     [START]

            return True

            # End of characteristics of module_device_five . [END]


          else:    #if we have another device, add elif argument here
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
    do_info
    """  
    if self.check() is True:

      print "PASS check test"         # For debug purpose

      if self.name_of_device == module_device_one :

        result = self.transaction( main_scpi_one input_one )                

        if result[0] == 0:             #check if it times out.

          return float(result[2])

        else:

          print  self.identify_vxi_11_error(result[0])      #print the error information.
          return False, result[0]   # return the error number. 


 
      elif self.name_of_device == module_device_two :

        result = self.transaction( main_scpi_two input_two )                

        if result[0] == 0:             #check if it times out.

          return float(result[2])

        else:

          print  self.identify_vxi_11_error(result[0])      #print the error information.
          return False, result[0]   # return the error number. 


      elif self.name_of_device == module_device_three :

        result = self.transaction( main_scpi_three input_three )                

        if result[0] == 0:             #check if it times out.

          return float(result[2])

        else:

          print  self.identify_vxi_11_error(result[0])      #print the error information.
          return False, result[0]   # return the error number. 


      if self.name_of_device == module_device_four :

        result = self.transaction( main_scpi_four input_four )                

        if result[0] == 0:             #check if it times out.

          return float(result[2])

        else:

          print  self.identify_vxi_11_error(result[0])      #print the error information.
          return False, result[0]   # return the error number. 


      if self.name_of_device == module_device_five :

        result = self.transaction( main_scpi_five input_five )                

        if result[0] == 0:             #check if it times out.

          return float(result[2])

        else:

          print  self.identify_vxi_11_error(result[0])      #print the error information.
          return False, result[0]   # return the error number. 
 
      
      else: 
        print "you should not be here at all. HOW DiD YOU PASS THE CHECK TEST !!"       # here , we add new devices with new commands. The user should not get here at all (hopefully)
        


    else:
      return self.check()
  
