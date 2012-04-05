"""The underlying support for the National Instruments DataSocket Transport Protocol (nati-dstp, port 3015)
with lots of widgets to make it possible not only to act as a basic server, but for Python code
to interact with the server by storing and retrieving data, which would then be reflected to any
LabVIEW clients listening"""
_rcsid="$Id: nati_dstp_basics.py 323 2011-04-06 19:10:03Z marcus $"

import struct
import array
import socket
import select
import types

try:
	import Numeric
	has_numeric=1
	numArrayType=Numeric.ArrayType
except ImportError:
	has_numeric=0
	numArrayType=0 #bogus type for non-existent arrays
	
prefer_Numeric_arrays=0

def UseNumericArray(flag=0):
	"set flag to 0 to use array.array, or nonzero to use Numeric.array (if available)"
	global prefer_Numeric_arrays
	assert has_numeric or not flag, "Cannot use Numeric.array, since it isn't available"
	prefer_Numeric_arrays=flag


__all__=["pack_object", "pack_object_completely", "parse_composite_object", "parse_typelist_and_string",
		"TimeoutError", "ClosedError", "NATI_DSTP_StreamHandler", "NATI_DSTP_DataServer",
		"UseNumericArray", "get_payload_from_string"]

#global flag for big-endian architectures
bigendian=struct.unpack('L','\1\0\0\0')[0] != 1

def packbytes(bytes):
	"efficiently convert a list of bytes to a string"
	return array.array('B', bytes).tostring()
	
arraytype=packbytes([0,8])
compositetype=packbytes([1,8])
ulonginttype=packbytes([1,3])
longinttype=packbytes([0,3])
ushortinttype=packbytes([1,2])
shortinttype=packbytes([0,2])
ubytetype=packbytes([1,1])
bytetype=packbytes([0,1])
stringtype=packbytes([0,9])
doubletype=packbytes([2,4])
floattype=packbytes([2,3])
booleantype=packbytes([2,1])

def getstr(objd, string):
	"extract a string with a little endian length from a buffer, and return string and offset to next data"
	l=struct.unpack("<L", string[:4])[0]
	return string[4:4+l], 4+(l+1)&(-2) #always even length, so pad

def getarray(objd, string):
	"extract an array described by object descriptor objd, and return ( (dimsizes, flattened array), <offset to next data>" 
	dimcount, objtypelen, atype=struct.unpack("<HL2s", objd[6:14])
	assert not atype in (compositetype, stringtype), "No variable-size-element arrays yet"
	elemsize, format=objectunpackers[atype]
	elems=1L
	dimsizes=[]
	for i in range(dimcount):
		dim=struct.unpack("<L",string[4*i:4*i+4])[0]
		dimsizes.append(dim)
		elems*=dim
	arraybytes=elems*elemsize
	data=array.array(format[1])
	data.fromstring(string[4*dimcount:4*dimcount+arraybytes])
	if bigendian:
		data.byteswap()	
	if prefer_Numeric_arrays:
		#hoping array.array typecodes correspond with Numeric.array typecodes
		data=Numeric.array(data, data.typecode) #do this after byteswapping, which only array.array knows how to do
		
	return (dimsizes, data), (4*dimcount+arraybytes+1) & (-2)
	
objectunpackers={
	longinttype: (4,"<l"),
	ulonginttype: (4,"<L"),
	ushortinttype: (2,"<H"),
	shortinttype: (2,"<h"),
	ubytetype: (1,"<B"),
	bytetype: (1,"<b"),
	doubletype:(8,"<d"), 
	floattype:(4,"<f"), 
	stringtype:  getstr,
	arraytype: getarray, 
	booleantype:(1,"<b"),
}

def pack_str(string):
	"convert string to NI format with length and even padding"
	pad=''
	s=struct.pack("<L",len(string))+string
	if len(s) & 1:
		pad='\0' #always pad to even
	return stringtype, s+pad

arraytypecodemap={
	'l' :longinttype,
	'L': ulonginttype,
	'd':doubletype,
	'f':floattype,
	'B':ubytetype,
	'b':booleantype,
	'H':ushortinttype,
	'h':shortinttype,
}

