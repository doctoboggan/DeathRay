"A basic wrapper for some of the more useful external functionality for the Hewlett-Packard / Agilent 8753E-class Network Analyzers"
_rcsid="$Id: hp_8753e_network_analyzer.py 323 2011-04-06 19:10:03Z marcus $"

from vxi_11 import vxi_11_connection
import struct
import Numeric
import time
import array

_bigendian=(struct.unpack('H','\00\01')[0] == 1)

class HP8753_Error(Exception):
	pass

class hp_8753e(vxi_11_connection):
	
	idn_head="HEWLETT PACKARD,8753E" 	
				
	default_lock_timeout=10000

	def check_errors(self):
		errorlist=[]
		while(1):
			err, stat=self.read_status_byte()
			has_error=stat & 8
			if not has_error: break
			err, reason, result=self.transaction("OUTPERRO;\n")
			s1, s2 = result.strip().split(',', 1)
			errorlist+=[(int(s1),s2[1:-1])]
		if errorlist:
			raise HP8753_Error(errorlist)
		
	def setup_simple_sweep(self, min=1e4, max=3e9, count=1601, sweeptype='lin', power=10.0):
		if sweeptype=='lin': #when switching frequencies, always disable transform mode and corrections
			s="TIMDTRAN OFF;CORR OFF;LINFREQ;"
		else:
			s="TIMDTRAN OFF;CORR OFF;LOGFREQ;"
		s+="POIN %d;STAR %.8e Hz;STOP %.8e Hz;POWE %.2f"%(count, min, max, power)
		self.lock()
		try:
			self.write(s)
			self.check_errors()
		finally:
			self.unlock()
	
	def enable_transform(self, tmin=-1e-8, tmax=1e-8, mode='impulse'):
		if mode=='impulse':
			s='LOWPIMPU'
		elif mode=='step':
			s='LOWPSTEP'
		elif mode=='bandpass':
			s='BANDPASS'
		else:
			raise HP8753_Error("Bad transform mode: "+mode)
		
		self.write("SETF;TIMDTRAN ON;%s;REAL;STAR %.8e;STOP %.8e;"%(s, tmin, tmax))
		self.check_errors() #make sure it worked
	
	def disable_transform(self):
		self.write("TIMDTRAN OFF;")

	def recall_setup(self, setup_reg):
		self.write("RECAREG%02d;" % setup_reg)
		self.check_errors()
	
	def get_converted_data(self, command):
		"return array of  data from active channel as a native-endian double array"
		err, reason, result=self.transaction("FORM3;"+command)
		if result[:2] != "#A":
			raise HP8753_Error("Bad data string returned: "+repr(result))
		count=struct.unpack(">H",result[2:4])[0]
		if len(result) != count+4:
			raise HP8753_Error("Bad data string length:  expected %d, got %d"%(count+4, len(result)))
		values=array.array('d')
		values.fromstring(result[4:])
		if not _bigendian:
			values.byteswap()		
		return values
		
	def get_complex_data(self):
		"return array of complex data from active channel"
		values=self.get_converted_data("OUTPDATF;")
		cv=Numeric.fromstring(values.tostring(), Numeric.Complex64)
		return cv

	def get_real_display_data(self):
		"return array of real data from active channel (assuming channel is a real format)"
		values=self.get_converted_data("OUTPFORF;")
		cv=Numeric.fromstring(values.tostring(), Numeric.Float64)
		return cv

	def get_complex_display_data(self):
		"return array of complex data from active channel"
		values=self.get_converted_data("OUTPFORF;")
		cv=Numeric.fromstring(values.tostring(), Numeric.Complex64)
		return cv

	def generate_xaxis_data(self):
		"figure out the correct x axis for the current data set"
		self.lock()
		try:
			info=[self.transaction(command)[2] for command in ["POIN?;","STAR?;","STOP?;","LINFREQ?;","LOGFREQ?;","TIMDTRAN?;"] ]
		finally:
			self.unlock()
		linf, logf, transform = [int(info[i]) for i in [3,4,5]] 
		fpoints, start, stop = [float(info[i]) for i in [0, 1,2]]
		points=int(fpoints)
		basearray=Numeric.array(range(points), Numeric.Float)*(1.0/(points-1)) #array on [0,1]
		
		if transform or linf:
			return basearray*(stop-start)+start
		elif logf:
			return Numeric.exp(basearray*Numeric.log(stop/start))*start
		else:
			raise HP8753_Error("Unknown x-axis mode... not linear, log, or time, and I don't handle segments yet")
	
	def release_to_local(self):
		self.write("CONT;") #return to continuous trigger
		self.local()
	
	def opc_setup(self):
		self.write("CLES;ESE 01;OPC;")
	
	def opc_wait(self, wait_loop_time=1.0, max_wait_time=10.0):
		opcstat=0
		starttime=time.time()
 		while(not opcstat and (time.time() - starttime) < max_wait_time):
			time.sleep(wait_loop_time)
			opcstat=self.read_status_byte()[1] & 0x20	
		
		if not opcstat:
			raise 	HP8753_Error("Data taking not completed before timeout")
		
	def average_and_wait(self, averages=1, wait_loop_time=1.0, max_wait_time=None):
		if max_wait_time is None:
			max_wait_time=averages #assume typical 1-second sweep time
		self.opc_setup()
		self.write("AVERFACT %d;NUMG %d;" % (averages, averages))
		self.opc_wait(wait_loop_time, max_wait_time)
	
if __name__=='__main__':		
	analyzer=hp_8753e(host="129.59.235.99", 
		 device="gpib0,3",  timeout=4000, device_name="network_analyzer", raise_on_err=1)
	print analyzer.idn	
	analyzer.lock()
	try:
		analyzer.setup_simple_sweep(min=1e7,max=6e9, sweeptype='lin', power=10.0)
		analyzer.write("S11;")
		analyzer.enable_transform(tmin=-10e-9, tmax=300e-9, mode='impulse')
		analyzer.check_errors()
		timedata=analyzer.get_real_display_data()
		xaxis=analyzer.generate_xaxis_data()*1e9
		
		analyzer.disable_transform()
		spectrum=analyzer.get_complex_data()
		freqaxis=analyzer.generate_xaxis_data()
		
	finally:
		analyzer.unlock()
		del analyzer
	

