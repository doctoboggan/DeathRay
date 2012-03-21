"""Compute Schrodinger equation eigenfunctions very quickly and efficiently using Numerov's method to solve the underlying differential equations"""
_rcsid="$Id: numerov_solve.py 323 2011-04-06 19:10:03Z marcus $"

import math
import Numeric
import sys

try:
	from _numerov import _numerov
	def numerov_iter(Y, coefs):
		_numerov(Y,coefs)
except:
	def numerov_iter(Y, coefs):
		npoints=len(Y)
		for i in range(1,npoints-1):
			yy=Y[i+1]=Y[i]*coefs[i]-Y[i-1]
			if abs(yy) > 1e20: #don't let exponential blow up
				Y*=1e-20

	
def bare_numerov(V, dx):
	"""generate a solution to Schrodinger's eqn for a potential V=(2m/hbar**2)(V-E) using the Numerov method.
	Always integrate in from forbidden region to center of potential from both ends, and solve to match boundary conditions.  The initial conditions will fail if started in an allowed (V-E < 0) region"""
	npoints=len(V)
	Y=Numeric.zeros(npoints,Numeric.Float)
	dx2=dx*dx
	ypsifact=1.0/(1.0-(dx2/12.0)*V)
	coef=2.0+dx2*V*ypsifact
	
	Y[0]=1.0/ypsifact[0]
	Y[1]=math.exp(math.sqrt(V[0])*dx)/ypsifact[1]
	
	numerov_iter(Y,coef)

	return Y*ypsifact


def zbrent(func, x1, x2, tol, itmax=100, trace=0):
	"find zeros using the van Wijngaarden-Dekker-Brent method a la Numeric Recipes"
	a=x1; b=x2
	fa=func(a); fb=func(b)

	assert fb*fa < 0.0, "Root must be bracketed in ZBRENT"
	fc=fb
	for iter in range(itmax):
		if trace: print iter, a, b, fa, fb
		if (fb*fc > 0.0):
			c=a
			fc=fa
			e=d=b-a
		if abs(fc) < abs(fb):
			a=b
			b=c
			c=a
			fa=fb
			fb=fc
			fc=fa
		tol1=2.0*1e-14*abs(b)+0.5*tol
		xm=0.5*(c-b)
		if abs(xm) <= tol1 or fb == 0.0: return b
		if abs(e) >= tol1 and abs(fa) > abs(fb):
			s=fb/fa
			if a==c:
				p=2.0*xm*s
				q=1.0-s
			else:
				q=fa/fc
				r=fb/fc
				p=s*(2.0*xm*q*(q-r)-(b-a)*(r-1.0))
				q=(q-1.0)*(r-1.0)*(s-1.0)
			if p>0.0: q = -q
			p=abs(p)
			min1=3.0*xm*q-abs(tol1*q)
			min2=abs(e*q)
			if 2.0*p < min(min1,min2):
				e=d
				d=p/q
			else:
				d=xm
				e=d
		else:
			d=xm; e=d
		a=b
		fa=fb
		if abs(d) > tol1:
			b += d
		elif xm > 0.0:
			b+=tol1
		else:
			b-=tol1 
		fb = func(b);
		
	assert 0, "Maximum number of iterations exceeded in ZBRENT"

def single_well_numerov_match(V0, dx, parity=1, overlapsize=5):
	"generate a candidate eigenfunction with given potential, assuming the potential well has a single allowed region bounded on both sides"
	assert len(V0) & 1, "Must have a grid with an odd number of points"
	vminchan=Numeric.argmin(V0) #position of bottom of well
	right_turn=Numeric.searchsorted(V0[vminchan:], 0.0)+vminchan #position of right-hand turning point

	#integrate from left end to right-hand turning point, at which point numerov method becomes unstable
	leftpsi=bare_numerov(V0[:right_turn], dx)
	#iterate backwards on right part to turning point, and flatten to normal array
	rightpsi= Numeric.array(bare_numerov(V0[right_turn-overlapsize:][::-1], dx)[::-1]) 
	
	#remember that since Numeric handles slices without copying, leftend and rightend also scale here
	slopeweight=Numeric.array(range(overlapsize),Numeric.Float)-overlapsize/2.0
	leftend=leftpsi[-overlapsize:]
	rightend=rightpsi[:overlapsize]
	
	scale=abs(Numeric.sum(leftend*rightend)/Numeric.sum(leftend**2)) #'least-squares' scale estimate
	#note that since leftend and rightend are Numeric slice references, modifying psi also changes them!
	rightpsi*=float(parity)/scale	
	error=Numeric.sum((leftend-rightend)*slopeweight) #average derivative
	psi0=Numeric.concatenate((leftpsi, rightpsi[overlapsize:]))

	psi2=psi0*psi0
	integral=psi2[0]+psi2[-1]+4.0*Numeric.sum(psi2[1:-1:2])+2.0*Numeric.sum(psi2[2:-2:2]) #use simpson's rule
	psimag=1.0/math.sqrt(integral*dx/3.0)
	
	return psi0*psimag, error*psimag

def single_well_numerov_solve(V0, dx, parity, emin, emax, overlapsize=5):
	"generate an eigenfunction with given potential with emin<(2m/hbar**2)E<emax, assuming the potential well has a single allowed region bounded on both sides"
	e=zbrent(lambda x: single_well_numerov_match(V0-x, dx, parity, overlapsize=overlapsize)[1], emin, emax, 1e-15, trace=0)
	psi, slope_error=single_well_numerov_match(V0-e, dx, parity, overlapsize)
	return e, psi

def find_spectrum(V0, dx, levels, ground_state_estimate, state_separation_estimate=None, trace=0, subdivide=4):
	results=[]
	if state_separation_estimate is None:
		state_separation_estimate=ground_state_estimate
	#prime the bookkeeping to guess where next state lies and make it point to ground_state_estimate
	e0, e1= ground_state_estimate-2*state_separation_estimate, ground_state_estimate-state_separation_estimate
	for i in range(levels):
		if trace: print '***', i, e0, e1
		delta_e=(e1-e0)/subdivide
		if i & 1:
			parity=-1
		else:
			parity=1
		try:
			firstguess=e1+(e1-e0)*0.5 #1/2 to next estimated level
			psi, slope=single_well_numerov_match(V0-firstguess, dx, parity) #initial slope
			for s in range(1,10*subdivide):
			
				e_test=firstguess+delta_e
				psi, test_slope=single_well_numerov_match(V0-e_test, dx, parity) #initial slope
				if trace:
					print "%4d %4d %8.2e %8.2e %8.2e %8.2e" % (i, s, firstguess, slope, e_test, test_slope) 
				if test_slope==0.0 or test_slope*slope < 0.0: #got a sign change
					break
				if s==(10*subdivide-1):
					assert 0,"No root found" #bail out completely
				firstguess=e_test
				slope=test_slope
			e_n, psi_n=single_well_numerov_solve(V0, dx, parity, e1+(s-1)*delta_e, e_test) #must bracket root
			results.append((i,e_n, psi_n))
			e0, e1=e1, e_n #use last two energies to estimate search size
		except:
			print sys.exc_value
			break #stop if we can't find a level!		
	return results
		

if __name__=='__main__':	
	potlen=101
	xmax=7.0
	dx=2.0*xmax/(potlen-1)
	xar=(Numeric.array(range(potlen),Numeric.Float)-(potlen-1)/2.0)*(xmax*2.0/(potlen-1))
	testpot=xar**2
	
	results=find_spectrum(testpot, dx, 10, 1.,  trace=0)
	for n, e_n, psi_n in results:
		print n, e_n
