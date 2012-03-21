"""Hessian and Levenberg-Marquardt Curve Fitting Package with resampling capability.

This is loosely derived from the information in 'Numerical Recipes' 2nd Ed. by Press, Flannery, Teukolsky and Vetterling.
Implementation by Marcus H. Mendenhall, Vanderbilt University Free Electron Laser Center, Nashville, TN, USA
Implemented around 3 December, 2002.
This implementation is in the public domain, although some of its algorithms 
may be at least in part owned by the 'Numerical Recipes' people.
Check with them before using this in commercial software.

To use it, subclass the fit class and, at minimum, define function(self, params, x) as below

	from fitting_toolkit import fit
	class myfit(fit):
		"a really terrible way to fit a polynomial to data!"
		def function(self, params, x):
			return params[0]+params[1]*x+params[2]*x*x

This function takes a Numeric array of parameters 'params', and a Numeric array of independent variable values 'x'.  If the 
independent variable is a scalar, the function will be passed a 1-d array.  If the independent variable is a vector,
the function will be passed a 2-d array with each _row_ holding one component of the vector, so x[0] would be x, x[1] would be y, etc.

Then, instantiate this class, give it initial parameter estimates, set the autoderivative step size if numerical derivatives
are being used (the default value is 0.001*parameter values), add points, and repeatedly call hessian_compute_fit until 
fitting has converged (which, with Hessian fitting, it often won't!)
	
	x=myfit()
	x.set_initial_params([1.,1.,1.])
	x.auto_deriv_steps((1,1,1))
	
	x.add_point(0, 2)
	x.add_point(1, 5)
	x.add_point(2, 10)
	x.add_point(3, 17)
	x.add_point(4, 26.1)
	
	print "***Start test fit***" 
	for i in range(5):
		x.hessian_compute_fit()
		print x.fitmat, x.fitvector, x.funcparams, x.funcvals[:x.pointcount], sqrt(x.chi2/x.pointcount)

To add more than one point at a time, do

	x.add_points(<array of independent variables>, <array of dependent variables>, x_transpose=<0 | 1>)

If the independent variable is a vector and the independent array has the components of the vector in columns, 
so each column is one vector, the default x_transpose=0 is correct.  
If the components are along rows, and each row is a vector, use x_transpose=1.

For a more robust fitter, use the Levenberg-Marquardt stepping as follows e.g.  (this example shows one convergence checker):
	
	savechi2=1e30		
	acceptcount=0
	for i in range(maxloops):
		reject=x.lm_compute_fit(trace=1)
		chi2=sqrt(x.chi2/x.pointcount)		
		if not reject:
			if chi2/savechi2 >0.99 and acceptcount > 5: 	break
			else:	
				savechi2=chi2
				acceptcount += 1
		elif chi2/savechi2 > 1.01: #only penalize for really bad steps, not  noise!
			acceptcount=0
	
	print x.funcparams, chi2

For more advanced fitting (variable weight, analytic derivatives, etc.) other methods can be overridden.  Note that
except for the function() override, all other function use raw access to the internal variables of the fitter.  Since the data are
stored in arrays which are larger than the number of points, one must always calculate based on
self.xarray[:,self.pointcount] and self.yarray[:self.pointcount] to return data of the right length.

If weighted fitting is desired, include the function weight_func(self) in the subclass, \e e.g. 
	def weight_func(self): #throw out points with < 5 a/d counts in the bin.  
		#This is a bad way to do this if lots of points are being tossed, 
		#but doesn't cost much for the expected case that it doesn't happen often
		return Numeric.greater(self.yarray[:self.pointcount], 5.0)		

If analytic derivatives are desired, do, \e e.g. 
	class gauss_fit_2d(fit):
		def function(self, p, r):
			#print p
			z0, a, xmu, xsigma, ymu, ysigma = p
			xsigi=-1.0/(2.0*xsigma**2)
			ysigi=-1.0/(2.0*ysigma**2)
			return z0+a*Numeric.exp(xsigi*(r[0]-xmu)**2+ysigi*(r[1]-ymu)**2)
	
		def derivs(self): 
			#analytic derivatives for a 2-d gaussian
			#z0+a*exp( -(x-xmu)**2/(2*xsig**2) -(y-ymu)**2/(2.0*ysig**2))
			z0, a, xmu, xsigma, ymu, ysigma = self.funcparams
			n=self.pointcount
			x=self.xarray[0,:n]
			y=self.xarray[1,:n]
			xsigi=-1.0/(2.0*xsigma**2)
			ysigi=-1.0/(2.0*ysigma**2)
			dx=x-xmu
			dx2=dx*dx
			dy=y-ymu
			dy2=dy*dy
			expfact=Numeric.exp(xsigi*dx2+ysigi*dy2)
			z=a*expfact
			
			dd = zeros((n, 6), self.atype)
			dd[:,0]=1.0
			dd[:,1]=expfact
			dd[:,2]=(-2.0*xsigi)*(dx*z)
			dd[:,3]=(-2.0*xsigi/xsigma)*(dx2*z)
			dd[:,4]=(-2.0*ysigi)*(dy*z)
			dd[:,5]= (-2.0*ysigi/ysigma)*(dy2*z)
			
			return dd	

"""

_rcsid="$Id: fitting_toolkit.py 323 2011-04-06 19:10:03Z marcus $"

try:
	import numpy as Numeric
	import numpy
	numeric_float=Numeric.float64
	numeric_int=Numeric.int
	from numpy import linalg
	solve_linear_equations=linalg.solve
	def  singular_value_decomposition(mat):
		return  linalg.svd(mat, full_matrices=0, compute_uv=1)
		
	matinverse=linalg.inv
	from numpy import dot, zeros, transpose, array, array_str
