"Another sample of a vxi-11 scope, with graphics via graphite.  Probably out of date"
_rcsid="$Id: vxi11_scope_test.py 323 2011-04-06 19:10:03Z marcus $"

import vxi_11
import graphite
import time
import traceback
import Numeric

try: #if the persistent scope module exists, use it
	from hp_scope_module import scope
except:
	class hp54542(vxi_11.agilentscope):
		
		default_lock_timeout=5000
		
		idn_head="HEWLETT-PACKARD,54542C,US36040757" #key this device down to the serial-number level
		
		def abort(self): #aborts hang on this device, just override 
			return 0

	if 0:
		scope=hp54542(host="129.59.235.196", portmap_proxy_host="127.0.0.1", portmap_proxy_port=1111,
				 device="gpib0,7",  timeout=4000, device_name="hp54542",
				raise_on_err=1)
	else:
		scope=hp54542(host="129.59.235.196", 
				 device="gpib0,7",  timeout=5000, device_name="hp54542",
				raise_on_err=1)

def dots(color):
	reddots = graphite.PointPlot()
	reddots.lineStyle =None
	reddots.symbol = graphite.SquareSymbol
	reddots.symbolStyle=graphite.SymbolStyle(size=1, fillColor=color, edgeColor=color)
	return reddots

def lines(color):
	reddots = graphite.PointPlot()
	reddots.lineStyle = graphite.LineStyle(width=1, color=color, kind=graphite.SOLID)
	reddots.symbol = None
	return reddots

def test1():
	try:
		scope.lock()
		scope.write("*rst")
		#vxi_11.vxi_11_connection.abort(scope)
		print scope.core.port, scope.abort_channel.port, scope.idn				
		
		grablen=512; loops=1; averages=16; mode="real"; timerange=1e-5
		
		if mode=="rep":
			scope.average_mode(averages)
		else:
			scope.realtime_mode(grablen)

		if 1:  #do setup, which should always be done if the scope has been unlocked, since someone else might have used it.
			scope.set_edge_trigger(2, level=0, slope=-1, auto_trigger=1, coupling=scope.ac)
			scope.set_timebase(range=timerange)
			scope.set_channel(2, range=5, offset=2.5, coupling=scope.dc, lowpass=0, impedance=None)
			scope.set_channel(3, range=0.1, offset=0, coupling=scope.dc, lowpass=0, impedance=None)
		
									
		sum=None
		
		for i in range(loops):
			scope.digitize((2,3))
			scope.wait_for_done(sleep=0.1, max_loops=100)									
			waveform=Numeric.array( scope.get_current_data((2,3)) )
			
			if sum is None:
				sum = waveform
			else:
				sum += waveform
				
			print i
		
		sum *= (1.0/loops)
		
		scope.unlock()

		g=graphite.Graph()
		g.formats=[dots(graphite.green), dots(graphite.red)]
		
		axis=g.axes[graphite.X]
		tick=axis.tickMarks[0]				
		tick.labels = "%.2g"
		axis.label.text = "&mu;Seconds"
		#tick.spacing = 0.05
		#axis.range=[-tick.spacing,plottime]
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
				
		d=graphite.Dataset()
		d.x=scope.xaxis*1e6
		d.y=sum[0]
		g.datasets.append(d)

		d=graphite.Dataset()
		d.x=scope.xaxis*1e6
		d.y=sum[1]
		g.datasets.append(d)

		graphite.genOutput(g,'QD',canvasname="Scope data", size=(800,500))
		#graphite.genOutput(g,'PDF',canvasname="Scope_data", size=(800,500))
	except:
		scope.unlock_completely()
		scope.abort()
		traceback.print_exc()
		
			
test1()
