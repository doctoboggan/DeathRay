"""A group of classes which make it easy to manipulate smooth functions, including cubic splines. 

C2Functions know how to keep track of the first and second derivatives of functions, and to use this information in, for example, find_root()
to allow much more efficient solutions to problems for which the general solution may be expensive.

The two primary classes are 
	C2Function, which represents an unevaluted function and its derivatives, and 
	InterpolatingFunction,  which represent a cubic spline of provided data.

C2Functions can be combined with unary operators (nested functions) or binary operators (+-*/ etc.)

Developed by Marcus H. Mendenhall, Vanderbilt University Keck Free Electron Laser Center, Nashville, TN USA
email: mendenhall@users.sourceforge.net
Work supported by the US DoD  MFEL program under grant FA9550-04-1-0045
version $Id: C2Functions.py 323 2011-04-06 19:10:03Z marcus $
"""
_rcsid="$Id: C2Functions.py 323 2011-04-06 19:10:03Z marcus $"

##\file
## \brief Provides the analysis.C2Functions package.
##\package analysis.C2Functions
# \brief A group of classes which make it easy to manipulate smooth functions, including cubic splines. 
#\version $Id: C2Functions.py 323 2011-04-06 19:10:03Z marcus $
#
#C2Functions know how to keep track of the first and second derivatives of functions, and to use this information in, for example, C2Function.find_root() and 
#C2Function.partial_integrals()
#to allow much more efficient solutions to problems for which the general solution may be expensive.
#
#The two primary classes are 
#	C2Function which represents an unevaluated function and its derivatives, and 
#	InterpolatingFunction which represent a cubic spline of provided data.
#
#C2Functions can be combined with unary operators (nested/composed functions) or binary operators (+-*/ etc.)
#
#Note that if SciPy is available, the C2Functions package will adopt useful bits from it to speed things up, but is otherwise not dependent on it.
#
#Developed by Marcus H. Mendenhall, Vanderbilt University Keck Free Electron Laser Center, Nashville, TN USA
#
#email: mendenhall@users.sourceforge.net
#
#Work supported by the US DoD  MFEL program under grant FA9550-04-1-0045
#

import math
import operator
import types

try:
	#prefer numpy over Numeric since it knows how to handle Numeric arrays, too (maybe, but not reliably!)
	import numpy as _numeric 
	_numeric_float=_numeric.float64

	def native(y, yp, ypp):
		"make sure returned scalar arguments are not numpy scalars"
		if not operator.isSequenceType(y):
			return float(y), float(yp), float(ypp)
		else:
			return y, yp, ypp

except:
	import Numeric as _numeric
	_numeric_float=_numeric.Float64

	def native(y, yp, ypp):
		"make sure returned scalar arguments are not numpy scalars... not needed with Numeric"
		return y, yp, ypp

_myfuncs=_numeric

##
## \brief Our own exception class
class	C2Exception(Exception):
	pass

##
## \brief Raised if an abscissa is out of range
class	RangeError(IndexError):
	pass

##
## \brief Raised if the base class C2Function is called without a valid value_with_derivatives()
class	C2NakedFunction(C2Exception):
	pass

