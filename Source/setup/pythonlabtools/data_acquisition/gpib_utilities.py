"handle some scpi and gpib protocols"
_rcsid="$Id: gpib_utilities.py 323 2011-04-06 19:10:03Z marcus $"

import time

class SCPI_Error(Exception): #:syst:err? returned something
	pass

class Status_Byte_Flagged(UserWarning): #if standard event bit is set in status byte
	pass

class Timeout_Error(IOError):
	pass

def handle_iee488_binary_block( data):
	"data, rest = handle_iee488_variable_binary_block(data)"
	assert data[0]=="#", "Bad binary data block" + data[:20]
	cl=int(data[1])
	if cl:
		dlen=int(data[2:2+cl])
	else:
		dlen=len(data)-3 #don't include #0 at beginning or newline at end
		
	return data[2+cl:2+cl+dlen], data[2+cl+dlen:]



class gpib_device:
	"this is a mix-in class for vxi-11 devices to provide some useful functions"
	
	def check_scpi_errors(self):
		err=1
		errsum=0
		while(err):
			errstr=self.mav_transaction(":syst:err?", status_error_mask=0)[2]
			code, message = errstr.split(",",1)
			if message[-1]=="\n": message=message[:-1]
			err=int(code)
			if(err): 
				self.log_error(message, self.debug_error)
				errsum |= 1
				
		if errsum:
			raise SCPI_Error
	
	def mav_transaction(self, message, status_error_mask=32, max_wait=None):
		if max_wait is None:
			max_wait=self.max_message_wait
		self.lock()
		self.write(message)
		time.sleep(0.01) #allow thread switch
		start=time.time()
		while(1):
			junk, stat=self.read_status_byte()
			self.log_error("Status byte= %02x" % stat, self.debug_all)
			if (time.time() - start) > max_wait:
				raise Timeout_Error, "Timeout waiting for message"
			time.sleep(0.1) #allow thread switch
			if stat & (16 | status_error_mask): break #16 is MAV, 32=standard event
		if stat & status_error_mask:
			raise Status_Byte_Flagged
		result= self.read()
		self.unlock()
		return result
			

