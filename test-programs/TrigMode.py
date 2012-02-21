# Name: Sets the trigger mode for given channel of given devices.
# Made by: Nadiah Zainol Abidin
# Date: 02/17/12  (MM/DD/YY)
# Goal: sets the trigger mode of the oscilloscope, 
# Devices:  1) dso6032a
# Modifiers:  None 
# SCPI command: 1) dso6032a: ---> Command Syntax ==> :TRIGger:MODE <mode>
# -------------- <mode>: -----------------
# <mode> ::= {EDGE | GLITch | PATTern | CAN | DURation | I2S |IIC
# | EBURst | LIN | M1553| SEQuence | SPI | TV | UART| USB | FLEXray}
# ----------------------------------------
# Result: One string. it notifies the osc is set to the trigger mode requested  

import libgpib

class TrigMode:		
  """
  This class sets the trigger mode of the given device. 
  """

  def __init__(self, IPad, Gpibad, namdev, trigmode): 

    self.ip_id = IPad
    self.gpib_id = Gpibad
    self.name_of_device = namdev
    self.rightDevice = ['dso6032a']
    self.trigMode_for_dso = ['EDGE', 'GLITch', 'PATTern', 'CAN', 'DURation', 'I2S', 'IIC', 'EBURst', 'LIN', 'M1553', 'SEQuence', 'SPI', 'TV', 'UART', 'USB', 'FLEXray', 'GLITCH', 'PATTERN', 'DRATION', 'EBURST', 'SEQUENCE', 'FLEXRAY']      # incluse all "upper case" probabilities. So that, we can check them as "upper case". By the way, this is one line. I am not sure what will happen with the numbers?! (Anas)
    trigmodelower = upper(trigmode)
    self.trigMode = trigmodelower

  def check(self):
    """
    To check if the given device will work with CCurrentDC function (to avoid module from crashing).
    Also, it checks if the specified channel of certain device matchs the data base of the names of channels in that device        
    """
    if self.name_of_device not in self.rightDevice:
      return False
    if self.name_of_device is 'dso6032a':
      if self.trigMode not in self.trigMode_for_dso:
        return False

    return True
  


  def get(self):		
    """
    The main SCPI command. It sets the oscilloscope in the trigger mode requested
    """
    m = eval('libgpib.'+ self.name_of_device+'(host="'+self.ip_id+'", device="'+self.gpib_id+'")')   
    z , c , x = m.transaction('TRIG:MODE '+self.trigMode)
    m.disconnect() 
    return self.trigMode+' has been selected.'

# ------------ Information : -----------
# page 485
# :TRIGger:MODE
# (see page 798)
# Command Syntax :TRIGger:MODE <mode>
# <mode> ::= {EDGE | GLITch | PATTern | CAN | DURation | I2S |IIC
# | EBURst | LIN | M1553| SEQuence | SPI | TV | UART
# | USB | FLEXray}
# The :TRIGger:MODE command selects the trigger mode (trigger type).
# Query Syntax :TRIGger:MODE?
# The :TRIGger:MODE? query returns the current trigger mode. If the
# :TIMebase:MODE is ROLL or XY, the query returns "NONE".
# --------------------------------------