##
## \brief Provides support for the entire C2Function hierarchy
#
class	C2Function(object):
	"if f is a C2Function, f(x) returns the value at x, and f.value_with_derivatives returns y(x), y'(x), y''(x)"	
	ClassName='C2Function'
	name='Unnamed'
	##
	##Construct a new C2Function.  
	#\param args The default (no args) constructs with a range of (1e-308, 1e308).  
	#Otherwise,  C2Function(\a another_C2Function) copies the range.  \n
	# or \n
	#C2Function( \a first_C2, \a second_C2) sets the range to the intersection of the ranges
	def __init__(self, *args) : 
		if not args:
			self.xMin, self.xMax=-1e308, 1e308
		elif len(args)==1: #constructing from a single C2Function
			self.xMin, self.xMax=args[0].xMin, args[0].xMax
		else: #it should be two C2Functions, and we take the inner bounds of the two
			l,r=args
			self.xMin=max(l.xMin, r.xMin)
			self.xMax=min(l.xMax, r.xMax)
		
		self.sampling_grid=None
	
	##
	##Return our name	
	def __str__(self): 
		return '<%s %s, Domain=[%g, %g]>' % ((self.ClassName, self.name,)+ self.GetDomain())
	
	##
	## Set the name of this function to be returned by str()	
	#\param name the string to set the name to		
	def SetName(self, name): 
		"set the short name of the function for __str__"
		self.name=name; return self

	##
	## \brief get the value of the function, and its first & second derivative
	# \param x the point at which to evaluate the function
	# \return (f(x), f'(x), f''(x))
	def value_with_derivatives(self, x):
		raise C2NakedFunction
        
	##
	## get f(val) if val is numeric, otherwise generate the composed fonction f(val())
	#\param arg the independent variable, if numeric, otherise the inner function
	def __call__(self, arg): 
		"f(x) evaluates f(arg) without derivatives if arg is numeric, otherwise returns the composed function f(arg())"
		if isinstance(arg, C2Function): return C2ComposedFunction(self, arg)
		else: return self.value_with_derivatives(arg)[0] 
	
	##
	## Create a new interpolating function which is the evaluated composition of this with the original
	#\param interpolator an InterpolatingFunction object
	def apply(self, interpolator):
		"creates a new InterpolatingFunction which has this function applied to the original interpolater"
		return interpolator.UnaryOperator(self)

	##
	## solve f(x)==value very efficiently, with explicit knowledge of derivatives of the function
	# find_root solves by iterated inverse quadratic extrapolation for a solution to f(x)=y.  It
	# includes checks against bad convergence, so it should never be able to fail.  Unlike typical
	# secant method or fancier Brent's method finders, this does not depend in any strong wasy on the
	# brackets, unless the finder has to resort to successive approximations to close in on a root.
	# Often, it is possible to make the brackets equal to the domain of the function, if there is
	# any clue as to where the root lies, as given by the parameter \a start.  
	# \param lower_bracket the lower bound which is ever permitted in the search.
	# \param upper_bracket the upper bound. Note that the function have opposite signs at these two points
	# \param start an initial guess for where to start the search
	# \param value the target value of the function
	# \param trace print debugging info to sys.stderr if True
	def find_root(self, lower_bracket, upper_bracket, start, value, trace=False): 
		"solve f(x)==value very efficiently, with explicit knowledge of derivatives of the function"
		# can use local f(x)=a*x**2 + b*x + c 
		# and solve quadratic to find root, then iterate

		ftol=(5e-16*abs(value)+2e-308);
		xtol=(5e-16*(abs(upper_bracket)+abs(lower_bracket))+2e-308);

		root=start	#start looking in the middle
		cupper, yp, ypp=self.value_with_derivatives(upper_bracket)
		cupper -= value
		if abs(cupper) < ftol: return upper_bracket
		clower, yp, ypp=self.value_with_derivatives(lower_bracket)
		clower -= value
		if abs(clower) < ftol: return lower_bracket;

		if cupper*clower >0:
			# argh, no sign change in here!
			raise C2Exception("unbracketed root in find_root at xlower=%g, xupper=%g, bailing" %
					(lower_bracket, upper_bracket))

		delta=upper_bracket-lower_bracket	#first error step
		c, b, ypp=self.value_with_derivatives(root) # compute initial values
		c -= value
		
		while abs(delta) > xtol: # can allow quite small steps, since we have exact derivatives!
			a=ypp/2	#second derivative is 2*a
			disc=b*b-4*a*c
			if disc >= 0:
				if b>=0:
					q=-0.5*(b+math.sqrt(disc))
				else:
					q=-0.5*(b-math.sqrt(disc))

				if q*q > abs(a*c):
					delta=c/q	#since x1=q/a, x2=c/q, x1/x2=q^2/ac, this picks smaller step
				else: delta=q/a
				root+=delta;

			if disc < 0 or root<=lower_bracket or root>=upper_bracket or abs(delta) >= 0.5*(upper_bracket-lower_bracket):	
				#if we jump out of the bracket, or if the step is not smaller than half the bracket, bisect
				root=0.5*(lower_bracket+upper_bracket)	
				delta=upper_bracket-lower_bracket

			c, b, ypp=self.value_with_derivatives(root)	#get local curvature and value
			c -= value

			if trace: 
				import sys
				print >> sys.stderr, "find_root x, dx, c, b, a", ( (5*"%10.4g ") % 
					(root, delta, c, b, ypp/2) )
				
			if abs(c) < ftol or abs(c) < xtol*abs(b):	
				return root	#got it close enough

			# now, close in bracket on whichever side this still brackets
			if c*clower < 0.0:
				cupper=c
				upper_bracket=root
			else:
				clower=c
				lower_bracket=root

		return root

	##
	## \brief Set the domain of the function to (xmin, xmax).
	# Mostly, the domain is informative, and used by other functions to figure out where the function should be applied.
	# many functions can be evaluated without error outside their marked domain.
	# However, some functions for which it is wrong to do so (InterpolatingFunction, e.g.) will raise an exception
	# \param xmin the lower bound of the domain
	# \param xmax the upper bound of the domain
	def SetDomain(self, xmin, xmax): 
		"Set the domain of the function. This is mostly an advisory range, except for InterpolatingFunctions, where it matters"
		self.xMin=xmin; self.xMax=xmax; return self

	##
	## \brief get a tuple of the domain of the function
	# \return (xmin, xmax)
	def GetDomain(self):
		"returns xMin, xMax"
		return self.xMin, self.xMax

	##
	## \brief return the value of self(inner_function(x)) without explicitly creating a composed function
	#
	# If you really want the composed function self(inner), use C2ComposedFunction
	# \param inner the inner function
	# \param x the point at which to evaluate the composed function
	# \return self(inner(x)) and its two derivatives
	def compose(self, inner, x):
		"y=f.compose(g, x) returns f(g(x)), f'(g(x)), f''(g(x)) where the derivatives are with respect to x"
		y0, yp0, ypp0=inner.value_with_derivatives(x)
		y1, yp1, ypp1=self.value_with_derivatives(y0)
		return y1, yp1*yp0, ypp0*yp1+yp0*yp0*ypp1

	##
	## \brief utility to make sure python constants get converted to C2Constant objects in subclasses
	# \param arg something which might be a number or another C2Function
	# \return a C2Function
	def convert_arg(self, arg): 
		"convert constants to C2Constants"
		import operator
		if type(arg) is types.FloatType or type(arg) is types.IntType:
			return C2Constant(arg)
		else: 
			return arg
	##
	## \brief Python operator to return a function \a self +\a right 
	# \param right the right-hand term of the sum
	# \return the C2Function a+b
	def __add__(self, right):
		"a+b returns a new C2Function which represents the sum"
		return C2Sum(self, right)
	##
	## \brief Python operator to return a function \a self -\a right 
	# \param right the right-hand term of the difference
	# \return the C2Function a-b
	def __sub__(self, right):
		"a-b returns a new C2Function which represents the difference"
		return C2Diff(self, right)
	##
	## \brief Python operator to return a function \a self *\a right 
	# \param right the right-hand term of the product
	# \return the C2Function a*b
	def __mul__(self, right):
		"a*b returns a new C2Function which represents the product"
		return C2Product(self, right)
	##
	## \brief Python operator to return a function \a self /\a right 
	# \param right the denominator term of the ratio
	# \return the C2Function a/b
	def __div__(self, right):
		"a/b returns a new C2Function which represents the ratio"
		return C2Ratio(self, right)
	##
	## \brief Python operator to return a function \a self ^\a right
	# \note This includes an optimization for numerical powers.
	# \param right the exponent
	# \return the C2Function a^b
	def __pow__(self, right):
		"a**b returns a new C2Function which represents the power law, with an optimization for numerical powers"
		return C2Power(self, right)

	##
	## \brief For points in \a recur_data, compute {\f$ \int_{x_i}^{x_{i+1}} f(x) dx \f$} .
	#
	# Note: The length of the return is one less than the length of \a recur_data. 
	# partial_integrals() uses a method with an error O(dx**10) with full  information from the derivatives.
	#
	# the integration is adaptive, starting from the grid provided, and returning data in the intervals
	# between the grid points. 
	# \param recur_data grid defining the subdomains over which the integral is computed, and hints for the adaptive algorithm (on initial call)
	# \param absolute_error_tolerance total absolute error allowed on each explicit subdomain
	# \param relative_error_tolerance total relative error allowed on each explicit subdomain
	# \param derivs how much continuity?  derivs=2 => full method, 1 => less smooth function, 0 => Simpson's rule
	# \param allow_recursion allow adaptive behavior if true, otherwise just use subdomains provided
	# \param extrapolate carry out simple Richardson-Romberg extrapolation if true
	# \return  vector in which results from subdomains are returned.
	def partial_integrals(self, recur_data, **args):
		"""def partial_integrals(self, xgrid, relative_error_tolerance=1e-12, derivs=2, 
			absolute_error_tolerance=1e-12, depth=0, debug=0, extrapolate=1, allow_recursion=True)
			Return the integrals of a function between the sampling points xgrid.  
			The sum is the definite integral.
			The choices for derivs are 0, 1 or 2, anything else is an error.
			The derivs parameter is used as follows: 
				derivs=0 uses Simpsons rule (no derivative information).   
				derivs=1 uses a 6th order technique based the first derivatives, but no second derivatives
				derivs=2 uses a 9th (really 10th, since the 9th order error vanishes by symmetry) 
					order tehcnique based the first and second derivatives.
				Be very aware that the 9th order method will only really benefit with very smooth functions, 
					but then it is magic!
		"""
	
		if type(recur_data[1]) is not tuple:	#this is an initialization call, set everything up
			funcgrid=[ ( (x, )+ self.value_with_derivatives(x) ) for x in recur_data ] 
			self.total_func_evals=len(recur_data)
			
			derivs= args.get('derivs', 2)
			if derivs==0:
				eps_scale, extrap_coef= 0.1, 16.0
			elif derivs==1:
				eps_scale, extrap_coef = 0.1, 64.0
			elif derivs==2:
				eps_scale, extrap_coef = 0.01, 1024.0
			
			else:
				raise C2Exception("derivs passed to partial_integrals, must be 0, 1 or 2, got %d" % derivs)

			allow_rec= args.get('allow_recursion', True)
			extrapolate = args.get('extrapolate', True) and allow_rec #can only extrapolate after recursion
			
			recur_data=[0, funcgrid, ( ),
					args.get('absolute_error_tolerance', 1e-12),
					args.get('relative_error_tolerance', 1e-12),
					args.get('debug', 0),
					extrapolate, derivs, eps_scale, extrap_coef, allow_rec
				]			
		
		(depth, funcgrid, old_integrals, absolute_error_tolerance, relative_error_tolerance, 
				debug, extrapolate, derivs, eps_scale, extrap_coef, allow_rec)=recur_data
		
		retvals=[0.0]*(len(funcgrid)-1)
		
		for i in range(len(funcgrid)-1):
			x0, y0, yp0, ypp0=funcgrid[i]
			x2, y2, yp2, ypp2=funcgrid[i+1]
			x1=0.5*(x0+x2)
			y1, yp1, ypp1=self.value_with_derivatives(x1)
			self.total_func_evals+=1
			dx=x2-x0
			dx2=0.5*dx

			#check for underflow on step size, which prevents us from achieving specified accuracy. 
			if abs(dx) < abs(x1)*relative_error_tolerance:
				raise C2Exception("Step size underflow in partial_integrals, depth = %d, x = %.4f" %
						(depth, x1))
			
			#if we are below the top level, the previous term is already computed.  
			# Otherwise, compute it to one lower order
			if  old_integrals:
				total=old_integrals[i]
			elif derivs==2:
				total=( (14*y0 + 32*y1 + 14*y2) +  dx * (yp0 - yp2) ) * dx /60.

			elif derivs==1:
				total=(y0+4.0*y1+y2)*dx/6.0
			else:
				total=0.5*(y0+y2)*dx

			if derivs==2:
				#use ninth-order estimates for each side. (Thanks, Mathematica!)
				left=	( ( (169*ypp0 + 1024*ypp1 - 41*ypp2)*dx2 + (2727*yp0 - 5040*yp1 + 423*yp2) )*dx2 + 
						(17007*y0 + 24576*y1 - 1263*y2) )* (dx2/40320.0)
				right=	( ( (169*ypp2 + 1024*ypp1 - 41*ypp0)*dx2 - (2727*yp2 - 5040*yp1 + 423*yp0) )*dx2 + 
						(17007*y2 + 24576*y1 - 1263*y0) )* (dx2/40320.0)
			elif derivs==1:
				left= 	( (202*y0 + 256*y1 + 22*y2) + dx*(13*yp0 - 40*yp1 - 3*yp2) ) * dx /960.
				right= 	( (202*y2 + 256*y1 + 22*y0) - dx*(13*yp2 - 40*yp1 - 3*yp0) ) * dx /960.
			else:
				left=	(5*y0 + 8*y1 - y2)*dx/24.
				right=	(5*y2 + 8*y1 - y0)*dx/24.

			eps= abs(total-(left+right))*eps_scale 
			#the real error should be 2**order times smaller on this iteration, be conservative
			if extrapolate:
				eps=eps*eps_scale 
				#gain another factor of 2**order if extrapolating (typical), but be conservative
				
			if  (not allow_rec) or eps < absolute_error_tolerance or eps < abs(total)*relative_error_tolerance:
				if not extrapolate:
					retvals[i]=left+right
				else:
					retvals[i]=(extrap_coef*(left+right) - total) / (extrap_coef-1) 
					#since h fell by 2, h**6=64, and we are extrapolating in h**6
				if debug==1: 
					print "accepted results at depth ", depth,  "x, dx = %7.3f, %10.6f" % (x1, dx), 
					print "scaled error = ", eps/ (abs(total)*relative_error_tolerance)
			else:
				if debug==1: 
					print "rejected results at depth ", depth,  "x, dx = %7.3f, %10.6f" % (x1, dx), 
					print "scaled error = ", eps/ (abs(total)*relative_error_tolerance)
				recur_data[0:4]=(depth+1, (funcgrid[i], (x1, y1, yp1, ypp1), funcgrid[i+1]), 
						(left, right), absolute_error_tolerance/2 )
				l, r =self.partial_integrals(recur_data)
				retvals[i]=l+r
		if debug ==2:
			print "\nintegrating at depth ", depth
			print xgrid
			print funcgrid
			import operator
			print retvals
			if old_integrals: 
				print map(operator.sub, old_integrals, retvals)
			print "\nreturning from depth ", depth
		return retvals

	##
	## \brief give a C2Function hints about interesting points to sample for integration, etc.
	# \param grid an indexable list of points which is a starting point for any recursive sampling
	# \note typically, this grid can be quite coarse.  For periodic functions, it may be just more frequent
	# than 1 point per period.  DO NOT make it have the same period as the function, since this will certainly
	# break any recursive measures of convergence.  It will see the function the same at every point, and think
	# it is dealing with a constant.
	#
	def SetSamplingGrid(self, grid):
		"provide a set of 'interesting' points for starting to sample this function"
		self.sampling_grid=_numeric.array(grid)

	##
	## \brief Extract the list of 'interesting' points from the sampling grid which lie in the requested domain,
	# including q point at each endpoint.
	# \param xmin the lower bound for the grid.
	# \param xmax the upper bound for the grid.
	# \return a list of points at which to start looking at the function.
	def GetSamplingGrid(self, xmin, xmax):
		"get a set of points, including xmin and xmax, which are reasonable points to evaluate the function between them"
		if self.sampling_grid is None or xmin > self.sampling_grid[-1] or xmax < self.sampling_grid[0]:
			pass
			return (xmin, xmax) #dont really have any information on the funciton in this interval.
		else:

			sg=self.sampling_grid
			
			firstindex, lastindex=_numeric.searchsorted(sg, (xmin, xmax))
	
			grid=[xmin]+list(sg[firstindex:lastindex])+[xmax] #insert points  from source grid to destination into the middle of our grid
			
			if len(grid) > 2 : #attempt to clear out points put too close together at the beginning, if we have at least three points
				x0, x1, x2 = grid[:3]
				ftol=10.0*(1e-14*(abs(x0)+abs(x1))+1e-300)
				if (x1-x0) < ftol or (x1-x0) < 0.1*(x2-x0): del grid[1] #remove collision
			
			if len(grid) > 2 : #attempt to clear out points put too close together at the end, if we have at least three points
				x0, x1, x2 = grid[-3:]
				ftol=10.0*(1e-14*(abs(x0)+abs(x2))+1e-300)
				if (x2-x1) < ftol or (x2-x1) < 0.1*(x2-x0): del grid[-2] #remove collision
		
			return grid

	##
	## \brief return the definite integral from xmin to xmax of this function using our sampling_grid for hints.
	# 
	# \param xmin the lower bound
	# \param xmax the upper bound
	# \param args see partial_integrals() for meaning of these arguments 
	# \return the integral
	def integral(self, xmin, xmax, **args):
		"carry out integration using our sampling grid"
		grid=self.GetSamplingGrid(xmin, xmax)
		return sum(self.partial_integrals(grid, **args))

	##
	## \brief return a new C2Function which has integral \a norm on (\a xmin, \a xmax )
	# \param xmin the lower bound for the normalization
	# \param xmax the upper bound for the normalization
	# \param norm the desired integral
	# \return the new function
	def NormalizedFunction(self, xmin, xmax, norm=1):
		"return a function whose integral on [xmin, xmax] is norm"
		intg=self.integral(xmin, xmax)
		return C2ScaledFunction(self, norm/intg)
	##
	## \brief return a new C2Function which has square-integral \a norm on (\a xmin, \a xmax ) with weight function \a weight
	# \param xmin the lower bound for the normalization
	# \param xmax the upper bound for the normalization
	# \param weight the weight function.  Unity if omitted.
	# \param norm the desired integral
	# \return the new function
	def SquareNormalizedFunction(self, xmin, xmax, weight=None, norm=1):
		"return a function whose square integral on [xmin, xmax] with optional weight function is norm"
		mesquared=C2Quadratic(a=1.0)(self)
		if weight is not None:
			mesquared=mesquared*weight
			
		grid=self.GetSamplingGrid(xmin, xmax)
		intg=sum(mesquared.partial_integrals(grid))
		return C2ScaledFunction(self, math.sqrt(norm/intg))
	

