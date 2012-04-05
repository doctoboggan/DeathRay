"MeasurementComputingUSB supports connections of  Measurement Computing, Inc.  USB devices"

_rcsid="$Id: MeasurementComputingUSB.py 323 2011-04-06 19:10:03Z marcus $"



class MeasurementComputingError(Exception):
	pass

class MeasurementComputingTransientError(MeasurementComputingError):
	pass

class MeasurementComputingTimeout(MeasurementComputingTransientError):
	pass
	
import array
import Numeric

import time
import sys

import os
import threading
import traceback
import struct

_bigendian=(struct.unpack('H','\00\01')[0] == 1)

from operator import isSequenceType

try:
	import fcntl #on platforms with fcntl, use it!		
	class USB_libusb_mixin:
		"mixin class  to allow operation of MCC devices via USB port using libusb pipe server"
		
		server_executable_path=os.path.join(os.path.dirname(__file__),"MeasurementComputingServer")
		
		def __init__(self, idProduct, device_index):
			self.usb_send, self.usb_recv, self.usb_err=os.popen3(self.server_executable_path+( " %d %d" % (idProduct, -device_index) ),'b',0)
			self.usb_timestamp=0
			self.__usb_read_leftovers=''
			try:
				if fcntl:
					fcntl.fcntl(self.usb_recv, fcntl.F_SETFL, os.O_NONBLOCK) #pipes must be nonblocking, if possible
					fcntl.fcntl(self.usb_err, fcntl.F_SETFL, os.O_NONBLOCK) #pipes must be nonblocking
				firstmsg=''
				badloops=0
				while badloops<10  and not firstmsg:
					time.sleep(0.5)
					try:
						firstmsg=self.usb_err.read()
					except:
						badloops+=1
					
				if badloops==10:
					raise MeasurementComputingError("cannot find or communicate with USB Server: "+str(self.server_executable_path))
				print >> sys.stderr, firstmsg
				if firstmsg.find("Found device") < 0 :
					raise MeasurementComputingError("USB Server could not connect to a MCC device at index %d" % self.device_index)  
				
				self.idProduct=int(firstmsg[firstmsg.find("ID=")+3:],16) #which flavor of MCC device?
				self.__keep_running=1
				self.status_monitor=threading.Thread(target=self.read_status, name='USB MCC status monitor')
				self.status_monitor.start()
				self.__saved_realtime_fragment=''
			except:
				self.__keep_running=0
				self.close()
				raise
				
		def check_usb_status(self):
			if not self.__keep_running or not self.status_monitor.isAlive():
				raise MeasurementComputingError("MCC USB server has died...")
					
		def read(self, maxlen=8, feature=0, send_command=1):
			"read data from USB"
			self.check_usb_status()
			
			if feature:
				maxlen=104
				if send_command: 	self.usb_send.write("FEAT %d %d\n" %(maxlen,0));
			elif send_command:
				self.usb_send.write("READ %d\n" % maxlen);
			res=''
			tries=0
			
			actmax=maxlen+16
			while len(res)<actmax and tries < 20:
				try:
					res+=self.usb_recv.read(actmax-len(res)) #packet + header 
					if len(res) < actmax:
						time.sleep(0.05)
						tries+=1
				except IOError:
					err=sys.exc_info()[1].args
					if err[0] in (11, 29, 35): #these errors are sometimes returned on a nonblocking empty read
						time.sleep(0.01)
						tries+=1
						continue #just return empty data
					else:
						raise MeasurementComputingError("USB server disconnected unexpectedly", sys.exc_info()[1].args)
			
			if not res:
				return None
					
			flag, tv_sec, tv_usec, actbytecount=struct.unpack('LLLL', res[:16])
			if actbytecount < 0:
				raise MeasurementComputingTimeout("Probably USB Timeout, error %08lx" % actbytecount )
			elif actbytecount != maxlen:
				raise MeasurementComputingError("Bad data length from MCC device:  requested %d, got %d" 
						% (maxlen, actbytecount) )
				
			#print len(res), locals()
			if flag != 0x00ffffff:
				raise MeasurementComputingError("Bad packet header from MCC device: " + ("%04x %08x %08x"%(flag, tv_sec, tv_usec)))
			self.data_timestamp=float(tv_sec)+float(tv_usec)*1e-6
				
			return res[16:]
				
	
		def read_status(self):
			"monitor the pipe server's stderr in a thread"
			while(self.__keep_running):
				try:
					res=self.usb_err.read()
					if res: print >> sys.stderr, "MCC USB message: ", res
					if res.find("****EXITED****") >= 0: break #if this thread dies, device has gone away somehow
				except IOError:
					if sys.exc_info()[1].args[0] in (11,29, 35): #this error is returned on a nonblocking empty read
						time.sleep(1) #so just wait and try again
					else:
						raise
			
		def write(self, data_array):
			self.check_usb_status()
			datastr="%d "*len(data_array) % tuple(data_array) + "\n"
			#print "writing...", data_array, datastr
			self.usb_send.write(datastr)
			time.sleep(0.01)
						
		def close(self):
			self.__keep_running=0
			try:
				self.stop()
			except:
				pass
			try:
				self.usb_send.write("****QUIT****\n")
			except:
				pass
			time.sleep(2)
			self.usb_recv.close()
			self.usb_send.close()
			self.usb_err.close()	
		
	default_server_mixin=USB_libusb_mixin
	
