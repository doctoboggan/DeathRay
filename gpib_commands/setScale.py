# Name: window and voltage scaler
# Made by: Nadiah Zainol Abidin
# Date: 03/07/12  (MM/DD/YY)
# Goal: to set the horizontal scale and vertical scale of the window dsiplay
# Devices:  1) dso6032a
# Modifiers:  None 
# did not include autoScale yet
# 


import data_acquisition

class setScale (data_acquisition.vxi_11.vxi_11_connection,data_acquisition.gpib_utilities.gpib_device, data_acquisition.vxi_11.VXI_11_Error):		
  """
  This class sets the vertical and horizontal scale of the window display 
  """

  def __init__(self, IPad = '127.0.0.1', Gpibad = "inst0", namdev = "Network Device", channel = '1', verticalScale = '10' , verticalUnit = 'mV' , horizontalScale = '1', timeout = 2000):
    '''
    please enter information in this format
    (IP address, GPIB address, Channel {1|2|3|4}, vertical scale: units perdivision, vertical units {V, mV}, horizontalScale: <scale_value> ::= 500 ps through 50 s)
    EX of requirement (IPad = '127.0.0.1', Gpibad = "inst0", namdev = "Network Device", channel = '1', verticalScale = 10 , verticalUnit = 'mV' , horizontalScale = 1, timeout = 500)
    '''

    self.ip_id = IPad
    self.gpib_id = Gpibad
    self.name_of_device = namdev.lower()
    self.rightDevice = ['dso6032a']
    self.Channel = channel
    self.horScale = horizontalScale
    self.verScale = verticalScale
    self.verUnit = verticalUnit 
    self.ChannelType = ['1', '2']
    self.Units = ['mV', 'V']
    rise_on_error = 0
    data_acquisition.vxi_11.vxi_11_connection.__init__(self,host=IPad,device=Gpibad,raise_on_err=rise_on_error,timeout=timeout,device_name=namdev)  
    #here we are feeding the data_acquisition library
  


  
  def check(self):
    """
    To check if the given device will work with setScale.py (avoiding issues).
    Also, it makes sure that the input channels do exist (to aviod conflicts). 
    ALso, we take care of time-out minimum duration (to aviod run out of time).
    Also, we remind the user that the input channel is required for the given device. 
    """
    
    if self.name_of_device in self.rightDevice:

      if type(self.timeout) is int or float:

        if self.timeout >= 500:      # hardcoded. Also, the number was choosen after several testing.

          #   starting special case for "dso6032a"devcie:

          if self.name_of_device == 'dso6032a':   

            if type(self.Channel) is str: #[1, 2, 3, 4] #####vertical starts here

              try: 

                dump = int(self.Channel)

                if self.Channel in self.ChannelType: # for channel checking. (we can not accept unknown channel any more).

                  if type(self.verUnit) is str:    # make the input for 'vertical Unit' is string.
                  
                    if self.verUnit in self.Units: # [mV or V]. Also,  

                      if type(self.verScale) is str: # to make sure the the type of input is string. Also, vertical Scale is units per division in vertical scale in NR3 format(float) #####vertical ends here

                        try: 

                          self.verScale = int(self.verScale)
            
                          if type(self.horScale) is str: 

                            try:

                              self.horScale = int(self.horScale)

                              if self.horScale <= 50 and self.horScale >= (50*10^-9): #50 ps to 50s
                                self.horScale = str(self.horScale)    # I need to convert it back to work with SCPI command.
                                return True

                              else:
                                return False, 'z'  #horizontal scale entered is out of bounds

                            except ValueError:
                              print " The horizontal Scale input is not int (can not be converted to int)!"
                              return False, 'n'

                          
                          else:
                            print "the horizontal Scale input type is not string type even the input is an int."
                            return False, 's' #horizontal scale is not a float nor intege

                        except ValueError:
                          print "vertical Scale input is not int (can not be converted to int)!"
                          return False, 'n'
            
                      else:
                        print "the input vertical Scale type has to be string even if it is an int."
                        return False, 's' #vertical scale is not a float nor integer

                    else:
                      print " the vertical Unit input does not match the data base"
                      return False, 'd' #vertical suffix is not valid

                  else:
                    print "the input vertical Unit is not string!"
                    return False, 's'


                else:
                  print "chosen channel does not exist !!"     # For debug purpose                                             
                  return False, 'c'

              except ValueError:
                  
                print "the input is not real int (can not be converted to a int) !!"
                return False, 'n'

            else:
              print "the input channel needs to be an string tyoe (even if input is number (int)) !!"  # For debug purpose
              return False, 's'


                  # End of "dso62032" case configuration.


          else:
            print "the device is registre. but, there is no special configuration for it in the check method. Any way, you shell pass!" #if we have another device, add elif argument here
            return True 

        else:
          print "The time-out is too short"   # For debug purpose
          return False, 'o'

      else: 

        print "timeout input is not acceptable has to be int."
        return False, 'q'

    else:
      print "the device is not in data base"    # For debug purpose
      return False, 'x'


  def do(self):		
    """
    Command Syntax :CHANnel<n>:SCALe <scale>[<suffix>]
    <scale> ::= vertical units per division in NR3 format
    <suffix> ::= {V | mV}
    <n> ::= {1 | 2 | 3 | 4} for the four channel oscilloscope models
    <n> ::= {1 | 2} for the two channel oscilloscope models
    
    NR3 format is Floating point numbers 4.5E-1, 8.25E+1

    TIMebase:SCALe <scale_value>
    <scale_value> ::= 500 ps through 50 s in NR3 format
    The :TIMebase:SCALe command sets the horizontal scale or units per
    division for the main window.
    """

    re = self.check()

    if re is True:

      print "PASS check test"         # For debug purpose

      if self.name_of_device == 'dso6032a':

        # this line's purpose is if we want to add another device. 

          
          horizontal = self.write('TIM:SCAL '+self.horScale)   

          if horizontal[0] == 0:             #check if it times out.

            print "It works !!"               # For debug reasons. 
            return [True]                # I have to considre this test here because I need to know the result. 

          
            
            vertical = self.write('CHAN'+self.Channel+':SCAL '+self.verScale+'['+self.verUnit+']')    # to Nadiah: should we put the SCPI command here?
            
            if vertical[0] == 0:             #check if it times out.

              print "It works !!"               # For debug reasons. 
              return [True]                # I have to considre this test here because I need to know the result. 

            else:
              print self.identify_vxi_11_error(vertical[0])      #print the error information.
              return False, vertical[0]  # It is going to return the error number. 

          else:
            print self.identify_vxi_11_error(horizontal[0])      #print the error information.
            return False, horizontal[0]  # It is going to return the error number. 

      
      else: 
        print "you should not be here at all. HOW DiD YOU PASS THE CHECK TEST !!"       
        # here , we add new devices with new commands (using "elif" command). The user should not get here at all (hopefully).
        return False, 'w'


    else:
      return re