##
# \brief Create a function which is a simple scalar multiple of the parent
class C2ScaledFunction(C2Function):
	"a lightweight class to create a function scaled vertically by a scale factor"
	ClassName='Scaled'
	##
	# \brief construct the scaled function
	# \param fn the function to scale
	# \param yscale the mutiplicative factor to apply
	def __init__(self, fn, yscale):
		C2Function.__init__(self)
		self.fn=fn
		self.yscale=yscale
		self.name=fn.name+'* %g' % yscale
		self.xMin=fn.xMin
		self.xMax=fn.xMax
		
	##
	def value_with_derivatives(self, x): 
		y, yp, ypp = self.fn.value_with_derivatives(x)
		ys=self.yscale
		return  native(y*ys, yp*ys, ypp*ys)

##
# \brief Create a function which is a constant
class C2Constant(C2Function):
	"a constant and its derivatives"
	ClassName='Constant'
	##
	# \brief construct the constant
	# \param val the constant
	def __init__(self, val):
		C2Function.__init__(self)
		self.val=val
		self.name='%g' % val

	##
	# \brief reset the value of the constant
	# \param val the new constant
	def reset(self, val):
		"reset the value to a new value"
		self.val=val

        ##
	def value_with_derivatives(self, x): 
		return self.val, 0., 0.

##
# \brief Create a function which is the sine.  Use the singleton C2Functions.C2sin to access this.
class _fC2sin(C2Function):
	"sin(x)"
	name='sin'
	def value_with_derivatives(self, x):
		q=_myfuncs.sin(x)
		return  native(q, _myfuncs.cos(x), -q)

##
# \brief a pre-constructed singleton
C2sin=_fC2sin() #make singleton

##
# \brief Create a function which is the cosine. Use the singleton C2Functions.C2cos to access this.
class _fC2cos(C2Function):
	"cos(x)"
	name='cos'
	def value_with_derivatives(self, x):
		q=_myfuncs.cos(x)
		return  native(q, -_myfuncs.sin(x), -q)
##
# \brief a pre-constructed singleton
C2cos=_fC2cos() #make singleton

##
# \brief Create a function which is the natural log. Use the singleton C2Functions.C2log to access this.
class _fC2log(C2Function):
	"log(x)"
	name='log'
	def value_with_derivatives(self, x):
		return  native(_myfuncs.log(x), 1/x, -1/(x*x))
##
# \brief a pre-constructed singleton
C2log=_fC2log() #make singleton

##
# \brief Create a function which is the e^x. Use the singleton C2Functions.C2exp to access this.
class _fC2exp(C2Function):
	"exp(x)"
	name='exp'
	def value_with_derivatives(self, x):
		q=_myfuncs.exp(x)
		return  native(q, q, q)
##
# \brief a pre-constructed singleton
C2exp=_fC2exp() #make singleton

##
# \brief Create a function which is the square root. Use the singleton C2Functions.C2sqrt to access this.
class _fC2sqrt(C2Function):
	"sqrt(x)"
	name='sqrt'
	def value_with_derivatives(self, x):
		q=_myfuncs.sqrt(x)
		return  native(q, 0.5/q, -0.25/(q*x))
##
# \brief a pre-constructed singleton
C2sqrt=_fC2sqrt() #make singleton

##
# \brief Create a function which is the \a scale /\a x. Use the singleton C2Functions.C2recip to access this as 1/x.
class C2ScaledRecip(C2Function):
	"1/x"
	name='1/x'
	##
	# \brief construct the function, and set the scale factor.
	def __init__(self, scale=1.0):
		self.scale=scale
                
        ##
	def value_with_derivatives(self, x):
		q=1.0/x
		return  native(self.scale*q, -self.scale*q*q, 2*self.scale*q*q*q)
	
##
# \brief a pre-constructed singleton for 1/x
C2recip=C2ScaledRecip() #make singleton

##
# \brief Create a function which is \a x. Use the singleton C2Functions.C2identity to access this.
class _fC2identity(C2Function):
	name='Identity'
	def value_with_derivatives(self, x):
		return x, 1.0, 0.0
##
# \brief a pre-constructed singleton identity
C2identity=_fC2identity() #make singleton

##
# \brief Create a function which is (\a x - \a x0)*\a slope + \a y0.
class C2Linear(C2Function):
	"slope*(x-x0) + y0"
	##
	## \brief construct the function
	# \param x0 the \a x offset at which f(\a x) = \a y0
	# \param slope the slope
	# \param y0 the value of the function at \a x0
	def __init__(self, x0=0.0, slope=1.0, y0=0.0):
		C2Function.__init__(self)
		self.x0=x0
		self.slope=slope
		self.y0=y0
		self.name="(%g * (x - %g) + %g)" % (slope, x0, y0)
	
	##
	## \brief reset the parameters of the function
	# \param x0 the \a x offset at which f(\a x) = \a y0, None if not reset
	# \param slope the slope, None if not reset
	# \param y0 the value of the function at \a x0, None if not reset
	def reset(self, x0=None, slope=None, y0=None):
		"reset the x0, slope or intercept to a new value"
		if slope is not None:
			self.slope=slope
		if y0 is not None:
			self.y0=y0
		if x0 is not None:
			self.x0=x0
			
	def value_with_derivatives(self, x):
		return native((x-self.x0)*self.slope+self.y0, self.slope, 0.0)

##
# \brief Create a function which is \a a *(\a x - \a x0)**2 + \a b *(\a x - \a x0) + \a c 
class C2Quadratic(C2Function):
	"a*(x-x0)**2 + b*(x-x0) + c"
	##
	## \brief construct the function
	# \param x0 the \a x offset at which f(\a x) = \a c
	# \param a the coefficient of (\a x - \a x0)**2
	# \param b the coefficient of (\a x - \a x0)
	# \param c the value of the function at \a x0
	def __init__(self, x0=0.0, a=1.0, b=0.0, c=0.0):
		C2Function.__init__(self)
		self.x0, self.a, self.b, self.c = x0, a, b, c
		self.name="(%g*(x-x0)^2 + %g*(x-x0) + %g, x0=%g)" % (a, b, c, x0)
		
	##
	## \brief reset the parameters of the function
	# \param x0 the \a x offset at which f(\a x) = \a c, None if not reset
	# \param a the coefficient of (\a x - \a x0)**2, None if not reset
	# \param b the coefficient of (\a x - \a x0), None if not reset
	# \param c the value of the function at \a x0, None if not reset
	def reset(self, x0=None, a=None, b=None, c=None):
		"reset the parameters to new values"
		if x0 is not None:
			self.x0=x0
		if a is not None:
			self.a=a
		if b is not None:
			self.b=b
		if b is not None:
			self.c=c

	def value_with_derivatives(self, x):
		dx=x-self.x0
		return native(self.a*dx*dx+self.b*dx+self.c, 2*self.a*dx+self.b, 2*self.a)

##
# \brief Create a function which is \a a\a x**\a b 
class C2PowerLaw(C2Function):
	"a*x**b where a and b are constant"
	##
	## \brief construct the function \a a\a x**\a b 
	# \param a the scale factor
	# \param b the exponent
	def __init__(self, a=1.0, b=2.0):
		C2Function.__init__(self)
		self.a, self.b = a, b
		self.b2=b-2
		self.bb1=b*(b-1)
		self.name='%g*x^%g' % (a,b)
		
	##
	## \brief reset the parameters of the function \a a\a x**\a b 
	# \param a the scale factor, None if not reset
	# \param b the the exponent, None if not reset
	def reset(self, a=None, b=None):
		"reset the parameters to new values"
		if a is not None:
			self.a=a
		if b is not None:
			self.b=b

	def value_with_derivatives(self, x):
		xp=self.a*x**self.b2
		return  native(xp*x*x, self.b*xp*x, self.bb1*xp)

##
# \brief Create a function which is c0 + c1 (x-x0) + c2 (x-x0)^2 + ...
class C2Polynomial(C2Function):
	"poly(x)"	
	##
	## \brief construct the function c0 + c1 (x-x0) + c2 (x-x0)^2 + ...
	# \param coefs the coefficients c_n (first coefficient in list is the conatant term)
	# \param x0 the center for expansion of the polyomial
	def __init__(self, coefs, x0=0.0):
		"initialize the polynomial with coefficients specified, expanding around xcenter.  Constant coefficient is coefs[0]"
		
		self.coefs=tuple(coefs)
		self.rcoefs=tuple(enumerate(self.coefs))[::-1] #record power index with coef
		self.xcenter=x0
	
	def value_with_derivatives(self, x):
		x-=self.xcenter
		xsum=0.0
		for n,c in self.rcoefs: xsum=xsum*x+c
		xpsum=0.0
		for n,c in self.rcoefs[:-1]: xpsum=xpsum*x+c*n
		xp2sum=0.0
		for n,c in self.rcoefs[:-2]: xp2sum=xp2sum*x+c*n*(n-1)
		
		return  native(xsum, xpsum, xp2sum)

		