except ImportError:
	
	class USB_Win32_libusb_mixin:
		"mixin class for RawLabPro to allow operation of LabPro via USB port on Win32 using pipe server"
		
		server_executable_path=os.path.join(os.path.dirname(__file__),"MeasurementComputingServer.exe")
		
		def __init__(self):
			self.usb_send, self.usb_recv, self.usb_err=os.popen3(self.server_executable_path+( " %d" % -self.device_index),'b',-1)
			self.usb_timestamp=0
			self.__usb_read_leftovers=''
			try:
				firstmsg=''
				badloops=0
				while badloops<5 and (not firstmsg or not firstmsg[-1] in '\r\n'):
					try:
						firstmsg+=self.usb_err.readline(1000)
					except:
						traceback.print_exc()
						badloops+=1
					
				if badloops==5:
					raise MeasurementComputingError("cannot find or communicate with USB Server: "+str(self.server_executable_path))
				if firstmsg.find("No LabPro Found") >=0:
					raise MeasurementComputingError("USB Server could not connect to an MCC device at index %d" % self.device_index)  
	
				self.__keep_running=1
				self.status_monitor=threading.Thread(target=self.read_status, name='USB MCC status monitor')
				self.status_monitor.start()
				self.__saved_realtime_fragment=''
			except:
				self.__keep_running=0
				self.close()
				raise
				
		def check_usb_status(self):
			if not self.__keep_running or not self.status_monitor.isAlive():
				raise LabProError("LabPro USB server has died...")
				
		def high_speed_serial(self):
			"not implemented on USB"
			return 
	
		def high_speed_setup(self):
			"not implemented onUSB"
			return 
	
		def set_port_params(self):
			"not implemented on USB"
			return 
	
		def read(self, maxlen=8):
			"""read data from USB"""
			self.check_usb_status()
			res=''
			self.usb_send.write("READ %d\n", maxlen);
			
			while(len(res) < maxlen):
				while len(db)<20: #8 bytes + 8 byte timestamp + + 4 byte count + 4 byte 0xffffffff flag
	
					#a pipe is a seek-and-tallable object, so we can see how much data is there this way			
					self.usb_recv.seek(0,2)
					count=self.usb_recv.tell()
					self.usb_recv.seek(0)
					
					if count: db+=self.usb_recv.read(count)
					if not db: break #no data at all, just fall out of this inner loop
	
				if not db: break #doing uncounted read, just take data until it quits coming
								
				flag, tv_sec, tv_usec=struct.unpack('LLL', db[:12])
				if flag != 0x00ffffff:
					raise LabProError("Bad packet header from MCC device: " + ("%04x %08x %08x"%(flag, tv_sec, tv_usec)))
				self.data_timestamp=float(tv_sec)+float(tv_usec)*1e-6
				res+=db[12:20]
				db=db[20:]
				
			self.__usb_read_leftovers=db		
			return res[16:]
				
	
		def read_status(self):
			"monitor the pipe server's stderr in a thread"
			while(self.__keep_running):
				res=self.usb_err.readline(1000)
				if res: print >> sys.stderr, "MCC USB message: ", res
				if res.find("****EXITED****") >= 0: break #if this thread dies, LabPro has gone away somehow
			
		def write(self, data_array):
			self.check_usb_status()
			datastr="%d "*len(data_array) % tuple(data_array) + "\n"
			#print "writing...", data_array, datastr
			self.usb_send.write(datastr)
			time.sleep(0.02) #give a little extra time for message passing
			
		def close(self):
			time.sleep(2)
			self.__keep_running=0
			try:
				self.stop()
			except:
				pass
			try:
				self.usb_send.write("****QUIT****\n")
			except:
				pass
			time.sleep(2)
			self.usb_recv.close()
			self.usb_send.close()
			self.usb_err.close()	
	
	default_server_mixin=USB_Win32_libusb_mixin