'''
NR3 Floating point numbers 4.5E-1, 8.25E+1


Command Syntax :CHANnel<n>:SCALe <scale>[<suffix>]
<scale> ::= vertical units per division in NR3 format
<suffix> ::= {V | mV}
<n> ::= {1 | 2 | 3 | 4} for the four channel oscilloscope models

<n> ::= {1 | 2} for the two channel oscilloscope models

TIMebase:SCALe <scale_value>
<scale_value> ::= 500 ps through 50 s in NR3 format
The :TIMebase:SCALe command sets the horizontal scale or units per

division for the main window.

Command Syntax :AUToscale
:AUToscale [<source>[,..,<source>]]
<source> ::= CHANnel<n> for the DSO models

<source> ::= {DIGital0,..,DIGital15 | POD1 | POD2 | CHANnel<n>} for the
MSO models
<n> ::= {1 | 2 | 3 | 4} for the four channel oscilloscope models
<n> ::= {1 | 2} for the two channel oscilloscope models
The <source> parameter may be repeated up to 5 times.
The :AUToscale command evaluates all input signals and sets the correct
conditions to display the signals. This is the same as pressing the
Autoscale key on the front panel.
If one or more sources are specified, those specified sources will be
enabled and all others blanked. The autoscale channels mode (see
":AUToscale:CHANnels" on page 159) is set to DISPlayed channels. Then,
the autoscale is performed.
When the :AUToscale command is sent, the following conditions are
affected and actions are taken:
Thresholds.
Channels with activity around the trigger point are turned on, others
are turned off.
Channels are reordered on screen; analog channel 1 first, followed by

the remaining analog channels, then the digital channels 0- 15.
Delay is set to 0 seconds.
Time/Div.
The :AUToscale command does not affect the following conditions:
Label names.
Trigger conditioning.

The :AUToscale command turns off the following items:
Cursors.
Measurements.
Trace memories.
Zoomed (delayed) time base mode.

For further information on :AUToscale, see the User's Guide.
'''
# to Nadiah: are all inputs ints(not float)?

# Note:   ---> 'o' means time-out is too short.
#         ---> 'e' means empty string
#         ---> 'n' means input voltage is not number.
#         ---> 'c' means wrong channel input. 
#         ---> 'x' wrong name of device. 
#         ---> 'w' wired error (something wrong with code)
#         ---> 'z' out of range 
#         ---> 'q' timeout input is not number.
#         ---> 's' the input type is not string.
#         ---> 'n' the input can not be converted to int or float (depend)
#         ---> 'd' The given inut does not match the hardcode database.



