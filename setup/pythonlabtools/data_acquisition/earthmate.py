"""earthmate.py supports communication with a DeLorme (www.delorme.com) Earthmate GPS unit, and with other Rockwell/Conexant/Navman/SiRF Zodiac
and Jupiter type receivers"""

_rcsid="$Id: earthmate.py 323 2011-04-06 19:10:03Z marcus $"

import time
import Numeric
import os
import sys
import math
import array
import types
import threading
import operator
import struct
import traceback 

_bigendian=(struct.unpack('H','\00\01')[0] == 1)

import termios
class termios_serial:
	"mixin class for Unix, MacOSX and Linux termios serial control"
				
	def close(self):
		self.serial_read_port.close()
		if self.serial_write_port != self.serial_read_port:
			self.serial_write_port.close()
		
	def set_port_params(self, baud=termios.B9600):
		port=self.serial_read_port
		attrs=termios.tcgetattr(port)
		attrs[4]=attrs[5]=baud #set 38.4kbaud
		attrs[2] = attrs[2] | termios.CLOCAL  #ignore connection indicators
		cc=attrs[6]; cc[termios.VMIN]=0; cc[termios.VTIME]=0 #non-blocking reads
		termios.tcsetattr(port, termios.TCSADRAIN, attrs)
	
	def setup_serial(self, port_name):
		self.serial_write_port=port=open(port_name,"rb+" , 1000)
		self.serial_read_port=self.serial_write_port	
		self.set_port_params() #setup default port
		
	def write(self, data):
		"override this if communication is not over normal serial"
		self.serial_write_port.write(data)
		self.serial_write_port.flush()
	
	def read(self, maxlen=None):
		"override this as for write()"
		self.serial_read_port.seek(0) #try to clear EOF
		if maxlen is None:
			return self.serial_read_port.read()
		else:
			return self.serial_read_port.read(maxlen)
			
class EarthmateError(Exception):
	pass
class EarthmateTransientError(EarthmateError):
	pass
class EarthmateBadData(EarthmateTransientError):
	pass
class EarthmateReset(EarthmateTransientError):
	pass

