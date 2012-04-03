# Name: 
# Made by:  by Using add module tool.
# Date: 2012-04-03 04:50:17.046331  (MM/DD/YY)
# Goal: 
# Devcies:  1) '' 2) '' 3) '' 4) '' 5) ''    #if they are more than five, creat with five. Than use edit module to add more devices. mention that in GUI.Also, do not forget '""'
# Modifiers:  None (for now) 
# Dependancy: 1) QT GUI 
# SCPI command: 1) '' : ----> scpi_goal ===>  
#               2) '' : ----> scpi_goal ===> 
#               3) '': ----> scpi_goal ===> 
#               4) '': ----> scpi_goal ===> 
#               5) '': ----> scpi_goal ===> 
# Result: module_result

import data_acquisition

class setdafult(data_acquisition.vxi_11.vxi_11_connection,data_acquisition.gpib_utilities.gpib_device,data_acquisition.vxi_11.VXI_11_Error):

  '''
  class_info
  '''
  def __init__(self, IPad = '127.0.0.1', Gpibad ="inst0" , namdev = "Network Device",   = "",    timeout=2000): 

    '''
    init_info
    '''

    self.ip_id = IPad
    self.gpib_id = Gpibad
    self.name_of_device = namdev.lower()    #lower case the input 
    self.rightDevice = [ '' , '' , '' , '', '' ]
    
    
    
    
    
    rise_on_error = 0
    data_acquisition.vxi_11.vxi_11_connection.__init__(self,host=IPad,device=Gpibad,raise_on_err=rise_on_error,timeout=timeout,device_name=namdev)  #here we are feeding the data_acquisition library

  def check(self):
    """
    check_info
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
    To check if the given device will work with setvoltageDC function (to avoid module from crashing).
    We take care of time-out minimum duration (to aviod run out of time).
    Note: Some devices have its own characteristics. (deeloper must enter them manually)
    """  
    if self.check() is True:

      print "PASS check test"         # For debug purpose

      if self.name_of_device == '' :

        result = self.write( _input )                

        if result[0] == 0:             #check if it times out.

          return float(result[2])

        else:

          print  self.identify_vxi_11_error(result[0])      #print the error information.
          return False, result[0]   # return the error number. 


 
      elif self.name_of_device == '' :

        result = self.write( '' )                

        if result[0] == 0:             #check if it times out.

          return float(result[2])

        else:

          print  self.identify_vxi_11_error(result[0])      #print the error information.
          return False, result[0]   # return the error number. 


      elif self.name_of_device == '' :

        result = self.write( _input )                

        if result[0] == 0:             #check if it times out.

          return float(result[2])

        else:

          print  self.identify_vxi_11_error(result[0])      #print the error information.
          return False, result[0]   # return the error number. 


      if self.name_of_device == '' :

        result = self.write( '' )                

        if result[0] == 0:             #check if it times out.

          print "It works !!"
           return True

        else:

          print  self.identify_vxi_11_error(result[0])      #print the error information.
          return False, result[0]   # return the error number. 


      if self.name_of_device == '' :

        result = self.write( '' )                

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
  
