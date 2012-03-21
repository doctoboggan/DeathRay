"""Setups for many of the devices used in the Vanderbilt University Free-Electron laser Center VXI crate.
Useful to the public as drivers for some specific devices, plus lots of exemplary boilerplate"""
_rcsid="$Id: vxi_crate_devices.py 323 2011-04-06 19:10:03Z marcus $"

import vxi_11 
from vxi_11 import vxi_11_connection, device_thread
import time
import exceptions
import struct
import array
import threading
import traceback
import sys
import tagged_data
from control_subsystem import subsystem
from gpib_utilities import *

from alarm_system import local_vxi_11 as fel_vxi_11
class Timeout_Error(exceptions.Exception):
	pass

class AD_Fatal_Error(exceptions.Exception): #scanning A/D not responding!
	pass
	
class vxi_crate_device(fel_vxi_11, device_thread, gpib_device):
	my_base_device_name="gpib0,9,%d"
	
	from device_addresses import crate_host as my_host
	from device_addresses import crate_portmap_proxy_host as my_portmap_proxy_host
	from device_addresses import crate_portmap_proxy_port as my_portmap_proxy_port
	from device_addresses import crate_using_e5810 as using_e5810

	max_message_wait=1.0 #seconds
	device_loop_sleep=1.0
	default_lock_timeout=2000
	default_timeout=2000
				
	def  init(self, slot, name, shortname=None):	
		
		if shortname is None:
			shortname=name.strip().replace(' ','').replace('\t','')+("(%d)"%slot)

		fel_vxi_11.init(self, self.my_base_device_name%slot, name, shortname)
		self.log_error(self.idn.strip(), self.debug_info)
		self.setup_device()
						
	def setup_device(self):
		pass
	
	def close(self):
		th=self.get_monitor_thread()
		if th:
			self.stop_thread()
			th.join() #wait for thread to exit
		self.disconnect()
				
class crate_controller(vxi_crate_device):
	idn_head="HEWLETT-PACKARD,E1406A"

	def __init__(self):
		vxi_crate_device.init(self, 0, "slot0")

	def setup_device(self):
		self.lock()
		try:
			self.clear()
			try:
				self.check_scpi_errors()
			except SCPI_Error: #clear any initial errors without bailing out
				pass
			self.write("*rst;")
			self.write("outp:ext:state on;source ttlt0;")
		finally:
			self.unlock()

