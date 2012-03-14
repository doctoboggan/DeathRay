# Name: getImpedanceChannel
# Made by: Nadiah Zainol Abidin
# Date: 03/08/12  (MM/DD/YY)
# Goal: get the impedance Setting for specified analog channel
# Devices:  1) "dso6032a" 
# Modifiers:  None 

import data_acquisition

class getImpedanceChannel(data_acquisition.vxi_11.vxi_11_connection,data_acquisition.gpib_utilities.gpib_device):		
  """
This class selects the input impedance setting for the specified analog channel. The legal values for this command are
ONEMeg (1 M) and FIFTy (50),please use rightdevice function.
We are feeding the class with vxi_11.vxi_11_connection and gpib_utilities.gpib_device from data_acquisition library
The :CHANnel<n>:IMPedance command selects the input impedance setting
for the specified analog channel. The legal values for this command are
ONEMeg (1 M) and FIFTy (50).

Query Syntax :CHANnel<n>:IMPedance?
The :CHANnel<n>:IMPedance? query returns the current input impedance
setting for the specified channel.

Return Format <impedance value><NL>
<impedance value> ::= {ONEM | FIFT}

NOTE The analog channel input impedance of the 100 MHz bandwidth oscilloscope models is
fixed at ONEMeg (1 M).
  """

  def __init__(self, IPad = '127.0.0.1', Gpibad = "inst0", namdev = "Network Device", channel = 1, timeout = 500):
    self.ip_id = IPad
    self.gpib_id = Gpibad
    self.name_of_device = namdev
    self.rightDevice = ['dso6032a']
    self.channel = channel
    self.typeChannel = [1, 2, 3, 4]
    rise_on_error = 0
    data_acquisition.vxi_11.vxi_11_connection.__init__(self,host=IPad,device=Gpibad,raise_on_err=rise_on_error,timeout=timeout,device_name=namdev)  
    #here we are feeding the data_acquisition library



  def check(self):
    """
    To check if the given device will work with ImpedanceChannel (avoiding issues).
    Also, it makes sure that the input channels do exist (to aviod conflicts). 
    ALso, we take care of time-out minimum duration (to aviod run out of time).
    Also, we remind the user that the input channel is required for the given device. 
    """
    
    if self.name_of_device in self.rightDevice:

      if type(self.timeout) is int or float:

        if self.timeout >= 500:      # hardcoded. Also, the number was choosen after several testing.

          if type(self.channel) is int:

            if self.name_of_device == 'dso6032a':

              if self.channel in self.typeChannel: # for channel checking. (we can not accept unknown channel any more).
                return True
              else:
                print "chosen channel does not exist !!"     # For debug purpose
                                                              ###Nadiah: if the user enters blank string channel, does that default to the previous channel/or channel 1?
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
    The main SCPI command.  
''''
page 235
Command Syntax :CHANnel<n>:IMPedance <impedance>
<impedance> ::= {ONEMeg | FIFTy}

<n> ::= {1 | 2 | 3 | 4} for the four channel oscilloscope models
<n> ::= {1 | 2} for the two channel oscilloscope models
The :CHANnel<n>:IMPedance command selects the input impedance setting
for the specified analog channel. The legal values for this command are
ONEMeg (1 M) and FIFTy (50).
''''''  
    """

    if self.check() is True:

      print "PASS check test"         # For debug purpose

      if self.name_of_device == 'dso6032a':

        # this line's purpose is if we want to add another device. 

          
          impedance_channel = self.transaction('CHAN'+str(self.channel)+':IMP?')   

          print "the impedance at channel "+str(self.channel)+" is "+str(impedance_channel[2])    # For debug reasons. returns 

          if impedance_channel[0] == 0:             #check if it times out.

            print "It works !!"               # For debug reasons. 
            return impedance_channel[2].strip()    # I have to considre this test here because I need to know the result. 

          else:
            print self.identify_vxi_11_error(impedance_channel[0])      #print the error information.
            return False, impedance_channel[0]  # It is going to return the error number. 

      
      else: 
        print "you should not be here at all. HOW DiD YOU PASS THE CHECK TEST !!"       
        # here , we add new devices with new commands (using "elif" command). The user should not get here at all (hopefully).
        return False, 'w'


    else:
      return self.check()



 



 
    


'''
page 235
Command Syntax :CHANnel<n>:IMPedance <impedance>
<impedance> ::= {ONEMeg | FIFTy}
<n> ::= {1 | 2 | 3 | 4} for the four channel oscilloscope models
<n> ::= {1 | 2} for the two channel oscilloscope models
The :CHANnel<n>:IMPedance command selects the input impedance setting
for the specified analog channel. The legal values for this command are
ONEMeg (1 M) and FIFTy (50).
'''

