"very useable National Instruments dstp protocol server"
_rcsid="$Id: dstp_async.py 323 2011-04-06 19:10:03Z marcus $"

import socket
import SocketServer
import traceback
import select
import threading
import time
import struct
import array
import select

from nati_dstp_basics import *

#Edit this before loading the module to define whether the threaded responder is to be used.
#Hint... it's a really good idea, and always should be, in general, although the server will have
#slightly lower overhead without it.  

use_threaded_responses=1

if use_threaded_responses:
	class threaded_response_data(NATI_DSTP_DataServer):
		"""spin off a separate thread to send responses out, so server can receive new requests while sending is in progress.
		Many names here are double_underscored to avoid namespace collisions with the parent class"""
		def __init__(self):
			self.__sender_thread=threading.Thread(target=self.__send_data_thread, name='DSTP sender')
			self.__notifierEvent=threading.Event()
			self.__queue=[]
			NATI_DSTP_DataServer.__init__(self)
			self.__sender_thread.start()
				
		def echo_data(self, info):
			"This overrides the server's echo_data, and runs in the server's thread.  Blocking here blocks the server"
			self.__queue.insert(0,info)
			self.__notifierEvent.set()
		
		def __send_data_thread(self):
			"wait for data to appear in the queue, and send it from inside the thread, so the server doesn't block"
			while(self.keep_running): #keep_running is inherited from the main server, conveniently
				while len(self.__queue): 
					info=self.__queue.pop()
					NATI_DSTP_DataServer.echo_data(self, info)
				self.__notifierEvent.wait(10.0)
				self.__notifierEvent.clear() #got it.
	DataServer=threaded_response_data
else:
	DataServer=NATI_DSTP_DataServer		

class DSTPServer(SocketServer.TCPServer, DataServer):
	"DSTPServer is a class which creates a reasonably complete nati-dstp server"
	connect_ip=''
	connect_port=3015
	allow_reuse_address=1
	
	def __init__(self):
		SocketServer.TCPServer.__init__(self, (self.connect_ip,self.connect_port), None)
		self.debug=0
		self.socket_info={}
		self.connection_serial=0
		self.keep_running=1
		DataServer.__init__(self)
			
	def log_exception(self, explanation=''):
		print explanation
		traceback.print_exc()

	def verify_connection(self, request, client_address):
		"""verify_connection() returns 1 if the client address as acceptable, otherwise returns 0. 
		It is useful to limit connections to the server to only come from certain IPs or ranges.
		Can be overridden to provide real service."""
		return 1

	def new_connection(self, sock):
		request, client_address=sock.accept()
		if self.verify_connection(request, client_address):
			handler=NATI_DSTP_StreamHandler(self, request)
			self.socket_info[request]={"addr":client_address, 
					"handle":handler.handle_one_request, 
					"name":str(self.connection_serial)}
			self.connection_serial+=1
			if self.debug:
				print self.socket_info
		else:
			request.shutdown(2)
		
	def safe_socket_name(self, sock):
		return self.socket_info.get(sock,{"name":"closed"})["name"]
						
	def serve(self):
		"""Handle one request at a time until doomsday, or until self.keep_running is set to zero."""
		self.keep_running=1
		self.socket_info[self.socket]={"addr":'127.0.0.1', "handle":self.new_connection, "name":'main'}
		if self.debug:
			print "server started"
		try:
			while self.keep_running:
				streams=list(self.socket_info.keys())
				try:
					r,w,e=select.select(streams,[],[], 1.0)
				except select.error:
					#oops, got a bad socket, probably have to weed it out by hand
					for sock in streams:
						try:
							r,w,e=select.select([sock],[],[],0.0)
						except select.error:
							if self.debug:
								print "deleting session", self.safe_socket_name(sock)
							if sock is self.socket:
								self.keep_running=0 #ouch. someone closed or damaged our main socket
							del self.socket_info[sock]
					continue
				for sock in r:
					try:
						if self.debug:
							print "handling information for: ", self.socket_info[sock]["name"]
						self.socket_info[sock]["handle"](sock)
						if self.debug:
							print "done handling information for: ", self.safe_socket_name(sock)
					except KeyboardInterrupt:
						self.keep_running=0
						break
					except ClosedError:
						if self.debug:
							print "Closing: ", self.safe_socket_name(sock)
						del self.socket_info[sock] #exit gracefully
					except:
						if self.debug:
							print "failed handling information for: ", self.safe_socket_name(sock)
							traceback.print_exc()
						try:
							sock.shutdown(2) #terminate bad session
						except socket.error:
							pass
						if sock is self.socket:
							self.keep_running=0 #ouch. someone closed our main socket
						try:
							del self.socket_info[sock] #if it doesn't work, don't try again
						except KeyError:
							pass
		finally:
			if self.debug:
				print "server finished"
			self.keep_running=0
			self.close()
			
	def close(self):
		if self.debug:
			print "closing server"
		self.keep_running=0
		time.sleep(1)
		streams=list(self.socket_info.keys())
		for sock in streams:
			try:
				sock.shutdown(2)
			except:
				pass
		time.sleep(0.1)
			
	def __del__(self):
		self.close()

if __name__=='__main__':	
	savedserver=''
	threading._VERBOSE=0
		
	s=DSTPServer()
	s.debug=1
	thread_server=0
	UseNumericArray(1)
	
	import tagged_data
	
	data=tagged_data.tagged_data_system()

	data.define_field("test1", s, ("MyTest", 1), writable=1)
	data.define_field("test2", s, ("TestArray", array.array('d',[0])), writable=1)
	data.define_field("test3", s, ("BooleanArray", array.array('b',[0])), writable=1)
	data.define_field("test4", s, ("Boolean", 1), writable=1)
	data.define_field("cluster", s, ("cluster", [1.0,'', 1.0]), writable=1)
	
	data.test4=255
	#data.cluster=[2.3,'testing', -100.]
	def tryit():
		global saved_server
		print "started tweaking server"
		try:
			for i in range(20):
				data.test1=i
				data.test2=array.array('d',[i,i/2.0,i/3.0,i/5.0])
				data.test3=array.array('b', [i&1, (i+1)&1, i&1, (i+1)&1])
				time.sleep(1)	
				if i==10:
					saved_server=s.get_server_data()
		finally:
			s.restore_server_from_data(saved_server)
			s.close()
			
	if thread_server:	
		sth=threading.Thread(target=s.serve, name='server')
		sth.start()

	th=threading.Timer(1.0,tryit)
	th.start()
	
	def monitor_test(string):
		print get_payload_from_string(string)
		if 0: #try error bailout on server
			raise "oops"

	def quit_server(string):
		flag=get_payload_from_string(string)
		if flag:
			s.close()
	
	s.listen("MyTest", monitor_test)
	s.listen("TestArray", monitor_test)
	s.listen("Boolean", monitor_test)
	s.listen("BooleanArray", monitor_test)
	s.listen("cluster", monitor_test)
	s.listen("quit_server", quit_server)
	
		
	if thread_server:
		th.join()
		sth.join()	#the thread exits when somebody closes the server
	else:
		s.serve()

	s.close()
	time.sleep(1)
		
	del s
