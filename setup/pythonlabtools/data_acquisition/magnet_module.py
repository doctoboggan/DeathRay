"Prototype application of the magnets.py module"
_rcsid="$Id: magnet_module.py 323 2011-04-06 19:10:03Z marcus $"

from power_supplies import current_supply, scpi_power_supply, analog_power_supply
from tagged_data import system_data as data
from magnets import magnet_channel, magnet_system
from control_subsystem import close_all_subsystems
import alarm_system

import time

class scpi_magnet_supply(alarm_system.local_vxi_11, current_supply, scpi_power_supply):
	"a scpi_magnet_supply is a physical gpib device speaking scpi containing, possibly, multiple channels"
	from device_addresses import magnet_host as my_host, magnet_portmap_proxy_host as my_portmap_proxy_host
	from device_addresses import magnet_portmap_proxy_port as my_portmap_proxy_port
	from device_addresses import magnets_using_e5810 as using_e5810
	
		
class analog_magnet(current_supply, analog_power_supply):
	"""identical to a regular analog power supply, but only sets current, and uses the FEL global data system
	keywords from analog_power_supply are:
		shortname=None, da_name="", da_transconductance=1.0, da_v0=0.0, 
		ad_current_name=None, ad_transconductance=1.0, ad_v0=0.0, 
		ad_voltage_name=None)
	"""	
	update_time_delta=0.0 #update timing handled elsewhere
	
	def  __init__(self, name, **keywords):
		analog_power_supply.__init__(self, data_system=data, name=name, **keywords)

class hp_magnet_supply(scpi_magnet_supply):
	idn_head="HEWLETT-PACKARD,E1406" #wrong head!
	channel_init_string=":CURR 0;:VOLT MAX"

class fluke_magnet_supply(scpi_magnet_supply):
	idn_head="HEWLETT-PACKARD,E1406" #wrong head!
	channel_init_string=":CURR 0;:VOLT MAX;:CURR:AUTO ON"
	channel_select_string=":INST:NSEL %d"
	physical_channels=(1,2,3)

class kepco_magnet_supply(scpi_magnet_supply):
	idn_head="HEWLETT-PACKARD,E1406" #wrong head!
	channel_init_string=":VOLT MAX;:CURR:AUTO ON"
	physical_channels=(1,2,3,4,5,6,7,8)

if __name__=="__main__":
	import alarm_system
	import vxi_crate_module
	from vxi_crate_module import *
	

	scan_adc.run_thread()
	dio.run_thread()
	thermo.run_thread()
	glue_board.run_thread()

	data.reset() #may as well start completely clean for this experiment
	
	#this is a singleton global magnet system
	class mymagsys(magnet_system):
		alarm_minimum_interval=1000.0

	serious_alarm_happened=0
	
	def handle_alarm(level):
		global serious_alarm_happened
		if isinstance(level, alarm_system.SeriousSystemError):
			serious_alarm_happened=1
		#print "********ALARM******** "+str(level)
	
	if not scan_adc.get_monitor_thread().isAlive():
		#this is for interactive testing, in case I have killed the thread
		scan_adc.run_thread()
		
	alarm_system.start_critical_thread_monitor()
	
	magnets=mymagsys()

	try:
		data.define_field("magnet_1_setpoint", dac1, 0, writable=1)
		data.define_field("magnet_1_current_rdbk", scan_adc, 2, writable=0)
		data.define_field("magnet_1_voltage_rdbk", scan_adc, 3, writable=0)
		data.define_field("magnet_1_relay", dio, (2,1), writable=1)
		data.define_field("adc_low_4", scan_adc,(0,1,2,3), writable=0)

		mymag=analog_magnet("magnet_1", da_name="magnet_1_setpoint",
			ad_voltage_name="magnet_1_voltage_rdbk", 
			ad_current_name="magnet_1_current_rdbk",
			ad_transconductance=0.99)
		
		magnets.add_supply(mymag)

		mymagchan=magnet_channel("magnet_1", mymag,  
				error_tol_absolute=0.03, error_tol_relative=0.005, settling_time=1, 
				max_wiring_resistance=None, min_wiring_resistance=None, 
				relay_channel_name="magnet_1_relay", max_switch_current=0.01)

		magnets.add_channel(mymagchan)

		data.define_field("mag1", mymagchan, 0, writable=1)

		data.mag1=0.0 #start rationally before we enable alarms
		
		alarm_system.register_warning_alarm_handler(handle_alarm)
		print "\n\n****Start"
		for i in range(-2,10):
			if serious_alarm_happened: break
			data.mag1=float(i)
			time.sleep(2)
			#print data.magnet_1_setpoint, data.magnet_1_relay, data.mag1
			#print data.adc_low_4
			if i==20:
				scan_adc.stop_thread() #create trouble
			if i==2:
				del scan_adc.loop_count #create trouble
				#del magnets.magnet_channels
	finally:
		alarm_system.clear_all_alarms() #dangerous in real code, OK for testing or shutting down
		alarm_system.stop_critical_thread_monitor() #do this so shutting down doesn't cause a panic!
		#magnets.close() 
		close_all_subsystems()
		time.sleep(2)
		

		