##
# \brief create a composed function outer(inner(...)).  The functions can either be unbound class names or class instances
class C2ComposedFunction(C2Function):
	"create a composed function outer(inner(...)).  The functions can either be unbound class names or class instances"
	##
	## \brief construct the function outer(inner)
	# \param outer the outer function of the composition
	# \param inner the inner function of the composition
	# \note The functions can either be unbound class names or class instances.
	# If they are class names, they will be instantiated with default arguments
	def __init__(self, outer, inner):
		if type(inner) is types.ClassType: inner=inner() #instatiate unbound class
		if type(outer) is types.ClassType: outer=outer() #instatiate unbound class
		C2Function.__init__(self, inner) #domain is that of inner function
		self.outer=outer
		self.inner=inner
		self.name=outer.name+'('+inner.name+')'
		
	def value_with_derivatives(self, x): return self.outer.compose(self.inner, x)

##
# \brief abstract class to create a binary function f (operator) g
class C2BinaryFunction(C2Function):
	"create a binary function using a helper function which computes the derivatives"
	##
	# \brief construct the function, making sure if an argument is passed as a constant that it is converted to a C2Constant
	# \param left the left function in the binary
	# \param right the right function in the binary
	def __init__(self, left,  right):
		self.left=self.convert_arg(left)
		self.right=self.convert_arg(right)
		C2Function.__init__(self, self.left, self.right)
		
		if isinstance(left, C2BinaryFunction): p1, p2 = '(', ')'
		else: p1, p2='', ''
		self.name=p1+self.left.name+p2+self.name+self.right.name #put on parentheses to kepp hierachy obvious
		
##
# \brief class to create function f + g
class C2Sum(C2BinaryFunction):
	"C2Sum(a,b) returns a new C2Function which evaluates as a+b"
	name='+'
	def value_with_derivatives(self, x):
		y0, yp0, ypp0=self.left.value_with_derivatives(x)
		y1, yp1, ypp1=self.right.value_with_derivatives(x)
		return y0+y1, yp0+yp1, ypp0+ypp1

##
# \brief  class to create function f - g
class C2Diff(C2BinaryFunction):
	"C2Diff(a,b) returns a new C2Function which evaluates as a-b"
	name='-'
	def value_with_derivatives(self, x):
		y0, yp0, ypp0=self.left.value_with_derivatives(x)
		y1, yp1, ypp1=self.right.value_with_derivatives(x)
		return y0-y1, yp0-yp1, ypp0-ypp1

##
# \brief class to create function f * g
class C2Product(C2BinaryFunction):
	"C2Product(a,b) returns a new C2Function which evaluates as a*b"
	name='*'
	def value_with_derivatives(self, x):
		y0, yp0, ypp0=self.left.value_with_derivatives(x)
		y1, yp1, ypp1=self.right.value_with_derivatives(x)
		return y0*y1, y1*yp0+y0*yp1, ypp0*y1+2.0*yp0*yp1+ypp1*y0

##
# \brief class to create function f / g
class C2Ratio(C2BinaryFunction):
	"C2Ratio(a,b) returns a new C2Function which evaluates as a/b"
	name='/'
	def value_with_derivatives(self, x):
		y0, yp0, ypp0=self.left.value_with_derivatives(x)
		y1, yp1, ypp1=self.right.value_with_derivatives(x)
		return y0/y1, (yp0*y1-y0*yp1)/(y1*y1), (y1*y1*ypp0+y0*(2*yp1*yp1-y1*ypp1)-2*y1*yp0*yp1)/(y1*y1*y1)
##
# \brief class to create function f ** g with optimization if g is a constant
class C2Power(C2BinaryFunction):
	"C2power(a,b) returns a new C2Function which evaluates as a^b where neither is necessarily constant.  Checks if b is constant, and optimizes if so"
	name='^'
	def value_with_derivatives(self, x):
		y0, yp0, ypp0=self.left.value_with_derivatives(x)
		y1, yp1, ypp1=self.right.value_with_derivatives(x)
		if isinstance(self.right, C2Constant): #all derivatives of right side are zero, save some time
			ab2=_myfuncs.power(y0, (y1-2.0)) #this if a^(b-2), which appears often
			ab1=ab2*y0 #this is a^(b-1)
			ab=ab1*y0 #this is a^b
			ab1 *= yp0
			ab1 *= y1 #ab1 is now the derivative
			ab2 *= y1*(y1-1)*yp0*yp0+y0*y1*ypp0 #ab2 is now the second derivative
			return  native(ab,  ab1, ab2)
		else:
			loga=_myfuncs.log(y0)
			ab2=_myfuncs.exp(loga*(y1-2.0)) #this if a^(b-2), which appears often
			ab1=ab2*y0 #this is a^(b-1)
			ab=ab1*y0 #this is a^b
			yp=ab1*(yp0*y1+y0*yp1*loga)
			ypp=ab2*(y1*(y1-1)*yp0*yp0+2*y0*yp0*yp1*(1.0+y1*loga)+y0*(y1*ypp0+y0*(ypp1+yp1*yp1*loga)*loga))
			return  native(ab, yp, ypp)

##

#the following spline utilities are directly from pythonlabtools.analysis.spline, version "spline.py,v 1.23 2005/07/13 14:24:58 mendenhall Release-20050805"
#and are copied here to reduce paxckage interdependency
try:
	from scipy import linalg as _linalg
	import numpy as _numpy
	_has_linalg=True
except:
	_has_linalg=False
## \brief solve for the spline coefficients y''
##
## If we have scipy support, use a fast tridiagonal algorithm and numpy arrays internally to compute spline coefficients.
## Without scipy support, use a raw python code to compute coefficients.
## \param x array of abscissas
## \param y array of ordinates
## \param yp1 first derivative at lower edge, None if natural spline (y''(0) -> 0)
## \param ypn first derivative at upper edge, None if natural spline (y''(n) -> 0)
## \return y'' array (spline coefficients)
def _spline(x, y, yp1=None, ypn=None):
	if _has_linalg:
		"y2 = spline(x_vals,y_vals, yp1=None, ypn=None) returns the y2 table for the spline as needed by splint()"
	
		n=len(x)
		u=_numpy.zeros(n,_numpy.float64)
		
		x=_numpy.asarray(x, _numpy.float64)
		y=_numpy.asarray(y, _numpy.float64)
		
		dx=x[1:]-x[:-1]
		dx2=(x[2:]-x[:-2])
		dy=(y[1:]-y[:-1])
		dydx=dy/dx
		
		# u[i]=(y[i+1]-y[i])/float(x[i+1]-x[i]) - (y[i]-y[i-1])/float(x[i]-x[i-1])
		u[1:-1]=dydx[1:]
		u[1:-1]-=dydx[:-1] #this is an incomplete rendering of u... the rest requires recursion in the loop

		trimat=_numpy.zeros((3, n), _numpy.float64)

		trimat[0, 1:]=dx
		trimat[1, 1:-1]=dx2
		trimat[2, :-1]=dx
		trimat[0] *= (1.0/6.0)
		trimat[1] *= (1.0/3.0)
		trimat[2] *= (1.0/6.0)

		if yp1 is None:
			u[0]=0.0
			trimat[1,0]=1
			trimat[0,1]=0
		else:
			u[0]=dydx[0]-yp1
			trimat[1,0] = dx[0]/(3.0)
			
		if ypn is None:
			u[-1]=0.0
			trimat[1,-1]=1
			trimat[2,-2]=0
		else:
			u[-1]=ypn-dydx[-1]
			trimat[1,-1] = dx[-1]/(3.0)
		
		y2=_linalg.solve_banded((1,1), trimat, u, debug=0)
		return _numeric.asarray(y2, _numeric_float)
	else:
		n=len(x)
		u=_numeric.zeros(n,_numeric_float)
		y2=_numeric.zeros(n,_numeric_float)
		
		x=_numeric.asarray(x, _numeric_float)
		y=_numeric.asarray(y, _numeric_float)
		
		dx=x[1:]-x[:-1]
		dxi=1.0/dx
		dx2i=1.0/(x[2:]-x[:-2])
		dy=(y[1:]-y[:-1])
		siga=dx[:-1]*dx2i
		dydx=dy*dxi
		
		# u[i]=(y[i+1]-y[i])/float(x[i+1]-x[i]) - (y[i]-y[i-1])/float(x[i]-x[i-1])
		u[1:-1]=dydx[1:]
		u[1:-1]-=dydx[:-1] #this is an incomplete rendering of u... the rest requires recursion in the loop
		
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
##
## \brief compute the correct coefficients and insert them to allow spline extrapolation
# \param x the array of abscissas for an already existing spline
# \param y the array of ordinates for an already existing spline
# \param x the array of spline coefficients for an already existing spline
# \param xmin the lower bound to which extrapolation should be permitted (None if no lower extension)
# \param xmax the upper bound to which extrapolation should be permitted (None if no upper extension)
# \return new arrays x, y, y'' with extesions added
def _spline_extension(x, y, y2, xmin=None, xmax=None):
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

	return _numeric.concatenate(xl), _numeric.concatenate(yl), _numeric.concatenate(y2l)

##
import operator

## \brief compute the interpolated value for a set of spline coefficients and either a scalar \a x or an array of \a x values
# \param xa the abscissa table for the spline
# \param ya the ordinate table for the spline
# \param y2a the spline coefficients (second derivatives) for the spline
# \param x the value or values at which to do the interpolation
# \param derivs if True, also compute and return derivatives.  If False, return value or values only
# \return (\a y, \a y', \a y'') if \a derivs is True, \a y if \a derivs is False.  Each item will be an array if \a x was an array.
def _splint(xa, ya, y2a, x, derivs=False):
	"""returns the interpolated from from the spline
	x can either be a scalar or a listable item, in which case a Numeric Float array will be
	returned and the multiple interpolations will be done somewhat more efficiently.
	If derivs is not False, return y, y', y'' instead of just y."""
	if not operator.isSequenceType(x):
		x=float(x) #this will throw an exception if x is an array!
		if (x<xa[0] or x>xa[-1]):
			raise RangeError, "%f not in range (%f, %f) in splint()" % (x, xa[0], xa[-1])
			 
		khi=max(_numeric.searchsorted(xa,x),1)
		klo=khi-1
		#convert everything which came out of an array to a float, since numpy arrays return numpy scalars, rather than native scalars
		#this speeds things up, and makes sure numbers coming back from here are native
		h=float(xa[khi]-xa[klo])
		a=float(xa[khi]-x)/h; b=1.0-a
		ylo=float(ya[klo]); yhi=float(ya[khi]); y2lo=float(y2a[klo]); y2hi=float(y2a[khi]) 
	else:
		#if we got here, we are processing a list, and should do so more efficiently
		if (min(x)<xa[0] or max(x)>xa[-1]):
			raise RangeError, "(%f, %f) not in range (%f, %f) in splint()" % (min(x), max(x), xa[0], xa[-1])
	
		npoints=len(x)
		khi=_numeric.clip(_numeric.searchsorted(xa,_numeric.asarray(x)),1,len(xa)) 
		
		klo=khi-1
		xhi=_numeric.take(xa, khi)
		xlo=_numeric.take(xa, klo)
		yhi=_numeric.take(ya, khi)
		ylo=_numeric.take(ya, klo)
		y2hi=_numeric.take(y2a, khi)
		y2lo=_numeric.take(y2a, klo)
		
		h=(xhi-xlo).astype(_numeric_float)
		a=(xhi-x)/h
		b=1.0-a
		
	y=a*ylo+b*yhi+((a*a*a-a)*y2lo+(b*b*b-b)*y2hi)*(h*h)/6.0
	if derivs:
		return y, (yhi-ylo)/h+((3*b*b-1)*y2hi-(3*a*a-1)*y2lo)*h/6.0, b*y2hi+a*y2lo
	else:
		return y
