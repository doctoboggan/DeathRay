"""generate voigt functions and their derivatives with respect to parameters"""
_rcsid="$Id: voigt_profile.py 323 2011-04-06 19:10:03Z marcus $"

##\file
##Provides the analysis.voigt_profile package.
##\package analysis.voigt_profile
#This is a function which efficiently computes Voigt profiles (convolutions of Lorentzian and Gaussian functions) which are useful for many types of spectroscopy.
#\verbatim version $Id: voigt_profile.py 323 2011-04-06 19:10:03Z marcus $ \endverbatim
#
#Developed by Marcus H. Mendenhall, Vanderbilt University Keck Free Electron Laser Center, Nashville, TN USA
#
#email: mendenhall@users.sourceforge.net
#
#Work supported by the US DoD  MFEL program under grant FA9550-04-1-0045
#

try:
	import numpy as Numeric
	from numpy import fft
	from numpy.fft import irfft as inverse_real_fft
	_numeric_float=Numeric.float64
	
except ImportError:	
	import Numeric
	from FFT import inverse_real_fft
	_numeric_float=Numeric.Float64

import math

## 
## the class allows one to set up multiple instances of the Voigt function calculator, each with its own private cache
## so that cache thrashing is avoided if one is computing for many peaks with widely varying parameters

class Voigt_calculator:
	
	## 
	## Construct the function instance, and create an empty cache
	def __init__(self):
		##
		## This is a cache which is used to store the most recently computed data grids, so similar computations can be done very quickly.
		self.saved_params=(0,0, None, None, None, None) #k_points, xfullwidth, kvals, xvals, k2, cosarray, x2

	##
	## Compute a block of Voigt function values
	## \param sigma The Gaussian width for the convolution, such that the Gaussian is y=exp[-x^2 / (2 sigma^2)]
	## \param alpha The half-width of the Lorentzian, i.e. y=1/(alpha^2 + x^2), suitably normalized
	## \param k_points The number of points in k-space to compute.  If it is None, autorange based on kexptail (see below)
	## \param xfullwidth The maximum value of X for which the function is calculated.  The domain is (-xfullwidth, xfullwidth)
	## \param kexptail The number of exponential decrements to compute in k-space.  kexptail=25 gives about 10^-11 amplitude at the Nyquist frequency.  
	##	Larger values give finer sampling of the peak in x-space.
	##
	## \retval xvals The grid of x values on which the function is computed.
	## \retval yft The array of function values corresponding to the xvals given.  The function is normalized so that sum(yft*dx)=1
	## \retval dsig The derivative of the Voigt function with respect to sigma
	## \retval dalpha The derivative of the Voigt function with respect to alpha.
	##
	def voigt_with_derivs(self, sigma, alpha, k_points=None, xfullwidth=10.0, kexptail=25):
		"""return an x grid, voigt function with specified params, and d/dsigma and d/dalpha of this.  
			Function is normalized to unit integral of points"""
		if k_points is None:
			#autorange k by solving for k such that 0.5*sigma**2*k**2+alpha*k==kexptail 
			# so exp(-kexptail) is smallest point in spectrum
			q=-0.5*(alpha+math.sqrt(alpha*alpha+4.0*kexptail*(0.5*sigma**2))) #the Numerical Recipes quadratic trick
			k1=-kexptail/q
			kp=k1*xfullwidth/math.pi
			k_points=2**int(1+math.floor(math.log(kp)/math.log(2.0))) #next power of two up
			
		if self.saved_params[:2] != (k_points, xfullwidth):
			kmax=math.pi*k_points/(xfullwidth)
			kvals=Numeric.array(range(k_points+1), _numeric_float)*(kmax/k_points)
			dx=xfullwidth/(2.0*k_points)
			xvals=Numeric.array(range(2*k_points), _numeric_float)*(xfullwidth/float(k_points))-xfullwidth
			k2=kvals*kvals
			x2=xvals*xvals
			cosarray=Numeric.cos((math.pi/xfullwidth)*xvals)
			self.saved_params=(k_points, xfullwidth, kvals, xvals, k2, cosarray, x2)
		else:
			k_points, xfullwidth, kvals, xvals, k2, cosarray, x2=self.saved_params
			kmax=math.pi*k_points/(xfullwidth)
			dx=xfullwidth/(2.0*k_points)
			
		yvals=Numeric.exp(Numeric.clip((-0.5*sigma*sigma)*k2 - alpha*kvals, -100, 0))
		yvals[1::2]*=-1.0 #modulate phase to put peak in center for convenience
		yft=inverse_real_fft(yvals)
		yft *= 0.5/dx #scale to unit area
	
		#apply periodic boundary correction to function
		delta=2*xfullwidth
		k1=2*math.pi*alpha/delta
		shk1=math.sinh(k1)/delta
		chk1=math.cosh(k1)
		uu1=1.0/(chk1-cosarray ) 
		uu2=Numeric.array(1.0/(x2+alpha**2))
		deltav=shk1*uu1-(alpha/math.pi)*uu2
	
		#this is an empirical correction on top of the analytical one, to get the next order correct
		#it is derived from a scaling argument (much hand waving) about 
		#the effect of a gaussian convolution on a second derivative
		yft -= deltav*(1+(2*sigma**2/xfullwidth**4)*x2)
		
		#transform of df/d(alpha) = d(transform of f)/d(alpha) = -k*transform	
		yvals*=kvals
		dalpha=inverse_real_fft(yvals)
		dalpha*= -0.5/dx
		
		#apply periodicity correction to d/dalpha
		deltad=(-2.0*math.pi*shk1*shk1)*(uu1*uu1) 
		deltad +=  ( 2.0*math.pi*chk1/(delta*delta))*uu1
		deltad += (alpha*alpha - x2)*(uu2*uu2)/math.pi
		dalpha -= deltad
		
		#transform of df/d(sigma) = d(transform of f)/d(sigma) = -k*k*sigma*transform	
		yvals*=kvals
		dsig=inverse_real_fft(yvals)
		dsig*= -0.5*sigma/dx
		
		#d/dsigma is very localized... no correction needed
		
		return (xvals,  yft, dsig, dalpha)