except:
	import Numeric
	numeric_float=Numeric.Float64
	numeric_int=Numeric.Int
	from LinearAlgebra import solve_linear_equations, inverse as matinverse, singular_value_decomposition
	from Numeric import dot, zeros, transpose, array, array_str

import random

import gc
import math
from math import sqrt
import copy
import operator

##\file
## Provides the analysis.fitting_toolkit package.
##\package analysis.fitting_toolkit
## Hessian and Levenberg-Marquardt Curve Fitting Package with resampling capability.
#\verbatim version $Id: fitting_toolkit.py 323 2011-04-06 19:10:03Z marcus $ \endverbatim
#This is loosely derived from the information in 'Numerical Recipes' 2nd Ed. by Press, Flannery, Teukolsky and Vetterling.
#Implementation by Marcus H. Mendenhall, Vanderbilt University Free Electron Laser Center, Nashville, TN, USA
#Implemented around 3 December, 2002.
#This implementation is in the public domain, although some of its algorithms may be at least in part owned by the 'Numerical Recipes' people.
#Check with them before using this in commercial software.
#
#To use it, subclass the fit class and, at minimum, define function(self, params, x) as below
#\code
#	from fitting_toolkit import fit
#	class myfit(fit):
#		"a really terrible way to fit a polynomial to data!"
#		def function(self, params, x):
#			return params[0]+params[1]*x+params[2]*x*x
#\endcode
#This function takes a Numeric array of parameters \a params, and a Numeric array of independent variable values \a x.  If the 
#independent variable is a scalar, the function will be passed a 1-d array.  If the independent variable is a vector,
#the function will be passed a 2-d array with each _row_ holding one component of the vector, so x[0] would be x, x[1] would be y, etc.
#
#Then, instantiate this class, give it initial parameter estimates, set the autoderivative step size if numerical derivatives
#are being used (the default value is 0.001*parameter values), add points, and repeatedly call hessian_compute_fit until 
#fitting has converged (which, with Hessian fitting, it often won't!)
#\code	
#	x=myfit()
#	x.set_initial_params([1.,1.,1.])
#	x.auto_deriv_steps((1,1,1))
#	
#	x.add_point(0, 2)
#	x.add_point(1, 5)
#	x.add_point(2, 10)
#	x.add_point(3, 17)
#	x.add_point(4, 26.1)
#	
#	print "***Start test fit***" 
#	for i in range(5):
#		x.hessian_compute_fit()
#		print x.fitmat, x.fitvector, x.funcparams, x.funcvals[:x.pointcount], sqrt(x.chi2/x.pointcount)
#\endcode
#To add more than one point at a time, do
#\code
#	x.add_points(<array of independent variables>, <array of dependent variables>, x_transpose=<0 | 1>)
#\endcode
#If the independent variable is a vector and the independent array has the components of the vector in columns, 
#so each column is one vector, the default x_transpose=0 is correct.  
#If the components are along rows, and each row is a vector, use x_transpose=1.
#
#For a more robust fitter, use the Levenberg-Marquardt stepping as follows (\a e.g. ) (this example shows one convergence checker):
#\code	
#	savechi2=1e30		
#	acceptcount=0
#	for i in range(maxloops):
#		reject=x.lm_compute_fit(trace=1)
#		chi2=sqrt(x.chi2/x.pointcount)		
#		if not reject:
#			if chi2/savechi2 >0.99 and acceptcount > 5: 	break
#			else:	
#				savechi2=chi2
#				acceptcount += 1
#		elif chi2/savechi2 > 1.01: #only penalize for really bad steps, not  noise!
#			acceptcount=0
#	
#	print x.funcparams, chi2
#\endcode
#For more advanced fitting (variable weight, analytic derivatives, etc.) other methods can be overridden.  Note that
#except for the function() override, all other function use raw access to the internal variables of the fitter.  Since the data are
#stored in arrays which are larger than the number of points, one must always calculate based on
#self.xarray[:,self.pointcount] and self.yarray[:self.pointcount] to return data of the right length.
#
#If weighted fitting is desired, include the function weight_func(self) in the subclass, \e e.g.  \code
#	def weight_func(self): #throw out points with < 5 a/d counts in the bin.  
#		#This is a bad way to do this if lots of points are being tossed, 
#		#but doesn't cost much for the expected case that it doesn't happen often
#		return Numeric.greater(self.yarray[:self.pointcount], 5.0)		
#\endcode
#If analytic derivatives are desired, do, \e e.g. \code
#	class gauss_fit_2d(fit):
#		def function(self, p, r):
#			#print p
#			z0, a, xmu, xsigma, ymu, ysigma = p
#			xsigi=-1.0/(2.0*xsigma**2)
#			ysigi=-1.0/(2.0*ysigma**2)
#			return z0+a*Numeric.exp(xsigi*(r[0]-xmu)**2+ysigi*(r[1]-ymu)**2)
#	
#		def derivs(self): 
#			#analytic derivatives for a 2-d gaussian
#			#z0+a*exp( -(x-xmu)**2/(2*xsig**2) -(y-ymu)**2/(2.0*ysig**2))
#			z0, a, xmu, xsigma, ymu, ysigma = self.funcparams
#			n=self.pointcount
#			x=self.xarray[0,:n]
#			y=self.xarray[1,:n]
#			xsigi=-1.0/(2.0*xsigma**2)
#			ysigi=-1.0/(2.0*ysigma**2)
#			dx=x-xmu
#			dx2=dx*dx
#			dy=y-ymu
#			dy2=dy*dy
#			expfact=Numeric.exp(xsigi*dx2+ysigi*dy2)
#			z=a*expfact
#			
#			dd = zeros((n, 6), self.atype)
#			dd[:,0]=1.0
#			dd[:,1]=expfact
#			dd[:,2]=(-2.0*xsigi)*(dx*z)
#			dd[:,3]=(-2.0*xsigi/xsigma)*(dx2*z)
#			dd[:,4]=(-2.0*ysigi)*(dy*z)
#			dd[:,5]= (-2.0*ysigi/ysigma)*(dy2*z)
#			
#			return dd	
#\endcode