def pack_array(data):
	"convert array to NI format"
	if type(data) is numArrayType:
		typecode=data.typecode()
		if bigendian: #must swap bytes
			d=array.array(data.typecode())
			d.fromstring(data.tostring())
			d.byteswap()
			datastr=d.tostring()
		else:
			datastr=data.tostring()
	elif bigendian:
		typecode=data.typecode
		data.byteswap()		
		datastr=data.tostring()
		data.byteswap()	#don't want to leave data hideously swapped
	else:
		typecode=data.typecode
		datastr=data.tostring()

	packtype=arraytypecodemap.get(typecode, None)
	#print data, typecode, `packtype`, `datastr`
	
	assert packtype, "No idea how to pack array of type: "+data.typecode
	header=struct.pack("<2sHL2s",arraytype,1,6,packtype)
	return header, struct.pack("<L",len(data))+datastr	

objectpackers={ #only re-pack from reasonable python types
	type(1L):(ulonginttype, "<L", 1),
	type(1.0): (doubletype, "<d", 1),
	type(""): (stringtype, pack_str, 0),
	type([]): (compositetype, 0, 0),
	type(1): (longinttype, "<l", 1),
	array.ArrayType: (arraytype, pack_array, 0),
	numArrayType: (arraytype, pack_array, 0),
}

def pack_object(obj):
	"pack a python data type into NI format, returning the descriptor and data separately"
	this=type(obj)
	assert this in objectpackers, "Attempting to pack unknown object: " + str(obj)
	if this is types.ListType: #recursive run through composite object
		datastr=''
		typestr=compositetype+struct.pack("<H", len(obj))
		for item in obj:
			obtypes, datas = pack_object(item)
			datastr+=datas
			typestr+=obtypes
	else:
		typestr, packer, use_struct = objectpackers[this]
		if use_struct:
			datastr=struct.pack(packer, obj)
		elif packer:
			typestr, datastr=packer(obj)
	return struct.pack("<L", len(typestr)+4)+typestr, datastr

def pack_object_completely(obj):
	"pack an object into a full packet, where the length header describes the entire length, rather than the descriptor length"
	t,d = pack_object(obj)
	s=(t+d)[4:] #combine and strip length header
	return struct.pack("<L", len(s)+4)+s #and return with complete header

def parse_composite_object(string, max_items=None):
	"recursively parse one composite object of type (1,8), not including a length header, and stopping at end or after <max_items>"
	types=[]
	chunklen, objtype, count=struct.unpack("<L2sH",string[:8])
	assert objtype==compositetype, "attempt to unpack non-composite object, type=%04x" %objtype
	string=string[8:]
	for i in range(count):
		chunklen, objtype=struct.unpack("<L2s",string[:6])
		if objtype==compositetype or objtype==arraytype:
			objdata=string[:chunklen] #just save it raw for later descent, if needed
		else:
			objdata=''
		string=string[chunklen:]
		types.append( (objtype, objdata) )

	if max_items is not None and (max_items < len(types)):
		types, leftovers=types[:max_items], types[max_items:]	
	else:
		leftovers=()

	vals, string = parse_typelist_and_string(types, string)	
	return vals, (leftovers, string)
	
def parse_typelist_and_string(typelist, string):	
	vals=[]	
	for objt, objd in typelist:
		if objt==compositetype:
			v, leftovers = parse_composite_object(objd+string) #pass a synthetic string down for recursion
			noleftovers, string = leftovers
		else:
			handler=objectunpackers.get(objt,None)
			if not handler:
				print 'unknown object type: ', array.array('B', objt), array.array('B', string[:20])
				return ([],'')
			if type(handler) is types.TupleType: #tuples just use struct.unpack
				l, f = handler
				v=struct.unpack(f, string[:l])[0]
				string=string[(l+1)&(-2):] #all real lengths are even
			else:
				v, l = handler(objd, string)
				string=string[l:]
		vals.append(v)	
	return vals, string

class TimeoutError(IOError):
	pass

class ClosedError(IOError):
	pass