##
## A singleton of the class for convenience
_voigt_instance=Voigt_calculator()
## create one global function so the module can be used directly, without instantiating a class, in the style of the random module
## See documentation for Voigt_calculator.voigt_with_derivs for usage.
def voigt_with_derivs(*args, **kwargs):
	return _voigt_instance.voigt_with_derivs(*args, **kwargs)
##

##
##\cond NEVER
##
if __name__=='__main__':
	from graceplot import GracePlot
	
	datasets=[]
	
	stylecolors=[GracePlot.green,  GracePlot.blue, GracePlot.red, GracePlot.orange, GracePlot.magenta, GracePlot.black]
	s1, s2, s3, s4, s5, s6 =[GracePlot.Symbol(symbol=GracePlot.circle, fillcolor=sc, size=0.5, linestyle=GracePlot.none) for sc in stylecolors]
	l1, l2, l3, l4, l5, l6=linestyles=[GracePlot.Line(type=GracePlot.solid, color=sc, linewidth=2.0) for sc in stylecolors]		
	noline=GracePlot.Line(type=GracePlot.none)				
	
	
	if 0:
		alpha0=.005
		sigma0=0.5
		xvals, vgta1, dsig, dalpha = voigt_with_derivs(sigma0, alpha0+0.0001)
		xvals, vgta2, dsig, dalpha = voigt_with_derivs(sigma0, alpha0-0.0001)
		
		xvals, vgts1, dsig, dalpha = voigt_with_derivs(sigma0+0.0001, alpha0)
		xvals, vgts2, dsig, dalpha = voigt_with_derivs(sigma0-0.0001, alpha0)
		
		xvals, vgt, dsig, dalpha = voigt_with_derivs(sigma0, alpha0)
		
		scale=1.0
		
		datasets.append(GracePlot.Data(x=xvals, y=vgt*scale,  type='xy', line=l1))
		datasets.append(GracePlot.Data(x=xvals, y=dsig*sigma0,  type='xy', line=l2))
		datasets.append(GracePlot.Data(x=xvals, y=dalpha*alpha0,  type='xy', line=l3))
		datasets.append(GracePlot.Data(x=xvals, y=5000.0*alpha0*(vgta1-vgta2),  type='xy', symbol=s3, line=noline))
		datasets.append(GracePlot.Data(x=xvals, y=5000.0*sigma0*(vgts1-vgts2),  type='xy', symbol=s2, line=noline))
	else:
		from analysis import C2Functions
		class gauss(C2Functions.C2Function):
			scale=1.0/math.sqrt(2.0*math.pi)
			sigma=1.0
			
			def set_width(self, wid):
				self.sigma=wid

			def value_with_derivatives(self, x):
				x=x/self.sigma
				a=math.exp(-x*x/2)*self.scale/self.sigma
				return a, -x*a/self.sigma, (x*x-1)*a/self.sigma**2
		
		class lorentz(C2Functions.C2Function):
			def set_center(self, center):
				self.center=center
			def set_width(self, wid):
				self.width=wid
						
			def value_with_derivatives(self, x):
				x=(x-self.center)/self.width
				scale=1/(self.width*math.pi)
				a=1.0/(1.0+x*x)
				return a*scale, -2*x*a*a*scale/self.width, (6*x*x-2)*a*a*a*scale/self.width**2
		
		ll=lorentz()
		gg=gauss()
		prod=ll*gg
		
		alpha0=1.0
		import time
		
		for pidx, (xfw, sigma0) in enumerate(((500., 1.), (500., 50.), (2000., 50.))):
			t0=time.time()
			for i in range(100):
				xvals1, vgta1, dsig, dalpha = voigt_with_derivs(sigma0, alpha0, kexptail=25, xfullwidth=xfw)
			t1=time.time()
			
			convlist=[]
			ll.set_width(alpha0)
			gg.set_width(sigma0)
			for x in xvals1:
				ll.set_center(float(x)) #need to cast to float if numpy is used to avod horrible numpy-objects as the float
				convlist.append(prod.integral(-10.0*sigma0, 10.0*sigma0, relative_error_tolerance=1e-13, absolute_error_tolerance=1e-16))
			
			t2=time.time()
			
			diff=vgta1-convlist
			print len(xvals1), (t1-t0)/100.0, t2-t1, math.sqrt(sum(diff*diff)/len(diff))
			
			datasets.append(GracePlot.Data(x=xvals1, y=vgta1,  type='xy', line=linestyles[2*pidx], legend=r"Function: \xs\f{} = %.0f, \xD\f{} = %.0f"%(sigma0, 2*xfw) ))	
			datasets.append(GracePlot.Data(x=xvals1, y=diff/vgta1*1e3,  type='xy', line=linestyles[2*pidx+1], legend=r"10\S3\N \x\#{b4}\f{} Relative Error: \xs\f{} = %.0f, \xD\f{} = %.0f"%(sigma0, 2*xfw)))

	try:
		graceSession.clear()
	except:
		class myGrace(GracePlot.GracePlot):
			
			def write(self, command):
				"make a graceSession look like a file"
				self._send(command)
				self._flush()
		
			def send_commands(self, *commands):
				"send a list of commands, and then flush"
				for c in commands:
					self._send(c)
				self._flush()

		graceSession=myGrace(width=11, height=7)
	
	g=graceSession[0]
	
	g.plot(datasets[::2]+datasets[1::2])	
	g.legend()
	g.xaxis(label=GracePlot.Label('offset'), xmin=0, xmax=500)
	g.yaxis(label=GracePlot.Label('Amplitude'), scale='logarithmic', ymin=1e-6, ymax=1,
			tick=GracePlot.Tick(major=10, minorticks=9))

	graceSession.send_commands('hardcopy device "PDF"', 'print to "voigt_errors.pdf"')

##
##\endcond
##
		
