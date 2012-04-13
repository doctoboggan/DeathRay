"Sample code to  stress an vxi_11_connection_multiplexer"
_rcsid="$Id: test_mux.py 323 2011-04-06 19:10:03Z marcus $"

import vxi_11 
import vxi_11_connection_mux
import dg600_program
import tagged_data
import time
import traceback
import vxi_crate_devices
from vxi_crate_devices import vxi_crate_device
import threading

class system_device(vxi_crate_device):
	"a subsystem for logging top-level error messages"
	idn="Main Control System"
	
	def reconnect(self):
		pass #no real device to connect to, overriding reconnect fixes this

	def  __init__(self):	
		vxi_crate_device.init(self,0,"Main System","MainSystem")

mainsystem=system_device()

def test():
	try:
		try:
			threadlist=[]
			threadlist.append(scan_adc)
			threadlist.append(dio)
			threadlist.append(thermo)
			threadlist.append(glue_board)
			
			if lock_fail_test:
				class slow_lock(vxi_crate_devices.e1413b):
					default_lock_timeout=20000
					default_timeout=30000
					def __init__(self, slot=2):
						vxi_crate_devices.vxi_crate_device.init(self, slot, "slow-locking adc")
					
				extra_adc=slow_lock(2) #get a second instance to try to lock
				def killit():
					extra_adc.log_error("Timer triggered", extra_adc.debug_info)
					try:
						extra_adc.abort()
					except:
						extra_adc.log_exception('Abort error')
					else:
						extra_adc.log_error("Abort sent", extra_adc.debug_info)
			
				def lock_extra():
					try:
						extra_adc.lock()
					except:
						extra_adc.log_exception('Lock error: ')
					extra_adc.unlock_completely()
				
				t=threading.Timer(10., killit)
				lockit=threading.Thread(target=lock_extra, name="Lock attempt")
							
			def end_everything():
				global keep_running
				keep_running=0
				mainsystem.log_info("********Sent termination!")

			ender=threading.Timer(120.0, end_everything)
			
			dg600_program.last_kly_sub=-1 #force complete rewrite
			
			clock, closest=dg600_program.setup_clock(10, 10)
			#pattern.log_info("Clock setup:\n"+clock)
			pattern.lock()
			pattern.send(clock)
			pattern.unlock(60.0) #ok, try to hold us for one minute
			pattern.log_info(pattern.transaction("ERROR?")[2])

			for i in threadlist:
				i.run_thread()
				time.sleep(0.25) #offset thread starts
				
			if lock_fail_test:	
				lockit.start()
				t.start()
				
			ender.start()
			
			starttime=time.time()
			myloops=0
			
			
			while(keep_running):
				myloops+=1
				data["dq_voltage"]=1.23
				time.sleep(0.5)
				data["hv_setpoint"]=5.1
				time.sleep(0.5)
				if not(myloops & 7):
					
					muxdata='MUX:\n'
					muxhost=mux.hosts[mux.hosts.keys()[0]]
					muxhost[mux.host_lock].acquire()
					try:
						muxactive=muxhost[mux.active_connections]
						for i in muxactive:
							state, timer, prio=muxactive[i]
							muxdata+="%12s: %4d %6.1f %4d\n"%(i, state, timer-time.time(), prio)
					finally:
						muxhost[mux.host_lock].release()
					mainsystem.log_info(muxdata)
	
					pattern.lock() #nest call in an extra lock, so we control the unlock
					pattern.send(clock) #stress test this
					pattern.unlock(-10) #unlock and mark very stale
					
					scan_adc.log_info("Loops "+str(scan_adc.loop_count)+" data: "+str(data["analog_sample"]))
					thermo.log_info(thermo.loop_count)
					glue_board.log_info("%d %02x"%(glue_board.loop_count, data["glue"]))
					dio.log_info("%d %024x %024x" % (dio.loop_count, data.dio96, dio.unstable))
				data.cameras=scan_adc.loop_count&255
				data["glue"]=scan_adc.loop_count&255
				
				summary=1
				for i in threadlist:
					summary = summary and i.running
				if not summary: break
		except:
			mainsystem.log_traceback("uncaught problem at top level: "	)							
	finally:
		try:
			ender.cancel() #make sure timer gives up!
		except:
			mainsystem.log_exception("Couldn't cancel ender")
			
		for i in threadlist:
			try:
				i.stop_thread()
			except:
				i.log_exception("Couldn't stop!")
		running=1
		while(running):
			time.sleep(1.0)
			running=0
			for i in threadlist:
				running = running or i.running
						
		if lock_fail_test:	extra_adc.unlock_completely()

mux=vxi_11_connection_mux.connection_mux()
data=tagged_data.tagged_data_system()
	
try:
	from vxi_crate_module import * #this module is safe for this
	from device_addresses import crate_host as vxi_host_address
		
	data.define_field("cameras",dio, (35,8),1)
	data.define_field("valves", dio, (8,8),1)
	data.define_field("system_status", dio, (16,8),0)
	data.define_field("dio96", dio, (0,96),1)
	data.define_field("analog_sample", scan_adc, [0,1,2,3])
	data.define_field("glue",glue_board, (0,8),1)
	data.define_field("dq_voltage", dac1, 0,1)
	data.define_field("hv_setpoint", dac2, 1, 1)
	
	mux.add_host(vxi_host_address, max_connections=15)

	mux["scanner"]=scan_adc
	mux["dio96"]=dio
	mux["thermometers"]=thermo
	mux["video_mux"]=video
	mux["dac1"]=dac1
	mux["dac2"]=dac2
	mux["dg600"]=pattern
	mux["glue"]=glue_board


	scan_adc.run_thread()
	dio.run_thread()
	thermo.run_thread()
	glue_board.run_thread()

	keep_running=1
	lock_fail_test=0
	test()

except:
	mainsystem.log_traceback()

mux.release_all()
mainsystem.log_info("Completely exited")
time.sleep(0.1) #let any running threads finish on Mac
		
		
	
		