class raw_earthmate:
	
	reset_detect_string="EARTHA"
	reset_output_string="EARTHA"
	
	def __init__(self, portname):
		self.setup_serial(port_name=portname)
		self.serial_buffer=''
		self.times=[]
		self.buffer_lock=threading.RLock()
		self.transmit_lock=threading.RLock()
		self.data_monitor=threading.Thread(target=self.read_data, name='gps data monitor')
		self.keep_running=1
		self.data_monitor.start()	
		self.message_collector=None
		self.msg_sequence=0
		
	def read_data(self):
		print "starting data reader..."
		while self.keep_running:
			try:
				time.sleep(0.005)
				newdata=self.read(-1)
				#print '*', repr(newdata)
				if not newdata: continue
				t=time.time()
				self.buffer_lock.acquire()
				try:
					self.serial_buffer+=newdata
					self.times+=(len(newdata)*[t]) #timestamp these bytes
				finally:
					self.buffer_lock.release()
			except:
				traceback.print_exc()
				break
									
	def read_bytes(self, count):
		result=''
		while not result:
			if not self.data_monitor.isAlive():
				raise EarthmateError("Reader died")
				
			try:
				self.buffer_lock.acquire()
				if len(self.serial_buffer) >= count:
					result=self.serial_buffer[:count]
					self.serial_buffer=self.serial_buffer[count:]
					times=self.times[:count]
					del self.times[:count]
			finally:
				self.buffer_lock.release()
			if not result: time.sleep(0.1)
		return result, times

	def handle_reset(self):
		raise EarthmateReset("got reset header from Earthmate")
		
	def find_header(self, maxloops=None):
		"wait until serial buffer contains zodiac header, then trim any junk before header"
		done=0
		loops=0
		while not done and (maxloops is None or loops < maxloops):
			if not self.data_monitor.isAlive():
				raise EarthmateError("Reader died")
			self.buffer_lock.acquire()
			try:
				pos=self.serial_buffer.find('\xff\x81')
				#print repr(self.serial_buffer), pos
				done=pos>=0
				if done:
					if pos> 0: 
						pass
						#print "garbage in buffer, length %d %s" % (pos , repr(self.serial_buffer[:10]))
					self.serial_buffer=self.serial_buffer[pos:]
					del self.times[:pos]
				else:
					pos=self.serial_buffer.find(self.reset_detect_string)
					if pos >=0:
						self.transmit_lock.acquire()
						try:
							self.write(self.reset_output_string) #restart Earthmate
						finally:
							self.transmit_lock.release()
						time.sleep(1)
						self.handle_reset()
			finally:
				self.buffer_lock.release()
			if not done: time.sleep(0.25)
			loops+=1
			
	def readmsg(self):
		self.find_header()
		headerdata, times=self.read_bytes(10)
		header=struct.unpack('<HHHHH', headerdata)
		count=header[2]
		err=reduce(operator.add, header) & 0xffff
		if err:
			raise EarthmateBadData("bad header checksum %04x: data is %04x %04x %04x %04x %04x" % tuple([err]+list(header)))
		if not count:
			return header, [], times[0]
		packetdata, packtimes=self.read_bytes(2*(count+1))
		packet=struct.unpack('<'+(count+1)*'H', packetdata)
		err=reduce(operator.add, packet) & 0xffff
		if err:
			raise EarthmateBadData("bad packet checksum %04x, message=%d, count=%d" % (err, header[1], count))
		return header, packet, times[0]

	def enable_message_queue(self):
		self.message_collector=threading.Thread(target=self.collect_messages_thread, name='gps message collector')
		self.message_queue=[]
		self.message_collector.start()	
	
	def message_queue_running(self):
		return self.keep_running and self.message_collector and self.message_collector.isAlive() 

	def collect_messages_thread(self):
		while self.keep_running:
			try:
				header, packet, times=self.readmsg()
				if len(self.message_queue) > 100:
					self.message_queue.pop()
				self.message_queue.insert(0,(header, packet, times))
				
			except EarthmateTransientError:
				pass
			except EarthmateError:
				break
			except:		
				traceback.print_exc()
				break
	
	def di_convert(self, data):
		base=long(data[1])<<16 | data[0]
		if base & 0x80000000L:
			base-=0x100000000L
		return int(base)
		
	def parse1000(self, msg):
		latrad=self.di_convert(msg[21:23])*1e-8
		longrad=self.di_convert(msg[23:25])*1e-8
		lat=latrad*180.0/math.pi
		longi=longrad*180.0/math.pi
		err=msg[4] & 0x1f
		utchour=msg[16]
		utcmin=msg[17]
		utcsec=msg[18]
		utcnsec=self.di_convert(msg[19:21])
		satcount=msg[6]
		return { 'raw': msg, 'latrad':latrad, 'lat':lat, 'longrad':longrad, 'long': longi,
				'err':err, 'utchour':utchour, 'utcmin':utcmin, 'utcsec':utcsec, 'utcnsec':utcnsec,
				'utcday':msg[13], 'utcmonth':msg[14],'utcyear':msg[15],
				'groundspeed':(msg[29]<<16 | msg[28])*0.01,
				'groundcourserad':msg[30]*0.001, 
				'groundcourse':msg[30]*0.001*180.0/math.pi, 
				'altitude':self.di_convert(msg[25:27])*0.01,
				'climb':msg[32]*0.01,  
				'satcount':satcount,
				'datum':msg[33], 
				'EHPE': self.di_convert(msg[34:36])*0.01,
				'EVPE': self.di_convert(msg[36:38])*0.01,
				'ETE': self.di_convert(msg[38:40])*0.01,
				'EHVE': msg[40]*0.01,
				 }
				
	def send_msg(self,id, flags=0, datawords=[]):
		hdr=[0x81ff, id, len(datawords), flags]
		hdrchk= -(reduce(operator.add,hdr)) & 0xffff
		hdr.append(hdrchk)
		if datawords:
			datachk= -(reduce(operator.add,datawords)) & 0xffff
			hdr+=datawords+[datachk]
		s=struct.pack('<'+len(hdr)*'H', *hdr)
		#print hdr, array.array('B', s)
		self.transmit_lock.acquire()
		try:
			self.write(s)
			time.sleep(0.1)
		finally:
			self.transmit_lock.release()

	def enable_msg(self, id):
		self.send_msg(id,0x4000)

	def disable_msg(self, id):
		self.send_msg(id,0x8000)

	def configure_logging(self, id, trig=0, interval=1, offset=0):
		self.send_msg(id, 0x2000, [trig, interval, offset])
	
	def next_sequence(self):
		self.msg_sequence=(self.msg_sequence+1) & 0x7fff
		return self.msg_sequence
		
	def set_datum(self, datum):
		self.send_msg(1211,0,[self.next_sequence(), datum])
	
	def set_elev_mask(self, angle_degrees=5.0):
		self.send_msg(1212, 0, [self.next_sequence(), int(1000.0*angle_degrees*math.pi/180.0)])
	
	def set_pinned_position(self, flags):
		self.send_msg(1221, 0, [self.next_sequence(), flags & 0x0f,0,0,0,0,0,0,0])

	def set_nav_configuration(self, pinning_disable=0, smoothing_disable=0, held_altitude_disable=0, filtering_disable=0):
		flags= (bool(filtering_disable)<<3) | (bool(pinning_disable) << 2) | (bool(smoothing_disable) << 1) | bool(held_altitude_disable)
		self.send_msg(1221, 0, [self.next_sequence(), flags,0,0,0,0,0,0,0])

	platforms={ 'default':0, 0:0, 
			'static':1, 1:1,
			'pedestrian':2, 2:2,
			'lakes':3, 'lake':3, 3:3,
			'sealevel':4, 'sea level':4, 'sea':4, 4:4,
			'land':5, 'auto':5, 5:5, 
			'air':6, 6:6 }
	def set_platform(self, platform='default'):
		self.send_msg(1220, 0, [self.next_sequence(), self.platforms[platform]])
	
	def query_message(self, id):
		self.send_msg(id, flags=8) #cause one packet to be queried
	
	def parse1012(self, msg):
		opstat=msg[3]
		elev_mask=msg[6]
		satcount=msg[10]
		platform=msg[15]
		
		return { 'power_management':bool(opstat & 0x0001),
				'cold_start_disable':bool(opstat&0x0002),
				'opstat':opstat, 
				'dgps_disable':bool(opstat&0x0004),
				'held_altitude_disable':bool(opstat&0x0008),
				'smoothing_disabled':bool(opstat&0x0010),
				'position_pinning_disabled':bool(opstat&0x0020),
				'elev_mask':elev_mask*180.0/(math.pi*1000.0), 'satcount':satcount, 'platform':platform
		}

