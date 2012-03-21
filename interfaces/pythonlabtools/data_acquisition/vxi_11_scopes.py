"Some simple oscilloscope drivers built around an abstract oscilloscope"
_rcsid="$Id: vxi_11_scopes.py 323 2011-04-06 19:10:03Z marcus $"

from vxi_11 import vxi_11_connection
import struct
import time

try:
	#prefer numpy over Numeric since it knows how to handle Numeric arrays, too (maybe, but not reliably!)
	import numpy as _numeric 
	_numeric_float=_numeric.float64

except:
	import Numeric as _numeric
	_numeric_float=_numeric.Float64

class oscilloscope(vxi_11_connection):
	
	dc="dc"
	ac="ac"
	line="line"
	aux="aux"
	ext="ext"
	left="left"
	center="center"
	right="right"
	
	def handle_binary_block(self, data):
		assert data[0]=="#", "Bad binary data block" + data[:20]
		cl=int(data[1])
		len=int(data[2:2+cl])
		return data[2+cl:2+cl+len], data[2+cl+len:]

	def parse_preamble(self, data):
		self.preamble["RAW_PREAMBLE"]=data
		
		for name, normal_name, data_type in self.preamble_items:
			start=data.find(name)+len(name)
			end=data[start:].find(self.preamble_delimiter)+start
			result=data_type(data[start:end])
			self.preamble[normal_name]=result
		return self.preamble
		
	def parse_binary_data(self, data):
		bytes=self.preamble["BYT_NR"]
		count=self.preamble["POINTS"]*self.preamble["SHOT_COUNT"]
		if bytes==1:
			bdata=struct.unpack("%db"%count, data)
		elif bytes==2:
			bdata=struct.unpack(">%dh"%count, data)
		elif bytes==4:
			bdata=struct.unpack(">%di"%count, data)		
		
		#print bdata[:100]
		fdata=(_numeric.array(bdata,_numeric_float)-self.preamble["YREF"])*self.preamble["YINC"]+self.preamble["YORG"]
		
		self.xaxis=(_numeric.array(range(len(fdata)),_numeric_float)-self.preamble["XREF"])*self.preamble["XINC"]+self.preamble["XORG"]
		return fdata
	
	def post_init(self):
		self.preamble={}
	
			
class tekscope(oscilloscope):
	idn_head="TEKTRONIX"
	preamble_items=( ("BYT_NR", "BYT_NR", int),("BIT_NR", "BIT_NR", int), ("XINCR", "XINC", float), 
		("XZERO", "XORG", float), ("PT_OFF", "XREF", int),
		("YMULT", "YINC", float), ("YOFF", "YREF", float), ("YZERO", "YORG", float),
		("WFID ", "INFO", str), ("NR_PT", "POINTS", int))
	preamble_delimiter=";"

	def get_current_data(self, max_points=None):
		if max_points is None:
			count=None
		else:
			count=500+4*max_points
			
		err, reason, data = self.transaction("wfmo:byt_nr 2;:data:enc ribinary;:wavf?",  count=count)
		if not err:
			curve=data.find(":CURVE ")
			self.parse_preamble(data[:curve])
			self.preamble["SHOT_COUNT"]=1
			wave, rest  =self.handle_binary_block(data[curve+7:])
			return self.parse_binary_data(wave)
		else:
			self.saved_error=err
			self.saved_reason=reason
			return None