class MCC_Device(default_server_mixin):
	
	
	BASE_CLOCK_RATE=6000000 #correct for MiniLab1008
	
	DATA_SAMPLE_SIZE = 64
	DATA_PACKET_SIZE=96
	MAX_STORED_SAMPLES=4096
	
	#command codes from MCC USBUTIL.H
	CBDIN=0
	CBDOUT=1
	CBDBITIN=2
	CBDBITOUT=3
	CBCIN32=4
	CBCINIT=5
	CBAIN=6
	CBALOADQ=7
	CBAOUT=8
	CBMEMREAD=9
	CBMEMWRITE=10
	CBBLINK=11
	CBSETID=12
	CBDCONFIG=13
	CBAINSCAN=14
	CBGETID=15
	CBAINSTOP=16
	CBRESET=17
	CBWATCHDOG=18
	CBGETERROR=19
	CBSETTRIG=20
	
	DIO_DIR_IN=1
	DIO_DIR_OUT=0

	DIO_PORTA=1
	DIO_PORTB=4
	
	USER_MEMORY_BASE=0x1800
	USER_MEMORY_SIZE=0x06ff
	
	CALIBRATION_MEMORY_BASE=0x1f00
	CALIBRATION_MEMORY_SIZE=0x00ef
			
	def __init__(self, device_index=1):
		self.device_index=device_index
		default_server_mixin.__init__(self, self.idProduct, device_index)
		self.scanning=0
		self.post_init()
		
	def post_init(self):
		pass
		
	def blink_led(self):
		self.write((self.CBBLINK,))
		time.sleep(2)
		
	def set_id(self, id_code):
		assert id_code >=0 and id_code <=255, "Bad ID code for MCC device"
		self.write((self.CBSETID,id_code))

	def get_id(self):
		self.write((self.CBGETID,))
		res=self.read()
		return ord(res[0])

	def read_memory(self, base=USER_MEMORY_BASE, count=8):
		results=''
		while(count):
			actcount=min(count,8)
			self.write((self.CBMEMREAD, base & 0xff, (base >> 8) & 0xff, actcount))
			res=self.read()
			results+=res[:actcount]
			base+=actcount
			count-=actcount
		return results

	def write_memory(self, base=USER_MEMORY_BASE, data=''):
		tc=0
		ld=len(data)
		bd=map(ord,data) #convert string to list for concatenation onto other list
		while(tc<ld):
			actcount=min(ld-tc,4)
			self.write([self.CBMEMWRITE, base & 0xff, (base >> 8) & 0xff, actcount]+bd[tc:tc+actcount])
			base+=actcount
			tc+=actcount
	
	def write_user_memory(self, data):
		assert len(data) < self.USER_MEMORY_SIZE-2, "Too much data for user memory"
		lencode=struct.pack(">H",len(data))
		self.write_memory(base=self.USER_MEMORY_BASE, data=lencode+data)
	
	def read_user_memory(self):
		lendata=self.read_memory(base=self.USER_MEMORY_BASE, count=2)
		bytes=min(struct.unpack(">H", lendata)[0], self.USER_MEMORY_SIZE-2) #protect against junk if reading uninited memory
		return self.read_memory(base=self.USER_MEMORY_BASE+2, count=bytes)

	def clear_counter(self):
		self.write((self.CBCINIT,))
	
	def read_counter(self):
		self.write((self.CBCIN32,))
		res=self.read()
		return struct.unpack('<L',res[:4])[0]
	
	def configure_digital_port(self, port=DIO_PORTA, dir=DIO_DIR_IN):
		self.write((self.CBDCONFIG, port, dir))
	
	def digital_out(self, port=DIO_PORTA, data=0):
		self.write((self.CBDOUT, port, data))

	def digital_in(self, port=DIO_PORTA):
		self.write((self.CBDIN,port))
		res=self.read()
		return ord(res[0])

