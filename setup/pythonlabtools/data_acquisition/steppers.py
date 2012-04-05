"""steppers.py defines abstract intelligent stepper motor channels and clusters and has a sample implementation for Norberg Consulting BiStep and SimStep stepper controllers"""

_rcsid="$Id: steppers.py 323 2011-04-06 19:10:03Z marcus $"

import time
import os
import sys

class StepperOwner:
	"this is a template class for the minimal requirements to be owned by a StepperChannel"
	
	def  has_encoder(self, channel):
		"returns 0 if this channel has no encoder, 1 if it has one"
		return 0
			
	def get_encoder(self, channel):
		"return the encoder readback for the specified channel"
		raise NotImplementedError, "get_encoder() not instantiated"
		
	def prepare_step(self, channel, count):
		"prepare a channel for taking a step of <count> steps, without actually taking it"
		raise NotImplementedError, "prepare_step() not instantiated"
	
	def go(self):
		"cause all channels with steps prepared to take the steps.  Repeated calls MUST do nothing after the first call starts the step"
		raise NotImplementedError, "go() not instantiated"
		
	def stop(self, channel):
		"abort motion suddenly on specified channel"
		raise NotImplementedError, "stop() not instantiated"
	 
	def stop_all(self):
		"abort motion suddenly on all channels"
		raise NotImplementedError, "stop_all() not instantiated"
	
class StepperChannel:
	"""A stepper channel remembers where it is, knows how to convert steps to engineering units, etc.
	It stores the steps per unit conversion as a rational number (numerator,denominator).
	Close attention is given to rounding during steps->engineering units conversion to avoid walkoff.
	It can optionally read an encoder from hardware.
	The owner_channel can be whatever snippet of information the owner needs to identify this axis.
	"""
	
	def __init__(self, owner, owner_channel=1, steps_per_eng_unit=(1,1), steps_per_encoder_step=(1,1)):
		self.current_steps=0
		self.steps_per_eng_unit=steps_per_eng_unit
		self.steps_per_encoder_step=steps_per_encoder_step
		self.encoder_offset=0
		self.current_eng_pos=0.0
		self.next_steps=None
		self.next_pos=None
		self.owner=owner
		self.owner_channel=owner_channel
		self.has_encoder=owner.has_encoder(owner_channel) #set a flag for whether we know how to encode
		self.encoding_enabled=self.has_encoder
		
	def compute_stepcount_from_engineering_position(self, position):
		"compute an absolute stepper index from the given engineering position.  Override for non-linear systems"
		n,d=self.steps_per_eng_unit
		return n*float(position)/d
		
	def compute_engineering_position_from_stepcount(self, stepcount):
		"""Compute an engineering position from an absolute stepper index. 
		Must be exact inverse of compute_stepcount_from_engineering_position() """
		n,d=self.steps_per_eng_unit
		return d*float(stepcount)/n

	def disable_encoding(self):
		"ignore the encoder, even if we have one"
		self.encoding_enabled=0
		
	def enable_encoding(self):
		"use the encoder if we have one"
		self.encoding_enabled=self.has_encoder

	def get_encoded_steps(self):
		"return raw encoder readback as equivalent stepper steps.  Override if transform not linear (unlikey!)"
		if self.encoding_enabled:
			encoder=self.owner.get_encoder(self.owner_channel)
			n,d=self.steps_per_encoder_step
			return n*float(encoder)/d+self.encoder_offset
		else:
			return self.current_steps+self.encoder_offset
	
	def synchronize_to_encoder(self):
		"""set our internal step counter to agree with the encoder reasonably well,
		so moves end up _approximately_ in the same place whether or not encoding is active"""
		self.current_steps=self.get_encoded_steps()-self.encoder_offset
		
	def get_encoded_position(self):
		"return engineering position as seen by the encoder"
		return  self.compute_engineering_position_from_stepcount(self.get_encoded_steps())
		
	def set_encoder_offset(self, current_engineeering_position):
		"adjust the encoder offset so that the apparent engineering position is as specified"
		steps=self.compute_stepcount_from_engineering_position(current_engineeering_position)
		self.encoder_offset+=steps-self.get_encoded_steps()
		
	def compute_steps_from_absolute_position(self, position):
		"return how many steps away the requested engineering position is from the current position"
		steps=self.compute_stepcount_from_engineering_position(
				position
			)- self.get_encoded_steps()

		self.next_steps=int(steps)
		self.next_pos=position
		return self.next_steps
			
	def update_steps(self):
		"after making a real move, update variables with this"
		self.current_steps+=self.next_steps
		self.current_eng_pos=self.next_pos
		self.next_steps=0 #make sure that gratuitously repeated 'go' calls don't mess up our settings
		
	def setup_move_absolute(self, engineering_pos):
		"prepare for an absolute move without actually doing it"
		steps=self.compute_steps_from_absolute_position(engineering_pos)
		self.prepare_step(steps)

	def setup_move_relative(self, engineering_pos_change):
		"prepare for a relative move without actually doing it"
		self.setup_move_absolute(self.current_eng_pos+engineering_position_change)

	def move_absolute(self, engineering_pos):
		"setup and execute a move"
		self.setup_move_absolute(engineering_pos)
		self.go()
	
	def move_relative(self, engineering_pos_change):
		"setup and execute a move"
		self.setup_move_relative(engineering_pos_change)
		self.go()

	def get_current_position(self):
		return self.current_eng_pos

	def hardware(self):
		"get our hardware device for passing on special commands"
		return self.owner

	def prepare_step(self, count):
		"""this prepare a motor for stepping.  It is separated from step, since motor controllers may choose
		to combine steps along ultiple axes into a single move when go is called"""
		self.owner.prepare_step(self.owner_channel, count)
	
	def go(self):
		"""trigger the hardware which owns this axes to make any and all moves queued up""" 
		self.update_steps()
		self.owner.go()
