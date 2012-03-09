# Name: window and voltage scaler
# Made by: Nadiah Zainol Abidin
# Date: 03/07/12  (MM/DD/YY)
# Goal: to set the horizontal scale and vertical scale of the window dsiplay
# Devices:  1) dso6032a
# Modifiers:  None 
# did not include autoScale yet
# 


import libgpib

class Scale:		
  """
  This class sets the vertical and horizontal scale of the window display 
  """
print "please enter information in this format\n"
print "(IP address, GPIB address, Channel {1|2|3|4}, vertical scale: units perdivision, vertical units {V, mV}, horizontalScale: <scale_value> ::= 500 ps through 50 s)"
  def __init__(self, IPad, Gpibad, namdev, Channel, verticalScale, verticalUnit, horizontalScale

    self.ip_id = IPad
    self.gpib_id = Gpibad
    self.name_of_device = namdev
    self.rightDevice = ['dso6032a']
    self.Channel = Channel
    self.horScale = horizontalScale
    self.verScale = verticalScale
    self.verUnit = verticalUnit
    self.ChannelType = ['1', '2', '3', '4']
    self.Units = ['mV', 'V']
  

  def check(self):
    """
    
    """
    if self.name_of_device not in self.rightDevice:
      return False
    if self.name_of_device is 'dso6032a':
      if self.Channel not in self.ChannelType:
        return False
    if self.verUnit not in self.Units:
        return False
    ###############how do u say if 500ps>(float)self.verScale>50s, then return false?
    return True
  


  def get(self):		
    """
    The main SCPI command. 
    """
    m = eval('libgpib.'+ self.name_of_device+'(host="'+self.ip_id+'", device="'+self.gpib_id+'")')   
    z , c , x = m.transaction('CHAN'+self.Channel+':SCAL '+self.verScale+'['+self.verUnit+']')
    m.disconnect() 
    z , c , y = m.transaction('TIM:SCAL '+self.horScale)
    m.disconnect()
    z , c , hor = m.transaction('TIM:SCAL?')
    m.disconnect()
    z, c, ver = m.transcation('CHAN'+self.Channel+':SCALe?')
    return ('horizontal scale: '+ hor+'\nvertical scale: '+ver+' is the current setting for your window')

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



