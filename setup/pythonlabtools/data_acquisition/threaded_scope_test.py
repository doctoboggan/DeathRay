"A sample of multi-threaded vxi-11 code... probably not up-to-date"
_rcsid="$Id: threaded_scope_test.py 323 2011-04-06 19:10:03Z marcus $"

import vxi_11
import graphite
import time
import traceback
import Numeric
import exceptions
import threading
import graphite

from vxi_11 import VXI_11_Transient_Error, VXI_11_Error

import infinium_module
from infinium_module import infinium 

def dump_scpi_errors(device, prefix=""):
	err=1
	count=0
	while(err):
		errstr=device.transaction(":syst:head 0;err? string")[2]
		err=int(errstr.split(',')[0])
		if err:
			count+=1
			device.log_error(prefix+"SCPI error: "+errstr)
	return count

class scope_monitor_thread(vxi_11.device_thread):
	def __init__(self, scope, channels, data_wait_sleep=1.00, data_wait_loops=10, main_sleep=1.0, name="Device", debug=0):
		vxi_11.device_thread.__init__(self, scope, main_sleep=main_sleep, name=name)
		self.scope=scope
		self.data=None
		self.setup=scope.transaction(":syst:head off;:syst:setup?")[2]
		self.channels=channels
		self.data_wait_sleep=data_wait_sleep
		self.data_fail=0
		self.data_wait_loops=data_wait_loops
		
	def get_data(self):
		try:
			scope=self.connection()
			scope.clear()
			scope.abort()
			dump_scpi_errors(scope, self.name+": pre-setup: ")
			scope.write("*sav 1;:syst:setup "+self.setup)
			dump_scpi_errors(scope, self.name+": post-setup: ")
			scope.digitize(self.channels)
			scope.wait_for_done(sleep=self.data_wait_sleep, max_loops=self.data_wait_loops)									
			self.waveform=Numeric.array( scope.get_current_data(self.channels) )
			self.data_fail=0
			dump_scpi_errors(scope, self.name+": post-readout: ")
			scope.log_error("thread %s got data, %d points" % (self.name,len(self.waveform[0])), self.connection().debug_info)
		except UserWarning:
			self.data_fail+=1
			scope.log_error(self.name+": no trigger")
			scope.clear()			
		except VXI_11_Transient_Error:
			self.data_fail+=1
			scope.log_exception(self.name+": transient error, ")		
		except:
			scope.clear()
			scope.log_traceback(self.name)
			self.run=0
			
		try:
			scope.write("*rcl 1;:run;")
			scope.local() #release control
		except VXI_11_Transient_Error:
			pass
		
		if 0:
			try:
				scope.log_info(self.name + ": Preparing to reconnect!")
				scope.close()
				scope.reconnect() #very abnormal thing to do!
				scope.log_info(self.name + ": Reconnected")
				scope.lock() #and relock, since we should be locked
				scope.log_info(self.name + ": Locked")
			except VXI_11_Error:
				scope.log_error(self.name + ": reconnect failed")
			
		if self.data_fail > 10:
			raise UserWarning, "10 repeated tries to scope produced no data"
		

def test1():
	
	scope=infinium
	scope.default_timeout=5000
	scope.default_lock_timeout=1000
	
	if not scope.connected:
		scope.reconnect()
		
	err, reason, main_setup=scope.transaction(":syst:setup?")
	dump_scpi_errors(scope)
	scope.write(":syst:setup "+main_setup)
	if dump_scpi_errors(scope): #if re-sending the original setup creates an error, the setup is irrational and will be reset
		scope.write("*rst")
	
	try:
		scope.lock()
				
		#these setting are in common in this case...
		scope.set_channel(1, range=5, offset=0, coupling=scope.ac, atten=10.0, lowpass=0, impedance=50)
		dump_scpi_errors(scope)
		scope.set_channel(2, range=0.1, offset=0, coupling=scope.dc, atten=1.0, lowpass=0, impedance=None)
		dump_scpi_errors(scope)
		scope.set_channel(3, range=0.1, offset=0, coupling=scope.dc, atten=10.0, lowpass=1, impedance=None)
		dump_scpi_errors(scope)
		scope.set_channel(4, range=5, offset=2, coupling=scope.dc, atten=1.0, lowpass=1, impedance=50)
		dump_scpi_errors(scope)
				
		#now, set up specifics for one thread
		scope.average_mode(16)
		dump_scpi_errors(scope)
		scope.set_timebase(range=2e-6, reference=scope.left, delay=-1e-8)
		dump_scpi_errors(scope)
		scope.set_edge_trigger(1, level=0, slope=1, auto_trigger=1, coupling=scope.ac)
		dump_scpi_errors(scope)
		fast_trace=scope_monitor_thread(scope, (1,), name="Fast", main_sleep=60.0, data_wait_loops=100)
		dump_scpi_errors(scope)
			
		#and specifics for the other
		scope.set_edge_trigger(scope.line, level=0, slope=1, auto_trigger=1, coupling=scope.ac)
		timerange=2e-2; loops=1; plotskip=1
		scope.set_timebase(range=2e-2, reference=scope.left, delay=-2e-9)
		scope.realtime_mode(2048)
		slow_trace=scope_monitor_thread(scope, (1,2,), name="Slow", main_sleep=30.0)
	
		dump_scpi_errors(scope)
		
	finally:
		scope.clear()
		scope.write(":syst:setup "+main_setup)
		scope.write("run")
		scope.local()
		scope.unlock_completely()
	
	try:
		if 0:
			scope.lock()
			fast_trace.get_data()
			print len(fast_trace.waveform[0])
			scope.unlock()
		if 1:
			fast_trace.run_thread()
			slow_trace.run_thread()
		
			while(1):
				time.sleep(1)
				if not (fast_trace.running and slow_trace.running): break
			
	finally:
		if 1:
			fast_trace.stop_thread()
			slow_trace.stop_thread()																
			while(fast_trace.running or slow_trace.running):
				time.sleep(1.0)
		print time.asctime(), "Completely exited"
		scope.unlock_completely()
					
test1()
