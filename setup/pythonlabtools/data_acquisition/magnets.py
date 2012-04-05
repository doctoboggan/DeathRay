"A group of magnets, with lots of error checking"
_rcsid="$Id: magnets.py 323 2011-04-06 19:10:03Z marcus $"

#use the global data cache
from tagged_data import system_data

import time
import math
import threading
from control_subsystem import subsystem
from power_supplies import *

from alarm_system import *
import alarm_system

class magnet_system(subsystem):
	"a container class to talk to various magnet supplies"

	Thread=alarm_system.critical_thread
	
	alarm_minimum_interval=3600.0
	
	def  __init__(self):
		subsystem.__init__(self, name="Magnet Control System", shortname='magnets')
		self.magnet_supplies=[]
		self.magnet_channels=[]
		self.keep_running=1
		self.monitor_thread=self.Thread(target=self.monitor_thread, name="magnet monitor")
		self.monitor_thread.setDaemon(1) #make it daemonic, in case we forget to close it (leave off so it is easy to detect bad closing!)
		self.monitor_thread.start()
		self.current_info=[]
			
		self.alarms={}
	
	def add_supply(self, magnet_supply):
		if magnet_supply not in self.magnet_supplies:
			#magnet supplies may be added multiple times, and ignored, to make multi-channel supplies easy
			self.magnet_supplies.append(magnet_supply)
	
	def add_channel(self, magnet_channel):
		"""Add a magnet channel.
		It is polite to add channels grouped on a single supply consecutively,
		since this results in less re-reading of magnet supplies during monitoring."""
		assert magnet_channel not in self.magnet_channels, "Only add a magnet once!"
		self.magnet_channels.append(magnet_channel)
		self.alarms[magnet_channel.name]=(0,0)
		
	def monitor_thread(self):
		while self.keep_running:
			time.sleep(1.0) #take a breath between scans, so we don't thrash if there are no supplies
			current_magnets=tuple(self.magnet_channels) #freeze a copy
			current_info=[]
			for chan in current_magnets:
				if not self.keep_running: break #quit early if we are stopped
				#return set, rdbk, volts, scaled_error, error_summary, tolerance_worry, tolerance_big_trouble, resistance, resistance_low, resistance_high
				info=chan.read_magnet_info(())
				current_info.append((chan.name, info))
				fatal=info["tolerance_big_trouble"]
				if info["error_summary"]:
					when, howbig=self.alarms[chan.name]
					errordescription='\n'.join([i+": "+str(info[i]) for i in info.keys()])
					if (howbig==0 and fatal) or when<(time.time()-self.alarm_minimum_interval):
						#log right now if error has escalated, otherwise log at most once an hour
						self.log_error("Magnet out of tolerance: "+chan.name+"\n"+errordescription)
						self.alarms[chan.name]=(time.time(), fatal)
					
				if fatal:
					serious_alarm("magnet "+chan.name+" way off!\n"+errordescription)
				elif info["error_summary"] and not fatal:
					warning_alarm("magnet "+chan.name+" drifting off!\n"+errordescription)
				
				time.sleep(0.25) #max update rate is 4 channels/second
				
			self.current_info=current_info

	def close(self):
		self.keep_running=0
		self.monitor_thread.join()  #let monitor quit before pulling the plug
		
		for c in self.magnet_channels:
			try:
				c.close()
			except:
				self.log_traceback("Couldn't close magnet channel: "+c.name)
		self.magnet_channels=[]
		for p in self.magnet_supplies:
			try:
				p.close()
			except:
				self.log_traceback("Couldn't close magnet supply: "+p.name)
		self.magnet_supplies=[]

	def __del__(self):
		self.close()
	