##
##The main class which is the host for all the fitting techniques
class fit:
	## Create the fitter, and give it a hint as to the size blocks to allocate for data arrays.

	## If collect_garbage is True, the fitter will clean up with gc.collect() between passes, to reduce memory consumption.  
	## Useful for huge fits. Override in subclass if huge-dataset capabilities will be needed
	collect_garbage=False
	
	def __init__(self, pointhint=1000):
		"""create the fitter, and give it a hint as to the size blocks to allocate for data arrays."""
		self.pointhint=pointhint
		self.pointcount=0
		self.arraysexist=0
		self.firstpass=1
		self.atype=self.DefaultArrayType()
		
	## collect garbage if we are enabled to do it.  Useful for huge fits to reduce peak memory
	##
	def collect(self):
		if self.collect_garbage: gc.collect()
	
	##
	## Override this function if you want to fit in single precision, \e e.g.  
	# Default is numeric_float i.e. double precision
	def DefaultArrayType(self):
		"""override this function if you want to fit in single precision, \e e.g.
			Default is numeric_float i.e. double precision"""
		return numeric_float
	
	##
	## Set up initial values for function parameters to get the fit off to a good start.
	# 
	# \param params A array of starting values. The array has one value per free parameter in the fit, and must be ordered as it will be used by function()
	def set_initial_params(self, params):
		"set up initial values for function parameters to get the fit off to a good start"
		self.funcparams=array(params, self.atype)
		self.firstpass=1	#probably need to recompute function if we did this
		self.param_count=len(params)
		if not hasattr(self, "deriv_step"):
			self.deriv_step=self.funcparams*0.001
	
	##
	## Define the step sizes to be used by auto_derivs()
	# \param deriv_step an indexable object with the same number of elements as free parameters.
	#										
	def auto_deriv_steps(self, deriv_step):
		"set the step sizes used for each parameter if numerical derivatives are to be used"
		self.deriv_step=array(deriv_step, self.atype)

	##
	##  Make sure arrays are big enough to add the specified number of points
	# \param sample_x A sample abscissa vector or scalar to determine the shape of the arrays to build.
	# \param points_to_add The number of points to be appended in the next operation (at least).
	def check_arrays(self, sample_x, points_to_add=1):
		"make sure arrays are big enough to add the specified number of points"
		if not self.arraysexist:
			if operator.isSequenceType(sample_x):
				self.arg_count=len(sample_x)
			else:
				self.arg_count=1
			self.frozen=zeros(self.param_count)
			self.xarray=zeros((self.arg_count, self.pointhint), self.atype)
			self.yarray=zeros(self.pointhint, self.atype )
			self.currentlen=self.pointhint
			self.arraysexist=1
		
		if self.pointcount+points_to_add  >= self.currentlen:
			#expand arrays to accept more data
			realmax = max(2*self.currentlen, self.currentlen+2*points_to_add) 
			xarray=zeros((self.arg_count, realmax ), self.atype)
			yarray=zeros(realmax, self.atype)
			xarray[:, :self.pointcount]=self.xarray[:,:self.pointcount]
			yarray[:self.pointcount]=self.yarray[:self.pointcount]
			self.xarray=xarray
			self.yarray=yarray
			self.currentlen=realmax	
	
	##
	## Set the indexed parameter to be frozen in the fit.
	#
	# Freezing the parameter cuases its row and column to be set to the identity in the design matrix.   
	# It can be used to prevent very unstable parameters in a fit from drifting away from their starting values until more stable
	# ones have been allowed to converge.  
	def freeze_parameter(self, param_index):		
		self.frozen[param_index]=1
	
	##
	## Unfreeze a previously-frozen parameter.  See freeze_parameter()
	#
	def unfreeze_parameter(self, param_index):
		self.frozen[param_index]=0	
	
	##
	# Add one data point to the fit.
	#\param xvector A scalar (for fits with a single independent variable) or a vector (multiple independent variables)
	#\param yval A scalar value for the function at the specified point
	#
	def add_point(self, xvector, yval):
		self.check_arrays(xvector)
		n=self.pointcount			
		if self.arg_count > 1:
			self.xarray[:,n]=xvector
		else:
			self.xarray[0,n]=xvector
		self.yarray[n]=yval
		self.pointcount=self.pointcount+1

	##
	## Add multiple points to the fit simultaneously.
	#\param xvector A 1-d or 2-d array of abscissas
	#\param yval A 1-d array of ordinates
	#\param x_transpose If x_transpose is False or 0, xvector has one point per column.  If True, xvector has one point per row.
	def add_points(self, xvector, yval, x_transpose=0):
		n=self.pointcount	
		
		if x_transpose:
			xv=Numeric.transpose(array(xvector))
		else:
			xv=array(xvector)
		
		n1=xv.shape[-1]
		if len(xv.shape) == 1:	
			self.check_arrays(1.0, n1) #elements of x are scalar
		else:
			self.check_arrays(xv[:,0], n1) #elements of x are vector
			
		if self.arg_count > 1:
			self.xarray[:,n:n+n1]=xv
		else:
			self.xarray[0,n:n+n1]=xv
		self.yarray[n:n+n1]=yval
		self.pointcount=self.pointcount+n1
	
	##
	## compute the set of values for the function evaluated at the positions provided, and with the paramaters provided.
	#\param xvals An array of abscissas
	#\param params An array of the parameters to be used.  If None, use whatever the current fit's funcparams are.
	#\param x_transpose If False or 0, each point is a column in xvals.  If True, each point is a row in xvals.
	def compute_funcvals(self, xvals=None, params=None, x_transpose=0):
		"evaluate the fitter's function, providing some convenient glue for passing in data arrays of various shapes"
		if params is None:
			params=self.funcparams

		if xvals is None:
			n=self.pointcount
			if self.arg_count > 1:
				xvals=self.xarray[:,:n]
			else:
				xvals=self.xarray[0, :n]
		elif x_transpose:
			xvals = Numeric.transpose(xvals) #allow array sideways to be handled
		
		return self.function(params, xvals)
	
	## 
	## Compute the numeric derivative of the target function with respect to the indexed parameter, using a stepsize of delta_x
	#\param param_index Index of the parameter in funcparams.
	#\param delta_x Full size of step to use in the numerical differentiation.	
	def numeric_deriv(self, param_index, delta_x):
		"""numerically differentiate the fitter's function with respect
		 to the indexed parameter, using the specified step size"""
		delta=zeros(self.param_count, self.atype)
		delta[param_index]=delta_x/2.0
		newrow=((self.compute_funcvals(params=self.funcparams+delta)-
				self.compute_funcvals(params=self.funcparams-delta))/delta_x)
		return newrow
	
	##
	#Compute derivatives by default numerical differentiation for all non-frozen parameters,
	# This must be overridden for fits which have analytic derivatives.  See example in class documentation.
	#Note in particular that the array returned is organized with all the values for a point in each row.  The columns correspond to the parameters.
	def derivs(self): 
		"default deriv is automatic numeric derivatives, override this for analytic derivatives"
		n=self.pointcount
		fxarray=zeros((n, self.param_count), self.atype)
		for i in range(self.param_count):
			if not self.frozen[i]:
				fxarray[:,i]=self.numeric_deriv(i, self.deriv_step[i])
		return fxarray
	
	##
	#return the weight values to use for each point in this fit.  If a variable exists in the class 'explicit_weightlist	', return this.
	#If it does not exist, return 1.0 as the weight.  
	#
	#This method should be overridden if anything fancy is being done with weights (correlated fits, etc.) 
	def weight_func(self):
		"default weight is 1 or, if explicit_weightlist exists, that is returned"
		w=getattr(self, 'explicit_weightlist', 1.0)
		if w is None: w=1.0
		return w
	
	##
	## This prepares the fitter for doing resampling (bootstrapping) to estimate the true shape of the chi^2 surface.
	# Makes shadow copies of the main data arrays so they resampled data
	def setup_resampling(self):
		"setup_resampling() caches the 'real' arrays of x and y, so they can be resampled for bootstrapping, and seeds a random generator"
		assert not hasattr(self, "saved_xarray"), "Don't even think of initializing the resampling more than once!"
		self.saved_xarray=array(self.xarray[:,:self.pointcount]) #these must be copies, not slices!
		self.saved_yarray=array(self.yarray[:self.pointcount]) 
		self.saved_explicit_weightlist=getattr(self, 'explicit_weightlist', None)
		self.initialize_random_generator()
	
	##
	## This resets the fitter back to non-resampling mode so all the original data are available.
	# Removes shadow copies of the main data arrays so they resampled data
	def clear_resampling(self):
		"clear_resampling() removes resampling machinery"
		self.xarray=self.saved_xarray
		self.yarray=self.saved_yarray
		self.explicit_weightlist=self.saved_explicit_weightlist
		
		self.firstpass=1
		del self.saved_xarray, self.saved_yarray, self.saved_explicit_weightlist
		self.collect()

	##
	## Initialize the random number generator to be used in resampling.  Override this for non-default radnom generators.
	def initialize_random_generator(self):
		"initialize the random number generator to be used in resampling.  Overide to use other than random.Random. r250_521 is much faster and better!"
		self.randoms=random.Random()
	
	##
	##return a list of \a count randoms, possibly by an efficient technique, if the generator supports it.	
	def get_random_list(self, count):
		"return a list of count randoms on [0,1) for resampling.  Override to pick a different random generator"
		r=self.randoms.random
		return array([r() for i in range(count)])
	
	##
	## Take a new sample of the data for  resampling/bootstrapping.  
	## can be put in the main arrays.
	def resample(self):
		"resample() randomly draws a set of points equal in size to the original set from the cached data for bootstrapping"
		assert hasattr(self, "saved_xarray"), "resampling not set up yet.  Call setup_resampling() first."
		ranlist=Numeric.floor(self.get_random_list(self.pointcount)*self.pointcount).astype(numeric_int)
		
		#before we cone possibly huge arrays, clean up a bit to reduce huge transient memory usage 
		if hasattr(self, 'fitmat'):
			del self.fitmat
		if hasattr(self, 'xarray'):
			del self.xarray
		self.collect()
		
		self.xarray=Numeric.take(self.saved_xarray, ranlist, -1) #take columns since vectors lie this way
		self.yarray=Numeric.take(self.saved_yarray, ranlist)
		if hasattr(self.saved_explicit_weightlist, '__getitem__'): #it's a sequence if it has a __getitem__
			self.explicit_weightlist=Numeric.take(self.saved_explicit_weightlist, ranlist)
			
		self.firstpass=1
	
	## 
	## Evaluate the weight function, and flag whether the weights are scalar or not.
	## (Internal use mostly)
	def set_weights(self):
		self.weights=self.weight_func()
		self.scalar_weights = (type(self.weights) is type(1.0) or len(self.weights.shape)==1)		
	
	##
	## Left-multiply a y-vector or function matrix by the weights.  If the weights are special (sparse, etc.), override this. 
	def weights_multiply(self, right_array):
		"left multiply  vector or matrix by weights... override if weights are sparse matrix, etc."
		if self.scalar_weights:
			if len(right_array.shape)==1:
				return right_array*self.weights
			else:
				r=copy.copy(right_array)
				for k in range(self.param_count):
					r[k]*=self.weights
				return r
		else:
			return dot(self.weights, right_array)	

	##
	## Evaluate residuals, and compute proper chi^2 with weights.		
	def compute_chi2(self):
		self.residuals=self.yarray[:self.pointcount]-self.funcvals
		self.chi2=float(dot(self.residuals,self.weights_multiply(self.residuals)))
		self.reduced_chi2=float(self.chi2/(self.pointcount-self.param_count))

	##
	## Take one inverse-Hessian or Levenberg-Marquardt step in a fit.  
	#\param lm_lambda The Levenberg-Marquardt  lambda parameter
	def hessian_compute_fit(self, lm_lambda=None): 
		"take one Hessian fitting step  if lm_lambda undefined, otherwise make Levenberg-Marquardt adjustment"
		
		if hasattr(self, 'fitmat'):
			del self.fitmat
			self.collect() #if we are recycing, thoroughly clean up possibly huge objects
			
		n=self.pointcount		
		fxarray=self.derivs()

		self.set_weights()
		fxwarray=self.weights_multiply(Numeric.transpose(fxarray))
		self.fitmat=dot(fxwarray, fxarray)
		
		if lm_lambda is not None: #make Levenberg-Marquardt correction to inverse-covariance matrix
			for i in range(self.param_count):
				self.fitmat[i,i]*=(1.0+lm_lambda)
				
		for i in range(self.param_count): #handle frozen parameters
			if self.frozen[i]:
				self.fitmat[i,:]=0.0
				self.fitmat[:,i]=0.0
				self.fitmat[i,i]=1.0

		if(self.firstpass):
			self.funcvals=self.compute_funcvals()
			self.firstpass=0

		self.fitvector=solve_linear_equations(self.fitmat, dot(fxwarray, self.yarray[:n]-self.funcvals) )
		self.funcparams=self.funcparams+self.fitvector*(1-self.frozen)
		self.funcvals=self.compute_funcvals()
		self.compute_chi2()			

	##
	## Take one inverse-Hessian step, using SVD to control funny steps
	#\param damping A damping factor.  The computed step size is multiplied by this before taking the step.
	def svd_hessian_compute_fit(self, damping=None): 
		"take one Hessian fitting step  using singular-value-decomposition"
		
		try:
			n=self.pointcount		
			self.set_weights()
	
			if not self.scalar_weights:
				raise exceptions.AssertionError, "SVD solutions require, for now, scalar weights"
							
			sigi=Numeric.sqrt(self.weights)
			if not operator.isSequenceType(sigi):
				design=self.derivs()*float(sigi)
			else:
				design=self.derivs()*sigi[:,Numeric.NewAxis] #w should be a column vector
						
			if(self.firstpass):
				self.funcvals=self.compute_funcvals()
				self.firstpass=0
	
			u, w, v = singular_value_decomposition(design)
			w=self.singular_value_edit(w)
			for i in range(self.param_count):
				if w[i] != 0:
					w[i] = 1.0/w[i]
			b=(self.yarray[:n]-self.funcvals)*sigi
			self.fitvector=Numeric.sum(dot(Numeric.transpose(u*w),b)*Numeric.transpose(v), -1)
			self.svd_u=u
			self.svd_v=v
			self.svd_winv=w
		except:
			import traceback
			traceback.print_exc()
			raise
					
		if damping is None:
			self.funcparams=self.funcparams+self.fitvector*(1-self.frozen)
		else:
			self.funcparams=self.funcparams+self.fitvector*(1-self.frozen)*damping
			
		self.funcvals=self.compute_funcvals()
		self.compute_chi2()			
	##
	##Edit the singular values.  By default, look at the variable svd_tolerance, and if it exists
	#clip the singular values to that factor less than the largest.  If the variable does not exist, use 10^-10 	
	def singular_value_edit(self, values):
		"zap unreasonably small singular values based on svd_tolerance"
		if hasattr(self, "svd_tolerance"):
			tol=self.svd_tolerance
		else:
			tol=1e-10
		clip=max(values)*tol
		for i in range(len(values)):
			if values[i]<clip: values[i]=0.0
		return values 
		
	##
	##This is just a shortcut so a class can select which type of kernel is used. 
	# If you directly call one of the specific fitters (hessian or svd), you may never use this.
	def compute_fit(self, lm_lambda=None):
		"override this to select which fitting kernel is being used"
		self.hessian_compute_fit(lm_lambda)
	
	##
	## Return the variance-covariance matrix for the fit.
	def covariance_matrix(self):
		"return the variance-covariance matrix resulting from this fit"
		return matinverse(self.fitmat)
	
	##
	## Return the variance-covariance matrix for the fit if svd fitting was used.
	def svd_covariance_matrix(self):
		"return the variance-covariance matrix resulting from this fit when svd stepping was used"
		return dot(self.svd_v, Numeric.transpose(self.svd_winv**2*self.svd_v))
	
	##
	##One choice of a schedule for adjusting the Levenberg-Marquardt parameter.  Not the only one!
	def lm_lambda_recipe(self, old_chi2=None, new_chi2=None):
		"adjust the Levenberg-marquardt lambda parameter based on the old and new chi^2 values"
		if old_chi2 is None:
			self.lm_lambda=0.001
		elif old_chi2 < new_chi2:
			if new_chi2/old_chi2 < 1.1:
				self.lm_lambda *=10.0 #on a slightly bad fit (bobbling), don't penalize too badly
			else:
				self.lm_lambda = max(self.lm_lambda*10.0, 1.0) #always jump to at least 1 on a bad fit
		else:
			self.lm_lambda *= 0.1
	
	##
	## Take an L-M fit step, and adjust the L-M parameter based on the behavior of chi^2.
	##\param trace If True (or non-zero), print out diagnostics on each step.
	def lm_fit_step(self, trace=0): 
		"take one Levenberg-Marquardt step and adjust lambda based on chi^2"
		n=self.pointcount
		if self.firstpass: #do an initial measurement of chi2 first time through
			self.lm_lambda_recipe()
			self.funcvals=self.compute_funcvals()
			self.set_weights()
			self.compute_chi2()
			self.firstpass=0 #we've done all the first-pass stuff now
			
		save_chi2=self.chi2
		save_params=self.funcparams
		save_vals=self.funcvals
		self.hessian_compute_fit(self.lm_lambda)
		self.lm_lambda_recipe(save_chi2, self.chi2)
		if save_chi2 < self.chi2: #ouch, bad step, back up
			if trace:
				print "rejected step: old chi2=%.3e, new chi2=%.3e, lambda=%.3e" % (save_chi2, self.chi2, self.lm_lambda)
				print "params =", self.funcparams
			self.funcparams=save_params
			self.funcvals=save_vals
			self.chi2=save_chi2
			return 1 #flag rejected step
		else:
			if trace:
				print "accepted step: old chi2=%.3e, new chi2=%.3e, lambda=%.3e" % (save_chi2, self.chi2, self.lm_lambda)
				print "params =", self.funcparams
			return 0 #flag accepted step

	##
	## A lot like lm_lambda_recipe but for svd fits.  It  adjusts the damping depending on the behavior of chi^2
	##\param old_chi2 The value of chi^2 from the previous fit step
	##\param new_chi2 The value of chi^2 from the current fit step.
	def svd_damping_recipe(self, old_chi2=None, new_chi2=None):
		"adjust the damping parameter based on the old and new chi^2 values"
		if old_chi2 is None:
			self.svd_damping=1.0
		elif old_chi2 < new_chi2:
			if new_chi2/old_chi2 < 1.1:
				self.svd_damping *=0.8 #on a slightly bad fit (bobbling), don't penalize too badly
			else:
				self.svd_damping  *= 0.25 
		else:
			self.svd_damping   = min(self.svd_damping *2.0, 1.0)

	##
	## A lot like lm_fit_step
	def damped_svd_fit_step(self, trace=0): 
		"take one svd-hessian step and adjust damping  based on chi^2"
		n=self.pointcount
		if self.firstpass: #do an initial measurement of chi2 first time through
			self.svd_damping_recipe()
			self.funcvals=self.compute_funcvals()
			self.set_weights()
			self.compute_chi2()
			self.firstpass=0 #we've done all the first-pass stuff now
			
		save_chi2=self.chi2
		save_params=self.funcparams
		save_vals=self.funcvals
		try:
			self.svd_hessian_compute_fit(self.svd_damping)
		except KeyboardInterrupt:
			raise
		except:
			self.chi2=2.0*save_chi2 #just consider a failure to be a bad step
		self.svd_damping_recipe(save_chi2, self.chi2)
		if save_chi2 < self.chi2: #ouch, bad step, back up
			if trace:
				print "rejected step: old chi2=%.3e, new chi2=%.3e, lambda=%.3e" % (save_chi2, self.chi2, self.svd_damping)
				print "params =", self.funcparams
			self.funcparams=save_params
			self.chi2=save_chi2
			self.funcvals=save_vals
			return 1 #flag rejected step
		else:
			if trace:
				print "accepted step: old chi2=%.3e, new chi2=%.3e, lambda=%.3e" % (save_chi2, self.chi2, self.svd_damping)
				print "params =", self.funcparams
			return 0 #flag accepted step

