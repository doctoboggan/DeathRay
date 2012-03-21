"""Compute Hermite-Gauss basis functions very quickly and efficiently using 
Numerov's method to solve the underlying differential equations"""
_rcsid="$Id: hermite_numerov.py 323 2011-04-06 19:10:03Z marcus $"

import math
import Numeric
import spline
import time

hermite_x_bound=15.0
hermite_n_points=5000

def generate_table(order, final_x=None, npoints=None):
	"generate a spline table of H[n](x) exp(-x^2/2) ... a Hermite-Gauss basis function, using the Numerov method"
	if final_x is None:
		final_x=hermite_x_bound

	if npoints is None:
		npoints=hermite_n_points

	Y=Numeric.zeros(npoints+1, Numeric.Float)
	dx=float(final_x)/npoints
	dx2=dx*dx
	e2=2*order+1
	x=-final_x+Numeric.array(range(npoints+1),Numeric.Float)*dx
	V=(x*x-e2)
	
	ypsifact=1.0/(1.0-(dx*dx/12.0)*V)
	coef=2.0+dx2*V*ypsifact

	Y[0]=1.0/ypsifact[0]
	Y[1]=math.exp(math.sqrt(V[0])*dx))/ypsifact[1]
			
	for i in range(1,npoints):
		yy=Y[i+1]=Y[i]*coef[i]-Y[i-1]
		if abs(yy) > 1e20: #don't let exponential blow up
			Y*=1e-20

	psi = Y*ypsifact

	x=-final_x+Numeric.array(range(2*npoints+1),Numeric.Float)*dx
	
	if order%2 == 0: #even function
		y=Numeric.concatenate((psi, psi[::-1][1:]))
	else:
		psi[-1]=0 #enforce oddness exactly
		y=Numeric.concatenate((psi, -psi[::-1][1:]))

	y=y*math.sqrt(1.0/(Numeric.dot(y,y)*dx))
	y2=spline.spline(x, y)
	return (final_x, x,y,y2)

hermite_cache={}

def hermite_gauss(order,x, cache_key=None):
	"compute h[order](x)*exp(-x^2/2).  x may be an array, and cache_key should be a unique identifier for x if cacheing is desired."
	if type(x) is not type(1.0):
		xmax=max(abs(x))
	else:
		xmax=abs(x)
		
	if (not hermite_cache.has_key(order)) or hermite_cache[order][0] < xmax:
		q=generate_table(order, max(1.5*xmax, hermite_x_bound))
		hermite_cache[order]=q
	
	if cache_key and hermite_cache.has_key((order, cache_key)):
		hermite_cache[(order, cache_key)][0]=time.time() #update time stamp
		return hermite_cache[(order, cache_key)][1]
	else:
		xmax, xa, ya, y2a=hermite_cache[order]
		y= spline.splint(xa, ya, y2a, x)
		if cache_key:
			hermite_cache[(order,cache_key)]=[time.time(), y]
		return y

def purge_cache():
	"purge_cache() clears all pre-gridded datasets from the cache, leaving the raw interpolating functions"
	k=hermite_cache.keys()
	for i in k:
		if type(i) is not type(1):
			del hermite_cache[i]

integral_cache={}

def hermite_gauss_integral(m, n, x0, x1, stepsize=0.01):
	"compute integral(h[m](x}*h[n](x)*exp(-x^2),{x,x0,x1})"
	if m>n:
		m,n = n,m #always make m<=n
	xmax=max(abs(x0), abs(x1))
	if not integral_cache.has_key((m,n)) or integral_cache[(m,n)][0] < xmax:
		#just use Simpson's rule for this
		#first, load up cache
		hermite_gauss(m,xmax)
		hermite_gauss(n,xmax)
		xm, xa1, ya1, y2a1 = hermite_cache[m]
		xm, xa2, ya2, y2a2 = hermite_cache[n]

		stepcount=int(2.0*xmax/stepsize)
		if stepcount%2==0:
			stepcount=stepcount+1 #always odd for Simpson
		stepsize=2*xmax/(stepcount-1) #exact step size
		xlist=Numeric.array(range(stepcount),Numeric.Float)*stepsize - xmax
		y=spline.splint(xa1, ya1, y2a1, xlist)*spline.splint(xa2, ya2, y2a2, xlist)
		hmn2=spline.spline(xlist, y)
		yint=Numeric.cumsum(y[0:-2:2]+y[2::2]+4.0*y[1::2])*(stepsize/3.0)
		yint=Numeric.concatenate( ( (0,), yint )) #first element of integral is 0
		yi2=spline.spline(xlist[::2], yint)
		integral_cache[(m,n)]=(xmax, xlist[::2], yint, yi2, stepsize, xlist, y, hmn2)

	xmax, xa, ya, y2a, stepjunk, xjunk, yjunk, hmn2junk=integral_cache[(m,n)]
	iv1, iv2=spline.splint(xa, ya, y2a, (x0, x1) )
	return iv2-iv1

def hermite_gauss_matrix_element(m, n, x0, x1, f, stepsize=0.01):
	"compute integral(h[m](x}*h[n](x)*exp(-x^2)*f(x),{x,x0,x1}) : f should be able to be evaluated with a vector x"
	if m>n:
		m,n = n,m #always make m<=n
	xmax=max(abs(x0), abs(x1))
	if not integral_cache.has_key((m,n)) or integral_cache[(m,n)][0] < xmax:
		hermite_gauss_integral(m,n,x0,x1) #preload cache with raw data

	jxmax, jxa, jya, jy2a, jstepsize, xa, hmn, hmn2=integral_cache[(m,n)]
	
	stepcount=int((x1-x0)/stepsize)
	if stepcount%2==0:
		stepcount=stepcount+1 #always odd for Simpson
	stepsize=(x1-x0)/(stepcount-1) #exact step size
	xlist=Numeric.array(range(stepcount),Numeric.Float)*stepsize + x0
	y=spline.splint(xa, hmn, hmn2, xlist)*f(xlist)
	yint=Numeric.sum(y[0:-2:2]+y[2::2]+4.0*y[1::2])*(stepsize/3.0)
	return yint

if __name__=="__main__":
	print "\n***Start"
	for m in range(10):
		for n in range(10):
			print m,n,("%10.4f " % hermite_gauss_integral(m,n,-10., 10.)), 
			print "%10.4f" % hermite_gauss_matrix_element(m,n,-.5, 0.5, lambda x: 1.0),
			print "%10.4f" % hermite_gauss_integral(m,n,-.5, 0.5)
		

		
		
		
	   

