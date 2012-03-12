# this calss suppose to be able to bring the name of device.


import data_acquisition


class getIDN(data_acquisition.vxi_11.vxi_11_connection):

  def __init__(self, IPad = '127.0.0.1', Gpibad ="inst0"):

    self.ip_id = IPad
    self.gpib_id = Gpibad
    rise_on_error = 0
    timeout = 100
    namdev = 'nothing' 
    data_acquisition.vxi_11.vxi_11_connection.__init__(self,host=IPad,device=Gpibad,raise_on_err=rise_on_error,timeout=timeout,device_name=namdev)
    self.rightDevice = ['']

  def do(self):

    z, x, a = self.transaction('*IDN?')
    return a

# It works, I need to comment it. 
