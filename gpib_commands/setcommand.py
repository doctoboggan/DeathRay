# Name: Sending command via gpib
# Made by: Anas Alfuntukh
# Date: 26/03/12  (DD/MM/YY)
# Goal: This moduel suppose to be able to send SCPI command via gpib.
# Devcies:  any device
# Modifiers:  None (for now) 
# Dependancy: 1) QT GUI 
# SCPI command: Any
# Result: Whatever the result.

import data_acquisition

class setcommand(data_acquisition.vxi_11.vxi_11_connection,data_acquisition.gpib_utilities.gpib_device,data_acquisition.vxi_11.VXI_11_Error):		
  """
  Sending SCPI command
  """

  def __init__(self, IPad = '127.0.0.1', Gpibad ="inst0" , namdev = "Network Device", command ='*IDN?', timeout=2000): 
    """
    Requiremend: ( IPad, Gpibad, namdev, command ='*IDN?', timeout=2000)
    Ex of requirement: '129.59.93.179', 'gpib0,22', 'e3631a', command = '*IDN?', timeout=2000)
    """
    self.ip_id = IPad
    self.gpib_id = Gpibad
    self.name_of_device = namdev.lower()    #lower case the input 
    self.cmdd = command.lower()          #lower case the input
    self.rightDevice = ['34401a', 'e3631a','dso6032a']
    rise_on_error = 0
    data_acquisition.vxi_11.vxi_11_connection.__init__(self,host=IPad,device=Gpibad,raise_on_err=rise_on_error,timeout=timeout,device_name=namdev)  #here we are feeding the data_acquisition library

  def do(self):

    '''
    --> Here is the SCPI command. 
    '''
    result = self.write(self.cmdd)

    if result[0] == 0:             
      return True
    else:
      return False, result[0]
