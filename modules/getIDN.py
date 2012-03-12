# Name: IDN reader.
# Made by: Anas Alfuntukh
# Date: 3/4/12
# Goal: TO get the name of device by given a gpib address.
# Device: all gpib devices. 
# Modifiers:  None (for now) 
# Dependancy: 1) getdevice.py   2) QT GUI
# Result: a name of device.



import data_acquisition  # This library is going to be used later. 


class getIDN(data_acquisition.vxi_11.vxi_11_connection):

  '''
  --> This class is for getting IDN inofrmation from a device. 
  --> This is a module. 
  --> This class requires "os" library.
  '''

  def __init__(self, IPad = '127.0.0.1', Gpibad ="inst0"):

    '''
    Requirement: (ip address, Gpib address)
    Ex: getIDN.getIDN('129.59.93.179','gpib0,10')
    _________________
    --> The rightDevice list has to be there. It responsibles for flexibility of this file. Because this module works with all devices (hopfully), The list is going to be a star.
    --> IPad is the number of ip-address with quotation mark. 
    --> Gpibad is the number of Gpib address with quotation mark.
    --> namdev is the name of the device.
    --> Time-out value is 500ms.It can not be less than that. IT WILL CRASH IN VACUUM !!
    --> load data-acquisition library.
    '''

    self.ip_id = IPad
    self.gpib_id = Gpibad
    rise_on_error = 0   # do not worry about it. It is required by data-acquisition library.
    timeout = 500
    namdev = 'nothing'  # as dafult. it will make any different.
    data_acquisition.vxi_11.vxi_11_connection.__init__(self,host=IPad,device=Gpibad,raise_on_err=rise_on_error,timeout=timeout,device_name=namdev)
    self.rightDevice = ['*']

  def do(self):

    '''
    --> Here is the SCPI command. 
    '''

    z, x, a = self.transaction('*IDN?')
    return a

# It works, I need to comment it. 
# In the manual: rightDevice list should contain: 
# 1) emppty string ==>[""] <== means that the file does not work with any device.
# 2) a star ==> ["*"] <== means that the file work with all devices. 
# 3) given names ==> ["hpxxxx", "kexxxx"] <== means that the file works with given devices (ex: "hpxxxx" and "kexxxx") . 