def recvfrag_with_timeout(sock, timeout_seconds=1.0):
	"receive a dstp packet with timeout handling"
	rlist, wlist, xlist=select.select([sock],[],[], timeout_seconds)
	if not rlist:
		raise TimeoutError, "No header at all in recvfrag()"
	header = sock.recv(4)
	if not header:
		raise ClosedError, "No header at all in recvfrag()"	
	elif len(header) < 4:
		raise EOFError, "incomplete header in recvfrag(), length: "+str(len(header))
	n = struct.unpack("<L",header)[0] #grab little-endian length word 
	
	#preallocate an array for the data to speed up storing it
	frag=array.array('c',n*'\0')
	frag[:4]=array.array('c',header)
	start=4
	
	while(start<n):	
		rlist, wlist, xlist=select.select([sock],[],[], timeout_seconds)
		if not rlist:
			raise EOFError, "Broken data after header in recvfrag()"
		newchunk = array.array('c',sock.recv(n-start))
		l=len(newchunk)
		frag[start:start+l]= newchunk
		start+=l
	return frag.tostring()

def sendfrag_with_timeout(sock, block, timeout_seconds=1.0):
	"send a packet with timeout handling"
	n=len(block)
	nsent=0
	while(nsent<n):
		rlist, wlist, xlist=select.select([],[sock],[], timeout_seconds)
		if not wlist:
			raise EOFError, "Blocked write in sendfrag()"		
		nsent+=sock.send(block[nsent:])

class NATI_DSTP_StreamHandler:
	def __init__(self, server, request, read_timeout=1.0):
		self.server=server
		self.request=request
		self.read_timeout=read_timeout
				
	def respond(self, bytes):
		sendfrag_with_timeout(self.request, bytes)
	
	def blackhole(self, string, req, payload):
		return
			
	def firstecho(self, string, req, payload):
		self.respond(pack_object_completely([9,2]))

	def listen(self, string, req, payload):
		result=self.server.listen(req[1], self.respond)
		fullrequest=parse_composite_object(string)[0]
		self.respond(pack_object_completely([6, fullrequest[1], fullrequest[2]])) #first send usual connect string
		self.respond(result) #and send whatever data we already have...
		
	def store(self, string, req, payload):		
		self.server.store(req[1], string)

	def delete_listener(self, string, req, payload):
		self.server.unlisten(req[1], self.respond)	

	def close(self):
		try:
			self.request.shutdown(2)
		except socket.error:
			pass
		raise ClosedError, "handler exited"
	
	def goodbye(self, string, req, payload):
		self.close()

	commandhandlers=[None,  blackhole, firstecho, goodbye, listen, delete_listener, store ] 
			
	def handle_one_request(self, sock):
		r=self.request
		try:
			line = recvfrag_with_timeout(r, timeout_seconds=self.read_timeout) #if we got here, select already says we have data, so be impatient				
		except TimeoutError:
			return #huh!?, we should have had data!
						
		req, payload=parse_composite_object(line, max_items=2) #just for databasing, don't try to parse payload (3rd item in object)
		command=req[0]
		if self.server.debug:
			print "handling command ", command
		self.commandhandlers[command](self, line, req, payload)

