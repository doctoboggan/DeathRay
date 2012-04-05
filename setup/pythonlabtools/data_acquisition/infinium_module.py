"Some protocol for Agilent 548xx scopes"
_rcsid="$Id: infinium_module.py 323 2011-04-06 19:10:03Z marcus $"

from vxi_11_scopes import agilentscope

class infinium_54825a(agilentscope):
	idn_head="HEWLETT-PACKARD,54825A"
	default_timeout=4000
	default_lock_timeout=1000

	preamble_items=(("format", int), ("type", int), ("POINTS", int), ("SHOT_COUNT", int),
			("XINC", float), ("XORG", float), ("XREF", int), 
			("YINC", float), ("YORG", float), ("YREF", int),
			("coupling", int), ("xdisprange",float), ("xdisporg", float), 
			("ydisprange", float), ("ydisporg", float), ("date", str), ("time", str), ("model", str),
			("acqmode", int), ("complete", int), ("xunits", int), ("yunits", int), ("bandpass-upper", float), ("bandpass-lower", float) )

	def get_current_data(self, chan_list, max_points=None):

		if max_points is None:
			count=None
		else:
			count=500+2*max_points
		channels=[]
		preambles=[]
		for i in chan_list:
			#print self.transaction(":wav:sour chan%d;:wav:type?" % i)[2]
			err, reason, data = self.transaction(":syst:head off;:wav:sour chan%d;form word;byt msbf;pre?;data?" %i, count=count)
			if not err:
				curve=data.find(";#")
				self.parse_preamble(data[:curve])
				wave, rest  =self.handle_binary_block(data[curve+1:])
				channels.append( self.parse_binary_data(wave))
				preambles.append([self.preamble])
			else:
				self.saved_error=err
				self.saved_reason=reason
				channels.append(None)
		
		self.preambles=preambles
		return channels

	def average_mode(self, averages):
		self.write(""":acquire:mode etime;average 1;count %d;points auto;complete 100""" % averages)

	def realtime_mode(self, length):
		self.write(""":acquire:mode rtime;average 0;points %d;complete 100""" % length)
	
	def set_channel(self, chan, range, offset=0, coupling=agilentscope.dc, impedance=None, atten=1.0, lowpass=None):
		if impedance==50 and coupling==self.dc:
			coupling="dc50"
		if  lowpass:
			lp=1
		else:
			lp=0
		setup=":chan%d:probe %f;range %.0e;offs %.2e;inp %s;bwl %d;" % (chan,atten, range, offset,coupling,lp)
		self.write(setup)

	def set_edge_trigger(self, source, level=0, slope=1,coupling=agilentscope.dc, auto_trigger=1):
		if not(source==self.line or source==self.aux or source==self.ext):
			source="chan%d"%source
		
		if slope>0:
			slope="pos"
		else:
			slope="neg"
			
		if auto_trigger:
			mode="auto"
		else:
			mode="trig"

		if source != self.line:
			levelstr="level %s,%.2e;edge:source %s;coup %s;slop %s;:trig:sweep %s"%(source, level, source, coupling, slope, mode)
		else:
			 levelstr="edge:source line"
		
		s="trig:mode edge;%s;"%(levelstr)
		self.write(s)

	def parse_binary_data(self, data):

		if self.preamble["type"]==2: #fix shot count on averaged data
			shots=self.preamble["SHOT_COUNT"]
			self.preamble["SHOT_COUNT"]=1
				
		result=agilentscope.parse_binary_data(self, data)

		if self.preamble["type"]==2: #fix shot count on averaged data
			self.preamble["SHOT_COUNT"]=shots
		
		return result

if 1:	
	infinium=infinium_54825a(host="129.59.235.144", 
		 device="inst0",  timeout=4000, device_name="infinium", raise_on_err=1)
else:
	infinium=infinium_emulated(host="129.59.235.144",  portmap_proxy_host='127.0.0.1', portmap_proxy_port=1111, 
			 device="inst0",  timeout=4000, device_name="infinium", raise_on_err=1)

if __name__=="__main__":
	try:
		print infinium.idn
		#infinium.maxRecvSize=1024
		
		for i in range(10):
			err, reason, s=infinium.transaction(":syst:setup?")
			print i, len(s)
	finally:	
		infinium.close()	
