"LabPro_PyUSB supports connections of the Vernier LabPro system via USB using the PyUSB library"

import usb

_rcsid="$Id: LabPro_PyUSB.py 323 2011-04-06 19:10:03Z marcus $"

import LabPro
from LabPro import RawLabPro, LabProError, LabProTimeout, _bigendian

import array


try:
	import numpy as Numeric
	import numpy
	numeric_float=Numeric.float64
	numeric_int32=Numeric.int32
except:
	import Numeric
	numeric_float=Numeric.Float64
	numeric_int32=Numeric.Int32

import time
import sys

import os
import threading
import Queue
import traceback
import struct

import LabPro_USB
import array

class PyUSB_mixin:
	"mixin class for RawLabPro to allow operation of LabPro via PyUSB library"
	idVendor = 0x8f7
	idProduct = 1
	
	def setup_serial(self,port_name=None):
		self.usb_timestamp=0
		matchcount=0
		matchdev=None
		self.write_queue=Queue.Queue()
		self.read_queue=Queue.Queue()
		self.__keep_running=1
		try:
			#scan busses and devices to find appropriately indexed device
			for bus in usb.busses():
				for dev in bus.devices:	
					if dev.idVendor==self.idVendor and dev.idProduct==self.idProduct:
						matchcount+=1
						matchdev=dev
						if matchcount==self.device_index: break
				
				if matchcount==self.device_index: break
			if not matchdev or matchcount != self.device_index: 
				raise IOError("no USB LabPro found with requested index %d" % self.device_index)
				
			udev=self.usbdev=matchdev.open()
			udev.claimInterface(0)
			time.sleep(0.020) # wait 20 ms for safety 
			udev.setConfiguration(1) #default configure interface 
			time.sleep(0.020) # wait 20 ms for safety 
			udev.claimInterface(0) #reclaim after configure
			
			self.read_thread=threading.Thread(target=self.reader_thread_task)
			self.read_thread.start()
			self.write_thread=threading.Thread(target=self.writer_thread_task)
			self.write_thread.start()
		except IOError:
			raise
		except:
			self.__keep_running=0
			self.close()
			raise
						
	def high_speed_serial(self):
		"not implemented on USB"
		return 

	def high_speed_setup(self):
		"not implemented onUSB"
		return 

	def set_port_params(self):
		"not implemented on USB"
		return 

	def reader_thread_task(self):
		"""monitor USB input for data and post to queue as it comes in"""
		try:
			stop_time=time.time()
			while self.__keep_running:
				start_time=stop_time #close enough to detect timeouts
				data = self.usbdev.bulkRead(usb.ENDPOINT_IN | 2 , 64, 10000);
				stop_time=time.time()
				if stop_time - start_time > 9.5:  continue #probably a timeout, just keep going
				self.read_queue.put((stop_time, array.array('B', data).tostring()))
		except:
			self.__keep_running=0
			try:
				self.usbdev.clearHalt(usb.ENDPOINT_OUT | 2)
			except:
				pass
			try:
				self.usbdev.clearHalt(usb.ENDPOINT_IN | 2)
			except:
				pass
				
	def writer_thread_task(self):
		"""monitor USB input for data and post to queue as it comes in"""
		try:
			while self.__keep_running:
				try:
					newdata=self.write_queue.get(True, 1)
				except Queue.Empty:
					continue
				while newdata:  #break into 64-byte chunks
					self.usbdev.bulkWrite(usb.ENDPOINT_OUT | 2 , newdata[:64], 1000)
					newdata=newdata[64:]
				self.write_queue.task_done()
		except:
			if self.__keep_running: #got an error which wasn't on termination
				import traceback
				traceback.print_exc()
			self.__keep_running=0
			try:
				self.usbdev.clearHalt(usb.ENDPOINT_OUT | 2)
			except:
				pass
			try:
				self.usbdev.clearHalt(usb.ENDPOINT_IN | 2)
			except:
				pass
		
	def read(self, maxlen=None, mode=None):
		"read data from USB.  If mode is None or 0, strip trailing nulls for ASCII, otherwise leave alone"
		res=''
		while (not maxlen or (maxlen and len(res) < maxlen)) and self.__keep_running:
			try:
				timestamp, data = self.read_queue.get(True, 1)
			except Queue.Empty:
				continue
			res=res+data			
			self.data_timestamp=timestamp
			if not mode and data.find('\r'): break #ascii data terminator
		if not mode:
			zp=res.find('\0')
			if zp>=0:
				res=res[:zp] #trim any nulls
		
		if not self.__keep_running: raise IOErr("USB Labpro index %d closed, reading still going on" % self.device_index)
		return res
			
		
	def write(self, data):
		self.write_queue.put(data)
		
	def close(self):
		if self.__keep_running:
			try:
				self.stop()
			except:
				pass
		self.__keep_running=0
		time.sleep(2)
		try:
			self.usbdev.clearHalt(usb.ENDPOINT_OUT | 2)
		except:
			pass
		try:
			self.usbdev.clearHalt(usb.ENDPOINT_IN | 2)
		except:
			pass
		try:
			self.usbdev.releaseInterface()
		except:
			pass

class LabPro_PyUSB(LabPro_USB.USB_data_mixin, PyUSB_mixin, RawLabPro):
	def __init__(self, device_index=1):
		self.device_index=device_index
		RawLabPro.__init__(self,'')

if __name__=='__main__':
	
	class LabProData(Exception):
		pass
	
	def monitor_humidity(filepath="humidity.txt", sample_period=30.0):
		
		badloops=0
		lp=LabPro_PyUSB()
		start_time=time.time()
		
		try:	
			lp.wake()
			lp.reset()
			print lp.get_system_config() #just to vacuum the connection
			lp.setup_channel(chan=2, operation=14, equation=0) #set up 0-5 volts readback for humidity sensor
			lp.command(107, .001, 1000) #setup 1000-1 oversampling for 1 second		
			while(1):
				time.sleep(sample_period)
				try:
	
					lp.setup_data_collection(samptime=2.0, numpoints=1, filter=0)
					lp.wait_for_data_done(flasher=0)
					lp.binary_mode()
					value=lp.get_data_binary(chan=2, scaled_range=(0.,5.))						
					if len(value)>1:
						raise LabProData("got too much data...: "+str(value))
					value=value[0]
		
					grabtime=time.time()
					try:
						if filepath is not None:
							f=file(filepath,"a")
						else:
							f=sys.stdout
							
						print >> f, "%s\t%.3f\t%.3f\t%.1f" % (time.asctime(), grabtime-start_time, value, value*31.47-31.74)
						
					finally:
						if f != sys.stdout:
							f.close()
							
					badloops=0
				
				except KeyboardInterrupt:
					break
				except:
					badloops+=1
					if badloops >= 5: raise #re-raise on 5th consecutive failure
	
		finally:
			lp.close()
		
	
	monitor_humidity(filepath=None, sample_period=1.0)