class earthmate(termios_serial, raw_earthmate):

	def close(self):
		self.keep_running=0
		self.data_monitor.join()
		termios_serial.close(self)

if __name__=='__main__':
	class my_em(earthmate):
		"an earthmate with a specific reset configuration"
		
		def handle_reset(self):
			self.enable_msg(1000)
			self.configure_logging(1002, interval=5, offset=3)
			self.disable_msg(1002)
			self.configure_logging(1003, interval=5, offset=2)
			self.disable_msg(1003)
			self.configure_logging(1012, interval=5, offset=1)
			self.disable_msg(1012)
			self.set_elev_mask(5)
			self.set_platform('default')
			self.set_pinned_position(7)
			self.set_datum(0)
			print "reset!"
			
	def test_earthmate(outfile=None, longform=1):
		print "go!"
		if outfile:
			out=file(outfile,"a")
		else:
			out=sys.stdout
			
		em=my_em(portname='/dev/cu.USA28X21P1.1')
		loops=0
		try:
			em.enable_message_queue()
			em.handle_reset() 
			
			while(1):
				try:
					loops+=1
					
					if not em.message_queue:
						time.sleep(0.25)
						continue
					header, packet, times=em.message_queue.pop()
					#print  header[1], ("%.3f" % (times-int(times)))
					if longform:
						print >> out, time.asctime(time.localtime(times)), '\t',  "%.3f"%(times-int(times)), '\t', header[1], '\t', 
						if header[1]==1000: 
							res=em.parse1000(packet)
							print  >> out, res['err'], '\t', 
							print  >> out, res['satcount'], '\t', res['utcsec'], '\t', "%.6f \t %.6f \t %.9f \t" % ( 
									res['long'], res['lat'], res['utcnsec']*1e-9),
							print >> out, "%.2f \t %.2f \t %.2f \t %.2f \t %.2f" % (res['altitude'], res['EHPE'], res['EVPE'], res['ETE'], res['EHVE'])
							#print >> out, res['datum']
						elif header[1]==1012: 
							res=em.parse1012(packet)
							print >> out, res
						else:
							print >> out
					else:
						print >> out, time.asctime(), '\t', time.asctime(time.localtime(times)),'\t', header[1]
										
					out.flush()
				except KeyboardInterrupt:
					break
				except:
					traceback.print_exc()
					break	
		finally:
			em.close()
	
			if out != sys.stdout:
				out.close()	
	
	test_earthmate(longform=1,outfile='earthmate.txt')
			
