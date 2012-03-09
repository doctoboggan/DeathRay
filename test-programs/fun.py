


import data_acquisition

class fun(data_acquisition.vxi_11.vxi_11_connection,data_acquisition.gpib_utilities.gpib_device,data_acquisition.vxi_11.VXI_11_Error):

  def __init__(self, IPad, Gpibad, command, namdev = 'nothing'):

    self.ip_id = IPad
    self.gpib_id = Gpibad
    self.name_of_device = namdev.lower()
    self.com = command
    data_acquisition.vxi_11.vxi_11_connection.__init__(self,host=IPad,device=Gpibad,raise_on_err=0,timeout=500,device_name=namdev)

  def doing(self):

    l = self.com
    k = '"'+self.com+'"'
    print "l is " +l
    error, reason, goal = self.transaction(l) 
    #print error
    #print reason
    return goal

# fun.fun('129.59.93.179','gpib0,10', '*idn?').doing()