class e1413b(vxi_crate_device, tagged_data.array_device):
	idn_head="HEWLETT-PACKARD,E1413B"

	from device_addresses import e1413b_scan_list as scan_list
	from device_addresses import e1413b_scan_channels as scan_channels
	
	debug_level=vxi_crate_device.debug_error
	device_loop_sleep=0.001
	#timeout=250000.0
	recent_timeouts_warning_threshold=1
	consecutive_failures_limit=5
	max_message_wait=1.0
	
	def __init__(self, slot=2):
		vxi_crate_device.init(self, slot, "64 channel scanning adc")
		tagged_data.array_device.init(self)
		self.save_read_data(self.scan_channels*[0.0])
		
	def setup_device(self):
		self.lock()
		try:
			self.clear()
			try:
				self.check_scpi_errors()
			except SCPI_Error: #clear any initial errors without bailing out
				pass
			self.write("*cls;*sre 0;:stat:ques:enable #H0800;*ese 63;:init:cont off;")
			err, reason, setup_check=self.mav_transaction(":diag:otd? (@100);:stat:ques:cond?")
			otdstat, qstat = [int(i) for i in setup_check.split(";")]
			self.log_error("otd status = %d, questionable status = %04x" % (otdstat, qstat), self.debug_info)
			if otdstat:
				self.write(":diag:otd off,(@100,108);")
				self.log_error("Waiting 2 minutes for otd to settle before recalibrating", self.debug_info)
				time.sleep(120)
			if qstat & 0x2000:  #configuration changed... must recalibrate
				self.log_error("recalibrating a/d... this takes a while", self.debug_info)
				self.write("*cls;:func:volt:dc 10,(@100:155);:cal:set")
				done=0
				time.sleep(30) #let cal get started, during which time system is basically hung
				self.write(":cal:set?")
				while(not (done & 16)):
					time.sleep(60)
					try:
						err,done=self.read_status_byte() 
					except (IOError, VXI_11_Error):
						pass
					self.log_error("tapping fingers on desk while a/d recalibrates... status = %02x" % done, self.debug_info)
				err, reason, result=self.read()				
				r=int(result)
				if r:
					self.log_error("Calibration failed!", self.debug_error)
					err, reason, badchans=self.mav_transaction(
							"*cls;:form:data ascii;:sense:data:fifo:all?", status_error_mask=0)
					badchans=badchans.split(",")
					badchan_num=[int(float(x)+0.5) for x in badchans]
					self.log_error("Bad channel list from FIFO:" + str(badchan_num), self.debug_error)
					raise AD_Fatal_Error,"Calibration failed!"
				else:
					self.log_error("Calibration passed", self.debug_info)
					
			self.check_scpi_errors()
		finally:
			self.unlock_completely() #must unlock, since next activity is in thread
	
	def prepare_scanning(self):
		self.lock()
		self.clear()
		try:
			self.write("*cls")
			self.write(":rout:seq:def LIST1, "+self.scan_list)
			#self.scan_channels=int(self.transaction(":route:seq:points? LIST1")[2])
			self.log_error( "Scan channels %d" % self.scan_channels, self.debug_info)
			self.write(":route:scan LIST1;:trig:source imm;:trig:count 1;")
			self.write(":format real;")
			self.check_scpi_errors()
			self.write(":init") #start data collection
		finally:
			self.unlock()
				
	def monitor(self): #override this since we are forever locked
		self.lock() #adding one to the locklevel prevents us from unlocking until the very end
		try:
			self.prepare_scanning()			
		except:
			self.log_exception()
			self.running=0			
			self.unlock_completely()
		else:
			device_thread.monitor(self) #and call normal monitor loop (which completely unlocks at the end)
		
	def onepass(self): #used by our device thread to read out data, overridden here due to permanent lock
		self.consecutive_failures+=1
		try:
			err, reason, data = self.transaction("*wai;:data:fifo?;:init;")
			result, junk = handle_iee488_binary_block( data)
			count=len(result)//4
			if count==self.scan_channels:
				self.save_read_data(array.array('f',list(struct.unpack(">%df"%count, result))))
				self.consecutive_failures=0 #reset! got good data
				self.last_good_data_time=time.time()
				
			else:
				self.log_error("Wrong length data on loop %d, len= %d"%(self.loop_count, count))
				self.clear()
				
		except (IOError, Timeout_Error):
			#self.log_error("Timeout on loop %d"%self.loop_count)
			self.clear()
			self.write("*cls")
			self.recent_timeouts+=1
			
		if self.consecutive_failures >= self.consecutive_failures_limit:
			raise AD_Fatal_Error, "Too many consecutive failures: n= %d" % self.consecutive_failures
				
		if self.loop_count%100==0:

			err, status=self.read_status_byte()
			if status & 8:
				raise AD_Fatal_Error,"Overvoltage on A/D, must *rst to clear"
			elif status & 32: #something in standard events???
				err, reason, val = self.transaction("*esr?") #get event register
				self.log_error("Event in standard standard events: %02x" % val)
				self.clear()
				self.write("*cls")

			if self.recent_timeouts >= self.recent_timeouts_warning_threshold:
				warn_level=self.debug_error
			else:
				warn_level=self.debug_all
			self.log_error("Loop %d, recent timeouts=%d" % (self.loop_count, self.recent_timeouts), warn_level)
			self.recent_timeouts=0
			self.log_error("Data[:8]= "+str(self.scan[:8]), self.debug_all)
			try:
				self.check_scpi_errors()
			except IOError:
				self.log_error("Timeout checking SCPI errors")
				self.clear()
				self.write("*cls")
				
		self.loop_count+=1

class e1328a(vxi_crate_device, tagged_data.array_device):
	idn_head="HEWLETT-PACKARD,E1328A"

	def __init__(self, slot=3):
		vxi_crate_device.init(self, slot, "4 channel dac")
		tagged_data.array_device.init(self)
		self.save_read_data([0,0,0,0])
		self.debug_scpi=0
		
	def setup_device(self):
		self.lock()
		try:
			self.clear()
			try:
				self.check_scpi_errors()
			except SCPI_Error: #clear any initial errors without bailing out
				pass
			self.write("*rst;*cls;")
			self.write(":cal1:state on;:cal2:state on;:cal3:state on;:cal4:state on")
			time.sleep(2)
			self.check_scpi_errors()
			
		finally:
			self.unlock()

	def write_data(self, chanlist):
		outstr=""
		for chan, val in chanlist:
			outstr += ":volt%d %.3f;" % (chan+1, val)
			self.scan[chan]=val #make sure it appears in our readback
		self.lock() #normally, we should already be locked by the time we get here
		try:
			self.write(outstr)
			if self.debug_scpi:
				self.check_scpi_errors()
		finally:
			self.unlock(priority=2.0) 
			#if a write occurred, don't yield too quickly, since more might follow
		
class video_mux(vxi_crate_device, tagged_data.array_device):
	idn_head="HEWLETT-PACKARD,SWITCHBOX"

	def __init__(self, slot=5):
		vxi_crate_device.init(self, slot, "75 ohm video multiplexer")
		tagged_data.array_device.init(self)
		self.save_read_data([0,0,0,0,0,0])
	
