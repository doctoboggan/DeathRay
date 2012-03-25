# Name: IDN reader.
# Made by: Anas Alfuntukh
# Date: 3/4/12
# Goal: TO get the name of device by given a gpib address.
# Device: all gpib devices. 
# Modifiers:  None (for now) 
# Dependancy: 1) getdevice.py   2) QT GUI
# Result: a name of device.



import data_acquisition  # This library is going to be used later. 

from pdb import set_trace as bp #DEBUGING


class getIDN(data_acquisition.vxi_11.vxi_11_connection):

  '''
  --> This class is for getting IDN inofrmation from a device. 
  --> This is a module. 
  --> This class requires "os" library.
  '''

  def __init__(self, IPad = '127.0.0.1', Gpibad ="inst0", namedev = 'filler', timeout = 2000):

    '''
    Requirement: (ip address, Gpib address)
    Ex: getIDN.getIDN('129.59.93.179','gpib0,10')
    _________________
    --> The rightDevice list has to be there. It responsibles for flexibility of this file. Because this module works with all devices (hopfully), The list is going to be a star.
    --> IPad is the number of ip-address with quotation mark. 
    --> Gpibad is the number of Gpib address with quotation mark.
    --> namdev is the name of the device.
    --> Time-out value is 500ms.It can not be less than that. IT WILL CRASH IN VACUUM !! IF THE DEVICE DOES NOT EXIST.
    --> load data-acquisition library.
    '''

    self.ip_id = IPad
    self.gpib_id = Gpibad
    rise_on_error = 0   # do not worry about it. It is required by data-acquisition library.
    namdev = 'nothing'  # as dafult. it will make any different.
    data_acquisition.vxi_11.vxi_11_connection.__init__(self,host=IPad,device=Gpibad,raise_on_err=rise_on_error,timeout=timeout,device_name=namdev)
    self.rightDevice = ['dso6032a', 'e3631a', '34401a']

  def do(self):

    '''
    --> Here is the SCPI command. 
    '''

    try:    # to take care of the error.
      x, y, a = self.transaction('*IDN?')
      print "a is " + a     #debugging 
    except:   # we are going to use less than 500ms for timeout (the dafult is going to be 100ms). So, to aviod error, we have to have "except"
      a = None    # just return "None" to work well woth "getdevice" filter. 
    
    return a    #return name of the device.

# It works, I need to comment it. 
# In the manual: rightDevice list should contain: 
# 1) emppty string ==>[""] <== means that the file does not work with any device.
# 2) a star ==> ["*"] <== means that the file work with all devices. 
# 3) given names ==> ["hpxxxx", "kexxxx"] <== means that the file works with given devices (ex: "hpxxxx" and "kexxxx") . 
# There is no check function Here, I have write a check method in case of if the given gpib address does not exist (aviod run out in vacuum) <-- only happen in very small time-out (less than 500ms).
# In other words, it will run out in vacuum if the timeout too short even if the device exist (less than 50ms).
# If timeout is higher than 500ms and the device does not exist, it will return "None".  
# an idea to improve the speed. I should use the "Except" method for "VXI_11_Stream_Sync_Lost" error. I did this idea. I did not see much improvement ...!
# we have to have a layer of protection from wrong IP address. It suppose to be in the begining of the program. 
# in the manual, askthe developer to add manually the name of device in the working commands for that devcie.
