"Sample VXI-11 interface with National Instruments DSTP protocol server"
_rcsid="$Id: dstp_vxi_example.py 323 2011-04-06 19:10:03Z marcus $"
import sys
import os
def addpath(path_string):
	if path_string not in sys.path:
		sys.path.append(path_string)
def add_sibling_path(sibling):
	addpath(os.path.join(os.path.dirname(__file__),sibling))
add_sibling_path("data_acquisition") #look in 'data acquisition' folder for needed routines, too
add_sibling_path("analysis") #look in 'data acquisition' folder for needed routines, too

import vxi_crate_devices as vxi
import array
import threading
import time
import tagged_data
from dstp_async import DSTPServer, UseNumericArray
try:
	import MacOS
	MacOS.SchedParams(1,1,1,0.1,0.05) #allow nullEvent handling on Classic/Carbon
except:
	MacOS=None #in case we want to check later
	
class voltmeter(vxi.scanning_voltmeter): #almost like those, just use a different range!
	idn_head="HEWLETT-PACKARD,E1326B"	
	device_loop_sleep=0.5		
	initial_config_string=":conf:volt:dc 10.0,(@100:107);"

	def get_data(self):
		vxi.scanning_voltmeter.get_data(self)
		data.volts=[v.loop_count, v.scan]

	def monitor(self):
		self.lock() #stay locked!
		vxi.scanning_voltmeter.monitor(self)
		#self.unlock() #not needed... monitor does unlock_completely 
		
s=DSTPServer()
UseNumericArray(0)
v=voltmeter(3)
try:	
	data=tagged_data.tagged_data_system()
	data.define_field("volts", s, ("DVMVolts", [1,array.array('f',[0])]), writable=1)	
	data.define_field("quit", s, ("quit", 0), writable=0)	
	sth=threading.Thread(target=s.serve, name='server')
	sth.start()
	v.run_thread()
	loops=0	
	while (not data.quit) and sth.isAlive():
		time.sleep(0.25)
		loops=loops+1	
		if loops > 100: break		
finally:
	print v.loop_count
	s.close()	
	v.close()

