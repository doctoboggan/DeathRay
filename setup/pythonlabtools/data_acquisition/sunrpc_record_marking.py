"sunrpc_record_marking implements the Record Marking Standard such as used in SunRPC records sent via sockets per RFC-1831 section 10"

_rcsid="$Id: sunrpc_record_marking.py 323 2011-04-06 19:10:03Z marcus $"

from select import select as _select

class NoDataError(EOFError):
	pass

class BrokenFragmentError(EOFError):
	pass

class BlockedWriteError(EOFError):
	pass


def sendfrag_with_timeout(sock,  last, frag, timeout_seconds=None):
	x = len(frag)
	if last: x = x | 0x80000000L
	header = (chr(int(x>>24 & 0xff)) + chr(int(x>>16 & 0xff)) + \
		  chr(int(x>>8 & 0xff)) + chr(int(x & 0xff)))
	block=header+frag
	n=len(block)
	nsent=0
	while(nsent<n):
		if _select and timeout_seconds:
			rlist, wlist, xlist=_select([],[sock],[], timeout_seconds)
			if not wlist:
				raise BlockedWriteError		
		nsent+=sock.send(block[nsent:])
	
def recvfrag_with_timeout(sock, timeout_seconds=None):
	if _select and timeout_seconds:
		rlist, wlist, xlist=_select([sock],[],[], timeout_seconds)
		if not rlist:
			raise NoDataError

	header = sock.recv(4)
	if not header:
		raise NoDataError #somehow, we got a _select response but still no data
		
	if len(header) < 4:
		raise BrokenFragmentError
	x = long(ord(header[0]))<<24 | ord(header[1])<<16 | \
	    ord(header[2])<<8 | ord(header[3])
	last = ((x & 0x80000000L) != 0)
	n = int(x & 0x7fffffff)
	
	frag=''
	
	while(len(frag) < n):	
		if _select and timeout_seconds:
			rlist, wlist, xlist=_select([sock],[],[], timeout_seconds)
			if not rlist:
				raise BrokenFragmentError
			
		frag += sock.recv(n-len(frag))
				
	return last, frag


def recvrecord(sock, timeout_seconds=None):
	record = ''
	last = 0
	while not last:
		last, frag = recvfrag_with_timeout(sock, timeout_seconds)
		record = record + frag
	return record

def sendrecord(sock, record, timeout_seconds=None):
	sendfrag_with_timeout(sock, 1, record, timeout_seconds)


