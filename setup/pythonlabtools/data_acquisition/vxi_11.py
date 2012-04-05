"The basic infrastructure for maintaining a vxi-11 protocol connection to a remote device"
_rcsid="$Id: vxi_11.py 323 2011-04-06 19:10:03Z marcus $"

import rpc
from rpc import TCPClient, RawTCPClient
import exceptions
import struct
import traceback
import time
import weakref
import sys
import select

try:
	import threading
	threads=1
except:
	threads=0

connection_dict={}

def close_all_connections():
	"disconnect and close out all vxi_11 connections created here, even if their object references have been lost" 
	for wobj in connection_dict.keys():
		name, wconn=connection_dict[wobj]
		conn=wconn() #dereference weak ref
		if conn is not None:
			try:
				conn.disconnect()
			except:
				conn.log_exception("***vxi_11.close_all_connections exception: ")
				
		else:
			del connection_dict[wobj] #how did this happen?

class Junk_OneWayAbortClient(RawTCPClient):
	"""OneWayAbortClient allows one to handle the strange, one-way abort rpc from an Agilent E5810.
	Really, it doesn't even do a one-way transmission... it loses aborts, so this is history """
	
	def do_call(self):
		call = self.packer.get_buf()
		rpc.sendrecord(self.sock, call)
		self.unpacker.reset('\0\0\0\0') #put a valid return value into the unpacker

class VXI_11_Error(IOError):
	vxi_11_errors={
				0:"No error", 1:"Syntax error", 3:"Device not accessible",
				4:"Invalid link identifier", 5:"Parameter error", 6:"Channel not established",
				8:"Operation not supported", 9:"Out of resources", 11:"Device locked by another link",
				12:"No lock held by this link", 15:"IO Timeout", 17:"IO Error",  21:"Invalid Address",
				23:"Abort", 29:"Channel already established" ,
				"eof": "Cut off packet received in rpc.recvfrag()",
				"sync":"stream sync lost",
				"notconnected": "Device not connected"}
	
	def identify_vxi_11_error(self, error):
		if self.vxi_11_errors.has_key(error):
			return `error`+": "+self.vxi_11_errors[error]
		else:
			return `error`+": Unknown error code"
	

	def __init__(self, code,  **other_info):
		IOError.__init__(self, self.identify_vxi_11_error(code))
		self.code=code
		self.other_info=other_info
	
	def __repr__(self):
		if self.other_info:
			return str(self)+": "+str(self.other_info)
		else:
			return str(self)

class VXI_11_Device_Not_Connected(VXI_11_Error):
	def __init__(self):
		VXI_11_Error.__init__(self,'notconnected')

class VXI_11_Device_Not_Locked(VXI_11_Error):
	pass
		
class VXI_11_Transient_Error(VXI_11_Error): #exceptions having to do with multiple use which might get better
	pass
	
class VXI_11_Timeout(VXI_11_Transient_Error):
	pass

class VXI_11_Locked_Elsewhere(VXI_11_Transient_Error):
	pass

class VXI_11_Stream_Sync_Lost(VXI_11_Transient_Error):
	def __init__(self, code, bytes):
		VXI_11_Transient_Error.__init__(self, code)
		self.other_info="bytes  vacuumed = %d" % bytes

	
class VXI_11_RPC_EOF(VXI_11_Transient_Error):
	pass

_VXI_11_enumerated_exceptions={ #common, correctable exceptions
		15:VXI_11_Timeout,
		11:VXI_11_Locked_Elsewhere,
		12:VXI_11_Device_Not_Locked
}