class e1458a(vxi_crate_device, tagged_data.dio_device):
	idn_head="HEWLETT-PACKARD,E1458A"
	deglitch_buffer_depth=2
	device_loop_sleep=1.0
	consecutive_failures_limit=2
	recent_timeouts_warning_threshold=1
	
	def __init__(self, slot=5):
		self.default_timeout=2000
		self.default_lock_timeout=2000
		vxi_crate_device.init(self, slot, "96 channel dio")
		self.deglitch_buffer=8*[0L]
		tagged_data.dio_device.init(self)
		self.all_ones=0xffffffffffffffffffffffffL
		self.latched_output_data=self.all_ones #*rst left all lines high
		
	def setup_device(self):
		self.lock()
		try:
			self.clear()
			try:
				self.check_scpi_errors()
			except SCPI_Error: #clear any initial errors without bailing out
				pass
			self.write("*rst") #set to all high-impedance (input)
		finally:
			self.unlock()

	def get_data(self): #used by our device thread to read out data
		self.consecutive_failures+=1
		try:
			self.write_data(0,0) #only write lazy data
			err, reason, data = self.transaction(":dig:data:lw96:mon?")
			words=[long(i) for i in data.split(",")]
			if len(words)==3:
				for i in range(3):
					if words[i] < 0: words[i] += 2L<<31
				#now, put bytes in reasonable order! the words come back reversed-endian w.r.t the byte number sent in a write
				w0, w1, w2 = struct.unpack("<LLL", struct.pack(">LLL", words[0], words[1], words[2])) 
				self.save_read_data(w2 << 64 | w1 << 32 | w0)
				
				#do digital debouncing by compaing ands and ors of history
				self.deglitch_buffer[:-1]=self.deglitch_buffer[1:] #bump data up one row
				self.deglitch_buffer[-1]=self.scan
				andstart=self.all_ones
				orstart=0L
				for i in self.deglitch_buffer:
					andstart &= i
					orstart |= i
				
				self.unstable = andstart ^ orstart
				
				self.consecutive_failures=0 #reset! got good data
				self.last_good_data_time=time.time()
				
			else:
				self.log_error("Wrong length data on loop %d, len= %d"%(self.loop_count, count))
				self.clear()
				
		except (IOError, Timeout_Error):
			#self.log_error("Timeout on loop %d"%self.loop_count)
			self.clear()
			self.write("*cls")
			self.recent_timeouts+=1
			
		if self.consecutive_failures >= self.consecutive_failures_limit:
			raise AD_Fatal_Error, "Too many consecutive failures: n= %d" % self.consecutive_failures
				
		if self.loop_count%100==0:

			if self.recent_timeouts >= self.recent_timeouts_warning_threshold:
				warn_level=self.debug_error
			else:
				warn_level=self.debug_all
			self.log_error("Loop %d, recent timeouts=%d" % (self.loop_count, self.recent_timeouts), warn_level)
			self.recent_timeouts=0
			self.log_error("Data= "+str(self.scan), self.debug_all)
			try:
				self.check_scpi_errors()
			except IOError:
				self.log_error("Timeout checking SCPI errors")
				self.clear()
				self.write("*cls")
				
		self.loop_count+=1

	def write_raw(self, data, mask):
		"write_raw() is called from write_data() after thread locking and lazy data handling is set up"
		datastring="%024x" % data
		maskstring="%024x" % mask
		outputstring=''
		for i in range(12):
			if maskstring[-2:] != "00": #changed bytes here
				outputstring += ":dig:data%d:byte #h%s;" % (i,datastring[-2:])
			maskstring=maskstring[:-2]
			datastring=datastring[:-2]
		self.lock()
		try:
			self.write(outputstring)
		finally:
			self.scan = (self.scan & ~mask) | (data & mask) 
			#update apparent readbacks immediately, and while we are still locked, 
			#so the real readback process doesn't get confused or overwritten by this
			#if a write occurred, don't yield too quickly, since more might follow
			self.unlock(priority=2.0)
				
		
