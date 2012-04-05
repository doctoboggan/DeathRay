"Control system global alarm handlers... make it hard for failures not to get noticed."
_rcsid="$Id: alarm_system.py 323 2011-04-06 19:10:03Z marcus $"

import weakref
import threading
import time
from control_subsystem import subsystem
from vxi_11 import vxi_11_connection, device_thread
from gpib_utilities import gpib_device

__all__=["register_serious_alarm_handler", "register_fatal_alarm_handler", "register_warning_alarm_handler",
		"clear_all_alarms", "fatal_alarm", "serious_alarm", "warning_alarm",
		"start_critical_thread_monitor", "stop_critical_thread_monitor",
		"critical_thread", "local_vxi_11" ]
		
		
class SystemWarning(Exception):
	"A system warning means incipient trouble, maybe run machine gently"
	pass
	
class SeriousSystemError(SystemWarning):
	"serious alarms mean the system cannot continue to run safely, but the problem may be correctable"
	pass

class FatalSystemError(SeriousSystemError):
	"fatal alarms means a sufficiently terrible thing has happened that the software is shutting the machine down and quitting"
	pass


_alarm_handlers=[]
		
def register_serious_alarm_handler(handler):
	_alarm_handlers.append((SeriousSystemError, weakref.ref(handler)))
def register_fatal_alarm_handler(handler):
	_alarm_handlers.append((FatalSystemError, weakref.ref(handler)))
def register_warning_alarm_handler(handler):
	_alarm_handlers.append((SystemWarning, weakref.ref(handler)))

alarm_subsystem=subsystem(name="Alarm Handler", shortname="*****ALARM*****")

def clear_all_alarms():
	"this is very dangerous to do, and should only happen in interactive test code"
	global _alarm_handlers
	_alarm_handlers=[] #Zap!
	
def _alarm(level):
	#alarm_subsystem.log_error("Alarm raised: \n"+str(level))
	for minlevel, wr in list(_alarm_handlers): #use frozen copy
		if  isinstance(level, minlevel):
			ref=wr()
			if ref:
				try:
					ref(level)
				except:
					alarm_subsystem.log_traceback("Software failure: Alarm handler failed. Shutting down.")
					_alarm_handlers.remove((minlevel, wr)) #and remove this handler
					#and escalate since an alarm failure is a disaster
					fatal_alarm("Software failure, shutting down... see log file")
					
def fatal_alarm(string="Big ouch!"):
	_alarm(FatalSystemError("Fatal Error: "+string))
def serious_alarm(string="ouch"):
	_alarm(SeriousSystemError("Serious Error: "+string))
def warning_alarm(string="oops"):
	_alarm(SystemWarning("Warning: "+string))

_threadmonitor_keep_running=0
			
def start_critical_thread_monitor():
	global _threadmonitor_keep_running
	_threadmonitor_keep_running=1

def stop_critical_thread_monitor():
	global _threadmonitor_keep_running
	_threadmonitor_keep_running=0

class critical_thread(threading.Thread):
	
	def start(self):
		#self.setDaemon(1)
		threading.Thread.start(self)
		
	def run(self):
		try:
			threading.Thread.run(self)
		except:
			alarm_subsystem.log_traceback("Uncaught exception in critical thread: "+self.getName())

		if _threadmonitor_keep_running: #we are still critical!
			alarm_subsystem.log_error("A Critical thread has died: "+self.getName())
			fatal_alarm("A Critical thread has died: "+self.getName())

class local_vxi_11(subsystem, vxi_11_connection, device_thread, gpib_device):
	"a subclass of vxi_11_connection implementing any local requirements"
	using_e5810=1 #set this if device is on Agilent E5810 bridge, which doesn't abort correctly

	max_message_wait=1.0 #seconds
	device_loop_sleep=1.0
	default_lock_timeout=2000
	default_timeout=2000
	Thread=critical_thread #all of these threads are critical
	
	def abort(self):
		if self.using_e5810:
			self.log_info('e5810 Abort ignored')
		else:
			vxi_11.vxi_11_connection.abort(self)

	def init(self, sicl_device, name, shortname=None):
		subsystem.__init__(self, name, shortname)
		vxi_11_connection.__init__(
			self, host=self.my_host, portmap_proxy_host=self.my_portmap_proxy_host, portmap_proxy_port=self.my_portmap_proxy_port,
			device=sicl_device, timeout=self.default_timeout, device_name=name, raise_on_err=1)
		device_thread.__init__(self, self, main_sleep=self.device_loop_sleep, name=name)
		