##
## Fit to a function which is a linear combination of basis functions, so no iteration is needed.
class linear_combination_fit(fit):
	"fit a linear combination of basis functions"
	
	##
	## Set up the fit.  
	##\param funclist a list of functions to be evaluated at the points which will be added to the fit. The functions are evaluated a f(parmindex, x)
	# so the function can parametrically depend on its position in the parameter list (for example, it may be an n'th power for position n).
	#\param pointhint An estimate of the number of points to be added in a block.
	def __init__(self, funclist, pointhint=1000):
		fit.__init__(self, pointhint)
		self.basis=funclist
		self.param_count=len(funclist)

	##	
	## Evaluate the appropriate linear combination
	def function(self, p, x):
		if self.firstpass: #first call from hessian_fit is meaningless, all coefficients zero, save time
			return 0.0

		sumarray=zeros(x.shape[-1], self.atype)
		for i in range(self.param_count):
			sumarray+=p[i]*self.basis[i](i, x)
		return sumarray
	
	##	
	## Compute the (trivial) derivatives for a linear combination
	def derivs(self):
		if self.firstpass: #may get used more than once if weights are not constant, but no need to recompute
			if hasattr(self, 'saved_derivs'):
				#if we have been reset to firstpass, but have really run before,
				#delete old stuff before creating new, since memory usage may be very large
				del self.saved_derivs
				self.collect()
				
			n=self.pointcount
			self.funcparams=zeros(self.param_count, self.atype)
			dd = zeros((n, self.param_count), self.atype)
			if self.arg_count==1:
				x=self.xarray[0,:n]
			else:
				x=self.xarray[:,:n]
			for i in range(self.param_count):
				dd[:,i]=self.basis[i](i,x)
			self.saved_derivs=dd					
		return self.saved_derivs

	##
	## Given a vector of x values and y values, and optional weights, compute the fit.				
	def fit_data(self, xvector, yvector, weightlist=None):
		"compute the fit of the supplied data, all in one call"
		self.pointcount=0 #reset the fitter for easy reuse once set up
		self.firstpass=1
		self.add_points(xvector, yvector)
		self.explicit_weightlist=weightlist
		self.compute_fit() #one pass needed, no fancies, since the system is linear

