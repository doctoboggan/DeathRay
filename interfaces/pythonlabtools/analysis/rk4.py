"simple 4th order Runge-Kutta integration"
_rcsid="$Id: rk4.py 323 2011-04-06 19:10:03Z marcus $"

from Numeric import *

rk4nsave=0

def rk4(y, dydx, n, x, h, yout, derivs):
	
	global rk4nsave, dyt, dym, yt
	
	if n!=rk4nsave:
		dyt=zeros(n,Float)
		dym=zeros(n,Float)
		yt=zeros(n,Float)
		rk4nsave=n
	
	hh=h*0.5
	h6=h/6.0
	xh=x+hh
	
	#dyt=derivs(xh, hh*dydx+y) the fast way
	multiply(dydx, hh, yt)
	add(yt, y, yt)
	derivs(xh, yt, dyt)
	
	#dym=derivs(xh, hh*dyt+y)
	multiply(hh, dyt, yt)
	add(yt, y, yt)
	derivs(xh, yt, dym)
	
	#yt=h*dym+y
	#dym=dym+dyt
	multiply(dym, h, yt)
	add(yt, y, yt)
	add(dym, dyt, dym)
	
	derivs(x+h, yt, dyt)
	
	#yout=h6*(2.0*dym+dyt+dydx)+y
	multiply(dym, 2.0, yt)
	add(yt, dyt, yt)
	add(yt, dydx, yt)
	multiply(yt, h6, yt)
	add(yt, y, yout)

def rk4dumb(vstart, nvar, x1, x2, nstep, derivs):
	
	v=zeros(nvar, Float)
	vout=zeros(nvar,Float)
	dv=zeros(nvar,Float)
	
	y=zeros((nstep+1, nvar),Float)
	xx=zeros(nstep+1,Float)
	
	y[0,:]=vstart[:]
	v[:]=vstart[:]
	
	xx[0]=x1
	x=x1
	h=(x2-x1)/nstep
	
	for k in range(nstep):
		derivs(x, v, dv)
		rk4(v, dv, nvar, x, h, vout, derivs)
		x += h
		xx[k+1]=x
		v[:]=vout[:]
		y[k+1,:]=v[:]
	
	return (xx,y)
	
