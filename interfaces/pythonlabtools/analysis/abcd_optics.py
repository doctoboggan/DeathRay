"""Gaussian (paraxial) Optics matrix formalism and diffration calculations
Marcus H. Mendenhall, Vanderbilt University Keck Free Electron Laser Center, Nashville, TN, 37235
16 April, 2002
This is really the little brother of general_optics.py, which mostly should be used instead"""
_rcsid="$Id: abcd_optics.py 323 2011-04-06 19:10:03Z marcus $"

import math

try:
  import numpy as Numeric
  import numpy.linalg
  numeric_float=Numeric.float
  numeric_complex=Numeric.complex
  eigenvectors=numpy.linalg.eig

except:
  import Numeric
  import LinearAlgebra
  numeric_float=Numeric.Float
  numeric_complex=Numeric.Complex
  eigenvectors=LinearAlgebra.eigenvectors

Infinity="Infinity"

class qparms:
  "qparms is a class for the q-parameter structure"
  def __init__(self, lambda0, q=None, w=None, r=None):
    if q is None:
      if r is Infinity:
        rinv=0
      else:
        rinv=1.0/r
      self.q=1.0/ complex(rinv , -lambda0 / (math.pi*w**2) )
      self.w=w
      self.r=r
    else:
      self.q=q
      qi=1.0/q
      self.w=math.sqrt(-lambda0/qi.imag/math.pi)
      if abs(qi.real) < 1e-15:
        self.r=Infinity
      else: 
        self.r=1.0/qi.real      
    self.lambda0=lambda0
  
  def __str__(self):
    if self.r is Infinity:
      rstr=self.r
    else:
      rstr="%.3f"%self.r
    return "lambda= %.4e, q= (%.3f %+.3fj), w=%.3f,  r=%s"%(self.lambda0, self.q.real, self.q.imag, self.w, rstr)
    
  def qw(self, abcd):
    if isinstance(abcd, optic):
      a,b,c,d=abcd.abcd().flat
    else:
      a,b,c,d=abcd.flat
    qout=qparms(self.lambda0, q=(self.q*a+b)/(self.q*c+d))
    return qout
    
  def ztrace(self, matlist, end_z):
    return ztrace(matlist, end_z, self)

def fixname(name):
  if name is not None:
    return "("+name+")"
  else:
    return ""

class optic:
  def __init__(self, abcd,  tagstr=None):
    if tagstr is not None:
      self.tag=tagstr
    else:
      self.tag=""
    self.mat=abcd
    self.qparm=None
    
  def __str__(self):
    return self.tag
  def abcd(self):
    return self.mat
  
  def setqparm(self, qparm=None):
    self.qparm=qparm
    
  def __mul__(self, other):
    "optic2*optic1 is an optic representing the right-hand optic followed by the left i.e. left matrix multiplication semantics"
    if isinstance(other, optic):
      mat=Numeric.dot(self.mat, other.mat)
      return optic(mat , "Composite Optic:  \n"+Numeric.array_str(mat, precision=3, suppress_small=1))
    else:
      return Numeric.dot(self.mat, other)

  def __add__(self, other): #addition runs left-to-right 
    "optic1+optic2 is an optic representing the left-hand optic followed by the right i.e. algebraic semantics"
    if isinstance(other, optic):
      mat=Numeric.dot(other.mat, self.mat)
      return optic(mat, "Composite Optic:  \n"+Numeric.array_str(mat, precision=3, suppress_small=1) )
    else:
      return Numeric.dot(other, self.mat)
      
class space(optic):
  "space(l) returns abcd for a drift space of length l"
  def __init__(self, l, name=None):
    optic.__init__(self, Numeric.array(((1.0,l),(0.0,1.0))), 
        "Drift space%s:, l=%.3f" % (fixname(name), l) )

class lens(optic):
  "lens(f) returns abcd for a lens of focal length f"
  def __init__(self, f, name=None):
    optic.__init__ (self, Numeric.array(((1.0,0.0),(-1.0/f,1.0))),  
        "Lens%s: f= %.3f"%(fixname(name), f))

class identityoptic(optic):
  "identityoptic is a class used to tag optics which do not actually change the beam"
  def __init__(self, name=None):
    optic.__init__ (self, ((1,0),(0,1)),  name)
  
class aperture(identityoptic):
  "aperture(diameter) returns an identity optic labelled by diameter"
  def __init__(self, dia, name=None):
    identityoptic.__init__ (self, 
        "Aperture%s: dia= %.3f"%(fixname(name),dia))
    self.diameter=dia
    
  def __str__(self):
    if self.qparm is None:
      return self.tag
    else:
      transmission=1.0-math.exp(-((self.diameter/(2*self.qparm.w))**2))
      return self.tag + (" Transmission = %.3f" % transmission)
    
