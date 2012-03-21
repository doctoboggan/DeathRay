"""cubic spline handling, in a manner compatible with the API in numpy Recipes"""
_rcsid="$Id: spline.py 323 2011-04-06 19:10:03Z marcus $"

__all__=["spline","splint","cubeinterpolate","RangeError",
"spline_extension", "spline_extrapolate", "approximate_least_squares_spline" ]

class RangeError(IndexError):
	"X out of input range in splint()"

from numpy import zeros, float, searchsorted, array, asarray, take, clip
import numpy

def spline(x, y, yp1=None, ypn=None):
	"""y2 = spline(x_vals,y_vals, yp1=None, ypn=None) 
	returns the y2 table for the spline as needed by splint()"""

	n=len(x)
	u=zeros(n,float)
	y2=zeros(n,float)
	
	x=asarray(x, float)
	y=asarray(y, float)
	
	dx=x[1:]-x[:-1]
	dxi=1.0/dx
	dx2i=1.0/(x[2:]-x[:-2])
	dy=(y[1:]-y[:-1])
	siga=dx[:-1]*dx2i
	dydx=dy*dxi
	
	# u[i]=(y[i+1]-y[i])/float(x[i+1]-x[i]) - (y[i]-y[i-1])/float(x[i]-x[i-1])
	u[1:-1]=dydx[1:]-dydx[:-1] #this is an incomplete rendering of u... the rest requires recursion in the loop
	
	if yp1 is None:
		y2[0]=u[0]=0.0
	else:
		y2[0]= -0.5
		u[0]=(3.0*dxi[0])*(dy[0]*dxi[0] -yp1)

	for i in range(1,n-1):
		sig=siga[i-1]
		p=sig*y2[i-1]+2.0
		y2[i]=(sig-1.0)/p
		u[i]=(6.0*u[i]*dx2i[i-1] - sig*u[i-1])/p

	if ypn is None:
		qn=un=0.0
	else:
		qn= 0.5
		un=(3.0*dxi[-1])*(ypn- dy[-1]*dxi[-1] )
		
	y2[-1]=(un-qn*u[-2])/(qn*y2[-2]+1.0)
	for k in range(n-2,-1,-1):
		y2[k]=y2[k]*y2[k+1]+u[k]

	return y2

def spline_extension(x, y, y2, xmin=None, xmax=None):
	"""x, y, y2 = spline_extension(x_vals,y_vals, y2vals, xmin=None, xmax=None) 
	returns the x, y, y2 table for the spline as needed by splint() with adjustments to allow quadratic extrapolation 
	outside the range x[0]-x[-1], from xmin (or x[0] if xmin is None) to xmax (or x[-1] if xmax is None),
	working from x, y, y2 from an already-created spline"""

	xl=[x]
	yl=[y]
	y2l=[y2]
	
	if xmin is not None:
		h0=x[1]-x[0]
		h1=xmin-x[0]
		yextrap=y[0]+((y[1]-y[0])/h0 - h0*(y2[0]+2.0*y2[1])/6.0)*h1+y2[0]*h1*h1/2.0
		yl.insert(0, (yextrap,))
		xl.insert(0, (xmin,))
		y2l.insert(0, (y2[0],))

	if xmax is not None:
		h0=x[-1]-x[-2]
		h1=xmax-x[-1]
		yextrap=y[-1]+((y[-1]-y[-2])/h0 + h0*(2.0*y2[-2]+y2[-1])/6.0)*h1+y2[-1]*h1*h1/2.0
		yl.append((yextrap,))
		xl.append((xmax,))
		y2l.append((y2[-1],))

	return numpy.concatenate(xl), numpy.concatenate(yl), numpy.concatenate(y2l)

def spline_extrapolate(x, y, yp1=None, ypn=None, xmin=None, xmax=None):
	"""x, y, y2 = spline_extrapolate(x_vals,y_vals, yp1=None, ypn=None, xmin=None, xmax=None) 
	returns the x, y, y2 table for the spline as needed by splint() with adjustments to allow quadratic extrapolation 
	outside the range x[0]-x[-1], from xmin (or x[0] if xmin is None) to xmax (or x[-1] if xmax is None)"""

	return spline_extension(x, y, spline(x,y,yp1,ypn), xmin, xmax) 

