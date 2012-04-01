# Name: 
# Made by:   Using add module function
# Date: 2012-03-29 20:57:38.199846  (MM/DD/YY)
# Goal: 
# Devcies:  1) '' 2) '' 3) '' 4) '' 5) ''    #if they are more than five, creat with five. Than use edit module to add more devices. mention that in GUI.Also, do not forget '""'
# Modifiers:  None (for now) 
# Dependancy: 1) QT GUI 
# SCPI command: 1) '' : ----> scpi_goal ===>  ''_scpi
#               2) '' : ----> scpi_goal ===> ''_scpi
#               3) '': ----> scpi_goal ===> ''_scpi
#               4) '': ----> scpi_goal ===> 
#               5) '': ----> scpi_goal ===> ''_scpi
# Result: 

import data_acquisition

class setdafult(data_acquisition.vxi_11.vxi_11_connection,data_acquisition.gpib_utilities.gpib_device,data_acquisition.vxi_11.VXI_11_Error):

  '''
  
  '''
  def __init__(self, IPad = '127.0.0.1', Gpibad ="inst0" , namdev = "Network Device", timeout=2000): 

    '''
    
    '''

    self.ip_id = IPad
    self.gpib_id = Gpibad
    self.name_of_device = namdev.lower()    #lower case the input 
    self.rightDevice = [ '' , '' , '' , '', '' ]
    rise_on_error = 0
    data_acquisition.vxi_11.vxi_11_connection.__init__(self,host=IPad,device=Gpibad,raise_on_err=rise_on_error,timeout=timeout,device_name=namdev)  #here we are feeding the data_acquisition library

  def check(self):
    """
    
    """
    if self.name_of_device in self.rightDevice:

      if type(self.timeout) is float or type(self.timeout) is int:

        if self.timeout >= 300:      # hardcoded. Also, the number was choosen after several testing.

          if self.name_of_device == '' :

            # start configure '' .     [START]

            return True

            # End of characteristics of '' . [END]

          elif self.name_of_device ==  '' :

            # start configure '' .     [START]

            return True

            # End of characteristics of '' . [END]

          elif self.name_of_device ==  '' :

            # start configure '' .     [START]

            return True

            # End of characteristics of '' . [END]

          elif self.name_of_device ==  '' :

            # start configure '' .     [START]

            return True

            # End of characteristics of '' . [END]

          elif self.name_of_device ==  '' :

            # start configure '' .     [START]

            return True

            # End of characteristics of '' . [END]


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
    
    """  
    if self.check() is True:

      print "PASS check test"         # For debug purpose

      if self.name_of_device == '' :

        result = self.write( '' input_one )                

        if result[0] == 0:             #check if it times out.

          return float(result[2])

        else:

          print  self.identify_vxi_11_error(result[0])      #print the error information.
          return False, result[0]   # return the error number. 


 
      elif self.name_of_device == '' :

        result = self.write( '' input_two )                

        if result[0] == 0:             #check if it times out.

          return float(result[2])

        else:

          print  self.identify_vxi_11_error(result[0])      #print the error information.
          return False, result[0]   # return the error number. 


      elif self.name_of_device == '' :

        result = self.write( main_scpi_three input_three )                

        if result[0] == 0:             #check if it times out.

          return float(result[2])

        else:

          print  self.identify_vxi_11_error(result[0])      #print the error information.
          return False, result[0]   # return the error number. 


      if self.name_of_device == '' :

        result = self.write( '' input_four )                

        if result[0] == 0:             #check if it times out.

          print "It works !!"
           return True

        else:

          print  self.identify_vxi_11_error(result[0])      #print the error information.
          return False, result[0]   # return the error number. 


      if self.name_of_device == '' :

        result = self.write( '' input_five )                

        if result[0] == 0:             #check if it times out.

          print "It works !!"
           return True

        else:

          print  self.identify_vxi_11_error(result[0])      #print the error information.
          return False, result[0]   # return the error number. 
 
      
      else: 
        print "you should not be here at all. HOW DiD YOU PASS THE CHECK TEST !!"       # here , we add new devices with new commands. The user should not get here at all (hopefully)
        


    else:
      return self.check()
  
