"Basic power supply types"
_rcsid="$Id: power_supplies.py 323 2011-04-06 19:10:03Z marcus $"

import tagged_data

import time
import array
import math
import threading
import gpib_utilities

from control_subsystem import subsystem
import types
from vxi_11 import vxi_11_connection

	
class power_supply(subsystem):
	"""a multi-channel power supply, which has voltage & current setpoints, current readbacks, and voltage readbacks (possibly).
	Note that by having bind_field_info, read_field, and write_field, it conforms to the tagged_data requirements"""

	update_time_delta=1.0
	physical_channels=(1,) #mapping of logical channel numbers to physical on this device
	
	def init(self, name, shortname):
		self.supply_channels=len(self.physical_channels)
		subsystem.__init__(self, name, shortname)
		self.scan=4*self.supply_channels*[None]
		self.next_update_time=time.time()-10.0 #long ago!
			
	def save_read_data(self, data):
		"""override the usual behavior here since we have setpoints and readbacks in this array.  
		Returned data should be voltage, current, voltage, current,..."""
		
		self.scan[2*self.supply_channels:4*self.supply_channels]=data
	
	def save_setpoint(self, channel, value):
		"setpoints are voltage, current, and None is a legal choice for either"
		self.scan[2*channel:2*channel+2]=list(value)
	
	def read_channels(self): 
		"read all channels, current, voltage, current, voltage... override this for real supply"
		pass

	def update_data(self):
		"make sure data readbacks are within <update_time_delta> seconds of current, if someone is really watching actively"
		t=time.time()
		if t > self.next_update_time:
			self.read_channels()
			self.next_update_time=t+self.update_time_delta
	
	def bind_field_info(self, channel):
		"""return data that binds a logical channel to a (physical channel, voltage setpoint, current setpoint, voltage_readback, current_readback)  tuple.
		Note that our logical channels are numbered [0...channels-1], but the physical channels can be 
		identified any way desired by the content of the 'physical_channels' list"""
		return (self.read_field, self.write_field, self.write_field, 
			(self.physical_channels[channel], 2*channel, 2*channel+1, 2*channel+2*self.supply_channels, 2*channel+2*self.supply_channels+1))
	
	def write_field(self, channel_info, value_pair=(None,None)):
		"setpoints are a voltage, current pair, where None means don't change"
		self.scan[channel_info[1]:channel_info[1]+2]=value_pair
		self.write_data( (channel_info[0], value_pair) ) #the first element of our info tuple is the physical channel

	def read_field(self, channel_info):
		#our channel_info is always a physical channel number followed by the position information in self.scan 
		return [self.scan[c] for c in channel_info[1:]]