##

#these are functions to bypass the need for lambdas in the conversion functions.  This is compatible with pickling. 
def _identity(x): return x
def _one(x): return 1.0
def _zero(x): return 0.0
def _recip(x): return 1.0/x
def _mrecip2(x): return -1.0/(x*x)
def _myexp(x): return _myfuncs.exp(x)
def _mylog(x): return _myfuncs.log(x)

##
##\class InterpolatingFunction
# \brief the parent class for various interpolators. Does untransformed cubic splines by default.
#
#An InterpolatingFunction stores a cubic spline representation of a set of x,y pairs.
#	It can also transform the variable on input and output, so that the underlying spline may live in log-log space, 
#	but such transforms are transparent to the setup and use of the function.  This makes it possible to
#	store splines of, e.g., data which are very close to a power law, as a LogLogInterpolatingFunction, and
#	to then have very accurate interpolation and extrapolation, since the curvature of such a function is small in log-log space.
#	
#	InterpolatingFunction(x, y, lowerSlope, upperSlope, XConversions, YConversions) sets up a spline.  
#	If lowerSlope or upperSlope is None, the corresponding boundary is set to 'natural', with zero second derivative.
#	XConversions is a list of g, g', g'' to evaluate for transforming the X axis.  
#	YConversions is a list of f, f', f'', f(-1) to evaluate for transforming the Y axis.
#		Note that the y transform f and f(-1) MUST be exact inverses, or the system will melt.
#	
class InterpolatingFunction(C2Function):
	"""An InterpolatingFunction stores a cubic spline or piecewise linear representation of a set of x,y pairs.
		It can also transform the variable on input and output, so that the underlying spline may live in log-log space, 
		but such transforms are transparent to the setup and use of the function.  This makes it possible to
		store splines of, e.g., data which are very close to a power law, as a LogLogInterpolatingFunction, and
		to then have very accurate interpolation and extrapolation, since the curvature of such a function is small in log-log space.
		
		InterpolatingFunction(x, y, lowerSlope, upperSlope, XConversions, YConversions, cubic_spline) sets up a spline.  
		If lowerSlope or upperSlope is None, the corresponding boundary is set to 'natural', with zero second derivative.
		XConversions is a list of g, g', g'' to evaluate for transforming the X axis.  
		YConversions is a list of f, f', f'', f(-1) to evaluate for transforming the Y axis.
			Note that the y transform f and f(-1) MUST be exact inverses, or the system will melt.
		If cubic_spline is True (default), create a cubic spline, otherwise, create a piecewise linear interpolator.
				
	""" 
	YConversions=None
	XConversions=None
	name='data'
	ClassName='InterpolatingFunction'
	
	##
	## create the InterpolatingFunction
	#\param x the array of abscissas
	#\param y the array of ordinates
	#\param lowerSlope if not None, the slope at the lower end of the spline.  If None, use 'natural' spline with zero second derivative
	#\param upperSlope if not None, the slope at the lower end of the spline.  If None, use 'natural' spline with zero second derivative
	#\param XConversions a list of functions used for transforming the abscissa
	#\param YConversions a list of functions used for tranforming the ordinate
	#\param cubic_spline is true for a normal cubic spline, false for piecewise linear interpolation
	def __init__(self, x, y, lowerSlope=None, upperSlope=None, XConversions=None, YConversions=None, cubic_spline=True):
		C2Function.__init__(self) #just on general principle, right now this does nothing
		self.SetDomain(min(x), max(x))
		self.Xraw=_numeric.array(x) #keep a private copy
		self.xInverted=False
		
		if YConversions is not None: self.YConversions=YConversions #inherit from class if not passed		
		if self.YConversions is None:
			self.fYin, self.fYinP, self.fYinPP, self.fYout = self.YConversions = _identity, _one, _zero, _identity
			self.yNonLin=False
			F=self.F=_numeric.array(y)
		else:
			self.fYin, self.fYinP, self.fYinPP, self.fYout = self.YConversions
			self.yNonLin=True
			self.F=_numeric.array([self.fYin(q) for q in y])
			if lowerSlope is not None: lowerSlope *= self.fYinP(y[0])
			if upperSlope is not None: upperSlope *= self.fYinP(y[-1])

		if XConversions is not None: self.XConversions=XConversions #inherit from class if not passed		
		if self.XConversions is None:
			self.fXin, self.fXinP, self.fXinPP, self.fXout = self.XConversions =  _identity, _one, _zero, _identity
			self.xNonLin=False
			self.X=_numeric.array(x)
		else:
			self.fXin, self.fXinP, self.fXinPP, self.fXout = self.XConversions
			self.xNonLin=True
			self.X=_numeric.array([self.fXin(q) for q in x])
			if lowerSlope is not None: lowerSlope /= self.fXinP(x[0])
			if upperSlope is not None: upperSlope /= self.fXinP(x[-1])

			if self.X[0] > self.X[-1]: #make sure our transformed X array is increasing
				self.Xraw=self.Xraw[::-1]
				self.X=self.X[::-1]
				self.F=self.F[::-1]
				self.xInverted=True
				lowerSlope, upperSlope=upperSlope, lowerSlope
					
		dx=self.X[1:]-self.X[:-1]
		if min(dx) <  0 or min(self.X) < self.X[0] or max(self.X) > self.X[-1]:
			raise C2Exception("monotonicity error in X values for interpolating function: "  + 
				_numeric.array_str(self.X))
		if cubic_spline:
			self.y2=_spline(self.X, self.F, yp1=lowerSlope, ypn=upperSlope)
		else:
			#use a dummy y2 table if we are not really cubic splining
			self.y2=_numeric.zeros(len(self.X), _numeric_float)
	##
	
	def value_with_derivatives(self, x): 
		if self.xNonLin or self.yNonLin: #skip this if this is a completely untransformed spline
			y0, yp0, ypp0=_splint(self.X, self.F, self.y2, self.fXin(x), derivs=True)
			y=self.fYout(y0)
			fpi=1.0/self.fYinP(y)
			gp=self.fXinP(x)

			# from Mathematica Dt[InverseFunction[f][g[y[x]]], x]
			yprime=gp*yp0*fpi # the real derivative of the inverse transformed output 
			fpp=self.fYinPP(y)
			gpp=self.fXinPP(x)
			#also from Mathematica Dt[InverseFunction[f][g[y[x]]], {x,2}]
			yprimeprime=(gp*gp*ypp0 + yp0*gpp - gp*gp*yp0*yp0*fpp*fpi*fpi)*fpi
			return native(y, yprime, yprimeprime)
		else:
			return _splint(self.X, self.F, self.y2, x, derivs=True)
	##
	## \brief Set extrapolation on left end of data set.
	#
	# This will be dynamically assigned to either SetLowerExtrapolation or SetUpperExtrapolation by the constructor
	# depending on whether the transformed spline is running in increasing or decreasing order.
	# This is necessary since the arrays may have been  reversed because of a transformation of \a x.
	# \param bound the bound to which the left edge of the data should be extrapolated
	def SetLeftExtrapolation(self, bound):
		"""Set extrapolation on left end of data set.  
		This will be dynamically assigned to either SetLowerExtrapolation or SetUpperExtrapolation by the constructor
		"""
		xmin=self.fXin(bound)
		if xmin >= self.X[0]: 
			raise C2Exception("Attempting to extrapolate spline within its current range: bound = %g, bounds [%g, %g]" % 
				((bound,) + self.GetDomain()) )
		
		self.X, self.F, self.y2=_spline_extension(self.X, self.F, self.y2, xmin=xmin)
		self.Xraw=_numeric.concatenate(((bound, ), self.Xraw))
		self.SetDomain(min(self.Xraw), max(self.Xraw))
		
	##
	## \brief Set extrapolation on right end of data set.
	#
	# This will be dynamically assigned to either SetLowerExtrapolation or SetUpperExtrapolation by the constructor
	# depending on whether the transformed spline is running in increasing or decreasing order.
	# This is necessary since the arrays may have been  reversed because of a transformation of \a x.
	# \param bound the bound to which the right edge of the data should be extrapolated
	def SetRightExtrapolation(self, bound):
		"""Set extrapolation on right end of data set.  
		This will be dynamically assigned to either SetLowerExtrapolation or SetUpperExtrapolation by the constructor
		"""
		xmax=self.fXin(bound)
		if xmax <= self.X[-1]: 
			raise C2Exception("Attempting to extrapolate spline within its current range: bound = %g, bounds [%g, %g]" % 
				((bound,) + self.GetDomain()) )

		self.X, self.F, self.y2=_spline_extension(self.X, self.F, self.y2, xmax=xmax)
		self.Xraw=_numeric.concatenate((self.Xraw, (bound, )))
		self.SetDomain(min(self.Xraw), max(self.Xraw))

	##
	## \brief set the extrapolation permitted on the left edge of the original data set (lowest \a x value)
	# \param bound the bound to which the left edge of the data should be extrapolated		
	def SetLowerExtrapolation(self, bound):
		if not self.xInverted:
			self.SetLeftExtrapolation(bound)
		else:
			self.SetRightExtrapolation(bound)

	##
	## \brief set the extrapolation permitted on the right edge of the original data set (hightest \a x value)
	# \param bound the bound to which the right edge of the data should be extrapolated		
	def SetUpperExtrapolation(self, bound):
		if self.xInverted:
			self.SetLeftExtrapolation(bound)
		else:
			self.SetRightExtrapolation(bound)

	##
	## \brief legacy...
	def YtoX(self):
		"returns a new InterpolatingFunction with our current grid of Y values as the X values"
		
		yv=self.fYout(self.F) #get current Y values transformed out
		if yv[1] < yv[0]: yv=yv[::-1]
		f=InterpolatingFunction(yv, yv, XConversions=self.XConversions, YConversions=self.YConversions)
		f.SetName("x values: "+self.name)
		return f
	##
	## \brief create new InterpolatingFunction C2source(self) evaluated pointwise
	# \param C2Source the outer member of the composition
	# \return new InterpolatingFunction using the same transformation rules as the parent
	# \note This has different derivatives than C2ComposedFunction(\a self, \a right) since it is evaluated pointwise
	# and then re-splined.  If you want the full derivative information, use C2ComposedFunction()
	def UnaryOperator(self, C2source):
		"return new InterpolatingFunction C2source(self)"
		y=[C2source(self.fYout(yy)) for yy in self.F] #get array of y values efficiently
		#get exact derivative of composition at each end to seed new spline.
		junk, yp0, junk = C2source.compose(self, self.Xraw[0]) 
		junk, ypn, junk = C2source.compose(self, self.Xraw[-1]) 

		f=InterpolatingFunction(self.Xraw, y, lowerSlope=yp0, upperSlope=ypn,
			XConversions=self.XConversions, YConversions=self.YConversions)
		f.name=C2source.name+'('+self.name+')'
		return f

	##
	## \brief create new InterpolatingFunction self +-*/ rhs (or any other binary operator) evaluated pointwise
	# \param rhs the right hand function for the binary
	# \param c2binary the class (NOT an instance) for the binary operator
	# \return new InterpolatingFunction using the same transformation rules as the parent
	# \note This has different derivatives than a regular binary operator such as C2Product since it is evaluated pointwise
	# and then re-splined.  If you want the full derivative information, use C2Product() (e.g.)
	def BinaryOperator(self, rhs, c2binary):
		"return new InterpolatingFunction self +-*/ rhs (or any other binary operator)"
		bf=c2binary(self, rhs)

		yv=[bf.value_with_derivatives(x) for x in self.Xraw] #get array of ( ( y, y', y''), ...)
		y=[yy[0] for yy in yv] #get y values only

		f=InterpolatingFunction(self.Xraw, y, lowerSlope=yv[0][1], upperSlope=yv[-1][1],
			XConversions=self.XConversions, YConversions=self.YConversions)
		f.name=bf.name
		return f
	##
	## \brief python operator to return a new InterpolatingFunction \a self +\a right evaluated pointwise
	# \param right the function to add
	# \return a new InterpolatingFunction with the same transformations as the parent
	def __add__(self, right):
		return self.BinaryOperator(right, C2Sum)
	##
	## \brief python operator to return a new InterpolatingFunction \a self -\a right evaluated pointwise
	# \param right the function to subtract
	# \return a new InterpolatingFunction with the same transformations as the parent
	def __sub__(self, right):
		return self.BinaryOperator(right, C2Diff)
	##
	## \brief python operator to return a new InterpolatingFunction \a self *\a right evaluated pointwise
	# \param right the function to multiply
	# \return a new InterpolatingFunction with the same transformations as the parent
	# \note This has different derivatives than C2Product(\a self, \a right) since it is evaluated pointwise
	# and then re-splined.  If you want the full derivative information, use C2Product()
	def __mul__(self, right):
		return self.BinaryOperator(right, C2Product)
	##
	## \brief python operator to return a new InterpolatingFunction \a self /\a right evaluated pointwise
	# \param right the denominator function 
	# \return a new InterpolatingFunction with the same transformations as the parent
	# \note This has different derivatives than C2Ratio(\a self, \a right) since it is evaluated pointwise
	# and then re-splined.  If you want the full derivative information, use C2Ratio()
	def __div__(self, right):
		return self.BinaryOperator(right, C2Ratio)
