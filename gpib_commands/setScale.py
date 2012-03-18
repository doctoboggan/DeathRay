# Name: window and voltage scaler
# Made by: Nadiah Zainol Abidin
# Date: 03/07/12  (MM/DD/YY)
# Goal: to set the horizontal scale and vertical scale of the window dsiplay
# Devices:  1) dso6032a
# Modifiers:  None 
# did not include autoScale yet
# 


import data_acquisition

class Scale (data_acquisition.vxi_11.vxi_11_connection,data_acquisition.gpib_utilities.gpib_device, data_acquisition.vxi_11.VXI_11_Error):		
  """
  This class sets the vertical and horizontal scale of the window display 
  """
print "please enter information in this format\n"
print "(IP address, GPIB address, Channel {1|2|3|4}, vertical scale: units perdivision, vertical units {V, mV}, horizontalScale: <scale_value> ::= 500 ps through 50 s)"
  def __init__(self, IPad = '127.0.0.1', Gpibad = "inst0", namdev = "Network Device", channel = '1', verticalScale = 10 , verticalUnit = 'mV' , horizontalScale = 1, timeout = 500)
'''
def __init__(self, IPad = '127.0.0.1', Gpibad = "inst0", namdev = "Network Device", channel = '1', verticalScale = 10 , verticalUnit = 'mV' , horizontalScale = 1, timeout = 500)
'''

    self.ip_id = IPad
    self.gpib_id = Gpibad
    self.name_of_device = namdev
    self.rightDevice = ['dso6032a']
    self.Channel = Channel
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
    To check if the given device will work with Scale.py (avoiding issues).
    Also, it makes sure that the input channels do exist (to aviod conflicts). 
    ALso, we take care of time-out minimum duration (to aviod run out of time).
    Also, we remind the user that the input channel is required for the given device. 
    """
    
    if self.name_of_device in self.rightDevice:

      if type(self.timeout) is int or float:

        if self.timeout >= 500:      # hardcoded. Also, the number was choosen after several testing.


          if self.name_of_device == 'dso6032a'

            if :type(self.Channel) is str: #[1, 2, 3, 4] #####vertical starts here

              if self.Channel in self.ChannelType: # for channel checking. (we can not accept unknown channel any more).
                
                if self.verUnits in self.Units: # [mV or V]

                  if self.VerScale is float or int: #units per division in vertical scale in NR3 format(float) #####vertical ends here
        
                    if self.horScale is float or int: 

                      if self.horScale is <= 50 and self.horScale >= (50*10^-9): #50 ps to 50s

                      else:
                        return False, 'horizontal#'  #horizontal scale entered is out of bounds
                    
                    else:
                      return False, 'horFloat' #horizontal scale is not a float nor integer
        
                  else:
                    return False, 'verFloat' #vertical scale is not a float nor integer

                else:

                  return False, 'verSuf' #vertical suffix is not valid

              else:
                print "chosen channel does not exist !!"     # For debug purpose                                             
                return False, 'c'

            else:
              return False, "you dont have the right device" #if we have another device, add elif argument here

          else:
            print "the input channel needs to be an integer !!"  # For debug purpose
            return False, 'n'

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
  Command Syntax :CHANnel<n>:SCALe <scale>[<suffix>]
<scale> ::= vertical units per division in NR3 format
<suffix> ::= {V | mV}
<n> ::= {1 | 2 | 3 | 4} for the four channel oscilloscope models
<n> ::= {1 | 2} for the two channel oscilloscope models

TIMebase:SCALe <scale_value>
<scale_value> ::= 500 ps through 50 s in NR3 format
The :TIMebase:SCALe command sets the horizontal scale or units per
division for the main window.
    """

    if self.check() is True:

      print "PASS check test"         # For debug purpose

      if self.name_of_device == 'dso6032a':

        # this line's purpose is if we want to add another device. 

          
          horizontal = self.transaction('TIM:SCAL '+self.horScale)   

          print "the horizontal scale"+horizontal[2]    # For debug reasons. 

          if horizontal[0] == 0:             #check if it times out.

            print "It works !!"               # For debug reasons. 
            return True                # I have to considre this test here because I need to know the result. 

          
            
            vertical = self.transaction('CHAN'+self.Channel+':SCAL '+self.verScale+'['+self.verUnit+']')
            
            print "the vertical scale"+vertical[2]    # For debug reasons. 

            if vertical[0] == 0:             #check if it times out.

              print "It works !!"               # For debug reasons. 
              return True                # I have to considre this test here because I need to know the result. 

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
      return self.check()


''''
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
• Thresholds.
• Channels with activity around the trigger point are turned on, others
are turned off.
• Channels are reordered on screen; analog channel 1 first, followed by

the remaining analog channels, then the digital channels 0- 15.
• Delay is set to 0 seconds.
• Time/Div.
The :AUToscale command does not affect the following conditions:
• Label names.
• Trigger conditioning.

The :AUToscale command turns off the following items:
• Cursors.
• Measurements.
• Trace memories.
• Zoomed (delayed) time base mode.

For further information on :AUToscale, see the User's Guide.