##
## Fit a polynomial to data.  This is a special case of a linear combination fit, but code is optimized here
class polynomial_fit(fit):
	"fit a polynomial of selected degree, with x shifted by xcenter"
	
	##
	## Set up the fit
	#\param degree The degree of the polynomial (number of parameters=1+degree)
	#\param pointhint An estimate of how many points to allocate at a time. 
	#\param xcenter Expand the polynomial around this point
	def __init__(self, degree, pointhint=1000, xcenter=0.0):
		fit.__init__(self, pointhint)
		self.xcenter=xcenter
		self.param_count=degree+1
	
	##
	## compute the polynomial
	def function(self, coefs, xlist):
		if self.firstpass: #first call from hessian_fit is meaningless, all coefficients zero, save time
			return 0.0

		xc=xlist-self.xcenter
		y=xc*coefs[-1]
		for i in coefs[-2:0:-1]:
			y=xc*(i+y)
		return y+coefs[0]

	##
	## Compute the derivatives.
	def derivs(self):
		if self.firstpass: #may get used more than once if weights are not constant, but no need to recompute
			if hasattr(self, 'saved_derivs'):
				#if we have been reset to firstpass, but have really run before,
				#delete old stuff before creating new, since memory usage may be very large
				del self.saved_derivs
				self.collect()
			self.funcparams=zeros(self.param_count, self.atype)
			n=self.pointcount
			dd = zeros((n, self.param_count), self.atype)
			dd[:,0]=1.0
			xc=self.xarray[0,:n]-self.xcenter
			for i in range(1,self.param_count):
					dd[:,i]=dd[:,i-1]*xc
			self.saved_derivs=dd			
		return self.saved_derivs

	##
	## Given a vector of x values and y values, and optional weights, compute the fit.				
	def fit_data(self, xvector, yvector, weightlist=None, xcenter=0.0):
		"compute the fit of the supplied data, all in one call"
		self.pointcount=0 #reset the fitter for easy reuse once set up
		self.firstpass=1
		self.add_points(xvector, yvector)
		self.explicit_weightlist=weightlist
		self.xcenter=xcenter
		self.compute_fit() #one pass needed, no fancies, since the system is linear

