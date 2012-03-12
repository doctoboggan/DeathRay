# Goal: ImpedanceChannel
# Made by: Nadiah Zainol Abidin
# Date: 03/08/12  (MM/DD/YY)
# Goal: Input impedance Setting for specified analog channel
# Devices:  1) "dso6032a" 
# Modifiers:  None 

import libgpib

class ImpedanceChannel(data_acquisition.vxi_11.vxi_11_connection,data_acquisition.gpib_utilities.gpib_device):		
  """
This class selects the input impedance setting for the specified analog channel. The legal values for this command are
ONEMeg (1 MΩ) and FIFTy (50Ω),please use rightdevice' function.
We are feeding the class with vxi_11.vxi_11_connection and gpib_utilities.gpib_device from data_acquisition library 
  

The :CHANnel<n>:IMPedance command selects the input impedance setting
for the specified analog channel. The legal values for this command are
ONEMeg (1 MΩ) and FIFTy (50Ω).

Query Syntax :CHANnel<n>:IMPedance?
The :CHANnel<n>:IMPedance? query returns the current input impedance
setting for the specified channel.

Return Format <impedance value><NL>
<impedance value> ::= {ONEM | FIFT}

NOTE The analog channel input impedance of the 100 MHz bandwidth oscilloscope models is
fixed at ONEMeg (1 MΩ).
  """

  def __init__(self, IPad, Gpibad, namdev, channel, impedance): 

    self.ip_id = IPad
    self.gpib_id = Gpibad
    self.name_of_device = namdev
    self.rightDevice = ['dso6032a']
    self.channel = channel
    self.impedance = impedance
    self.typeChannel = ['1', '2', '3', '4', ' ']
    self.typeImpedance = ['ONEMeg', '1Meg', '1M', '1MEG', 'ONEMEG', 'ONEM', 'FIFTY', '50OHM', 'FIFT', 'fifty', 'fiftyohm', 'fiftyOhm', '50']
    self.ONEMegImpedance = ['ONEMeg', '1Meg', '1M', '1MEG', 'ONEMEG', 'ONEM', '1000']
    self.FiftyOhmImpedance = ['FIFTY', '50OHM', 'FIFT', 'fifty', 'fiftyohm', 'fiftyOhm', '50']
    rise_on_error = 0
    data_acquisition.vxi_11.vxi_11_connection.__init__(self,host=IPad,device=Gpibad,raise_on_err=rise_on_error,timeout=timeout,device_name=namdev)  #here we are feeding the data_acquisition library

  
  def check(self):
    """
    To check if the given device will work with ImpedanceChannel (avoiding issues).
    Also, it makes sure that the input channels do exist (to aviod conflicts). 
    ALso, we take care of time-out minimum duration (to aviod run out of time).
    Also, we remind the user that the input channel is required for the given device. 
    """
    
    if self.name_of_device in self.rightDevice:

      if self.timeout >= 2500:      # hardcoded. Also, the number was choosen after several testing.

        if self.name_of_device == 'dso6032a':

          if self.channel not in self.typeChannel :      # cor channel checking. We have to do this with each and every channelly device!!
            print "chosen channel does not exist !!"     # For debug purpose
            return False, 'c'

          else:
            if self.channel != '':
              print "The device does not have any channel. So, your input channel will be ignored."     # To remind the user about his/her mistake of entering channel, where the device does not have. 
              return True
         
         else:
            return True
            
          
            if self.impedance not in self.typeImpedance
              print "The impedance selected is not valid. Please enter only ONEM (1Meg Ohms) or FIFT (fifty Ohms)"
              return False, "i"
              
            else: 
              if self.impedance is in self.ONEMegImpedance:
                return self.impedance = 'ONEM' ##anas, please check this line if it is valid or not
    
            else:
              if self.impedance is in self.FiftyOhmImpedance:
                return self.impedance = 'FIFT' ##anas, please check if this is valid or not
      
      else:
        print "The time-out is too short"   # For debug purpose
        return False, 'o'

    else:
      print "the device is not in data base"    # For debug purpose
      return False, 'x'





  def get(self):		
    """
    The main SCPI command. It has ____ steps,
    
    Note: between each transaction, we have to disconnect the connection to aviod time-out errors. Also, to allow other connection to be established. 
    """
    m = eval('libgpib.'+ self.name_of_device+'(host="'+self.ip_id+'", device="'+self.gpib_id+'")')
    z , c , a = m.transaction('CHAN'+self.channel+':IMP'+self.impedance) 
    m.disconnect()
    z , c , impquer = m.transaction('CHAN'+self.channel+':IMP?') 
    m.disconnect()
    
    return ('the input impedance in channel '+self.channel+'is '+impquer)
    


''''
page 235
Command Syntax :CHANnel<n>:IMPedance <impedance>
<impedance> ::= {ONEMeg | FIFTy}
<n> ::= {1 | 2 | 3 | 4} for the four channel oscilloscope models
<n> ::= {1 | 2} for the two channel oscilloscope models
The :CHANnel<n>:IMPedance command selects the input impedance setting
for the specified analog channel. The legal values for this command are
ONEMeg (1 MΩ) and FIFTy (50Ω).

