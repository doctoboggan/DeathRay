# Name: Sets the oscilloscope mode.
# Made by: Nadiah Zainol Abidin
# Date: 02/17/12  (MM/DD/YY)
# Goal: set the mode of the oscilloscope <type> ::= {NORMal | AVERage | HRESolution | PEAK}
# Devices:  1) dso
# Modifiers:  None 
# SCPI command: ACQuire:TYPE <type>
# Result: One string. it notifies the osc is set to the mode requested  

import libgpib

class AcqType:		
  """
  This class sets the DC current for the selected channel of the given device. 
  """

  def __init__(self, IPad, Gpibad, namdev, setmode): 

    self.ip_id = IPad
    self.gpib_id = Gpibad
    self.name_of_device = namdev
    self.rightDevice = ['dso']
    self.modetype_for_dso = ['normal', 'NORMAL', 'Normal', 'average', 'AVERAGE', 'Average', 'HRESolution', 'hresolution', 'HRESOLUTION', 'PEAK', 'peak', 'Peak']
    self.setmode = setmode

  def check(self):
    """
    To check if the given device will work with CCurrentDC function (to avoid module from crashing).
    Also, it checks if the specified channel of certain device matchs the data base of the names of channels in that device        
    """
    if self.name_of_device not in self.rightDevice:
      return False
    if self.name_of_device is 'dso':
      if self.setmode not in self.modetype_for_dso:
        return False

    return True
  


  def get(self):		
    """
    The main SCPI command. It sets the oscilloscope in the mode requested
    """
    m = eval('libgpib.'+ self.name_of_device+'(host="'+self.ip_id+'", device="'+self.gpib_id+'")')   
    z , c , x = m.transaction('ACQ:TYPE '+self.setmode)
    m.disconnect() 
    return self.setmode+' has been selected.'

#so far, sponsor requested to have the osc in normal mode. other modes have not been accounted for. refer details below
# ---------------Information: ------------
# page 208
# :ACQuire:TYPE <type>
# <type> ::= {NORMal | AVERage | HRESolution | PEAK}
#
# ---> The :ACQuire:TYPE NORMal command sets the oscilloscope in the
# normal mode.
# ---> The :ACQuire:TYPE AVERage command sets the oscilloscope in the
# averaging mode. You can set the count by sending the :ACQuire:COUNt
# command followed by the number of averages. In this mode, the value
# for averages is an integer from 1 to 65536. The COUNt value determines
# the number of averages that must be acquired.
# Setting the :ACQuire:TYPE to AVERage automatically sets
# :ACQuire:MODE to ETIMe (equivalent time sampling).
# The AVERage type is not available when in segmented memory mode
# (:ACQuire:MODE SEGMented).
# ---> The :ACQuire:TYPE HRESolution command sets the oscilloscope in the
# high- resolution mode (also known as smoothing). This mode is used to
# reduce noise at slower sweep speeds where the digitizer samples faster
# than needed to fill memory for the displayed time range.
# -------------------------------------