class surface(optic):
  "surface(r, n) returns abcd for a dielectric surface with radius-of-curvature r and index ratio n"
  def __init__(self, r, n, name=None):
    optic.__init__(self, Numeric.array(((1.0,0.0),((1.0-n)/(n*r),1.0/n))),  
        "Dielectric surface%s: n'=%.3f r=%.3f" % (fixname(name), n,r) )

class mirror(optic):
  "mirror(r) returns abcd for a mirror with radius-of-curvature r (f=r/2)"
  def __init__(self, r, name=None):
    optic.__init__(self, Numeric.array(((1.0,0.0),(-2.0/r,1.0))), 
        "Mirror%s: roc=%.3f" % (fixname(name), r) )

class probe(identityoptic):
  "probe() returns an identity optic but is handled in matx and ztrace as adding no length"
  def __init__(self, name=None):
    identityoptic.__init__(self, 
        "Probe%s" % (fixname(name), ) )
      
def resonator(r1, r2, l, lambda0):
  "resonator(r1, r2, length, lambda0) returns (z0, w0, w(mirror1), w(mirror2), offset for resonator with mirrors and length"
  abcd0=mirror(r1)*space(l)* mirror(r2)* space(l)
  art,brt,crt,drt=tuple(abcd0.abcd().flat)
  iqci2= (1.0 - (art+drt)**2 / 4) / brt**2
  rqci = (drt - art) / (2.0*brt)
  zoff = -rqci / (rqci**2 + iqci2)
  z0 = math.sqrt(iqci2) / (rqci**2 + iqci2)
  w0 = math.sqrt((lambda0*z0)/math.pi)
  return z0, w0, w0*math.sqrt(1+(zoff/z0)**2), w0*math.sqrt(1+((l-zoff)/z0)**2), zoff-l/2

def abcd_resonator(abcd_rt, lambda0):
  "resonator(abcd_rt,  length, lambda0) returns (q0, w0, r0) for resonator with round-trip abcd_rt at wavelength lambda"
  abcd0=abcd_rt 
  art,brt,crt,drt=tuple(abcd0.abcd().flat)
  iqci2= (1.0 - (art+drt)**2 / 4) / brt**2
  rqci = (drt - art) / (2.0*brt)
  qout = 1.0 / complex(rqci,  -math.sqrt(iqci2) )
  return qparms(lambda0, q=qout)

def matx(matlist, x):
  "matx( ((drift0, abcd0),(drift1, abcd1)...), x) returns the accumulated abcd matrix at x.  Drift_n is _before_ the element abcd_n"
  m=optic(Numeric.identity(2).astype(numeric_float))
  z=0.0
  for (dz, abcd) in matlist:
    if not isinstance(abcd, probe):
      if z+dz >= x: break
      z += dz
      m=abcd*space(dz)*m
  return space(x-z)*m
  
class ztrace:
  """ztrace(matlist, end_dist, q0) creates a list of information about the beam through the system"""
  def __init__(self, matlist, end_dist, q0):
    zpos=0.0
    objectpos=[]
    objects=[]
    for (dz,obj) in matlist: #mark out positions of optical components, backup up over probes
      objectpos.append(zpos+dz)
      if not isinstance(obj,probe): zpos+=dz
      objects.append(obj)
    zpos=0.0
    opticindex=0
    resultlist=[]
    doing_optic=0
    while (zpos < end_dist):
      qparm=q0.qw(matx(matlist, zpos))
      next_waist=zpos-qparm.q.real
      resultlist.append((zpos, qparm))
      if opticindex < len(objectpos):
        next_optic=objectpos[opticindex]
        optic=objects[opticindex]
      else:
        next_optic=end_dist+1
        optic=None
      if not doing_optic:
        if next_waist > zpos and next_waist < next_optic-1:
          zpos=next_waist
        else:
          if isinstance(optic, identityoptic):
            zpos=next_optic
            optic.setqparm(q0.qw(matx(matlist, zpos)))
            resultlist.append((objectpos[opticindex],str(optic)))
            opticindex += 1
          else:
            zpos=next_optic-1
            doing_optic=1
      else:
        resultlist.append((objectpos[opticindex],str(matlist[opticindex][1])))
        zpos+=2
        opticindex+=1
        doing_optic=0
    resultlist.append((end_dist, q0.qw(matx(matlist, end_dist))))
    self.trace=resultlist
    
  def __str__(self):
    thestr="\n\n***Starting beam trace***\n"
    for (z,info) in self.trace:
      thestr += ("%10.1f  " % z)
      if type(info)==type(" "):
        thestr+= info 
      else:
        w, r = info.w, info.r
        if r is Infinity:
          rstr="r="+r
        elif abs(r)>10000.0:
          rstr=("r=%10.2e" %r)
        else:
          rstr="r=%10.1f" % r
        thestr += ("w=%6.2f "%w) + rstr
      thestr += "\n"
    return thestr