class scpi_power_supply(power_supply, vxi_11_connection, gpib_utilities.gpib_device):
	"a scpi_power_supply is a physical gpib device speaking scpi containing, possibly, multiple channels"
	my_host="127.0.0.1"
	my_portmap_proxy_host="127.0.0.1"
	my_portmap_proxy_port=111
	using_e5810=1
			
	channel_select_string=None
	current_set_string="CURR "
	voltage_set_string="VOLT "
	current_output_number_format="%.4f"
	voltage_output_number_format="%.4f"
	output_enable_string=":OUTP ON"
	output_disable_string=":OUTP OFF"
	current_readback_string=":MEAS:CURR?"
	voltage_readback_string=":MEAS:VOLT?"
	device_init_string="*RST"
	channel_init_string=""
	
	def  __init__(self, address, name, shortname=None):	
		local_vxi_11.init(self, "gpib0,%d,0"%address, name, shortname)
		power_supply.init(self, name, shortname)
		self.log_info(self.idn.strip())
		self.setup_device()
	
	def send_list(self, stringlist):
		self.lock()
		try:
			self.write(";".join([s for s in stringlist if s])) #send all non-blank strings with semicolons between them
		finally:
			self.unlock()

	def transact_list(self, stringlist):
		self.lock()
		try:
			a=self.transaction(";".join([s for s in stringlist if s]))[2] #send all non-blank strings with semicolons between them
		finally:
			self.unlock()
		
		return a.split(";")
		
	def setup_device(self):
		init=[]
		init.append(self.device_init_string)
		for i in range(len(self.physical_channels)):
			chan=self.physical_channels[i]
			if self.channel_select_string:
				init.append(self.channel_select_string%chan)
			init.append(self.channel_init_string)
			init.append(self.output_enable_string)

		self.lock()
		try:
			self.send_list(init)
			self.check_scpi_errors()
		finally:
			self.unlock(-10) #init ends at very low priority
		
	def read_channels(self): 
		"read all channels, current, voltage, current, voltage... override this for real supply"
		init=[]
		for i in self.physical_channels:
			if self.channel_select_string:
				init.append(self.channel_select_string%i)
			init.append(self.voltage_readback_string)
			init.append(self.current_readback_string)
		results=self.transact_list(init)
		self.save_read_data(results)
	
	def format_output(self, base_string, number_string, value):
		"format a general output, allowing for text values such as 'MAX' which some devices permit"
		if value is None:
			return None
		if type(value) is types.StringType:
			return base_string+value
		else:
			return base_string+(number_string%value)
		
	def write_data(self, channels):
		init=[]
		for phys_chan, (voltage, current) in channels:
			if self.channel_select_string:
				init.append(self.channel_select_string%phys_chan)
			init.append(self.format_output(self.voltage_set_string, self.voltage_number_format, voltage))
			init.append(self.format_output(self.current_set_string, self.current_number_format, current))
			self.save_setpoint(chan, (voltage, current))
		self.send_list(init)
	
	def close(self):
		init=[]
		for c in self.channels:
			c=self.physical_channels[chan] #convert virtual channels to real channels
			if self.channel_select_string:
				init.append(self.channel_select_string%c)
			init.append(self.channel_disable_string)
		self.send_list(init)
		
class analog_power_supply(power_supply):
	"an analog magnet owns a d/a channel for writing whichever parameter it writes, and optionally an ad channel for reading current and voltage"
	physical_channels=(0,)

	def  __init__(self, data_system, name, 
			shortname=None, da_name="", da_transconductance=1.0, da_v0=0.0, 
			ad_current_name=None, ad_transconductance=1.0, ad_v0=0.0, 
			ad_voltage_name=None):	
		power_supply.init(self, name, shortname)
		self.data_system=data_system
		self.ad_current_name=ad_current_name
		self.ad_transconductance=ad_transconductance
		self.ad_v0=ad_v0
		self.ad_voltage_name=ad_voltage_name
		self.da_name=da_name
		self.da_transconductance=da_transconductance
		self.da_v0=da_v0
		
	def read_channels(self):
		data=self.data_system
		if self.ad_voltage_name:
			v=data[self.ad_voltage_name]
		else:
			v=None
		if self.ad_current_name:
			i=data[self.ad_current_name]/self.ad_transconductance-self.ad_v0
		else:
			i=None
		self.save_read_data([v,i])

	def write_data(self, channels):
		c,(voltage, current)=channels #only one channel
		assert c==0 and  (voltage is None or current is None), "Analog supplies only have one channel and only one settable parameter!"
		self.save_setpoint(0,(voltage, current))
		if voltage is None:
			self.data_system[self.da_name]=current*self.da_transconductance+self.da_v0
		else:
			self.data_system[self.da_name]=voltage*self.da_transconductance+self.da_v0
				
	def close(self):
		self.save_setpoint(0,(0,0))
		self.data_system[self.da_name]=self.da_v0 #set output to zero

class current_supply:
	"a mix-in for a regular power supply which sets only the current"
	def write_field(self, channel_info, current):
		self.scan[channel_info[2]]=current
		self.write_data( (channel_info[0], (None, current)) ) #the first element of our info tuple is the physical channel

class voltage_supply:
	"a mix-in for a regular power supply which sets only the voltage"
	def write_field(self, channel_info, voltage):
		self.scan[channel_info[1]]=voltage
		self.write_data( (channel_info[0], (voltage, None)) ) #the first element of our info tuple is the physical channel