#a few exemplary (and possibly useful?) examples of subclasses of the fitter

find_peak_fitter=polynomial_fit(2, pointhint=100) #save this for reuse, so find_peak can be called vey quickly

##
##Find a positive peak in a data set, using a robust parabolic fitter.
#
#This looks for the highest channel in \a data and then fits a parabola to the half-height points around it.  This tends to be
# a very stable way to find a peak, even on a somewhat sloping background, and with little knowledge of the real shape.
# It does require that the peak be wide enough that at least 3 points fit between its half-height points.
#
#\param data either a list of ordinates (abscissas assumed to be integers starting at 0) or a list of x,y pairs.
def find_peak(data):
	"""find a positive peak in data, assuming the background is 0.  
	Data can either be a list of (x,y) or just a list of y, in which case integer x is assumed.
	find_peak returns xcenter, hwhm, height.  
	Algorithm is parabolic fit to data between half-height points around max of data.  
	This makes sense if hwhm > 1 channel, so at least 3 points
	get included in the fit.  It breaks for peaks narrower than this, 
	but in that case, using the highest point is about the best one can do, anyway. 
	"""
	da=array(data, numeric_float) #put it in a well-known format
	if type(data[0]) is type(1.0):
		x=range(len(data))
		y=data
	else:
		x=data[:,0]
		y=data[:,1]
	
	topchan=Numeric.argmax(y)
	topy=y[topchan]
	#find half-height points
	startx=topchan
	while(y[startx] >= 0.5*topy): startx -= 1
	endx=topchan
	while(y[endx] >= 0.5*topy): endx += 1
	
	#f=polynomial_fit(2, xcenter=x[topchan])
	f=find_peak_fitter
	f.fit_data(x[startx:endx+1], y[startx:endx+1], xcenter=x[topchan]) #clears the fitter and does  fit
	c,b,a=f.funcparams #a*(x-x0)^2+b*(x-x0)+c
	x0=-b/(2.0*a)+x[topchan]
	hwhm=math.sqrt(-c/(2.0*a))
	return x0, hwhm, c #returns center, hwhm, height
			
