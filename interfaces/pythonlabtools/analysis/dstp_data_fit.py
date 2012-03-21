"""A shakedown application for the use of the dstp server.  Maybe out of date"""
_rcsid="$Id: dstp_data_fit.py 323 2011-04-06 19:10:03Z marcus $"

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__),"data acquisition")) #look in 'data acquisition' folder for needed routines, too

import time
import threading
import array
import traceback
import Numeric
import math

import nati_dstp_basics
import tagged_data
import dstp_async


nati_dstp_basics.UseNumericArray(1) #use Numeric.array instead of array.array as standard format

print "go!"

s=dstp_async.DSTPServer()

data=tagged_data.tagged_data_system() #create a data cache with neatly nameable elements 

#define data types in the cache, and what device is responsible for them, and what format they have:
#data.define_field(<visible_name>, <device>, <internal name on device>, <sample object for this field>, <writable>
#note that for DSTP devices, the <internal name on device> much match the DSTP URL given in labVIEW (not case sensitive)
data.define_field("XY", s, ("xyvals", [array.array('d',[]), array.array('d',[])]), writable=0)
data.define_field("fitparms", s, ("parms", [0,array.array('d'),0.0,array.array('d')]), writable=1)
data.define_field("quit_server", s, ("quit_server", 0), writable=0)

#create a routine to listen for shutdown commands
def quit_server(string):
	if data.quit_server:
		s.close()
#tell the server to pass shutdown commands to this routine
s.listen("quit_server", quit_server)

try:
	loopcount=0

	def run_fit(string):
		global loopcount
		
		try:
			#note that arrays get passed flattened, and with the original dimensioning info in a tuple with the array.  I will fix this later.
			(xl,x),(yl,y)=data.XY
			
			#print x,y 
			loopcount += 1 #make sure each time we send data, this is different, so LabVIEW notices the change
			
			y*=7.0 #bogus data processing (put real fitting here)
			
			data.fitparms=[loopcount,y,math.sqrt(Numeric.sum((y-1)*(y-1))), y-1] #send computed results back to LabVIEW

		except: #clean up on errors
			traceback.print_exc() #dump what went wrong, then close the server so we can edit the program
			s.close()		
			
	#tell the server that any time new data appears in 'xyvals' to call 'run_fit'
	s.listen("xyvals", run_fit)
	
	#start server 
	s.serve()	
		
finally: #clean up on exit or errors
	s.close()
	time.sleep(1)