class vxi_11_connection:
	"""vxi_11_connection implements handling of devices compliant with vxi11.1-vxi11.3 protocols, with which
	the user should have some familiarity"""
	
	debug_info=0
	debug_error=1
	debug_warning=2
	debug_all=3
	
	debug_level=debug_error
	
	OneWayAbort=0 #by default, this class uses two-way aborts, per official vxi-11 standard
	
	def _list_packer(self, args):
		l=map(None, self.pack_type_list, args) # combine lists
		for packer, data in l:
			packer(data)

	def _list_unpacker(self):
		return [func() for func in self.unpack_type_list]
 
	def _link_xdr_defs(self, channel):
		"self.link_xdr_defs() creates dictionaries of functions for packing and unpacking the various data types"
		p=channel.packer
		u=channel.unpacker

		xdr_packer_defs={
			"write":  (p.pack_int, p.pack_int, p.pack_int, p.pack_int, p.pack_opaque),
			"read":  (p.pack_int, p.pack_int, p.pack_int, p.pack_int, p.pack_int, p.pack_int),
			"create_link": (p.pack_int, p.pack_bool, p.pack_uint, p.pack_string), 
			"generic": (p.pack_int, p.pack_int, p.pack_int, p.pack_int),
			"lock": (p.pack_int, p.pack_int, p.pack_int), 
			"id": (p.pack_int,)
		}
		
		xdr_unpacker_defs={
			"write": (u.unpack_int, u.unpack_int),
			"read": (u.unpack_int, u.unpack_int, u.unpack_opaque), 
			"create_link":  (u.unpack_int, u.unpack_int, u.unpack_uint, u.unpack_uint), 
			"read_stb":(u.unpack_int, u.unpack_int), 
			"error": (u.unpack_int,)
		}
		
		return xdr_packer_defs, xdr_unpacker_defs
	
	def _setup_core_packing(self, pack, unpack):
		self.pack_type_list, self.unpack_type_list=self._core_packers[pack],self._core_unpackers[unpack]
		
	def post_init(self):
		pass
	 
	def simple_log_error(self, message, level=debug_error, file=None):
		if level <= self.debug_level:
			if file is None:
				file=sys.stderr
			print >> file, self.device_name, message
			
	def fancy_log_error(self, message, level=debug_error, file=None):
		if level <= self.debug_level:
			message=str(message).strip()
			level_str=("**INFO*****", "**ERROR****", "**WARNING**", "**DEBUG****")[level]
			if file is None:
				file=sys.stderr
			print >> file, time.asctime().strip(), '\t', level_str, '\t', self.shortname, '\t', \
				message.replace('\n','\n\t** ').replace('\r','\n\t** ')

	def log_error(self, message, level=debug_error, file=None):
		"override log_error() for sending messages to special places or formatting differently"
		self.fancy_log_error(message, level, file)
		
	def log_traceback(self, main_message='', file=None):
		exlist=traceback.format_exception(*sys.exc_info())
		s=main_message+'\n'
		for i in exlist:
			s=s+i
			
		self.log_error(s, self.debug_error, file)
	
	def log_info(self, message, file=None):
		self.log_error(message, self.debug_info, file)
	
	def log_warning(self, message, file=None):
		self.log_error(message, self.debug_warning, file)

	def log_debug(self, message, file=None):
		self.log_error(message, self.debug_all, file)

	def log_exception(self, main_message='', file=None):
		self.log_error(main_message+traceback.format_exception_only(*(sys.exc_info()[:2]))[0], self.debug_error, file)

	def __init__(self, host='127.0.0.1', device="inst0", timeout=1000, raise_on_err=None, device_name="Network Device", shortname=None,
			portmap_proxy_host=None, portmap_proxy_port=rpc.PMAP_PORT, use_vxi_locking=True):
		
		self.raise_on_err=raise_on_err
		self.lid=None
		self.timeout=timeout
		self.device_name=device_name
		self.device_sicl_name=device
		self.host=host
		self.portmap_proxy_host=portmap_proxy_host
		self.portmap_proxy_port=portmap_proxy_port
		self.core=None
		self.abortChannel=None
		self.mux=None #default is no multiplexer active
		self.use_vxi_locking=use_vxi_locking
		
		if shortname is None:
			self.shortname=device_name.strip().replace(' ','').replace('\t','')     
		else:
			self.shortname=shortname.strip().replace(' ','').replace('\t','')   
					
		if threads:
			self.threadlock=threading.RLock()
	
		try:                            
			self.reconnect()    
			
		except VXI_11_Transient_Error:
			self.log_exception("Initial connect failed... retry later")
	
	def setup_mux(self, mux=None, global_name=None):
			self.mux=mux
			self.global_mux_name=global_name
		
	def command(self, id, pack, unpack, arglist, ignore_connect=0):
		
		if not (ignore_connect or self.connected):
			raise VXI_11_Device_Not_Connected

		#command has been made atomic, so that things like get_status_byte can be done 
		#in a multi-threaded environment without needed a full vxi-11 lock to make it safe
		if threads:
			self.threadlock.acquire() #make this atomic
		
		self._setup_core_packing(pack, unpack)

		try:
			try:
				result= self.core.make_call(id, arglist, self._list_packer, self._list_unpacker)
			except (RuntimeError, EOFError):
				#RuntimeError is thrown by recvfrag if the xid is off... it means we lost data in the pipe
				#EOFError is thrown if the packet isn't full length, as usually happens when ther is garbage in the pipe read as a length
				#so vacuum out the socket, and raise a transient error
				rlist=1
				ntotal=0
				while(rlist):
					rlist, wlist, xlist=select.select([self.core.sock],[],[], 1.0)
					if rlist:
						ntotal+=len(self.core.sock.recv(10000) )#get some data from it
				raise VXI_11_Stream_Sync_Lost("sync", ntotal)
		finally:
			if threads:
				self.threadlock.release() #let go

		err=result[0]
		
		if err and self.raise_on_err:
			e=_VXI_11_enumerated_exceptions #common, correctable exceptions
			if e.has_key(err):
				raise e[err](err) #raise these exceptions explicitly
			else:
				raise VXI_11_Error(err) #raise generic VXI_11 exception
				
		return result
				
	def do_timeouts(self, timeout, lock_timeout, channel=None):
		
		if channel is None:
			channel=self.core
			
		flags=0
		if  timeout is  None:
			timeout=self.timeout
		
		if not lock_timeout and hasattr(self,"default_lock_timeout"):
			lock_timeout=self.default_lock_timeout
	
		if  lock_timeout:
			flags |=  1 # append waitlock bit
		
		if channel:
			channel.select_timeout_seconds=0.5+1.5*max(timeout, lock_timeout)/1000.0 #convert ms to sec, and be generous on hard timeout
		
		return flags, timeout, lock_timeout

	def reconnect(self): #recreate a broken connection
		"""reconnect() creates or recreates our main connection.  Useful in __init__ and in complete communications breakdowns.
		If it throws a VXI_11_Transient_Error, the connection exists, but the check_idn() handshake or post_init() failed."""
		
		self.connected=0
				
		if self.core:
			self.core.close() #if this is a reconnect, break old connection the hard way
		if self.abortChannel:
			self.abortChannel.close()
			
		self.core=rpc.TCPClient(self.host, 395183, 1, 
				portmap_proxy_host=self.portmap_proxy_host, 
				portmap_proxy_port=self.portmap_proxy_port)
				
		self._core_packers, self._core_unpackers=self._link_xdr_defs(self.core) #construct xdr data type definitions for the core
		
		err, self.lid, self.abortPort, self.maxRecvSize=self.command(
			10, "create_link","create_link", (0, 0, self.timeout, self.device_sicl_name), ignore_connect=1) #execute create_link
		
		if err: #at this stage, we always raise exceptions since there isn't any way to bail out or retry reasonably
			raise VXI_11_Error(err)
		
		self.maxRecvSize=min(self.maxRecvSize, 1048576) #never transfer more than 1MB at a shot
					
		if self.OneWayAbort:
			#self.abort_channel=OneWayAbortClient(self.host, 395184, 1, self.abortPort)
			self.abort_channel=rpc.RawUDPClient(self.host, 395184, 1, self.abortPort)
		else:
			self.abort_channel=RawTCPClient(self.host, 395184, 1, self.abortPort)
			
		connection_dict[self.lid]=(self.device_name, weakref.ref(self))

		self.locklevel=0

		self.connected=1

		self.check_idn()
		self.post_init()            


	def abort(self):
		
		self.abort_channel.select_timeout_seconds=self.timeout/1000.0 #convert to seconds
		try:
			err=self.abort_channel.make_call(1, self.lid, self.abort_channel.packer.pack_int, self.abort_channel.unpacker.unpack_int) #abort
		except EOFError:
			raise VXI_11_RPC_EOF("eof")
			
		if err and self.raise_on_err:
			raise VXI_11_Error( err)
		return err

	def disconnect(self):
		if self.connected:
			try:
				err, =self.command(23,  "id", "error", (self.lid,)) #execute destroy_link
			except:
				self.log_traceback() #if we can't close nicely, we'll close anyway
			
			self.connected=0
			del connection_dict[self.lid]
			self.lid=None
			self.core.close()
			self.abort_channel.close()
			del self.core, self.abort_channel
			self.core=None
			self.abortChannel=None
		
	def __del__(self):
		if self.lid is not None:
			self.raise_on_err=0 #no exceptions here from simple errors
			try:
				self.abort()
			except VXI_11_Error:
				pass
			try:
				self.disconnect()
			except VXI_11_Error:
				pass            


				
	def write(self, data, timeout=None, lock_timeout=0):
		"""err, bytes_sent=write(data [, timeout] [,lock_timeout]) sends data to device.  See do_timeouts() for 
		semantics of timeout and lock_timeout"""
		
		flags, timeout, lock_timeout=self.do_timeouts(timeout, lock_timeout)
		base=0
		end=len(data)
		while base<end:
			n=end-base
			if n>self.maxRecvSize:
				xfer=self.maxRecvSize
			else:
				xfer=n
				flags |= 8 #write end on last byte          
				
			err, count=self.command(11, "write", "write",  (self.lid, timeout, lock_timeout, flags, data[base:base+xfer]))
			if  err: break  
			base+=count
		return err, base
		
	def read(self, timeout=None, lock_timeout=0, count=None, termChar=None):
		"""err, reason, result=read([timeout] [,lock_timeout] [,count] [,termChar]) reads up to count bytes from the device,
		ending on count, EOI or termChar (if specified).  See do_timeouts() for semantics of the timeouts. \n
		the returned reason is an inclusive OR of 3 bits (per the VXI-11 specs section B.6.4.device_read):
			Bit 2 = END/EOI received,
			bit 1 = Terminating Character received,
			bit 0 = full requested byte count received. 
		"""
		flags, timeout, lock_timeout=self.do_timeouts(timeout, lock_timeout)

		if termChar is not None:
			flags |= 128 # append termchrset bit
			act_term=termChar
		else:
			act_term=0
		
		accumdata=""
		reason=0
		err=0
		accumlen=0
		
		while  ( (not err) and (not (reason & 6) ) and 
			( (count is None) or (accumlen < count))  ):  #wait for END or CHR reason flag or count
                        
			readcount=self.maxRecvSize
			if count is not None:
				readcount=min(readcount, count-accumlen)
			err, reason, data = self.command(12, "read","read", (self.lid,  readcount, timeout, lock_timeout, flags, act_term))
			accumdata+=data     
			accumlen+=len(data)
			#print err, reason, len(data), len(accumdata)
		
		return err, reason, accumdata
	
	def generic(self, code, timeout, lock_timeout):
		flags, timeout, lock_timeout=self.do_timeouts(timeout, lock_timeout)

		err, = self.command(code, "generic", "error", (self.lid, flags, timeout, lock_timeout))

		return err

	def trigger(self, timeout=None, lock_timeout=0):
		return self.generic(14, timeout, lock_timeout)

	def clear(self, timeout=None, lock_timeout=0):
		return self.generic(15, timeout, lock_timeout)
		
	def remote(self, timeout=None, lock_timeout=0):
		return self.generic(16, timeout, lock_timeout)
	
	def local(self, timeout=None, lock_timeout=0):
		return self.generic(17, timeout, lock_timeout)
	
	def read_status_byte(self, timeout=None, lock_timeout=0):
		flags, timeout, lock_timeout=self.do_timeouts(timeout, lock_timeout)

		err, status = self.command(13, "generic","read_stb", (self.lid, flags, timeout, lock_timeout))

		return err, status 
	
	def lock(self,  lock_timeout=0):
		"""lock() acquires a lock on a device and the threadlock.  If it fails it leaves the connection cleanly unlocked.
		If self.use_vxi_locking is false, it acquires only a thread lock locally, and does not really lock the vxi-11 device.
		This is useful if only one process is talking to a given device, and saves time."""
		err=0
		if threads:
			self.threadlock.acquire()
		
		if self.use_vxi_locking and self.locklevel==0:
			flags, timeout, lock_timeout=self.do_timeouts(0, lock_timeout)
			try:
				if self.mux: self.mux.lock_connection(self.global_mux_name)
				try:
					err, = self.command(18, "lock","error", (self.lid, flags, lock_timeout))
				except:
					if self.mux: self.mux.unlock_connection(self.global_mux_name)
					raise                   
			except:
				if threads:
					self.threadlock.release()
				raise
		
		if err:
			if threads:
				self.threadlock.release()
		else:
			self.locklevel+=1
		return err
	
	def is_locked(self):
		return self.locklevel > 0
		
	def unlock(self, priority=0):
		"""unlock(priority=0) unwinds one level of locking, and if the level is zero, really unlocks the device.
		Calls to lock() and unlock() should be matched.  If there is a danger that they are not, due to bad
		exception handling, unlock_completely() should be used as a final cleanup for a series of operations.
		Setting priority to non-zero will bias the apparent last-used time in a multiplexer (if one is used),
		so setting priority to -10 will effectively mark this channel least-recently-used, while setting it to 
		+2 will post-date the last-used time 2 seconds, so for the next 2 seconds, the device will be hard to kick
		out of the channel cache (but not impossible).
		"""
		
		self.locklevel-=1
		assert self.locklevel>=0, "Too many unlocks on device: "+self.device_name
			
		err=0
		try:
			if self.use_vxi_locking and self.locklevel==0:
				try:
					err, = self.command(19, "id", "error", (self.lid,  ))   
				finally:
					if self.mux: 
						self.mux.unlock_connection(self.global_mux_name, priority) #this cannot fail, no try needed (??)
			elif priority and self.mux:
				#even on a non-final unlock, a request for changed priority is always remembered
				self.mux.adjust_priority(self.global_mux_name, priority)
		finally:            
			if threads:
				self.threadlock.release()

		return err

	def unlock_completely(self, priority=0):
		"unlock_completely() forces an unwind of any locks all the way back to zero for error cleanup.  Only exceptions thrown are fatal."
		if threads:
			self.threadlock.acquire() #make sure we have the threadlock before we try a (possibly failing) full lock
		try:
			self.lock() #just to be safe, we should already hold one level of lock!
		except VXI_11_Locked_Elsewhere: 
			pass #this is often called on error cleanup when we don't already have a lock, and we don't really care if we can't get it
		except VXI_11_Error:
			self.log_exception("Unexpected trouble locking in unlock_completely(): ")
	
		if threads:
			self.threadlock._RLock__count += (1-self.threadlock._RLock__count)
			#unwind to single lock the fast way, and make sure this variable    really existed, to shield against internal changes
		self.locklevel=1 #unwind our own counter, too           
		try:
			self.unlock(priority)
		except VXI_11_Device_Not_Locked:
			pass #if we couldn't lock above, we will probably get another exception here, and don't care
		except VXI_11_Transient_Error:
			self.log_exception("Unexpected trouble unlocking in unlock_completely(): ")
		except VXI_11_Error:
			self.log_exception("Unexpected trouble unlocking in unlock_completely(): ")
			raise
	
	def transaction(self, data, count=None, lock_timeout=0):
		"""err, reason, result=transaction(data, [, count] [,lock_timeout]) sends data and waits for a response. 
		It is guaranteed to leave the lock level at its original value on exit,
		unless KeyboardInterrupt breaks the normal flow.  If count isn't provided, there is no limit to how much data will be accepted.
		See do_timeouts() for semantics on lock_timeout."""
		
		self.lock(lock_timeout)
		reason=None
		result=None
		try:
			err,  write_count = self.write(data)
			
			if not err:
				err, reason, result = self.read(count=count)
		finally:        
			self.unlock()

		return err, reason, result

	def check_idn(self):
		'check_idn() executes "*idn?" and aborts if the result does not start with self.idn_head'
		if hasattr(self,"idn"):
			return #already done
		if hasattr(self,"idn_head") and self.idn_head is not None:

			self.lock()
			try:
				self.clear()
				err, reason, idn = self.transaction("*idn?")
			finally:
				self.unlock()

			check=idn.find(self.idn_head)
			self.idn=idn.strip() #save for future reference info    
			if  check:
				self.disconnect()               
				assert check==0, "Wrong device type! expecting: "+self.idn_head+"... got: "+self.idn
		else:
			self.idn="Device *idn? not checked!"

