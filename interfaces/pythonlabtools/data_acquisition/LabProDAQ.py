import DAQ_device
import time

class LabProDAQ(DAQ_device.DAQ_device):
	"this class must be initialized with a flavor of LabPro such as basic LabPro or LabPro_USB"
	
	channel_modes={'off':0, 'auto':1, '10volts':2, '10amps':3, 'resistance':4, 'period':5, 
			'frequency':6, 'count':7, '5volts':14, 'output_current':22}
	
	def __init__(self, labpro):
		self.lp=labpro
		self.reset_device()
		
	def reset_device(self):
		self.lp.reset()
		self.channel_info={}
		self.configured=0
		self.config_params=attrdict()
		
	def set_input_channel_properties(self, chan=1, range=5, offset=0, mode='auto', converter=None):
		"""for the LabPro, channel settings, only the mode parameter makes a difference.  If a converter is specified,
			it is used to convert the channel to engineering units at the end"""
		op=self.channel_modes[mode.lower()]
		self.lp.setup_channel(chan, operation=op)
		time.sleep(0.5)
		actconfig=self.lp.get_channel_setup(chan) #figure out what it really did
		self.channel_info[chan]=(mode, converter, actconfig) #remember how we set it up for conversion, if it isn't being turned off
		if not op:
			del self.channel_info[chan] #if channel ends up off, remove it from list
		pass
	
	def set_sample_properties(self, npoints=100, sampletime_seconds=1.0, averages=0, prestore_seconds=0, **kw):
		"set the block length, inter-sample time, and averageing for an acquisition. npoints=0 streams data"
		self.config_params.update(locals()) #at the entry, locals() just contains the argument list 
		self.configured=0
		
	def set_trigger_properties(self, trig_channel=0, trig_level=0.0, trig_slope=1, trig_mode='immediate', **kw):
		"set the trigger level for the device.  channel=None gives immediate triggering"
		self.config_params.update(locals()) #at the entry, locals() just contains the argument list 
		self.configured=0
	
	def start_collection(self):
		if not self.configured: #must send new config
			cp=self.config_params
			trigmode=cp.trig_mode.lower()
			
			if trigmode[:3] == 'imm':
				trigtype=0
			elif trigmode[:3]=='edg':
				trigchan=cp.trig_channel
				if cp.trig_slope == 1:
					trigtype=2
				else:
					trigtype=3
			else:
				raise ValueError, "unknown trigger type: "+trigmode
			
			if  cp.npoints:
				if cp.npoints*len(self.channel_info) > 12000:
					raise ValueError, "more than 12000 samples requested, not allowed on LabPro"
				prestore=int(100.0*cp.prestore_seconds/(cp.sampletime_seconds*cp.npoints))
				if prestore > 100:
					raise ValueError, "prestore of more than full acquisition time"
				if cp.sampletime_seconds<0.0001:
					fastmode=1
				else:
					fastmode=0
				npoints=cp.npoints
			else:
				npoints=-1 #this puts Labpro in realtime mode
			
			self.labpro_setup_data=locals().copy() #for debugging

			self.lp.binary_mode()
									
			self.lp.setup_data_collection(samptime=cp.sampletime_seconds, numpoints=npoints, 
				trigtype=trigtype, trigchan=cp.trig_channel, trigthresh=cp.trig_level, 
				prestore=prestore, rectime=0, filter=0, fastmode=fastmode)
			
			self.configured=1 #flag that this is done so it doesn't get repeated when nothing is changed
		else:
			self.lp.collect_data_again()
	
	def get_sample_now(self,wait_time_sec=0.5):
		self.start_collection()
		time.sleep(wait_time_sec)
		cp=self.config_params
		pointcount=cp.npoints
		results={}
		for chan, info in self.channel_info.iteritems():
			newdata=self.lp.get_data_binary(chan=chan, points=pointcount)
			results[chan]=newdata
		
		return results

if __name__=='__main__':
	import LabPro_USB
	
	def test():
		lp=LabPro_USB.LabPro_USB()
		lp.reset()
		try:
			lpDAQ=LabProDAQ(lp)
			lpDAQ.set_input_channel_properties(1) #channel 1 default configuration, on
			lpDAQ.set_sample_properties(npoints=100, sampletime_seconds=0.01, prestore_seconds=.005)
			lpDAQ.set_trigger_properties(trig_mode='immediate', trig_slope=-1)
			
			print lpDAQ.get_sample_now()
			print lpDAQ.get_sample_now()
			print lpDAQ.get_sample_now()
			
			print lpDAQ.channel_info
			
		finally:
			lp.reset()
			lp.close()
		
	for i in range(100):
		test()
	