try:
	import Numeric
	def _myarray(elems):
		return Numeric.array(elems, Numeric.Float64)
	
except: #if this happens, the actual subclass had better provide a real array class!
	_myarray=None
	
class StepperCluster:
	"""A stepper cluster remembers where it is, knows how to convert steps to engineering units, etc.
	It stores the steps per unit conversion as a rational number (numerator,denominator).
	Close attention is given to rounding during steps->engineering units conversion to avoid walkoff.
	It is capable of handling complex, nonlinearly-coupled, interacting motors."""
	
	#override this in real instances if NumPy isn't the right array class
	array=_myarray
	
	def __init__(self, channel_list):
		self.channels=channel_list
			
	def get_encoded_position(self):
		"override this for real encoders, otherwise it is just the engineering position"
		return self.array([chan.get_encoded_steps() for chan in self.channels])
		
	def compute_mechanical_from_engineering_position(self, position):
		"compute an absolute stepper index from the given engineering position.  Override for non-linear systems"
		assert 0, "Must override compute_stepcount_from_engineering_position"
			
	def compute_steps_from_absolute_position(self, position):
		current_pos=self.array([chan.get_current_position() for chan in self.channels])
		self.next_steps=(
			compute_mechanical_from_engineering_position(position)-current_pos)
		self.next_delta=position-self.current_eng_pos
		return self.next_steps
			
	def current_engineering_pos(self):
		return self.array([chan.get_current_pos() for chan in self.channels])

	def move_absolute(self, engineering_pos):
		steps=self.compute_steps_from_absolute_position(engineering_pos)
		for chan, count in zip(self.channels, steps-self.get_encoded_position()):
			chan.step(count)

	def move_relative(self, engineering_pos_change):
		self.move_absolute(self.current_eng_pos()+engineering_position_change)

_have_default_device=0

try:
	import termios
	import fcntl
	import tty
	
	class termios_mixin:
		"mixin class for RawLabPro to support Unix, MacOSX and Linux termios serial control"
					
		def close(self):
			self.serial_read_port.close()
			if self.serial_write_port != self.serial_read_port:
				self.serial_write_port.close()
			
		def set_port_params(self, baud=termios.B9600):
			port=self.serial_read_port
			tty.setraw(self.serial_read_port.fileno())
			attrs=termios.tcgetattr(port)
			attrs[4]=attrs[5]=baud #set 38.4kbaud
			attrs[2] = attrs[2] | termios.CLOCAL #ignore connection indicators
			cc=attrs[6]; cc[termios.VMIN]=0; cc[termios.VTIME]=0 #non-blocking reads
			termios.tcsetattr(port, termios.TCSADRAIN, attrs)
			fcntl.fcntl(self.serial_read_port, fcntl.F_SETFL, os.O_NONBLOCK) 
	
		def setup_serial(self, port_name):
			self.serial_write_port=port=open(port_name,"r+" , 16)
			self.serial_read_port=self.serial_write_port	
			self.set_port_params() #setup default port
			try:
				self.serial_read_port.seek(0) #see if seeking clears EOF (works on MacOSX, not on Linux)
				self.__allow_serial_seek=1
			except:
				self.__allow_serial_seek=0
		
		def write(self, data):
			"override this if communication is not over normal serial"
			self.serial_write_port.write(data)
			self.serial_write_port.flush()
		
		def read(self, maxlen=None):
			"override this as for write()"
			if self.__allow_serial_seek: self.serial_read_port.seek(0) #try to clear EOF
			try:
				if maxlen is None:
					return self.serial_read_port.read()
				else:
					return self.serial_read_port.read(maxlen)
			except IOError:
				return ''

	
	_have_default_device=1 #flag that this worked, don't look for other methods to make default
	
