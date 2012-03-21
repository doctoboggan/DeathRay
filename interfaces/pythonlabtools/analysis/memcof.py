"""Compute maximum entropy coefficients for data. Based loosely on the the
concepts in "Numerical Recipes in C", 2nd ed., by Press, Flannery, Teukolsky and Vetterling (q.v.)
but I don't think it is any copyright infringement"""
_rcsid="$Id: memcof.py 323 2011-04-06 19:10:03Z marcus $"

import numpy
import math

def memcof(data, poles):
	n=len(data)
	xms=numpy.dot(data,data)/float(n)
	wk1=data[:-1]
	wk2=data[1:]
	d=numpy.zeros(poles,numpy.float64)
	
	for k0 in range(poles):
		num=numpy.dot(wk1,wk2)
		denom=numpy.dot(wk1, wk1)+numpy.dot(wk2, wk2)
		d[k0]=2.0*num/denom
		xms*=(1.0-d[k0]**2)
		if k0!=0:
			d[:k0]=wkm-d[k0]*wkm[-1::-1]			
		if k0!=poles-1:
			wkm=d[:k0+1]
			wk1, wk2 = wk1[:-1]-wkm[k0]*wk2[:-1], wk2[1:]-wkm[k0]*wk1[1:]

	return xms, d


def evlmem(fdt, d, xms):
	n=len(d)
	theta=2*math.pi*fdt*(numpy.array(range(1,n+1), numpy.float64))
	zr=1.0-numpy.dot(numpy.cos(theta), d)
	zi=numpy.dot(numpy.sin(theta), d)
	return xms/(zr*zr+zi*zi)
	

if __name__=="__main__":
	
	datalen=10000
	poles=20
	zfreq=0.21345
	pspoints=200
	damping=-20.0/datalen
	noise=1.0
	
	xvals=numpy.array(range(datalen),numpy.float64)
	data=numpy.sin(xvals*(2.0*math.pi*zfreq)) * numpy.exp(xvals*damping)
	import random
	r=random.Random(1234)
	data+= numpy.array([r.random()-0.5 for i in range(datalen)])*noise
	
	d2=numpy.dot(data,data)/datalen #mean-square power
	
	xms, d = memcof(data, poles)
	
	freqlist = [0.5*i/pspoints for i in range(pspoints)]
	pspect = [evlmem(f, d, xms) for f in freqlist]
	
	pssum=2.0*numpy.sum(pspect)*(0.5/pspoints)
	
	print "input power = ", d2, "output power = ", pssum, "ratio =", pssum/d2
	
