"A concrete test sample of using a vxi-11-based oscilloscope. Probably not up-to-date with distro"
_rcsid="$Id: phase_digitizer_scope.py 323 2011-04-06 19:10:03Z marcus $"

import vxi_11
import graphite
import time
import traceback
import Numeric
import exceptions

from hp_scope_module import scope

def dots(color):
	reddots = graphite.PointPlot()
	reddots.lineStyle =None
	reddots.symbol = graphite.SquareSymbol
	reddots.symbolStyle=graphite.SymbolStyle(size=1, fillColor=color, edgeColor=color)
	return reddots

def lines(color):
	reddots = graphite.PointPlot()
	reddots.lineStyle = graphite.LineStyle(width=0.5, color=color, kind=graphite.SOLID)
	reddots.symbol = None
	return reddots

def test1():
	try:
		scope.lock()
		#scope.write("*rst")
		#vxi_11.vxi_11_connection.abort(scope)
		print scope.core.port, scope.abort_channel.port, scope.idn				
		
		#scope.set_edge_trigger(1, level=0.10, slope=1, auto_trigger=0, coupling=scope.dc)
		scope.set_edge_trigger(4, level=0.9, slope=1, auto_trigger=0, coupling=scope.dc)
		scope.set_channel(1, range=1, offset=0, coupling=scope.ac, atten=10.0, lowpass=0, impedance=None)
		scope.set_channel(2, range=5, offset=0, coupling=scope.dc, atten=1.0, lowpass=0, impedance=None)
		scope.set_channel(3, range=1, offset=1.2, coupling=scope.dc, atten=10.0, lowpass=1, impedance=None)
		scope.set_channel(4, range=1, offset=0.4, coupling=scope.dc, atten=1.0, lowpass=0, impedance=50)
		scope.end_sequential_mode()
		
		plotqd=1
		plotpdf=0
		xrange=None
		channels=(1,2,3)
		
		if 0: #plot one really slow plot
			grablen=8192;  timerange=1e-2 ; loops=1; plotskip=1
			scope.realtime_mode(grablen)
			scope.set_timebase(range=timerange, reference=scope.left, delay=-2e-8)
			#timescale=1e6; timename="&mu;Seconds"
			timescale=1e3; timename="milliSeconds"
			#timescale=1e9; timename="nanoSeconds"
			#xrange=[-20,60]
			channels=(2,3)
		if 1:
			timerange=2e-7 ; loops=1; plotskip=1
			scope.sequential_mode(npoints=80, nsegments=50)
			scope.set_timebase(range=timerange, reference=scope.left, delay=770e-9)
			timescale=1e9
			timename="nanoSeconds"
			channels=(1,2)
			plotqd=1
			plotpdf=1
			
		if 0:
			grablen=512;  timerange=1e-7 ; loops=1; plotskip=1
			scope.realtime_mode(grablen)
			scope.set_timebase(range=timerange, reference=scope.left, delay=-2e-7)
			#timescale=1e6; timename="&mu;Seconds"
			timescale=1e9; timename="nanoSeconds"
			#xrange=[-50,60]
			channels=(1,2,3,4)
		if 0:
			timerange=2e-7 ; loops=1; plotskip=1
			scope.sequential_mode(npoints=50, nsegments=1000)
			scope.set_timebase(range=timerange, reference=scope.left, delay=-2e-9)
			timescale=1e9
			timename="nanoSeconds"
			plotqd=0
			plotpdf=0
			
		if 0:
			timerange=1e-7 ; loops=1; plotskip=1
			scope.set_timebase(range=timerange, reference=scope.left, delay=-2e-9)
			scope.average_mode(16)
			xrange=[-20,60]
			timescale=1e9; timename="nanoSeconds"
									
		sum=None
		
		for i in range(loops):
			scope.digitize(channels)
			scope.wait_for_done(sleep=0.1, max_loops=1000)									
			waveform=Numeric.array( scope.get_current_data(channels) )
			
			if sum is None:
				sum = waveform
			else:
				sum += waveform
			
		try:
			times=(scope.get_time_tags()*480+0.5).astype(Numeric.Int) #if we have tags, print them as multiples of 1/480 second
			oops=Numeric.nonzero((times[1:]-times[:-1])-1)
			print oops
			print oops[1:]-oops[:-1]
			
			ranges=[]
			np=scope.preamble["POINTS"]
			for i in oops:
				ranges+=range((i-5)*np,(i+5)*np)
			sum=Numeric.take(sum,ranges,-1)
			scope.xaxis=Numeric.take(scope.xaxis, ranges, -1)
			
		except exceptions.AssertionError:
			pass
			
		sum *= (1.0/loops)
		
		scope.unlock()
		
		if plotqd or plotpdf:
	
			g=graphite.Graph()
			
			axis=g.axes[graphite.X]
			tick=axis.tickMarks[0]				
			tick.labels = "%.0f"
			scope.xaxis*=timescale
			axis.label.text = timename
			#tick.spacing = 0.05
			if xrange is not None: axis.range=xrange
			
			axis.label.points[0]=(0., -0.1, 0.) #move label closer to axis
			
			axis=g.axes[graphite.Y]
			tick=axis.tickMarks[0]
			tick.labels = "%+.3f"
			axis.label.text = "Volts"				
			tick.inextent= 0.02
			tick.labelStyle=graphite.TextStyle(hjust=graphite.RIGHT, vjust=graphite.CENTER, 
				font=graphite.Font(10,0,0,0,None), 
				color=graphite.Color(0.00,0.00,0.00))
			tick.labeldist=-0.01
			axis.label.points[0]=(-0.07, 0, 0.) #move label closer to axis
			
			
			g.top = 25
			g.bottom=g.top+400
			g.left=100
			g.right=g.left+600		
			
			for row in sum:		
				d=graphite.Dataset()
				d.x=scope.xaxis[::plotskip]
				d.y=row[::plotskip]
				g.datasets.append(d)
			
			if plotqd:
				g.formats=[dots(graphite.green), dots(graphite.red), dots(graphite.blue), dots(graphite.orange)]
				graphite.genOutput(g,'QD',canvasname="Scope data", size=(800,500))
			if plotpdf:
				g.formats=[lines(graphite.green), lines(graphite.red), lines(graphite.blue), lines(graphite.orange)]
				graphite.genOutput(g,'PDF',canvasname="Scope_data", size=(800,500))
			
	except:
		scope.clear()
		scope.unlock_completely()
		scope.abort()
		traceback.print_exc()
		
			
test1()