import types

def splint(xa, ya, y2a, x, derivs=False):
	"""returns the interpolated from from the spline
	x can either be a scalar or a listable item, in which case a numpy float array will be
	returned and the multiple interpolations will be done somewhat more efficiently.
	If derivs is not False, return y, y', y'' instead of just y."""
	if type(x) is types.IntType or type(x) is types.floatType: 
		if (x<xa[0] or x>xa[-1]):
			raise RangeError, "%f not in range (%f, %f) in splint()" % (x, xa[0], xa[-1])
			 
		khi=max(searchsorted(xa,x),1)
		klo=khi-1
		h=float(xa[khi]-xa[klo])
		a=(xa[khi]-x)/h; b=1.0-a
		ylo=ya[klo]; yhi=ya[khi]; y2lo=y2a[klo]; y2hi=y2a[khi]
	else:
		#if we got here, we are processing a list, and should do so more efficiently
		if (min(x)<xa[0] or max(x)>xa[-1]):
			raise RangeError, "(%f, %f) not in range (%f, %f) in splint()" % (min(x), max(x), xa[0], xa[-1])
	
		npoints=len(x)
		khi=clip(searchsorted(xa,x),1,len(xa)) 
		
		klo=khi-1
		xhi=take(xa, khi)
		xlo=take(xa, klo)
		yhi=take(ya, khi)
		ylo=take(ya, klo)
		y2hi=take(y2a, khi)
		y2lo=take(y2a, klo)
		
		h=(xhi-xlo).astype(float)
		a=(xhi-x)/h
		b=1.0-a
		
	y=a*ylo+b*yhi+((a*a*a-a)*y2lo+(b*b*b-b)*y2hi)*(h*h)/6.0
	if derivs:
		return y, (yhi-ylo)/h+((3*b*b-1)*y2hi-(3*a*a-1)*y2lo)*h/6.0, b*y2hi+a*y2lo
	else:
		return y

		
def cubeinterpolate(xlist, ylist, x3):
	"find point at x3 given 4 points in given lists using exact cubic interpolation, not splining"
	x1,x2,x4,x5=xlist
	x2,x3,x4,x5=float(x2-x1),float(x3-x1),float(x4-x1),float(x5-x1)
	y1,y2,y4,y5=ylist
	y2,y4, y5=float(y2-y1),float(y4-y1),float(y5-y1)
	
	y3=(
			(x3*(x2**2*x5**2*(-x2 + x5)*y4 + x4**3*(x5**2*y2 - x2**2*y5) + x4**2*(-(x5**3*y2) + x2**3*y5) + 
		           x3**2*(x2*x5*(-x2 + x5)*y4 + x4**2*(x5*y2 - x2*y5) + x4*(-(x5**2*y2) + x2**2*y5)) + 
		           x3*(x2*x5*(x2**2 - x5**2)*y4 + x4**3*(-(x5*y2) + x2*y5) + x4*(x5**3*y2 - x2**3*y5))))/
		      	 (x2*(x2 - x4)*x4*(x2 - x5)*(x4 - x5)*x5)
	)+y1
	return y3

from analysis import fitting_toolkit