except: #no termios serial support
	#insert check for other system architectures here, such as Windows or MacOS classic
	raise

class RawNorbergStepper(StepperOwner):
	"support for SimStep and BiStep commands.  RawStepper class has no I/O and needs a mixin for the serial port support"
	
	#this mapping generates a correspondence between the universal axis names and the hardware cod for that axis
	#in this case, it also includes information about the numerical channel number when a readback is done
	axisdict={'x_axis':('x',0), 'y_axis':('y',1)} 

	def __init__(self, port_name):
		self.setup_serial(port_name)
		self.stepsdict={}
		for axis in self.axisdict.keys():
			setattr(self, axis, axis) #put the axis name in our class dictionary
			self.stepsdict[axis]=0 #and initialize step count dictionary
		self.move_queued=0
		
	def get_all_input(self):
		instr=''
		gotit=1
		misses=0
		while(gotit and misses<2):
			gotit=self.read()
			if gotit:
				instr+=gotit
				misses=0
			else:
				misses+=1
				time.sleep(0.05)
		return instr
			
	def send_string(self, s='I'):
		"send a string and collect all responses"
		self.write(s)
		return self.get_all_input()

	def read_status(self):
		s=self.send_string('B-1?').strip().split('*')
		s=[a.strip().split() for a in s if a]
		if s and s[-1]:
			xs,ys=s[-1]  #only return infor from last valid reading
			x=int(xs.split(',')[-1])
			y=int(ys.split(',')[-1])
			return x,y
		else:
			 return None,None

	def is_running(self):
		x1,y1=self.read_status()
		x2,y2=self.read_status()
		return x1!=x2 or y1!=y2
	
	def set_move_parameters(self, axis='x_axis', rate=1000, accel=1000):
		self.send_string('%s%dr%dp'%(self.axisdict[axis][0],rate,accel))
	
	def prepare_step(self, axis, steps):
		self.stepsdict[axis]=steps
		self.move_queued=1
		
	def go(self):
		if not self.move_queued:
			return
		
		outstr=''
		for axis in self.axisdict.keys():
			outstr+='%s%ds'%(self.axisdict[axis][0], self.stepsdict[axis])
			self.stepsdict[axis]=0 #reset step count once we take it
			
		if self.debug:
			print >> sys.stderr, 'motor move command: ', outstr
		self.send_string(outstr)
		self.move_queued=0 #this move is running, don't re-execute it!
		
class NorbergStepper(termios_mixin, RawNorbergStepper):
	def __init__(self, port_name="/dev/tty.USA28X3b1P1.1", debug=0):
		self.debug=debug
		RawNorbergStepper.__init__(self, port_name)
		
		if debug:
			self.send_string('x1000gy1000g')
			while self.is_running():
				print self.read_status()
			self.send_string('x0gy0g')
			while self.is_running():
				print self.read_status()
	
	def get_encoder(self, channel):
		"fake out an encoder for this, for test purposes"
		a=None,None
		while(a[0] is None):
			a=self.read_status()
		return a[self.axisdict[channel][1]]
		
if __name__=='__main__':
	
	a=NorbergStepper(debug=0)
	#this stepper setup is a micrometer pair with 0.5mm/turn.  
	#The default Norberg setup runs 3200 microsteps/turn on the motor, so 6400 steps is 1 mm
	x=StepperChannel(a,owner_channel=a.x_axis,steps_per_eng_unit=(6400,1)) #program in millimeters
	y=StepperChannel(a,owner_channel=a.y_axis,steps_per_eng_unit=(6400,1))
	x.set_encoder_offset(5.0) #tell system that 0 (current) step count is at 5 engineering units
	
	x.setup_move_absolute(5.5)
	y.setup_move_absolute(1.0)
	x.go() #also makes y go since they are on the same controller
	while a.is_running():
		print a.read_status(), 
		print x.get_encoded_position(), y.get_encoded_position()
		time.sleep(1)
	y.go() #should do nothing, since move is already made
		
	x.setup_move_absolute(5.0)
	y.setup_move_absolute(0)
	x.go() #also makes y go since they are on the same controller
	while a.is_running():
		print a.read_status(), 
		print x.get_encoded_position(), y.get_encoded_position()
		time.sleep(1)
	y.go() #should do nothing, since move is already made
	
	del a, x, y