import copy

class device_thread:
	
	Thread=threading.Thread #by default, use canonical threads
	
	def __init__(self,  connection, main_sleep=1.0, name="Device"):
		self.running=0
		self.main_sleep=main_sleep
		self.__thread=None
		self.__name=copy.copy(name) #make a new copy to avoid a possible circular reference
		self.__wait_event=threading.Event()
		self.set_connection(connection)

	def set_connection(self, connection):
		#keep only a weak reference, so the thread cannot prevent the device from being deleted
		#such deletion creates an error when the thread tries to run, but that's OK
		#this allows the device_thread to be used as a clean mix-in class to a vxi_11 connection
		self.__weak_connection=weakref.ref(connection)
	
	def connection(self):
		return self.__weak_connection() #dereference weak reference
					
	def handle_lock_error(self):
		"handle_lock_error can be overridden to count failures and do something if there are too many"
		self.connection().log_exception(self.name+": Error while locking device")

	def onepass(self):
		connection=self.connection()

		try:
			connection.lock()
		except VXI_11_Transient_Error:
			self.handle_lock_error()
			return
		
		try:
			self.get_data()
		except:
			connection.log_traceback('Uncaught exception in get_data()')
			try:
				connection.clear()
			except:
				connection.log_exception('failed to clear connection after error')              
			self.run=0

		connection.unlock()
					
	def monitor(self):
		self.connection().log_info("Monitor loop entered")
		while(self.run):
			try:
				self.onepass()
				self.__wait_event.wait(self.main_sleep) #wait until timeout or we are cancelled
			except KeyboardInterrupt:
				self.connection().log_error("Keyboard Interrupt... terminating")
				self.run=0
			except:
				self.connection().log_traceback()
				self.run=0
				
		self.running=0
		self.connection().unlock_completely() 
		
	def run_thread(self):
		if not self.running: #if it's already running, just keep it up.
			self.run=1
			self.__thread=self.Thread(target=self.monitor, name=self.__name)
			self.__wait_event.clear() #make sure we don't fall through immediately
			self.__thread.start()
			self.running=1

	def get_monitor_thread(self):
		return self.__thread

	def stop_thread(self):
		if self.running:
			self.run=0
			self.__wait_event.set() #cancel any waiting