##
	
LogConversions=_mylog, _recip, _mrecip2, _myexp
##
## \brief An InterpolatingFunction which stores log(x) vs. y
class LogLinInterpolatingFunction(InterpolatingFunction):
	"An InterpolatingFunction which stores log(x) vs. y"
	ClassName='LogLinInterpolatingFunction'
	XConversions=LogConversions
##
## \brief An InterpolatingFunction which stores x vs. log(y)
class LinLogInterpolatingFunction(InterpolatingFunction):
	"An InterpolatingFunction which stores x vs. log(y), useful for functions with exponential-like behavior"
	ClassName='LinLogInterpolatingFunction'
	YConversions=LogConversions
##
## \brief An InterpolatingFunction which stores log(x) vs. log(y)
class LogLogInterpolatingFunction(InterpolatingFunction):
	"An InterpolatingFunction which stores log(x) vs. log(y), useful for functions with power-law-like behavior"
	ClassName='LogLogInterpolatingFunction'
	XConversions=LogConversions
	YConversions=LogConversions
##
## \brief legacy...
def LinearInterpolatingGrid(xmin, dx, count):
	"""create a linear-linear interpolating grid with both x & y set to (xmin, xmin+dx, ... xmin + dx*(count -1) )
		very useful for transformaiton with other functions e.g. 
		f=C2sin(LinearInterpolatingGrid(-0.1,0.1, 65)) creates a spline table of sin(x) slightly beyond the first period
	"""
	x=[xmin + dx*i for i in xrange(count)]
	return InterpolatingFunction(x,x).SetName('x')
##
## \brief legacy...
def LogLogInterpolatingGrid(xmin, dx, count):
	"create a log-log interpolating grid with both x & y set to (xmin, xmin*dx, ... xmin * dx**(count -1) )"
	x=[xmin]
	for i in xrange(count-1):
		x.append(x[-1]*dx)
	return LogLogInterpolatingFunction(x,x).SetName('x')

class AccumulatedHistogram(InterpolatingFunction):
	"""An InterpolatingFunction which is the cumulative integral of the (histogram) specified by binedges and binheights.
		Note than binedges should be one element longer than binheights, since the lower & upper edges are specified. 
		Note that this is a malformed spline, since the second derivatives are all zero, so it has less continuity.
		Also, note that the bin edges can be given in backwards order to generate the reversed accumulation (starting at the high end) 
	"""
	ClassName='AccumulatedHistogram'

	def __init__(self, binedges, binheights, normalize=False, inverse_function=False, drop_zeros=True, **args):
		be=_numeric.array(binedges, _numeric_float)
		bh=_numeric.array(binheights, _numeric_float)

		if drop_zeros or inverse_function: #invese functions cannot have any zero bins or they have vertical sections
		
			nz=_numeric.not_equal(bh, 0) #mask of non-empty bins, or lower edges
			if not inverse_function: nz[0]=nz[-1]=1 #always preserve end bins to keep X range, but don't dare do it for inverses
			bh=_numeric.compress(nz, bh)
			be=_numeric.compress(_numeric.concatenate( (nz, (nz[-1],) ) ), be)
				
		cum=_numeric.concatenate( ( (0,), _numeric.cumsum( (be[1:]-be[:-1])*bh ) ))
		
		if be[1] < be[0]: #fix backwards bins, if needed.
			be=be[::-1]
			cum=cum[::-1]
			cum*=-1 #the dx values were all negative if the bins were backwards, so fix the sums

		if normalize:
			cum *= (1.0/max(cum[0], cum[-1])) #always normalize on the big end

		if inverse_function:
			be, cum = cum, be #build it the other way around
			
		InterpolatingFunction.__init__(self, be, cum, **args)
		self.y2 *=0 #clear second derivatives... we know nothing about them

class LogLogAccumulatedHistogram(AccumulatedHistogram):
	"same as AccumulatedHistogram, but log-log axes"
	ClassName='LogLogAccumulatedHistogram'
	XConversions=LogConversions
	YConversions=LogConversions

class InverseIntegratedDensity(InterpolatingFunction):
	"""InverseIntegratedDensity starts with a probability density function, generates the integral, 
	and generates a LinLogInterpolatingFunction which, when evaluated using a uniform random on [0,1] returns values
	with a density distribution equal to the input distribution
	If the data are passed in reverse order (large X first), the integral is carried out from the big end,
	and then the data are reversed to the result in in increasing X order.  
	"""
	
	IntermediateInterpolator=InterpolatingFunction
	
	def __init__(self, bincenters, binheights):
		
		if not isinstance(binheights, C2Function): #must be a data table, create interpolator
			np=len(binheights)	
			be=_numeric.array(bincenters)
			bh=_numeric.array(binheights)
				
			reversed = be[1] < be[0]	#// check for backwards  channels
		
			if reversed:
				be=be[::-1]
				bh=bh[::-1]
		
			temp=self.IntermediateInterpolator(be, bh)		#// create a temporary InterpolatingFunction to integrate
		else:
			temp=binheights
			
		# integrate from first to last bin in original order, leaving results in integral
		# ask for relative error of 1e-6 on each bin, with absolute error set to 0 (since we don't know the data scale).
		integral=[0] + temp.partial_integrals(bincenters, 
				absolute_error_tolerance=0, 
				relative_error_tolerance=1e-6) 
	
		scale=1.0/sum(integral)	

		for i in range(1,len(integral)):
			integral[i]=integral[i]*scale + integral[i-1]
		integral[-1]=1.0 #force exact value on the boundary	
		
		InterpolatingFunction.__init__(self, integral, bincenters, 
							lowerSlope=1.0/(scale*temp(bincenters[0])), upperSlope=1.0/(scale*temp(bincenters[-1]))
				) 	# use integral as x axis in inverse function

class LinLogInverseIntegratedDensity(InverseIntegratedDensity):
	YConversions=LogConversions
	IntermediateInterpolator=LogLogInterpolatingFunction