class MCC_Analog_Support:
	
	GAIN1_SE=0x08
	GAIN1_DIFF=0x00
	GAIN2_DIFF=0x10
	GAIN4_DIFF=0x20
	GAIN5_DIFF=0x30
	GAIN8_DIFF=0x40
	GAIN10_DIFF=0x50
	GAIN16_DIFF=0x60
	GAIN20_DIFF=0x70
	
	TIMER_STEPS=( #prescaler and setup times for rates between given entry and next entry
			(100, 7, 0),
			(200, 6, 0),
			(400, 5, 0),
			(800, 4, 1),
			(1500, 3, 3),
			(3000, 2, 6),
			(6000, 1, 10),
			(8000, 0, 0) #no operation beyond this speed
	)
	
	
	AD_BURST_MODE=4
	AD_CONT_MODE=2
	AD_SINGLE_MODE=1
	AD_EXTTRIGGER=8
	
	AD_DIRECT_MODE=0x80
	
	TRIGGER_FLAG=0xc3
	DONE_FLAG=0xa5
		
	ad_gain_scale_dict = {
			GAIN1_SE :  (20.0/4096.0, 10.0, 1.0),
			GAIN1_DIFF: (40.0/4096.0, 20.0, 1.0),
			GAIN2_DIFF: (40.0/4096.0, 20.0, 2.0),
			GAIN4_DIFF: (40.0/4096.0, 20.0, 4.0),
			GAIN5_DIFF: (40.0/4096.0, 20.0, 5.0),
			GAIN8_DIFF: (40.0/4096.0, 20.0, 8.0),
			GAIN10_DIFF: (40.0/4096.0, 20.0, 10.0),
			GAIN16_DIFF: (40.0/4096.0, 20.0, 16.0),
			GAIN20_DIFF: (40.0/4096.0, 20.0, 20.0)
	}
			
	def counts_to_volts(self, gain, counts):
		if gain==self.GAIN1_SE:
			counts=counts*2
		else:
			counts = counts ^ 0x800 #sign bit is inverted, apparently, per MCC DLL
		scale1, offset, scale2 = self.ad_gain_scale_dict[gain]
		return ((counts*scale1)-offset)/scale2		
		
	def analog_output(self, channel, volts):
		counts=max(min(int(volts*4095.0/5.0 + 0.5), 4095),0)
		lowcounts=counts & 255
		highcounts = counts // 256
		self.write((self.CBAOUT, channel, lowcounts, highcounts))
	
	def analog_input(self, channel, gain=GAIN1_DIFF):
		self.write((self.CBAIN,channel, gain))
		retdata=self.read(8)
		if retdata:
			retval=ord(retdata[0]) + ( ord(retdata[1]) << 4 )
			return self.counts_to_volts(gain, retval)
		else:
			return None

	def setup_gain_list(self, channels, gains):
		self.channel_gain_list=zip(channels,gains)
		changain=[(self.AD_DIRECT_MODE | c & 0x07 | g )for c,g in self.channel_gain_list]
		while len(changain) >=6:
			self.write([self.CBALOADQ,6]+changain[:6])
			changain=changain[6:]
		
		if changain:
			self.write([self.CBALOADQ,len(changain)]+changain)

	def compute_timer_vals(self, Rate):
		ts=self.TIMER_STEPS
		if Rate < ts[0][0] or Rate > ts[-1][0]:
			raise MeasurementComputingError, "sample rate not in range %d-%d" % (ts[0][0], ts[-1][0])
		
		#find appropriate range in list
		lower=ts[0]
		for entry in ts[1:]:
			if entry[0] > Rate: break
			lower=entry
		
		baserate, timerPre, setupTime=lower
		timerMult= 1 << (timerPre+1)
		timerVal= int((256 - (self.BASE_CLOCK_RATE/(Rate * timerMult))) + 0.5)
	
		actRate = (float(self.BASE_CLOCK_RATE)/((256-timerVal) * timerMult))
	
		return timerPre, timerVal, setupTime, actRate
		
	def setup_analog_scan(self, channels=(0,1,2,3), sweeps=-1, rate=100, gains=GAIN2_DIFF, exttrig=0):
	
		if self.scanning:
			raise MeasurementComputingError, "cannot start new scan without stopping old one"
			
		if not isSequenceType(channels):
			channels=(channels,)
		if not isSequenceType(gains):
			gains=(gains,)*len(channels)
			
		if len(gains) != len(channels):
			raise MeasurementComputingError, \
				"gain list not compatible with channel list" +str(channels)+":"+str(gains)
		
		self.setup_gain_list(channels, gains)

		timerPre, timerVal, setupTime, actRate=self.compute_timer_vals(rate*len(channels))
		
		self.actRate=actRate
		
		if sweeps<=0: #continuous scan !
			blocking = self.DATA_SAMPLE_SIZE//len(channels)
			if len(channels)*blocking != self.DATA_SAMPLE_SIZE:
				raise MeasurementComputingError, \
					"continuous scan channel count must be submultiple of %d" % self.DATA_SAMPLE_SIZE
			tCount=self.DATA_SAMPLE_SIZE #each block is filled in continuous mode
			scanmode=self.AD_CONT_MODE
			
		elif sweeps==1: #use AD_SINGLEEXEC mode for single sweep
			tCount=len(channels)
			scanmode=self.AD_SINGLE_MODE
			
		else:
			#round block count up to next block above requested samples
			blocks=(len(channels)*sweeps+self.DATA_SAMPLE_SIZE-1)//self.DATA_SAMPLE_SIZE
			tCount=blocks*self.DATA_SAMPLE_SIZE
			if tCount>self.MAX_STORED_SAMPLES:
				raise MeasurementComputingError, \
					"burst scan sample count must be <  %d" % self.MAX_STORED_SAMPLES
			scanmode=self.AD_BURST_MODE
			self.burst_scan_count=tCount
			self.burst_scan_blocks=blocks
			
		tChigh=tCount>>8
		tClow=tCount&255
		self.write((self.CBAINSCAN, tClow, tChigh, timerVal+setupTime, timerPre, scanmode | exttrig))
		self.continuous_scan_packet_index=1
		self.got_last_packet=1
		self.last_packet_time=0.0 #long ago!
		self.packet_dt=self.DATA_SAMPLE_SIZE/actRate
		
	def get_burst_scan(self, max_trig_wait=None):
		start=time.time()
		res=''
		while(not res):
			time.sleep(0.1)
			res=self.read()
			if res:
				if res[0]==self.TRIGGER_FLAG: 
					res=''
					continue #got external trigger 	
				if res[0]==self.DONE_FLAG:
					break #got data
		
		datalist=''
		for i in range(self.burst_scan_blocks):
			res=self.read(feature=1)
			trailer=res[-8:]
			err, readaddr, writeaddr, index, junk=struct.unpack('<BHHHB', trailer)
			#print err, readaddr, writeaddr, index
			if index != i+1: #aack, packet out of sync
				raise MeasurementComputingError("scan packet out of sync... expected %d, got %d" % (i+1, index))

			datalist+=res[:-8]
		return self.unpack_scan(datalist)
	
	def get_continuous_scan_packet(self, resync=0):
		
		dt=self.packet_dt*0.8-(time.time()-self.last_packet_time)
		if dt>0.1:
			time.sleep(dt-0.09)
			
		res=self.read(feature=1, send_command=self.got_last_packet)
		if not res: 
			self.got_last_packet=0
			return None, None
		
		self.last_packet_time=time.time()
		self.got_last_packet=1
		trailer=res[-8:]
		err, readaddr, writeaddr, index, junk=struct.unpack('<BHHHB', trailer)

		#print err, readaddr, writeaddr, index
		if not resync and index != self.continuous_scan_packet_index: #aack, packet out of sync
			raise MeasurementComputingError("scan packet out of sync... expected %d, got %d" % (self.continuous_scan_packet_index, index))

		self.continuous_scan_packet_index=index+1		
		return index, self.unpack_scan(res[:-8])

	def unpack_scan(self, data):
		a=Numeric.array(data,Numeric.UnsignedInt8).astype(Numeric.Int32)
		b=Numeric.zeros(2*len(a)//3, Numeric.Int) #3 bytes hold 2 samples
		b[0::2]=a[0::3] + ( (a[1::3]  & 0xf0) << 4 )
		b[1::2]=( (a[1::3] & 0x0f) << 8 ) + a[2::3] 
		
		cl=self.channel_gain_list
		ncl=len(cl)
		fv=Numeric.zeros((len(b)//ncl, ncl), Numeric.Float)
		for i in range(ncl):
			g=cl[i][1] #get gain value for this channel
			fv[:,i]=self.counts_to_volts(g, b[i::ncl])
				
		return fv
		
	def stop_analog_scan(self):
		self.write((self.CBAINSTOP,))
		self.scanning=0


class MCC_PMD_1208LS(MCC_Analog_Support, MCC_Device):
	idProduct=0x7a #USB product id
			
class MCC_PMD_1024LS(MCC_Device):
	idProduct=0x76 #USB product id
	DIO_PORTCH=2
	DIO_PORTCL =8
	
class MCC_miniLAB_1008LS(MCC_Analog_Support, MCC_Device):
	idProduct=0x75 #USB product id
	DIO_PORTCH=2
	DIO_PORTCL =8
	DIO_AUXPORT=16

if __name__=='__main__':
	
	import cPickle
	
	mcc=MCC_PMD_1208LS()
	time.sleep(0.5)
	try:
		mcc.blink_led()
		
		oldid=mcc.get_id()
		mcc.set_id( (oldid+1) & 255 )

		try:
			id_dict=cPickle.loads(mcc.read_user_memory())
			print id_dict
		except:
			print "Memory looks trashy..."
			id_dict={'greeting': 'hello'}
			
		
		newid=mcc.get_id()
		print oldid, newid
		
		id_dict['serial']=newid
		id_dict['last_used_date']=time.asctime()
		id_dict['last_used_time']=time.time()
		
		mcc.write_user_memory(data=cPickle.dumps(id_dict) )
		
		
		if 1:
			for i in range(2):
				mcc.analog_output(0, 4.5*(i & 1))
				time.sleep(0.5)
			
			for i in range(10):
				print mcc.analog_input(0, gain=mcc.GAIN2_DIFF)
		if 1:
			mcc.setup_analog_scan(sweeps=1000, channels=(0,1), gains=mcc.GAIN2_DIFF, rate=500)
			time.sleep(2)
			print Numeric.array_str(mcc.get_burst_scan()[:100,0], precision=3, suppress_small=1, max_line_width=10000)
									
		if 1:
			mcc.setup_analog_scan(sweeps=-1, channels=(0,), gains=mcc.GAIN2_DIFF, rate=1000)
			print mcc.actRate
			
			try:
				actcount=0
				print time.asctime()
				start_time=time.time()
				countlimit=200
				while actcount<countlimit:
					actcount, res=mcc.get_continuous_scan_packet()
					if res:
						#print Numeric.array_str(res[:,0], precision=3, suppress_small=1, max_line_width=10000)
						if not actcount%100: print actcount
				dt=time.time()-start_time
				print time.asctime(), dt , mcc.DATA_SAMPLE_SIZE*countlimit/dt
			finally:
				mcc.stop_analog_scan()
			
	finally:
		mcc.close()
		

	pass