class scanning_voltmeter(vxi_crate_device, tagged_data.array_device):
	initial_config_string=":conf:volt dc,10.0,(@100:107);"
	scan_channels=8
	default_timeout=2000
	consecutive_failures_limit=5
	default_lock_timeout=2000
	device_loop_sleep=1.0
	recent_timeouts_warning_threshold=1
	max_message_wait=1.0

	def __init__(self, slot=7, name="multimeter"):
		vxi_crate_device.init(self, slot, name)
		tagged_data.array_device.init(self)
		self.scan=array.array('f') #set default scan data type
		self.save_read_data(self.scan_channels*[0.0])
	
	def save_read_data(self, data_list):
		self.scan=array.array(self.scan.typecode, data_list)
		
	def setup_device(self):
		self.lock()
		try:
			self.clear()
			try:
				self.check_scpi_errors()
			except SCPI_Error: #clear any initial errors without bailing out
				pass
			self.write("*rst;*sre 0;")
			self.write(self.initial_config_string)
			self.check_scpi_errors()
		finally:
			self.unlock()
				
	def get_data(self): #used by our device thread to read out data
		self.consecutive_failures+=1
		try:
			err, reason, data = self.mav_transaction(":init;:form real,32;:fetch?")
			result, junk = handle_iee488_binary_block( data)
			count=len(result)//4
			if count==self.scan_channels:
				self.save_read_data(list(struct.unpack(">%df"%count, result)))
				self.consecutive_failures=0 #reset! got good data
				self.last_good_data_time=time.time()
				
			else:
				self.log_error("Wrong length data on loop %d, len= %d"%(self.loop_count, count))
				self.clear()
				
		except (IOError, Timeout_Error):
			#self.log_error("Timeout on loop %d"%self.loop_count)
			self.clear()
			self.write("*cls")
			self.recent_timeouts+=1
			
		if self.consecutive_failures >= self.consecutive_failures_limit:
			raise AD_Fatal_Error, "Too many consecutive failures: n= %d" % self.consecutive_failures
				
		if self.loop_count%100==0:

			if self.recent_timeouts >= self.recent_timeouts_warning_threshold:
				warn_level=self.debug_error
			else:
				warn_level=self.debug_all
			self.log_error("Loop %d, recent timeouts=%d" % (self.loop_count, self.recent_timeouts), warn_level)
			self.recent_timeouts=0
			self.log_error("Data[:8]= "+str(self.scan[:8]), self.debug_all)
			try:
				self.check_scpi_errors()
			except IOError:
				self.log_error("Timeout checking SCPI errors")
				self.clear()
				self.write("*cls")
				
		self.loop_count+=1

class thermometers(scanning_voltmeter):
	idn_head="HEWLETT-PACKARD,E1411B"
	scan_channels=8
	device_loop_sleep=1.0
	recent_timeouts_warning_threshold=1
	max_message_wait=1.0
	initial_config_string=":conf:temp fth,2252,(@100:107);:trig:sour imm;:res:nplc 1;:samp:timer 33.333e-3;:trig:count 1;"
	default_timeout=2000
	default_lock_timeout=2000
	
	def __init__(self, slot=7):
		scanning_voltmeter.__init__(self, slot, "multimeter/thermometer")


class glue(vxi_crate_device, tagged_data.dio_device):
	idn_head=None
	idn="Homebrew glue board "
	device_loop_sleep=1.0

	def __init__(self, slot=11):
		self.data_read_str=":vxi:sel %d;reg:read? 4;write 8,0" % (slot*8) #read data and tweak watchdog
		self.data_write_str=":vxi:sel %d;reg:write 6,%%d" % (slot*8) #read data and tweak watchdog
		vxi_crate_device.init(self,0, "glue board", "glueboard(%d)" % slot) #we really talk to slot zero to control this
		tagged_data.dio_device.init(self)
		self.save_read_data(0)
	
	def setup_device(self):
		self.lock()
		try:
			self.clear()
			try:
				self.check_scpi_errors()
			except SCPI_Error: #clear any initial errors without bailing out
				pass

			self.write(self.data_write_str % 0) #preflight data write, and clear bits			
			self.transaction(self.data_read_str) #preflight a read and reset the watchdog
			self.check_scpi_errors()
		finally:
			self.unlock()
		
		
	def write_raw(self, data, mask):
		"write_raw() is called from write_data() after thread locking and lazy data handling is set up"
		self.lock()
		try:
			self.write(self.data_write_str % data)
		finally:
			self.unlock(priority=2.0)
			#if a write occurred, don't yield too quickly, since more might follow

	def get_data(self): #used by our device thread to read out data
		self.consecutive_failures+=1
		try:
			err, reason, data = self.transaction(self.data_read_str)
			d=int(data)
			if d<0:
				d+=256
			self.save_read_data(d)
			self.consecutive_failures=0
		except (IOError, Timeout_Error):
			self.log_error("Timeout on loop %d"%self.loop_count)
			self.clear()
			self.write("*cls")

		self.loop_count+=1


class dg600(vxi_crate_device):
	idn_head="INTERFACE TECHNOLOGY,DG600"
		
	def __init__(self, slot=12):
		vxi_crate_device.init(self, slot, "dg600 pattern generator")
				
	def setup_device(self):
		self.lock()
		try:
			self.clear()
			self.write("*rst") #clear it		
		finally:
			self.unlock()

	def send(self, multilines):
		
		if type(multilines) is type(""):
			lines=multilines.split("\r")
		else:
			lines=multilines
			
		self.lock()
		try:
			for i in lines:
				self.write(i+"\r")
		finally:
			self.unlock()

			
