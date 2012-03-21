"Fit the derivative of a Gaussian to a data set.  Mostly an example of using fitting_toolkit.py"
_rcsid="$Id: gauss_deriv_fit.py 323 2011-04-06 19:10:03Z marcus $"

import fitting_toolkit
import Numeric
from math import sqrt

class gauss_deriv_fit(fitting_toolkit.fit):
	"fit a constant baseline + (x-mu)*gaussian y=y0+a*(x-mu)*exp( -(x-xmu)**2/(2*xsig**2) )"
	def function(self, p, r):
		z0, a, xmu, xsigma = p
		xsigi=-1.0/(2.0*xsigma**2)
		return z0+a*(r-xmu)*Numeric.exp(xsigi*(r-xmu)**2)

	def derivs(self): 
		#analytic derivatives for a 1-d gaussian*(x-mu)
		#z0+a*(x-mu)*exp( -(x-xmu)**2/(2*xsig**2) )
		z0, a, xmu, xsigma = self.funcparams
		n=self.pointcount
		x=self.xarray[0,:n]
		xsigi=-1.0/(2.0*xsigma**2)
		dx=x-xmu
		dx2=dx*dx
		expfact=Numeric.exp(xsigi*dx2)
		z=a*expfact*dx
		
		dd = Numeric.zeros((n, 4), self.atype)
		dd[:,0]=1.0
		dd[:,1]=expfact*dx
		dd[:,2]=(-2.0*xsigi*dx*dx - 1)*a*expfact
		dd[:,3]=(-2.0*xsigi/xsigma)*(dx2*z)
		
		return dd	

if __name__=="__main__":
	
	x=gauss_deriv_fit()

	z0, a, xmu, xsigma =  1., 15., 73., 10.
	x.set_initial_params([z0+5, a-10, xmu+5, xsigma-5])
	
	xlist=Numeric.array(range(100),Numeric.Float)
	ylist=x.compute_funcvals(params=[z0, a, xmu, xsigma], xvals=xlist)
	
	x.add_points(xlist, ylist)
	
	print "\n\n***Start nonlinear test fit***" 
	for i in range(10):
		x.lm_fit_step()
		print Numeric.array_str(x.funcparams, precision=5),  sqrt(x.reduced_chi2)

