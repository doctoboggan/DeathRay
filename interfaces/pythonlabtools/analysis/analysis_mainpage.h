/** \file
\brief It looks like a header file, but it's really a giant comment with Doxygen documentation in it.
*/
/** \mainpage
\author Marcus H. Mendenhall (mendenhall@users.sourceforge.net)
\date 2006

Copyright &copy; 2005-2006 Vanderbilt University. All rights reserved. \n
Developed under funding from the U.S. Government MFEL Program. \n

Project page:  http://sourceforge.net/projects/pythonlabtools/
\section intro_sec Introduction to analysis

The analysis package of pythonlabtools contains a set of pure-python routines for carrying out many
useful functions common in the physical sciences.  If differs from packages such as SciPy in that it provides 
everything in pure-python form, so it is easier to install, and is much smaller.  However, it is not
intended to be a competitor for SciPy and such.  It provides different content.  

The main large modules in analysis are the fitting_toolkit.py and C2Functions.py.  

fitting_toolkit.py provides
a very strong basis of support for generalized non-linear least-squares fitting, including bootstrapping (resampling),
weighted fits, correlated data fits, inverse Hessian, Levenberg-Marquardt, and singular-value-decomposition Hessian searches.

C2Functions.py provides a framework for carrying out numerical operations on smooth (twice-differentiable) functions, especially
(but not limited to) cubic splines.  It provides fast root finding (using inverse quadratic extrapolation) and fast adaptive
integration (10th order convergence, if the derivatives are well behaved).

\section overview_sec Overview


\section use_case Typical Use Cases
\subpage fitting_subsec 

\page fitting_subsec Fitting functions
The main documentation for this is in the fitting_toolkit package
*/
