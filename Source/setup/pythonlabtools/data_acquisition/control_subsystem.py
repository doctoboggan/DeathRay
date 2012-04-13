"""A set of specific subclasses intended for the Vanderbilt University Free-Electron laser Center,
but very probably useful to many installations"""
_rcsid="$Id: control_subsystem.py 323 2011-04-06 19:10:03Z marcus $"

import time
import exceptions
import traceback
import sys
import vxi_11
from vxi_11 import vxi_11_connection, device_thread
from gpib_utilities import gpib_device
import threading
import weakref

_logfile_lock=threading.Lock() #this lock is shared by all devices

_all_subsystems=[]

_global_logfile=None

def setup_subsystem_logfile(file):
	global _global_logfile
	_global_logfile=file
	
def close_all_subsystems():
	subrefs=list(_all_subsystems) #freeze list
	subrefs.reverse() #probably smart to close in opposite order created
	for subref in subrefs: #freeze list
		sub=subref()
		if sub:
			try:
				sub.close()
			except:
				sub.log_exception("Couldn't close!")
		_all_subsystems.remove(subref)
	if _global_logfile:
		_global_logfile.close()

class subsystem:
	"a class from which most all FEL control system classes will be derived"
	__debug_info=0
	__debug_error=1
	__debug_warning=2
	__debug_all=3
	
	debug_level=__debug_error

	def __fancy_log_error(self, message, level, file):
		if level <= self.debug_level:
			message=str(message).strip()
			level_str=("**INFO*****", "**ERROR****", "**WARNING**", "**DEBUG****")[level]
			print >> file, time.asctime().strip(), '\t', level_str, '\t', self.__shortname, '\t', \
				message.replace('\n','\n\t** ').replace('\r','\n\t** ')
			file.flush()
					
	def log_error(self, message, level=1):
		_logfile_lock.acquire()
		if _global_logfile:
			file=_global_logfile
		else:
			file=sys.stderr
		try: #this is paranoid, but why not? We don't want the log getting stuck. 
			self.__fancy_log_error(message, level, file)
		finally:
			_logfile_lock.release()
		
	def log_traceback(self, main_message=''):
		exlist=traceback.format_exception(*sys.exc_info())
		s=main_message+'\n'+''.join(exlist)			
		self.log_error(s, self.__debug_error)
	
	def log_info(self, message):
		self.log_error(message, self.__debug_info)
	
	def log_warning(self, message):
		self.log_error(message, self.__debug_warning)

	def log_debug(self, message):
		self.log_error(message, self.__debug_all)

	def log_exception(self, main_message=''):
		self.log_error(main_message+' '+traceback.format_exception_only(*(sys.exc_info()[:2]))[0], self.__debug_error)
	
	def  __init__(self, name, shortname=None):	
		#self.debug_level=self.debug_all
		if shortname is None:
			shortname=name
			self.__shortname=shortname.strip().replace(' ','').replace('\t','')
		else:
			self.__shortname=shortname
		
		self.__longname=name
		#make shortname, but if it gets accidentally overwritten, error logging will still work
		self.shortname=self.__shortname 

		#set up some very commonly used variables
		self.loop_count=1
		self.consecutive_failures=0
		self.recent_timeouts=0
		self.last_good_data_time=time.time()
		_all_subsystems.append(weakref.ref(self))
		
	def close(self):
		pass #do whatever is needed

