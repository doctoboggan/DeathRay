# this calss suppose to be able to bring the name of device.


import data_acquisition


class name(data_acquisition.vxi_11.vxi_11_connection):

  def __init(self, IPad, Gpibad):

    self.ip_id = IPad
    self.gpib_id = Gpibad
    rise_on_error = 0
    timeout = 100
    namdev = 'nothing' 
    data_acquisition.vxi_11.vxi_11_connection.__init__(self,host=IPad,device=Gpibad,raise_on_err=rise_on_error,timeout=timeout,device_name=namdev)

  def do(self):

    z, x, a = self.transaction('*IDN?')
    return a

# It works, I need to comment it. 