class NATI_DSTP_DataServer:
	def __init__(self):
		self.__data={} #since this is a mix-in, and 'data' is pretty generic, make it private
		self.debug=0
		
	def log_exception(self, explanation=''):
		print explanation
		traceback.print_exc()

	def store(self, name, packed_string_or_tuple, force=0, never_send=0):
		"store a packed DSTP structure in element <name>, and echo it to everyone listening"
		name=name.upper()			
		d=self.__data #our data dictionary
		
		me=d.get(name,None)

		if not me: #add new key to dictionary
			d[name]= me = [[], '', {}] #list of listeners,  payload, and other information
	
		if type(packed_string_or_tuple) is types.TupleType: #a tuple of (header, data) needs repacking with correct length
			s=packed_string_or_tuple[0]+packed_string_or_tuple[1]
			packed_string=struct.pack("<L",len(s))+s[4:]
		else:
			packed_string=packed_string_or_tuple

		unchanged=(me[1]==packed_string)
		
		me[1]=packed_string #store packet

		if never_send or ((not force) and unchanged):
			return #data didn't change, don't waste time updating

		self.echo_data(me)
	
	def echo_data(self, me):
		listeners, packed_string=me[:2]
		deadlisteners=[]		
		for target in listeners: #the key is the value, no need to retrieve
			try:
				target(packed_string)
			except: #if data can't be sent, don't keep trying
				deadlisteners.append(target)
				if self.debug:
					self.log_exception("Disconnecting device from server due to exception sending data")
		for i in deadlisteners:
			try:
				listeners.remove(i) #unregister on error
			except ValueError:
				pass #maybe someone else tossed them while we weren't looking

	def listen(self, name, listener):
		"add <listener(string)> to the list of entities to be notified of changes to <name>"
		name=name.upper()
		d=self.__data #our data dictionary
		if name not in d: #add new key to dictionary
			string=pack_object_completely([6,name, 0])
			d[name]=[[], string, {}] #list of listeners, and payload		
		if listener not in d[name][0]: #we aren't registered
			d[name][0].append(listener)
		
		return d[name][1] #return data string
	
	def unlisten(self, name, listener):
		name=name.upper()			
		d=self.__data #our data dictionary
		try:
			d[name][0].remove(listener)
		except ValueError:
			if self.debug:
				self.log_exception("Couldn't delete listener")
			pass

	def bind_field_info(self, field_info):
		"return information of the type needed to access fields on this device"
		name, initial_value=field_info
		objt, objd = pack_object([6,name,initial_value])
		self.store(name, (objt, objd), never_send=1 ) #write a value to create the field		
		data=self.__data[name.upper()][2]
		data["structure"]=objt, initial_value #store the header and a sample 
		return self.read_field, self.write_field, self.write_field, name
				
	def write_field(self, name, value):
		"write_field(name, value) writes data now, so on return it is guaranteed to be sent"
		data=self.__data[name.upper()][2]
		objt, objd = pack_object([6,name,value])
		structure, sample=data["structure"]
		assert objt==structure, "Incompatible DSTP data in field: " + str(name)+",  expected: "+str(sample)+", got: "+str(value)
		self.store(name, (objt, objd))
			
	def read_field(self, name):
		return parse_composite_object(self.__data[name.upper()][1])[0][-1] #last stored item is actualy payload
			
	def get_server_data(self):
		"extract data from the server dictionary, but with socket keys deleted since they are meaningless"
		newdict={}
		keys=tuple(self.__data.keys()) #freeze a copy
		for k in keys:
			try:
				listeners, data, extras=self.__data[k]
				newdict[k]=[data, extras]
			except KeyError:
				pass		
		return newdict
	
	def restore_server_from_data(self, newdict):
		"restore the server data without losing any current connections. Beware of changes arising during reset!"
		for k in newdict.keys():
			data, extras=newdict[k]
			if k not in self.__data:
				self.__data[k]=[{}, data, extras]
			else:
				self.__data[k][1:]=[data, extras]
			self.store(k, data, force=1) #store and transmit to listeners
		
def get_payload_from_string(string):
	return parse_composite_object(string)[0][-1] #last stored item is actualy payload
		
if __name__=='__main__':
	def raw_unpacker_test():
		"try out some raw bytes for unpacking"
		data=[92,0,0,0,1,8,5,0, #92 byte composite object with 5 elements
				6,0,0,0,0,3, #element 1, u32
				6,0,0,0,0,3, #element 2, u32
				6,0,0,0,0,9, #element 3, string
				20,0,0,0,1,8,2,0, #element 4, composite with 2 elements, descriptor length=20 bytes
					6,0,0,0,0,3, #u32
					6,0,0,0,0,3,  #u32
				6,0,0,0,0,3, #u32
				1,0,0,0, #data for 1st u32
				0,1,0,0, #data for second u32
				11,0,0,0,65,66,67,68,69,97,98,99,100,101,102,0, #4byte length, string, pad byte
				123,0,0,0,234,0,0,0,  #u32, u32 data for embedded composite object
				0,0,1,0 #u32
			]
		
		datastr=array.array('B', data).tostring()
		vals, leftovers = parse_composite_object(datastr, max_items=2)
		print vals
		print leftovers
		
		print parse_typelist_and_string(leftovers[0], leftovers[1])[0]
		
	def packer_unpacker_test():
		"try out inverse functions for packing and unpacking"
		o=pack_object_completely([3,'hello', 2,[0.3,'goodbye',-1]])
		print `o`
		print parse_composite_object(o)[0]
		
		o=pack_object_completely([array.array('h',[1,2,3,4,5,4,3,2,1,0,-1])])
		print `o`
		print parse_composite_object(o)[0]
	
	raw_unpacker_test()
	packer_unpacker_test()