def approximate_least_squares_spline(xvals, yvals, nodelist=None, nodeindices=None, nodecount=None):
	"""Compute an approximation to the true least-squares-spline to the dataset.  If the <nodelist> is not None,
	nodes will be placed near the x values indicated.  If <nodelist> is None,<nodecount> equally-spaced nodes will be placed.
	Explicit indices for the node placement can be given in nodeindices, which overrides everything else."""
	
	assert nodelist or nodecount or nodeindices, "Must have either a list of nodes or a node count"
		
	fitter=fitting_toolkit.polynomial_fit(2) #will fit quadratic sections
	
	if not nodeindices:
		if not nodelist: #make equally-spaced nodelist
			nodelist=numpy.array(range(nodecount),numpy.float)*((xvals[-1]-xvals[0])/(nodecount-1))+xvals[0]
			nodelist[-1]=xvals[-1] #make sure no roundoff error clips the last point!
		else:
			nodecount=len(nodelist)
			
		nodeindices=numpy.searchsorted(xvals, nodelist)
		boundindices=numpy.searchsorted(xvals, (nodelist[1:]+nodelist[:-1])*0.5) #find halfway points
	else:
		boundindices=(nodeindices[1:]+nodeindices[:-1])//2 
		nodelist=numpy.take(xvals, nodeindices)
		
	nodecount=len(nodeindices)

	ya=numpy.zeros(nodecount,numpy.float)

	#fit first  chunk un-centered to get slope at start
	fitter.fit_data(xvals[:nodeindices[1]], yvals[:nodeindices[1]], xcenter=nodelist[0])
	ya[0]=fitter.funcparams[0]
	yp1=fitter.funcparams[1]

	for i in range(1,nodecount-1):
		chunkstart=boundindices[i-1]
		chunkend=boundindices[i]
		fitter.fit_data(xvals[chunkstart:chunkend], yvals[chunkstart:chunkend], xcenter=nodelist[i])
		ya[i]=fitter.funcparams[0]
	
	#fit last  chunk un-centered to get slope at end
	fitter.fit_data(xvals[nodeindices[-2]:], yvals[nodeindices[-2]:], xcenter=nodelist[-1])
	ya[-1]=fitter.funcparams[0]
	ypn=fitter.funcparams[1]
			
	y2a=spline(nodelist, ya, yp1=yp1, ypn=ypn)
	return nodelist, ya, y2a
	

if __name__=="__main__":
	import traceback
	testlist=((0,1), (1,1),(2,3),(3,4),(4,2),(5,6),(7,9),(10,6),(15,2), (16,-1))
	#testlist=((0,0), (1,1),(2,4),(3,9),(4,16),(5,25),(7,49),(10,100),(15,225), (16,256))
	xlist=[i[0] for i in testlist]
	ylist=[i[1] for i in testlist]
	print "\n\nStarting splint tests...\n", testlist
	y2=spline(xlist,ylist, yp1=-5, ypn=10)
	r=(0,1,2,3.5, 3.7, 4,6,7,2,8,9,10,11, 5, 12,13,14, 15, 16)
	v=splint(xlist, ylist, y2, r)	
	print y2
	for i in range(len(r)):
		print "%.1f %.3f %.3f" % (r[i], v[i], splint(xlist, ylist, y2, r[i]))
	
	v, vp, vpp=splint(xlist, ylist, y2, r, derivs=True)	
	for i in range(len(r)):
		print "%5.1f %10.3f %10.3f %10.3f" % (r[i], v[i], vp[i], vpp[i])
	
	print "The next operations should print exceptions"
	try:
		splint(xlist, ylist, y2, 100.0)
	except:
		traceback.print_exc()
	try:
		splint(xlist, ylist, y2, (1,2,2.5, 3,-5, 4,5,6,7,8,9,10,11,12,13,14,15,16,17,18))
	except:
		traceback.print_exc()
	
	try:
		
		xx, yy, yy2=spline_extrapolate(xlist,ylist, yp1=None, ypn=-2.5, xmin=xlist[0]-2, xmax=xlist[-1]+2)
		import graphite
		import numpy
		g=graphite.Graph()
		ds1=graphite.Dataset()
		ds1.x=xx
		ds1.y=yy
		g.datasets.append(ds1)
		f1 = graphite.PointPlot()
		f1.lineStyle = None
		f1.symbol = graphite.CircleSymbol
		f1.symbolStyle=graphite.SymbolStyle(size=5, fillColor=graphite.red, edgeColor=graphite.red)
		g.formats=[]
		g.formats.append(f1)
		finex=numpy.array(range(-20,181),float)*0.1
		finey=splint(xx, yy, yy2, finex)
		ds2=graphite.Dataset()
		ds2.x=finex
		ds2.y=finey
		g.datasets.append(ds2)
		f2 = graphite.PointPlot()
		f2.lineStyle = graphite.LineStyle(width=1, color=graphite.green, kind=graphite.SOLID)
		f2.symbol = None
		g.formats.append(f2)
		g.bottom=400
		g.right=700
		try:
			graphite.genOutput(g,'QD', size=(800,500))
		except:
			graphite.genOutput(g,'PDF', size=(800,500))
	except:
		import traceback
		traceback.print_exc()
		print "Graphite not available... plotted results not shown"
		
