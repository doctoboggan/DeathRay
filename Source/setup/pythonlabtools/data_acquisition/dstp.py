"very basic National Instruments dstp protocol server (see DSTP_async.py for a real one)"
_rcsid="$Id: dstp.py 323 2011-04-06 19:10:03Z marcus $"

import socket
import SocketServer
import traceback
from select import select as _select
import threading
import time
import struct
import array
import select

from nati_dstp_basics import *


class handler(NATI_DSTP_stream_handler):
	
	def __init__(self, request, client_address, server):
		NATI_DSTP_stream_handler.__init__(self, server, request)
		self.client_address=client_address
		self.handle_connection()
				
	def handle_connection(self):
		if self.server.debug:
			print "handling request"
		r=self.request
		self.server.request_closers[self]=self.close #record this so server can close us, if needed
		
		self.looping=1
		while(self.looping):				
			try:
				self.handle_one_request(r)
			except:
				if self.server.debug:
					self.server.log_exception("Request failed")
				self.looping=0

		try:
			del self.server.request_closers[self]
		except KeyError:
			pass #somebody already clean us out
		r.shutdown(2) #zap our socket on exit
				
class DSTPServer(SocketServer.ThreadingTCPServer, NATI_DSTP_DataServer):
	allow_reuse_address=1
	def __init__(self):
		SocketServer.TCPServer.__init__(self, ('',3015), handler)
		self.data={}
		self.debug=0
		self.request_closers={}
		NATI_DSTP_DataServer.__init__(self)
		
	def log_exception(self, explanation=''):
		print explanation
		traceback.print_exc()

	def handle_request(self):
		"""Handle one request, using select to avoid blocking."""
		try:
			r,w,e=select.select([self.socket],[],[], 1.0)
			if not r:
				return
			request, client_address=self.socket.accept()
		except:
			return		
		
		try:
			if self.debug:
				print "got request"
			self.process_request(request, client_address)
		except:
			self.handle_error(request, client_address)

	def serve(self):
		"""Handle one request at a time until doomsday, or until self.keep_running is set to zero."""
		self.keep_running=1
		if self.debug:
			print "server started"
		try:
			while self.keep_running:
				self.handle_request()
		finally:
			if self.debug:
				print "server finished"
			self.keep_running=0
			self.close()
			
	def handle_error(self, request, client_address):
		self.log_exception()
	
	def close(self):
		if self.debug:
			print "closing server"
		try:
			self.keep_running=0
			self.socket.shutdown(2)
			self.socket.close()
			time.sleep(0.1)
		except:
			pass
		
		requests=tuple(self.request_closers.keys()) #iterate over frozen copy of keys since idcionary may be changing
		for closer in requests: 
			try:
				self.request_closers[closer]()
			except:
				pass
		self.live_requests={}
		time.sleep(0.1)
		time.sleep(0.1)
		
if __name__=='__main__':		
	s=DSTPServer()
	s.debug=1
	thread_server=0
	threading._VERBOSE=0
		
	def tryit():
		print "started tweaking server"
		for i in range(30):
			s['MyTest']=i
			s['TestArray']=array.array('d',[i,i/2.0,i/3.0,i/5.0])
			time.sleep(1)
		
		s.close()
		time.sleep(1)
	
	if thread_server:	
		sth=threading.Thread(target=s.serve, name='server')
		sth.start()

	th=threading.Timer(1.0,tryit)
	th.start()
	
	def monitor_test(string):
		print parse_composite_object(string)[0][-2:]
		if 0: #try error bailout on server
			raise "oops"
	s.listen("MyTest", monitor_test)
	s.listen("TestArray", monitor_test)
			
	if thread_server:
		sth.join()	#the thread exits when somebody closes the server
	else:
		s.serve()

	time.sleep(1)
		
	del s