class C2InverseFunction(C2Function):
	"""C2InverseFunction creates a C2Function h(x) which is the solution to g(h)=x.  It is different than just finding the 
	root, because it provides the derivatives, so it is a first-class C2Function"""
	
	def __init__(self, sourceFunction):
		"create the C2InverseFunction from the given function, and set the initial search to be from the center of the domain"
		self.fn=sourceFunction
		l,r=sourceFunction.GetDomain()
		self.start_hint=(l+r)*0.5
		# compute our domain assuming the function is monotonic so its values on its domain boundaries are our domain
		ly=sourceFunction(l)
		ry=sourceFunction(r)
		if ly>ry: ly, ry = ry, ly 
		self.SetDomain(ly, ry)

	def set_start_hint(self, hint):
		"set a hint for where to start looking for the inverse solution.  Each time a solutions is found, this is automatically updated"
		self.start_hint=hint
		
	def value_with_derivatives(self, x): 
		"return the sought value, and update the start_hint so evaluations at nearby points will be very fast"
		l,r=self.fn.GetDomain()
		y = self.fn.find_root(l, r, self.start_hint, x)
		y0, yp, ypp=self.fn.value_with_derivatives(y)
		self.start_hint=y #always start looking near previous solution, unless value is reset explicitly
		return y, 1.0/yp, -ypp/yp**3 #appropriate inverse derivs from MMA

class C2ConnectorFunction(C2Function):
	"""C2ConnectorFunction generates a smooth conection between two other C2Function instances.
	"""
	def __init__(self, f1, f2, x0, x2, auto_center=False, y1=0.0):
		""" connect f1(x0) to f2(x2) with a very smooth polynomial.  If auto_center is False,
			function(midpoint)=y1 at midpoint of the join and poly is 6th order.
			If auto_center is True, poly is 5th order, and y(midpoint) is whatever it has to be.""" 
		fdx=self.fdx=(x2-x0)/2.0
		self.fhinv=1.0/fdx
		self.fx1=(x0+x2)/2.0
		
		y0, yp0, ypp0=f1.value_with_derivatives(x0) # get left wall values from conventional computation
		y2, yp2, ypp2=f2.value_with_derivatives(x2) # get right wall values from conventional computation

		# scale derivs to put function on [-1,1] since mma  solution is done this way
		yp0*=fdx
		yp2*=fdx
		ypp0*=fdx*fdx
		ypp2*=fdx*fdx
		
		ff0=(8*(y0 + y2) + 5*(yp0 - yp2) + ypp0 + ypp2)*0.0625
		if auto_center: y1=ff0 # forces ff to be 0 if we are auto-centering
		
		# y[x_] = y1 + x (a + b x) + x [(x-1) (x+1)] (c + d x) + x (x-1)^2 (x+1)^2 (e + f x)
		# y' = a + 2 b x + d x [(x+1)(x-1)] + (c + d x)(3x^2-1) + f x [(x+1)(x-1)]^2 + (e + f x)[(x+1)(x-1)](5x^2-1)  
		# y'' = 2 b + 6x(c + d x) + 2d(3x^2-1) + 4x(e + f x)(5x^2-3) + 2f(x^2-1)(5x^2-1)
		self.fy1=y1 
		self.fa=(y2 - y0)*0.5
		self.fb=(y0 + y2)*0.5 - y1
		self.fc=(yp2+yp0-2.*self.fa)*0.25
		self.fd=(yp2-yp0-4.*self.fb)*0.25
		self.fe=(ypp2-ypp0-12.*self.fc)*0.0625
		self.ff=(ff0 - y1)
		self.SetDomain(x0,x2) # this is where the function is valid
	def value_with_derivatives(self, x):
		fhinv=self.fhinv
		dx=(x-self.fx1)*fhinv
		x0, x2 = self.GetDomain()
		q1=(x-x0)*(x-x2)*fhinv*fhinv # exactly vanish all bits at both ends
		q2=dx*q1
		
		r1=self.fa+self.fb*dx
		r2=self.fc+self.fd*dx
		r3=self.fe+self.ff*dx
		
		y=self.fy1+dx*r1+q2*r2+q1*q2*r3
		
		q3=3*q1+2
		q4=5*q1+4
		yprime=(self.fa+2*self.fb*dx+self.fd*q2+r2*q3+self.ff*q1*q2+q1*q4*r3)*fhinv
		yprime2=2*(self.fb+self.fd*q3+3*dx*r2+self.ff*q1*q4+r3*(2*dx*(5*q1+2)))*fhinv*fhinv
		return y, yprime, yprime2
	
class C2LHopitalRatio(C2Ratio):
	"""C2LHopitalRatio(a,b) returns a new C2Function which evaluates as a/b with special care near zeros of the denominator.
		It caches coefficients once it has found a zero, and evaluates very quickly afterwards near that point.
	"""
	name='/'
	
	#these are tuning parameters.  Mostly, epsx1 is the touchiest, to get the right second derivative at the crossing
	#eps0 sets the range around a denominator zero which triggers L'Hopital's rule.  If abs(dx) < eps0*x, the rule is used
	epsx1=1e-4
	epsx2=1e-4
	eps0=1e-5
	eps1=1e-14
	dblmin=2e-308
	cache=None
	
	def dxsolve(self, x, y, yp, ypp):
		"find a very nearby zero of a function based on its derivatives"
		a=ypp/2	#second derivative is 2*a
		b=yp
		c=y
		
		disc=b*b-4*a*c
		if disc >= 0:
			if b>=0:
				q=-0.5*(b+math.sqrt(disc))
			else:
				q=-0.5*(b-math.sqrt(disc))

			if q*q > abs(a*c): delta=c/q	#since x1=q/a, x2=c/q, x1/x2=q^2/ac, this picks smaller step first
			else: delta=q/a
		else:
			raise C2Exception("Thought a root should be near x= %g, didn't find one" % x)
		
		return delta
	
	def value_with_derivatives(self, x):
		"combine left and right functions into ratio, being very careful about zeros of the denominator"
		cache=self.cache
		if cache is None or x < cache[0] or x > cache[1]:  #can't get it out of cache, must compute something
			y0, yp0, ypp0=self.left.value_with_derivatives(x)
			y1, yp1, ypp1=self.right.value_with_derivatives(x)
			
			if  ( abs(y1) < self.eps0*abs(yp1)*(abs(x)+self.dblmin) ): # paranoid check for relative proximity to a simple denominator zero
				dx0=self.dxsolve(x, y0, yp0, ypp0)
				dx1=self.dxsolve(x, y1, yp1, ypp1)
									
				if abs(dx1-dx0) > self.eps1*abs(x):
					raise C2Exception("y/0 found at x=%g in LHopitalRatio" % x)
						
				dx=abs(x)*self.epsx1+self.epsx2
				
				#compute the walls of the region to be fixed with l'Hopital
				x1=x+dx1
				x0=x1-dx
				x2=x1+dx 
		
				y0, yp0, ypp0=C2Ratio.value_with_derivatives(self, x0) #get left wall values from conventional computation
				y2, yp2, ypp2=C2Ratio.value_with_derivatives(self, x2) #get right wall values						
				
				yy0, yyp0, yypp0=self.left.value_with_derivatives(x1)
				yy1, yyp1, yypp1=self.right.value_with_derivatives(x1)
				#now use L'Hopital's rule to find function at the center
				y1=yyp0/yyp1

				conn=C2ConnectorFunction(
                                        C2Quadratic(x0=x0, a=ypp0/2, b=yp0, c=y0),
                                        C2Quadratic(x0=x2, a=ypp2/2, b=yp2, c=y2),
                                        x0, x2, False, y1)
				
				self.cache=x0, x2, conn
				
			else: #not close to a zero of the denominator... compute conventional answer for ratio
				return y0/y1, (yp0*y1-y0*yp1)/(y1*y1), (y1*y1*ypp0+y0*(2*yp1*yp1-y1*ypp1)-2*y1*yp0*yp1)/(y1*y1*y1)

		#if we get here, the poly coefficients are ready to go. 
		return self.cache[-1].value_with_derivatives(x)