##
##Fit y0+a*exp( -(x-xmu)**2/(2*xsig**2) ) to a data set
class gauss_fit(fit):
	"fit a constant baseline + gaussian y=y0+a*exp( -(x-xmu)**2/(2*xsig**2) )"
	def function(self, p, r):
		z0, a, xmu, xsigma = p
		xsigi=-1.0/(2.0*xsigma**2)
		return z0+a*Numeric.exp(xsigi*(r-xmu)**2)

	def derivs(self): 
		#analytic derivatives for a 1-d gaussian
		#z0+a*exp( -(x-xmu)**2/(2*xsig**2) )
		z0, a, xmu, xsigma = self.funcparams
		n=self.pointcount
		x=self.xarray[0,:n]
		xsigi=-1.0/(2.0*xsigma**2)
		dx=x-xmu
		dx2=dx*dx
		expfact=Numeric.exp(xsigi*dx2)
		z=a*expfact
		
		dd = zeros((n, 4), self.atype)
		dd[:,0]=1.0
		dd[:,1]=expfact
		dd[:,2]=(-2.0*xsigi)*(dx*z)
		dd[:,3]=(-2.0*xsigi/xsigma)*(dx2*z)
		
		return dd	

##
## Fit z0+a*exp( -(x-xmu)**2/(2*xsig**2) -(y-ymu)**2/(2.0*ysig**2)), an elliptical Gaussian
class gauss_fit_2d(fit):
	"fit a constant baseline + gaussian z=z0+a*exp( -(x-xmu)**2/(2*xsig**2) -(y-ymu)**2/(2.0*ysig**2))"
	def function(self, p, r):
		z0, a, xmu, xsigma, ymu, ysigma = p
		xsigi=-1.0/(2.0*xsigma**2)
		ysigi=-1.0/(2.0*ysigma**2)
		return z0+a*Numeric.exp(xsigi*(r[0]-xmu)**2+ysigi*(r[1]-ymu)**2)

	def derivs(self): 
		#analytic derivatives for a 2-d gaussian
		#z0+a*exp( -(x-xmu)**2/(2*xsig**2) -(y-ymu)**2/(2.0*ysig**2))
		z0, a, xmu, xsigma, ymu, ysigma = self.funcparams
		n=self.pointcount
		x=self.xarray[0,:n]
		y=self.xarray[1,:n]
		xsigi=-1.0/(2.0*xsigma**2)
		ysigi=-1.0/(2.0*ysigma**2)
		dx=x-xmu
		dx2=dx*dx
		dy=y-ymu
		dy2=dy*dy
		expfact=Numeric.exp(xsigi*dx2+ysigi*dy2)
		z=a*expfact
		
		dd = zeros((n, 6), self.atype)
		dd[:,0]=1.0
		dd[:,1]=expfact
		dd[:,2]=(-2.0*xsigi)*(dx*z)
		dd[:,3]=(-2.0*xsigi/xsigma)*(dx2*z)
		dd[:,4]=(-2.0*ysigi)*(dy*z)
		dd[:,5]= (-2.0*ysigi/ysigma)*(dy2*z)
		
		return dd	
