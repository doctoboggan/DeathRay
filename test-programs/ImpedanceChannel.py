# Goal: ImpedanceChannel
# Made by: Nadiah Zainol Abidin
# Date: 03/08/12  (MM/DD/YY)
# Goal: Input impedance Setting for specified analog channel
# Devices:  1) "dso6032a" 
# Modifiers:  None 


import libgpib

class ImpedanceChannel:		
  """
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
    self.typeChannel = ['1', '2', '3', '4']
    self.impedance = impedance
    self.typeImpedance = ['ONEMeg', '1Meg', '1M', '1MEG', 'ONEMEG', 'ONEM', 'FIFTY', '50OHM', 'FIFT', 'fifty', 'fiftyohm', 'fiftyOhm', '50']
    self.ONEMegImpedance = ['ONEMeg', '1Meg', '1M', '1MEG', 'ONEMEG', 'ONEM']
    self.50OhmImpedance = ['FIFTY', '50OHM', 'FIFT', 'fifty', 'fiftyohm', 'fiftyOhm', '50']

  def check(self):
    """
        
    """
    if self.name_of_device not in self.rightDevice:
      return False
    if self.channel not in self.typeChannel:
      return False
    if self.impedance is not in self.typeImpedance:
      return False
    if self.impedance is in self.ONEMegImpedance:
      return self.impedance = 'ONEM' ##please check this line if it is valid or not
    if self.impedance is in self.50OhmImpedance:
      return self.impedance = 'FIFT'
    return True



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