class agilentscope(oscilloscope):
	idn_head="AGILENT"
	preamble_items=(("format", int), ("type", int), ("POINTS", int), ("SHOT_COUNT", int),
			("XINC", float), ("XORG", float), ("XREF", int), 
			("YINC", float), ("YORG", float), ("YREF", int) )

	def parse_preamble(self, data):
		self.preamble["RAW_PREAMBLE"]=data
		preamble=map(None, self.preamble_items, data.split(","))
		for info, item in preamble:
			name, data_type=info
			x=data_type(item)		
			self.preamble[name]=x
		if self.preamble["format"]==2:
			self.preamble["BYT_NR"]=2
		else:
			raise "Unkown data type returned "+self.device_name+" "+data
		return self.preamble

	def get_current_data(self, chan_list, max_points=None):

		if max_points is None:
			count=None
		else:
			count=500+2*max_points
		channels=[]
		for i in chan_list:
			#print self.transaction(":wav:sour chan%d;:wav:type?" % i)[2]
			err, reason, data = self.transaction("syst:head off;:wav:sour chan%d;:wav:form word;:wav:pre?;:wav:data?" %i, count=count)
			if not err:
				curve=data.find(";#")
				self.parse_preamble(data[:curve])
				wave, rest  =self.handle_binary_block(data[curve+1:])
				channels.append( self.parse_binary_data(wave))
			else:
				self.saved_error=err
				self.saved_reason=reason
				channels.append(None)
		return channels

	def average_mode(self, averages):
		self.write(""":tim:sample rep;:acquire:type average;points 500;count %d;complete 100;""" % averages)

	def realtime_mode(self, length):
		self.write(""":tim:sample real;:acquire:type norm;points %d;count 1;complete 100;""" %length)

	def set_timebase(self, range, delay=0.0, reference=oscilloscope.center):
		self.write(":tim:range %.0e;ref %s;del %.2e;"%(range, reference, delay))

	def set_channel(self, chan, range, offset=0, coupling=oscilloscope.dc, impedance=None, atten=1.0, lowpass=None):
		if impedance==50 and coupling==self.dc:
			coupling="dcfifty"
		if  lowpass:
			lp=1
		else:
			lp=0
		setup=":chan%d:probe %f;range %.0e;offs %.2e;coup %s;hfr %d;" % (chan,atten, range, offset,coupling,lp)
		self.write(setup)

	def set_edge_trigger(self, source, level=0, slope=1,coupling=oscilloscope.dc, auto_trigger=1):
					
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

		self.write("trig:sour %s;slop %s;level %.2e;coup %s;:tim:mode %s"%(source,slope,level,coupling, mode))

	def digitize(self, chan_list=(1,)):
		self.transaction(":stop;*esr?;*ese 1;*cls;") #_must_ have the *esr? to clear old status bits!
		cl=((len(chan_list)*"chan%d,")%chan_list)[:-1] #drop the final comma from a channel list
		self.write(":dig "+cl+";*opc")
	
	def wait_for_done(self, sleep=1.0, max_loops=None):
		done=0
		loops=0
		while not done and (max_loops is None or loops<max_loops):
			done=self.read_status_byte()[1]
			#print "%02x"%done
			done = done & 32
			if not done: time.sleep(sleep)
			loops+=1
		
		err=0
		if max_loops is not None and loops==max_loops:
			if self.raise_on_err:
				raise UserWarning, "No data from scope %s within time limit" % self.device_name
			else:
				err=1
		return err
			
			
class tek_csa7404(tekscope):
	idn_head="TEKTRONIX,CSA7404"

class hp54542(agilentscope):
	
	default_lock_timeout=10000
	idn_head="HEWLETT-PACKARD,54542" 

	def parse_binary_data(self, data):
		bytes=self.preamble["BYT_NR"]
		shots=self.preamble["SHOT_COUNT"]
		count=self.preamble["POINTS"]*shots
		
		if self.preamble["type"]==4: #trim off the strange time-tag data before passing the buck
			tags, data = data[:8*shots],data[8*shots:]
			self.little_tags=struct.unpack(">%dd"%shots,tags)
				
		return agilentscope.parse_binary_data(self, data)
		
	def get_time_tags(self, max_grab_block=32):
		assert self.preamble["type"]==4,"No time-tagged data in scope"
		tags=[]
		
		shots=self.preamble["SHOT_COUNT"]
		
		if shots > max_grab_block:
			for grab_block in range(max_grab_block,8,-1):
				if shots%grab_block==0: break	#try to intelligently factor the transfer down as small as 10, with 9 being a bailout
			
			if grab_block==9:
				grab_block=max_grab_block #no reasonable factoring, just allow individual moves at end
		else:
			grab_block=shots
							
		com=":seq:"+grab_block*"ttag? %d;"
		
		for i in range(0, shots-(grab_block-1), grab_block):
			result=self.transaction(com%tuple(range(i+1, i+1+grab_block)))[2]
			tags+=[float(x) for x in result.split(";")]
		
		for i in range((shots//grab_block)*grab_block, shots):
			tags.append(float(self.transaction(":seq:ttag? %d"%(i+1))[2]))
	
		return _numeric.array(tags)
	
	def sequential_mode(self, npoints=100, nsegments=10):
		self.realtime_mode(512) #this is a good starting point
		self.write(":seq:npo %d;nseg %d;disp 1;"%(npoints, nsegments)) 

	def end_sequential_mode(self):
		self.write(":seq:disp 0;") 

class hp54522(hp54542):
	idn_head="HEWLETT-PACKARD,54522"
 