if __name__=="__main__":
	print _rcsid
	
	if 1:
		ag=ag1=LinearInterpolatingGrid(1, 1.0,4)	
		print ag	
		try:
			ag.SetLowerExtrapolation(2)
		except:
			import sys
			print "***got expected error on bad extrapolation: ", sys.exc_value
		else:
			print "***failed to get expected exception on bad extrapolation"
			
		ag.SetLowerExtrapolation(-2)
		ag.SetUpperExtrapolation(15)
		print ag
		
		print C2Constant(11.5)
		print C2Quadratic(x0=5, a=2, b=1, c=0)
		print C2PowerLaw(a=1.5, b=-2.3)
		print LogLogInterpolatingGrid(0.1, 1.1, 20)
		
		print C2Linear(1.3,2.5).apply(ag1)
		print C2Quadratic(0,1,0,0).apply(ag1)
		print ag1*ag1*ag1
		print (ag1*ag1*ag1).YtoX()
			
		try:
			ag13=(ag1*ag1).YtoX()
		except:
			import sys
			print "***got expected error on bad X axis: ", sys.exc_value
		else:
			print "***failed to get expected exception on bad X axis"
			
		fn=C2sin(C2sqrt(ag1*ag1*ag1)).SetDomain(0, ag1.GetDomain()[1]) #cut off sqrt(negative)
		print fn
		
		for i in range(10):
			print i, "%20.15f %20.15f" % (math.sin((i+0.01)**(3./2.)), fn(i+0.01) )
		
		x1=fn.find_root(0.0, 1.35128, 0.1, 0.995, trace=True)
		print x1, math.sin(x1**(3./2.)), fn(x1)-0.995
		
		print fn([1., 2., 3., 4.])
		
		print "\nPower law sin(x)**log(x) tests"
		fn=C2sin**C2log
		for i in range(10):
			x=0.1*i + 6.4
			print ( "%10.3f "+3*"%15.12f ")%( (x, )+fn.value_with_derivatives(x))
			
		print "\nPower law sin(x)**3.2 tests"
		fn=C2sin**3.2
		for i in range(10):
			x=0.1*i + 6.4
			print ( "%10.3f "+3*"%15.12f ")%( (x, )+fn.value_with_derivatives(x))

		import math
		print "\nIntegration tests"
		sna=C2sin(C2PowerLaw(1,2)) #integrate sin(x**2)
		for sample in (5, 11, 21, 41, 101):
			xg=_numeric.array(range(sample), _numeric_float)*(2.0/(sample-1))
			partials=sna.partial_integrals(xg)
			if sample==10: print _numeric.array_str(partials, precision=8, suppress_small=False, max_line_width=10000)
			sumsum=sum(partials)
			yg=sna(xg)
			simp=sum(sna.partial_integrals(xg, derivs=1)) 
			exact=0.804776489343756110
			print ("%3d "+6*"%18.10g") %  (sample, 
				simp, simp-exact, (exact-simp)*sample**4, 
				sumsum, sumsum-exact, (exact-sumsum)*sample**6) #the comparision is to the Fresnel Integral from Mathematica
	
	if 0:
		print "\nBessel Functions by integration"
		print """Warning... the adaptive integrator looks worse than the non-adaptive one here. 
		There is some subtle cancellation which makes uniform sampling give extremely accurate answers for Bessel's integral, 
		so it isn't the fault of the adaptive integrator.  The simple one works way too well, here, by accident.
		"""
			
		def bessj(n, z, point_density=2):
			f=C2cos(C2Linear(slope=n) - C2Constant(z) * C2sin)
			pc=int((abs(z)+abs(n)+2)*point_density)
			g=_numeric.array(range(pc), _numeric_float)*(math.pi/(pc-1))
			return sum(f.partial_integrals(g, allow_recursion=False))/math.pi, f.total_func_evals
		
		def bessj_adaptive(n, z, derivs=1):
			f=C2cos(C2Linear(slope=n) - C2Constant(z) * C2sin)
			pc=8
			g=_numeric.array(range(pc), _numeric_float)*(math.pi/(pc-1))
			return sum(f.partial_integrals(g, absolute_error_tolerance=1e-14, relative_error_tolerance=1e-14, debug=0, derivs=derivs))/math.pi, f.total_func_evals

		for order, x in ( (0, 0.1), (0,5.5), (2,3.7), (2,30.5)):
			v1, n1=bessj(order, x)
			v2, n2=bessj_adaptive(order, x, 1)
			v3, n3=bessj_adaptive(order, x, 2)
			print ("%6.2f %6.2f %6d %6d %6d "+3*"%20.15f ") % (order, x, n1, n2, n3, v1, v2, v3 )
		

	if 0:
		print "\nLogarithms  by integration"
		
		pc=3
		for lv in (0.1, 1.0, 2.0, 5.0, 10.0):
			b=math.exp(lv)
			np=int(pc*b)+4
			g=_numeric.array(range(np), _numeric_float)*(b-1)/(np-1)+1

			v0=C2recip.partial_integrals(g, allow_recursion=False)
			n0=C2recip.total_func_evals
			
			
			v1=C2recip.partial_integrals(_numeric.array((1.0,math.sqrt(b), b)), absolute_error_tolerance=1e-6, 
					extrapolate=1, debug=0, derivs=0)
			n1=C2recip.total_func_evals

			v2=C2recip.partial_integrals(_numeric.array((1.0,math.sqrt(b), b)), absolute_error_tolerance=1e-12, 
					extrapolate=1, debug=0, derivs=1)
			n2=C2recip.total_func_evals
			
			v3=C2recip.partial_integrals(_numeric.array((1.0,math.sqrt(b), b)), absolute_error_tolerance=1e-12, 
					extrapolate=1, debug=0, derivs=2)
			n3=C2recip.total_func_evals

			print ("%20.15f %10.2f %6d %6d %6d %6d "+4*"%20.15f ") % (lv, b, n0, n1, n2, n3, sum(v0), sum(v1), sum(v2), sum(v3) )

			
	if 0:
		print "\nPowers  by integration"
		
		fn=C2recip(C2Quadratic(a=1.0, b=0.01, c=0.01)) #make approximate power law
		
		pc=5
		for lv in (0.1, 1.0, 2.0, 5.0, 10.0):
			b=1.0+lv
			np=int(pc*b)+4
			g=_numeric.array(range(np), _numeric_float)*(b-1)/(np-1)+1

			v0=fn.partial_integrals(g, allow_recursion=False)
			n0=fn.total_func_evals
						
			v1=fn.partial_integrals(_numeric.array((1.0,math.sqrt(b), b)),
					absolute_error_tolerance=1e-8,  relative_error_tolerance=1e-8,
					extrapolate=0, debug=0, derivs=0)
			n1=fn.total_func_evals

			v2=fn.partial_integrals(_numeric.array((1.0,math.sqrt(b), b)),
					absolute_error_tolerance=1e-14,  relative_error_tolerance=1e-14,
					extrapolate=1, debug=0, derivs=1)
			n2=fn.total_func_evals
		
			v3=fn.partial_integrals(_numeric.array((1.0,math.sqrt(b), b)),
					absolute_error_tolerance=1e-14,  relative_error_tolerance=1e-14,
					extrapolate=1, debug=0, derivs=2)
			n3=fn.total_func_evals

			print ("%20.15f %10.2f %6d %6d %6d %6d "+4*"%20.15f ") % (lv, b, n0, n1, n2, n3, sum(v0), sum(v1), sum(v2), sum(v3) )

	if 0:
		print "\nAccumulatedHistogram tests"
		xg=(_numeric.array(range(21), _numeric_float)-10.0)*0.25
		yy=_numeric.exp(-xg[:-1]*xg[:-1])
		yy[3]=yy[8]=yy[9]=0
		ah=AccumulatedHistogram(xg[::-1], yy[::-1], normalize=True)
		print ah([-2, -1, 0, 1, 2])
		ah=AccumulatedHistogram(xg[::-1], yy[::-1], normalize=True, drop_zeros=False)
		print ah([-2, -1, 0, 1, 2])
		ahi=AccumulatedHistogram(xg, yy, normalize=True, inverse_function=True)
		print ahi([0, 0.01,0.5, 0.7, 0.95, 1])
	
	
	if 0:
		xv=_numeric.array([1.5**(0.1*i) for i in range(100)])
		yv=_numeric.array([x**(-4)+0.25*x**(-3) for x in xv])
		f=LogLogInterpolatingFunction(xv,yv, 
			lowerSlope=-4*xv[0]**(-5)+(0.25)*(-3)*xv[0]**(-4),
			upperSlope=-4*xv[-1]**(-5)+(0.25)*(-3)*xv[-1]**(-4))
		f0=C2PowerLaw(1., -4)+C2PowerLaw(0.25, -3)
		print f(_numeric.array([1.,2.,3.,4., 5., 10., 20.]))
		print f0(_numeric.array([1.,2.,3.,4., 5., 10., 20.]))
		partials=f.partial_integrals(_numeric.array([1.,2.,3.,4., 5., 10., 20., 21.]), debug=False)
		print partials, sum(partials)
		partials=f.log_log_partial_integrals(_numeric.array([1.,2.,3.,4., 5., 10., 20., 21.]), debug=False)
		print partials, sum(partials)
		pp=f0.partial_integrals(_numeric.array(range(11), _numeric_float)*0.1 + 20)
		print pp, sum(pp)
	
	if 0:
		print "\nTesting LinLogInverseIntegratedDensity for 1/e^2"
		energies=[float(2**(0.5*n)) for n in range(41)]
		spect=[10000.0/(e*e) for e in energies]
		
		e0=energies[-1]
		e1=energies[0]
		
		pf=LinLogInverseIntegratedDensity(energies[::-1], spect[::-1])
		
		print energies[0], energies[-1]
		
		for i in range(41):
			r=(0.025*i)**2
			mma=(e0*e1)/(r*e0 + e1 - r*e1)
			print "%12.6f %12.4e %12.4e %12.4f " % (r, pf(r), mma, 100*(pf(r)-mma)/mma)
		
		print "\nTesting LinLogInverseIntegratedDensity for 1/e using a C2Function instead of a table"
		energies=[float(2.0**n) for n in range(21)]
		
		e0=energies[-1]
		e1=energies[0]
				
		pf=LinLogInverseIntegratedDensity(energies[::-1], C2PowerLaw(a=1000.0, b=-1))
		
		print energies[0], energies[-1]
		
		for i in range(41):
			r=(0.025*i)**2
			mma=e0*(e1/e0)**r
			
			print "%12.6f %12.4e %12.4e %12.4e " % (r, pf(r), mma, 100*(pf(r)-mma)/mma)

	if 0:
		fn=C2sin *2.0 #make a new function
		print "\nInitial sampling grid =", 
		grid=(0., 3., 6., 9., 12.)
		for i in range(len(grid)): print grid[i],
		print
		
		fn.SetSamplingGrid(grid)
		
		print "Starting tests of samples from grid"
		
		for xmin,xmax in ( (-10,-1), (20,30), (-3, 15), (-3, 2), (-3, 7), (5.0, 5.5), (1., 7.), (5.99, 10), (2, 9.01), (5., 20.) ):
			v=fn.GetSamplingGrid(xmin,xmax)
			print "%10.3f %10.3f: " %(xmin, xmax),  
			for i in range(len(v)): print v[i],
			print
			
		sn=fn.NormalizedFunction(0., math.pi)
		
		print "integral of non-normalized and normalized function ", fn.integral(0., math.pi), sn.integral(0., math.pi)
		
		gn=fn.SquareNormalizedFunction(0., 4.0*math.pi)
		
		fn2=fn*fn
		fn2.SetSamplingGrid((0., math.pi, 2.0*math.pi, 3.0*math.pi, 4.0*math.pi))
		gn2=gn*gn
		gn2.SetSamplingGrid((0., math.pi, 2.0*math.pi, 3.0*math.pi, 4.0*math.pi))
		
		print "integral of square of non-normalized and square-normalized function ", fn2.integral(0., 4.0*math.pi), gn2.integral(0., 4.0*math.pi)
		
	
	if 1:
		import math
		print "\nL'Hopital's rule test"
		for fn, fn0 in (
			(C2LHopitalRatio(C2sin, C2Linear(y0=-math.pi) ) , lambda x: math.sin(x)/ (x-math.pi) ),
			(C2LHopitalRatio(C2sin, C2Linear(y0=-math.pi)/C2Linear()), lambda x: math.sin(x)/ (x-math.pi) * x),
			(C2LHopitalRatio(C2Linear()*C2sin, C2Linear(y0=-math.pi)), lambda x: math.sin(x)/ (x-math.pi) * x),	
		):
			print
			print fn
			for x in (0.1, 1, math.pi-0.1, math.pi-0.001, math.pi-1e-6, math.pi+1e-14, math.pi+1e-12):
				y, yp, ypp=fn.value_with_derivatives(x)
				print 5*"%22.15f" % ( x, y, yp, ypp, fn0(x) )
	
	if 1:
		import math
		print "inverse exponential function test"
		myexp=_fC2exp() #make a private copy of exp so we can change its domain
		myexp.SetDomain(-10,10)
		a=C2InverseFunction(myexp)
		y, yp, ypp=a.value_with_derivatives(3)
		print y, yp, ypp
		print myexp(y), math.log(3), (a(3.01)-a(2.99))*50, (a(3.01)+a(2.99)-2.0*a(3))*10000
		print a.GetDomain()		
	
