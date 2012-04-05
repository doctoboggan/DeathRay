"mix-in classes for handling tagged data fields"
_rcsid="$Id: tagged_data.py 323 2011-04-06 19:10:03Z marcus $"

import threading as _threading

class dio_device: #handle named data fields and lazy/immediate writing with this mix-in
	
	def init(self): 
		self.__device_lock=_threading.Lock()
		self.lazy_write_mask=0L
		self.lazy_data=0L
		self.latched_output_data=0L
		self.scan=0L
		
	def save_read_data(self, data):
		self.scan=long(data)
	
	def write_data(self, data, mask):
		self.lock()
		self.__device_lock.acquire() #make this thread-safe
		try:
			if mask or self.lazy_write_mask:
				ld=self.latched_output_data
				changemask = (self.lazy_data ^ ld) & self.lazy_write_mask #first look at lazy changes
				ld ^= changemask
				changemask ^= (data ^ ld) & mask #map of changed bits, with non-lazy vs. lazy conflicts favoring non-lazy
				self.latched_output_data ^= changemask #map changes into latched value
				self.lazy_write_mask=0
				self.lazy_data=0
				if changemask: #only do everything if data has changed within mask
					self.write_raw(self.latched_output_data, changemask)
		finally:
			self.__device_lock.release()
			self.unlock() 
			
	def bind_field_info(self, info=None):
		if info:
			startbit, bitcount=info
			mask=(-1L & ~(-1L << bitcount))<<startbit
		else:
			startbit, mask = 0,0		
		return self.read_field, self.write_field, self.write_field_lazy, (startbit, mask)
				
	def write_field(self, channel_info=None, value=None):
		"write_field(name, value) writes data now, so on return it is guaranteed to be sent"
		if channel_info:
			startbit, mask=channel_info
			self.write_data(long(value)<<startbit, mask)
		else:
			self.write_data(0,0) #flush lazy data
		
	def write_field_lazy(self, channel_info, value):
		"write_field_lazy(name, value) posts data so it gets written at the next read cycle, with no guarantee that it is changed on return"
		
		startbit, mask = channel_info
		assert writable != 0, "Attempt to write to read-only dio field %s" % name
		self.__device_lock.acquire()
		self.lazy_data = (self.lazy_data & ~mask) | (long(value)<<startbit)
		self.lazy_write_mask |= mask
		self.__device_lock.release()
		
	def read_field(self, channel_info):
		startbit, mask = channel_info
		return (self.scan & mask) >> startbit
			
class array_device: #handle named data fields and lazy/immediate writing with this mix-in
	
	def init(self): 
		self.__device_lock=_threading.Lock()
		if not hasattr(self,"scan"):
			self.scan=[] #don't trample on it if someone else set it up already
		self.lazy_items=[]
		
	def save_read_data(self, data):
		self.scan=data
				
	def bind_field_info(self, channels):
		"return information of the type needed to access fields on this device"
		if type(channels) is type(1):
			channels=(channels,) #make it a tuple
		return self.read_field, self.write_field, self.write_field_lazy, channels

	def write_field(self, channel_info=None, value=None):
		"write_field(name, value) writes data now, so on return it is guaranteed to be sent, and write lazy items first so non-lazy overwrites lazy"
		self.lock()
		self.__device_lock.acquire()
		try:
			items=self.lazy_items
			self.lazy_items=[]
		
			if channel_info is not None:
				if len(channel_info)==1:
					items+=[(channel_info[0],value)]
				else:
					items+=zip(channel_info, value)
			self.write_data(items) #send (channel,value) tuples

		finally:
			self.__device_lock.release()
			self.unlock() 
			
	def write_field_lazy(self, channel_info, value):
		if len(channel_info)==1:
			items=[(channel_info[0],value)]
		else:
			items=zip(channels, value)
		self.lazy_items+=items #this is atomic, so it is safe without locking
		
	def read_field(self, channel_info):
		if len(channel_info)==1:
			return self.scan[channel_info[0]]
		else:
			return [self.scan[c] for c in channel_info]
			
class tagged_data_system:
	"tagged_data_system is a container class for multiple devices with named data fields"

	def reset(self):
		"clear all entries"
		self.__dict__["fields"]={} #do it this way to avoid using __setattr__

	def __init__(self): 
		self.reset()
	
	def no_write(self, bogus_info, bogus_value):
		raise AssertionError, "Attempt to write to read-only field"
		
	def define_field(self, global_name, device, device_info, writable=0):
		"""define a field with global name <global_name> on device <device> described by
		any parameters the device needs to identify the the field in <device_info>. """ 
		assert global_name not in self.fields, "Adding same name twice to tagged data: "+global_name
		reader, writer, lazy_writer, bound_info = device.bind_field_info(device_info)
		if not writable:
			writer = lazy_writer = self.no_write
		self.fields[global_name]=(reader, writer, lazy_writer, bound_info)
	
	def __delitem__(self, name):
		del self.fields[name]
		
	def write_field(self, name, value):
		"write_field(name, value) writes data now, so on return it is guaranteed to be sent"
		reader, writer, lazy_writer, bound_info=self.fields[name]
		writer(bound_info, value)
	
	def write_field_lazy(self, name, value):
		"""write_field_lazy(name, value) posts data so it gets written 
		at the next read or write cycle, 
		with no guarantee that it is changed on return"""
		reader, writer, lazy_writer, bound_info=self.fields[name]
		lazy_writer(bound_info, value)
		
	def read_field(self, name):
		reader, writer, lazy_writer, bound_info=self.fields[name]
		return reader(bound_info)
	
		
	#these are convenient aliases for the above real routines, implemented this way
	#to avoid any extra layers of calling				
	__getattr__=read_field
	__getitem__=read_field
	__setattr__=write_field
	__setitem__=write_field	


#go ahead and create one of us globally, since this is probably the desired behavior
system_data=tagged_data_system()
