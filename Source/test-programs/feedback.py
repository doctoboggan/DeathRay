# feedback method to check if the gpib address is the right address for choosen device. 

import data_acquisition

class m(data_acquisition.vxi_11.vxi_11_connection,data_acquisition.gpib_utilities.gpib_device,data_acquisition.vxi_11.VXI_11_Error):		
  """
  This class set DC voltage for given channels of the given device. 
  This class provides the DC current value of the given devices (to know the devices, please use
  'rightdevice' function.
  We are feeding the class with vxi_11.vxi_11_connection and gpib_utilities.gpib_device from data_acquisition library.
  """

  def __init__(self, IPad, Gpibad, namdev, timeout = 500): 


    self.ip_id = IPad
    self.gpib_id = Gpibad
    self.name_of_device = namdev.lower()    #lower case the input
    self.idn_head = namdev.lower()
    self.timeout = timeout
    rise_on_error = 0
    data_acquisition.vxi_11.vxi_11_connection.__init__(self,host=IPad,device=Gpibad,raise_on_err=rise_on_error,timeout=timeout,device_name=self.idn_head)  #here we are feeding the data_acquisition library


  def ok(self):
    print "ok..."
    l = self.check_idn()
    print l