##
## Fit z0+(a*hwhm**2)/((x-xmu)**2+hwhm**2)
#
#This is a sample of a minimal fitting class which uses numerical derivatives, so all it has to declare is the function.
class cauchy_fit(fit):
	"Since class cauchy_fit provides no analytic derivatives, automatic numeric differentiation will be used.  This is a minimal fitter example"
	def function(self, p, x):
		z0, a, xmu, hwhm = p
		return z0+(a*hwhm**2)/((x-xmu)**2+hwhm**2)
##
## Fit z0+(a*hwhm**2)/((x-xmu)**2+hwhm**2)**(n/2) where n=2 fits a normal Cauchy/Lorentz
#
class generalized_cauchy_fit(fit):
	"generalized_cauchy_fit fits a cauchy-like distribution with a variable exponent in the tails.  exponent=2 is true cauchy."
	def function(self, p, x):
		z0, a, xmu, hwhm, exponent = p
		return z0+a*(hwhm**2/((x-xmu)**2+hwhm**2))**(0.5*exponent)

if __name__=="__main__":
	##
	## Sample/test code for this module
	class myfit(fit):
		def function(self, params, x):
			return params[0]+params[1]*x+params[2]*x**params[3]
	
	x=myfit()
	x.set_initial_params([1.,1.,1., 3])
	x.auto_deriv_steps((.1,.1,.1, 0.01))
	
	x.add_point(0, 2)
	x.add_point(1, 5)
	x.add_point(2, 10)
	x.add_point(3, 17)
	x.add_point(4, 26.1)
	x.add_point(5, 36.9)
	
	print "\n\n***Start nonlinear test fit***" 
	for i in range(10):
		x.lm_fit_step()
		print array_str(x.funcparams, precision=5), array_str(x.funcvals, precision=3), sqrt(x.reduced_chi2)
		
	print "\n\n***Start polynomial test fit***" 
	x=polynomial_fit(2)
	x.add_point(0, 2)
	x.add_point(1, 5)
	x.add_point(2, 10)
	x.add_point(3, 17)
	x.add_point(4, 26.1)
	x.add_point(5, 36.9)
	x.compute_fit()
	print x.funcparams, x.funcvals, sqrt(x.reduced_chi2)

	print "\n\n***Start svd polynomial test fit with funny weights ***" 
	##
	## More sample/test code for this module
	class my_svd_fit(polynomial_fit):
		def compute_fit(self, lm_lambda=None):
			self.svd_hessian_compute_fit(lm_lambda)
		def weight_func(self):
			return array(range(self.pointcount), self.atype)**2+2.0
		
	x=my_svd_fit(2)
	x.add_point(0, 2)
	x.add_point(1, 5)
	x.add_point(2, 10)
	x.add_point(3, 17)
	x.add_point(4, 26.1)
	x.add_point(5, 36.9)
	x.compute_fit()
	print array_str(x.funcparams, precision=5), array_str(x.funcvals, precision=3), sqrt(x.reduced_chi2)

	print "\n\n***Start svd degenerate function nonlinear test fit ***" 
	##
	## More sample/test code for this module
	class my_svd_bad_fit(fit):
		def function(self, p, x):
			return p[0]*Numeric.exp(-p[1]+p[2]*x) #p[0] and p[1] are degenerate
		
	x=my_svd_bad_fit()
	x.set_initial_params((1.,1.,2.2))
	x.add_point(0, 2)
	x.add_point(1, 5)
	x.add_point(2, 10)
	x.add_point(3, 17)
	x.add_point(4, 26.1)
	x.add_point(5, 36.9)
	for i in range(25):
		x.damped_svd_fit_step(trace=0)
		print array_str(x.funcparams, precision=5), array_str(x.funcvals, precision=3), sqrt(x.reduced_chi2)
	print x.svd_covariance_matrix()
	
	
