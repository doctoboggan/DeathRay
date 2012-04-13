# Name: getAttachedDevices.py
# Made by: Jack Minardi
# Date: 3/15/12
# Goal: Return all devices attached to gpib gateway specified by IP
# Result: Two lists (attached device name list, attached device gpibID list)
 
from gpib_commands import getIDN

class getAttachedDevices():

  def __init__(self, IP ='127.0.0.1', numberofdevices = 30):
    '''Returns the attached device names and their gpibID's in 2 different lists
    '''
    self.ip = IP
    self.numberOfDevices = numberofdevices
    self.attachedDevices = []
    self.attachedGPIB = []

  def do(self):
    for x in range(0,self.numberOfDevices-1):
      gpibID = 'gpib0,' + str(x).rjust(2,'0')
      IDNResponse = getIDN(self.ip,gpibID, timeout=500).do()
      if IDNResponse:
        self.attachedDevices.append(IDNResponse.split(',')[1].lower())
        self.attachedGPIB.append(gpibID)
    return self.attachedDevices, self.attachedGPIB