class magnet_channel:
	"""a magnet_channel is one channel on a possibly multichannel supply, 
	combined with a polarity-switching relay, if needed. 
	It also defines all the error checking parameters for the magnet (tolerances, wiring resistance, etc.)
	It will be owned by the global magnet system, probably"""
	
	Thread=alarm_system.critical_thread
	
	def __init__(self, channel_name, supply, logical_channel=0,   
			error_tol_absolute=0.01, error_tol_relative=0.005, settling_time=2.0, 
			max_wiring_resistance=None, min_wiring_resistance=None, 
			relay_channel_name=None, max_switch_current=0.01):

		self.name=channel_name
		self.supply=supply		
		self.relay_channel_name=relay_channel_name
		system_data.define_field(channel_name, self, (), writable=1)
		self.settled_time=time.time()+settling_time #in the future, don't worry now
		self.error_tol_absolute2=error_tol_absolute*error_tol_absolute #amps**2
		self.error_tol_relative2=error_tol_relative*error_tol_relative #(delta-I/I)**2
		self.settling_time=settling_time
		self.max_wiring_resistance=max_wiring_resistance
		self.min_wiring_resistance=min_wiring_resistance
		self.channel_reader, self.channel_writer, lazy_writer, self.channel_info=supply.bind_field_info(logical_channel) #save so we can read efficiently
		
		if relay_channel_name:
			system_data[relay_channel_name]=0 #clear relays at start for positive output (by definition)

		self.max_switch_current=max_switch_current

		self.handle_switch=self.Thread(target=self.handle_switch, name=channel_name+"_switcher")
		self.switch_event=threading.Event()
		#self.handle_switch.setDaemon(1) #make it daemonic, in case we forget to close it (leave off so it is easy to detect bad closing!)
		self.keep_running=1
		self.handle_switch.start()

	def set_value(self, no_channel_info, value):
		self.settled_time=time.time()+10.0+self.settling_time #we are never settled while waiting to switch
		self.newvalue=value #update target
		self.switch_event.set() # wake up switcher thread
					
	def read_magnet_info(self, no_channel_info=None):
		"read magnet status and process error flags"
		data=system_data
		self.supply.update_data() #make sure it's fresh
		
		#read data directly, instead of going through tagged data overhead
		vset, iset, volts, rdbk = self.supply.read_field(self.channel_info)
		
		if self.relay_channel_name:
			sign=(1-2*data[self.relay_channel_name]) #+1 if relay=0, -1 if relay=1
			iset, rdbk = iset*sign, rdbk*sign

		scaled_error=(rdbk-iset)/math.sqrt(iset*iset*self.error_tol_relative2+self.error_tol_absolute2)		
		settled= (time.time() > self.settled_time)
		tolerance_worry=settled and (abs(scaled_error)>0.5)
		tolerance_big_trouble=settled and (abs(scaled_error)>1.0)
		if settled and (self.min_wiring_resistance or self.max_wiring_resistance) and (rdbk*rdbk > 25.0*self.error_tol_absolute2):
			#check resistance if current is at least 5 times absolute current tolerance 
			resistance=abs(volts/rdbk)
			resistance_low=self.min_wiring_resistance and (resistance<self.min_wiring_resistance)
			resistance_high=self.max_wiring_resistance and (resistance>self.max_wiring_resistance)
		else:
			resistance_low=resistance_high=resistance=0
		
		error_summary=tolerance_worry or tolerance_big_trouble or resistance_low or resistance_high
		return {
				"set":iset, "rdbk":rdbk, "volts":volts, 
				"scaled_error": scaled_error, 
				"error_summary": error_summary, 
				"tolerance_worry": tolerance_worry, "tolerance_big_trouble": tolerance_big_trouble, 
				"resistance": resistance, 
				"resistance_low": resistance_low, "resistance_high": resistance_high
			}
			
	def bind_field_info(self, channels):
		"return information of the type needed to access fields on this device"
		return self.read_magnet_info, self.set_value, self.set_value, ()

	def handle_switch(self):
		decay_start=0
		event=self.switch_event
		data=system_data
		supply=self.supply
		while(1):
			event.wait() #park here until someone says go
			event.clear()
			if not self.keep_running: break

			target_value=self.newvalue #latch this locally
			
			if self.relay_channel_name: #handle sign switching
				#this is designed to efficiently ignore multiple changing requests 
				#during relay switching, and only waste time
				#on the final, stable value			
				target_newsign= (target_value<0) 
				target_value=abs(target_value)
				
				if not decay_start: 
					#if we're not already in the process of decaying, check for sign changes
					currentsign=data[self.relay_channel_name] # 0 -> positive, 1 -> negative
					#now, see if the relay has to switch, and if so start the timing sequence
					if (target_newsign != currentsign):
						self.settled_time=time.time()+10.0 #long in the future
						self.channel_writer(self.channel_info, 0.0) #start decay on sign switch
						decay_start=1
				
				while decay_start and self.keep_running and not event.isSet() and abs(self.channel_reader(self.channel_info)[1])>self.max_switch_current:
					self.settled_time=time.time()+2.0*self.settling_time+10.0 #keep this long in the future
					event.wait(self.settling_time)
					self.update_data() #read it now
				if not self.keep_running: break
				if event.isSet(): continue #someone tweaked us again, so start over, otherwise it timed out 
				
				decay_start=0 #we're done decaying
				data[self.relay_channel_name]=target_newsign
				time.sleep(0.1) #plenty of time for a relay
							
			self.settled_time=time.time()+self.settling_time #now we are really settling
			self.channel_writer(self.channel_info, target_value) #set supply			

	def close(self):
		if self.relay_channel_name:
			self.keep_running=0
			self.switch_event.set()
			self.handle_switch.join() #let switcher bail out
			del self.handle_switch

		self.channel_writer(self.channel_info, 0.0) #set supply

