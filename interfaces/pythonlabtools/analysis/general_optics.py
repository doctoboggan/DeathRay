"""Compute the properties of a diffracting TEM00 Gaussian beam as it passes through an optical system.
This provides utilities to enable the user to lay out a complete optical bench, with mirrors, lenses,
diffraction gratings, etc., and run a laser beam through it.  
It correctly handles off-axis optics of most types (tilted lenses & mirrors, e.g.).
It has been used to model a 10 Joule Nd:Glass CPA system at Vanderbilt University, for example
"""
_rcsid="$Id: general_optics.py 323 2011-04-06 19:10:03Z marcus $"

from math import *
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

import types
import traceback

clight=299792458. #m/sec
deg=pi/180.0

Infinity="Infinity"

ambient_index=1.0003 #air

def get_ambient_index(lambda0):
        if type(ambient_index) is types.FunctionType:
                return ambient_index(lambda0)
        else:
                return ambient_index

def reset():
        global ambient_index
        ambient_index=1.0003

def vec_mag(vec):
        return math.sqrt(Numeric.sum(vec*vec))

def planesolve(x0, u, x1, v):
        "planesolve(x0, u, x1, v) returns a, x such that x_=a*u_+x0_ solves (x_-x1_).v_=0"
        if vec_mag(x1-x0) < 1e-10:
                return 0, x1
        a=Numeric.dot((x1-x0), v) / Numeric.dot(u,v)
        #print "\nplanesolve: ", x0, u, x1, v, a, a*u+x0, "\n"
        return a, a*u+x0

def cross(a,b):
        x1,y1,z1=tuple(a)
        x2,y2,z2=tuple(b)
        return Numeric.array((y1*z2-z1*y2, z1*x2-x1*z2, x1*y2-y1*x2))
        
def wrap_angle(theta):
        "wrap_angle always returns an angle in (-180,180)"
        return ( (theta + 180) % 360 ) -180

def sincosdeg(theta_deg):
        return math.sin(theta_deg*deg), math.cos(theta_deg*deg)

def normalize(x,y):
        rho=math.sqrt(x*x+y*y)
        if rho < 1e-10:
                return 1., 0.
        else:
                return x/rho, y/rho

def eulermat(theta, eta, phi):
        "eulermat(theta, eta, phi) returns r(eta)*r(theta)*r(phi) phi=orientation around normal, theta=yaw, eta=normal roll"
        pm=Numeric.identity(3).astype(numeric_float)
        em=Numeric.identity(3).astype(numeric_float)
        tm=Numeric.identity(3).astype(numeric_float)
        sp, cp=sincosdeg(phi)
        st, ct=sincosdeg(theta)
        se, ce=sincosdeg(eta)
        pm[0,0]=pm[1,1]=cp; pm[0,1]=-sp; pm[1,0]=sp
        em[0,0]=em[1,1]=ce; em[0,1]=-se; em[1,0]=se
        tm[0,0]=tm[2,2]=ct; tm[2,0]=-st; tm[0,2]=st
        return Numeric.dot(em, Numeric.dot(tm, pm))


class euler:
        def __init__(self, theta, eta, phi):
                self.theta=theta
                self.eta=eta
                self.phi=phi
                self.mat=eulermat(theta, eta, phi)
        
        def __str__(self):
                s=""
                if self.theta != 0:
                        s=s+"theta = %.1f, " % self.theta
                if self.eta != 0:
                        s=s+"eta = %.1f, " % self.eta
                if self.phi != 0:
                        s=s+"phi = %.1f" % self.phi
                if s[-2:]==", ": s=s[:-2]
                return s

def general_simil_tens(transform, tens, reversed=0):
        "return transform^(-1)*tens*transform or the other way around if reversed=1"
        q,r,s,t=transform[0,0], transform[0,1], transform[1,0], transform[1,1]
        inverse=Numeric.array(((t,-r),(-s,q))) / (q*t-r*s)
        if reversed:
                inverse, transform=transform, inverse
        return Numeric.dot(inverse, Numeric.dot(tens, transform))

def simil_tens_cs(k, s, tens):
        "similarity transform a 2x2 tensor by angle k=cos(theta), s=sin(theta)."
        a,b,c,d=tens[0,0], tens[0,1], tens[1,0], tens[1,1]
        s2=s*s; k2=k*k; sk=s*k
        a1=a*k2+d*s2+sk*(b+c)
        b1=b*k2-c*s2+sk*(d-a)
        c1=c*k2-b*s2+sk*(d-a)
        d1=d*k2+a*s2-sk*(b+c)
        return Numeric.array(((a1,b1),(c1,d1)))

def simil_tens(theta, tens):
        "similarity transform a 2x2 tensor.  If the tensor is deeper than 2nd rank, the inner indices are passed through"
        return simil_tens_cs(math.cos(theta), math.sin(theta), tens)

def principal_axis_angle(q22):
        a,b,c,d=tuple(Numeric.ravel(q22))
        if abs(d-a) < 1e-10: return 0
        #if we are passed a q-tensor for which 2b/(d-a) isn't real, this is wrong!
        y=(2*b/(d-a))
        qtheta=math.atan(y.real)/2.0 #principal axis direction of q
        if abs(y.real) > 1e-20 and abs(y.imag)/abs(y.real) > 1e-6:
                raise "Bad tensor to diagonalize: y="+str(y)+" theta=: "+str(qtheta/deg)+"\n"+str(q22)
                
        return qtheta

def expand_to_2x2tensor(object):
        "expand x to ((x,0),(0,x)), (x,y) to ((x,0),(0,y)), ((x,t),(z,t)) to itself"
        a=Numeric.array(object)
        if a.shape==():
                return a[0]*Numeric.identity(2)
        elif a.shape==(2,):
                return Numeric.array(((a[0],0),(0,a[1])))
        else:
                return a
                

class qtens:
        "this is the heart of the general optics package: the 2x2 transverse tensor q parameter, and the book-keeping it needs"
        
        def __init__(self, lambda_initial, q=None, w=None, r=None, name=None, qit=None, medium_index=1.0):
                """build a q tensor from 
                        a) another valid inverse q tensor qit, 
                        b) a scalar complex q parameter which creates a diagonal q inverse tensor ( (1/q, 0), (0,1/q) )
                        c) a vector of two q parameters which creates a diagonal q inverse tensor ( (1/q[0], 0), (0, 1/q[1]) )
                        d) a radius of curvature r, wavelength lambda_initial, and medium index, which creates a diagonal tensor.  
                                If r is general_optics.Infinity, beam is collimated
                """
                
                self.name=name                  
                self.lambda0=lambda_initial*medium_index
                self.medium_index=medium_index
                if qit is not None: #we are given a real inverse-q tensor, just use it
                        self.qit=qit
                else:
                        if q is None:
                                if r is Infinity:
                                        rinv=0
                                else:
                                        rinv=1.0/r
                                qi=complex(rinv, -self.lambda0 / (self.medium_index*(math.pi*w**2)) )
                                self.qit=Numeric.array(((qi,0),(0,qi)))
                        elif isinstance(q, complex):
                                self.qit=Numeric.array(((1.0/q,0),(0,1.0/q)))
                        else:
                                self.qit=Numeric.array(((1.0/q[0],0),(0,1.0/q[1])))
                                
        def q_moments(self):
                "return the eigenvectors v and complex q eigenvalues for this q tensor"
                u,v=eigenvectors(self.qit)
                return v, 1.0/u[0], 1.0/u[1]
        
        def qi_moments(self):
                "return the eigenvectors v and complex inverse q eigenvalues for this q tensor"
                u,v = eigenvectors(self.qit)
                return v, u[0], u[1]


        def set_medium_index(self, new_index):
                "shift the current q tensor through a perpendicular planar boundary with a different index"
                self.qit=self.qit*(self.medium_index/new_index)
                self.medium_index=new_index
                
        def rw(self, qi):
                "get the radius of curvature r and the spot size w for a given inverse qi assuming our wavelength and index of refraction"
                w=math.sqrt(-self.lambda0/qi.imag/math.pi/self.medium_index)
                if abs(qi.real) < 1e-15:
                        r=Infinity
                else: 
                        r=1.0/qi.real                   
                return r, w
        
        def next_waist(self):
                "find the distance to the next waist on either of our principal axes.  If the number is negative, we are past the waist."
                theta, qx, qy=self.q_moments()
                qxr=qx.real
                qyr=qy.real
                if qxr*qyr < 0:
                        return -min((qxr,qyr)) #one is negative, use it
                else:
                        return -max((qxr, qyr)) #the least negative one is the first waist, or no waist if both positive
                
        def rwstr(self, qi):
                "format ourself as a nice string given r, w and the distance dz to the next waist"
                r,w=self.rw(qi)
                if r is not Infinity:
                        r="%.5g" % r
                dz=(1.0/qi).real
                return ("r=%s w=%.5g dz=%.4f" % (r,w, dz)) # +" qi=("+str(qi)+")"
                
        def __str__(self):
                theta, q0, q1=self.qi_moments()
                if self.name is not None:
                        s=self.name+": "
                else: 
                        s=""
                        
                if abs(q0-q1)/(abs(q0)+abs(q1)) < 1e-2:
                        s=s+"q={"+self.rwstr(q0)+"}"
                else:
                        s=s+"qxx={"+self.rwstr(q0)+"}, qyy={"+self.rwstr(q1)+"}"
                        
                return s
        def __repr__(self):
                return self.__str__()
                
        def qw(self, element):
                "for a given optical element which provides a q_transform method, apply it to ourself"
                element.q_transform(self)               
                return self #make daisy-chaining easy
        
        def abcd_transform(self, abcd):
                """for a given abcd matrix, apply it to ourself.  
                        If the matrix elements themselves are vectors, it is an on-axis transform with different x & y matrices.  
                        Such a matrox would look like ( ( (ax, ay), (by, by) ), ( (cx, cy), (dx, dy) ) ).
                        If the matrix elements themselves are tensors, it is operating off axis.  
                        Such a matrox would look like ( ( ( ( axx, axy ) , ( ayx, ayy )), ( ( bxx, bxy ) , ( byx, byy )) ), ( ... ) )
                """
                dot=Numeric.dot
                ar=Numeric.array
                a, b, c, d = [expand_to_2x2tensor(i) for i in ar(abcd).flat]
                q,r,s,t=(a+dot(b, self.qit)).flat
                inverse=ar(((t,-r),(-s,q))) / (q*t-r*s)
                self.qit=dot(c+dot(d, self.qit), inverse)
        
        def drift(self, length):
                "advance the beam forward a distance length"
                q,r,s,t=(Numeric.identity(2)+length*self.qit).flat
                inverse=Numeric.array(((t,-r),(-s,q))) *(1.0/ (q*t-r*s))
                self.qit=Numeric.dot(self.qit, inverse)

        def focus(self, strength):
                "apply a pure focusing strength.  It can be a scalar in diopters, a vector of x & y strengths, or a tensor for an off-axis cylindrical lens"
                self.qit=self.qit+expand_to_2x2tensor(strength)

        def clone(self, newname=None):
                "make a complete clone of ourself"
                q=copy.copy(self)
                if newname is not None:
                        q.name=newname
                return q

        def transform(self, tensor):
                "transform ourself by tensor . qinv . transpose(conjugate(tensor)).  Note that if tensor is not unitary, this isn't either."
                tr=Numeric.transpose
                dot=Numeric.dot
                self.qit=dot(tensor, dot(self.qit, Numeric.conjugate(tr(tensor))))
                return self
                
import exceptions

class OpticDirectionError(exceptions.AssertionError):
        "Light pointing the wrong way to hit this optic!"
import copy

class beam:
        """     the beam class carries around information for a beam of light: starting point, polarization, wavelength... starting along +z.
                It also carries around a dictionary of markers which record snapshots of the beam at interesting pointds along its trajectory
        """
        def __init__(self, x0, q, lam=None, polarization=(1,0), medium_index=None):
                
                self.x0=Numeric.array(x0,numeric_float)
                self.matrix_to_global=Numeric.identity(3).astype(numeric_float)
                self.polarization=Numeric.array(polarization, numeric_complex)
                if isinstance(q, qtens):
                        self.q=q.clone()
                else:
                        if medium_index is None:
                                medium_index=get_ambient_index(lam)
                        self.q=qtens(lam, q=q, medium_index=medium_index)
                self.total_drift=0.0 #accumulated travel distance
                self.total_drift_time=0.0 #accumulated distance*index
                self.marks={"order":[]}
        
        def direction(self):
                "get the current propagation direction of the beam"
                return Numeric.array(self.matrix_to_global[:,2])
        
        def set_medium_index(self, new_index):
                "adjust the beam for a new index of refraction"
                self.q.set_medium_index(new_index)
                return self
        
        def get_medium_index(self):
                "get the index of the material in which the beam is currently propagating"
                return self.q.medium_index
                
        def set_lambda(self, lambda0):
                "set the wavelength of the beam to a new value"
                self.q.lambda0=lambda0
                return self
        
        def get_lambda(self):
                "get the wavelength that has been set"
                return self.q.lambda0
                
        def free_drift(self, distance):
                "allow the beam to step forward a specified distance, and set some variables which can be recorded in a marker, if desired" 
                self.q.drift(distance)
                self.total_drift=self.total_drift+distance
                self.x0=self.x0+self.direction()*distance
                self.total_drift_time=self.total_drift_time+distance*self.q.medium_index
                self.incoming_q=self.q.clone()
                self.footprint_q=self.q.clone()
                return self
                
        def localize(self, optic):
                """transform the beam into the local coordinate system of an optic, taking care to handle intersecting an optic at any angle and position. 
                This is typically used by optics to get the q parameter (etc.) of the beam as it appears in the optic's preferred coordinate system
                It also records information about the shape of the beam which can be captured by setting a marker.
                """
                ar=Numeric.array
                dot=Numeric.dot
                tr=Numeric.transpose
                
                if hasattr(self,"local_x0"):
                        raise "attempt to localize already localized beam at optic: "+optic.name
                self.incoming_direction=self.direction()
                cm=dot(optic.matrix_to_local, self.matrix_to_global)
                cm2=ar(cm[0:2,0:2])
                a,b,c,d=tuple(cm2.flat)
                cm2inv=ar(((d,-b),(-c,a)))/(a*d-b*c)
                self.incoming_q=self.q.clone()
                self.q.transform(cm2)
                self.footprint_q=self.q.clone() #keep a copy of the localized q for markers
                self.local_x0=dot(optic.matrix_to_local, self.x0-optic.center)
                self.local_direction=ar(cm[:,2])
                self.localize_tensor_transform=cm2inv
                self.local_polarization=dot(cm2, self.polarization)
                
        def globalize(self, optic):     
                "undo the localizing transform.  Typically called by an optic after it has applied itself to us in its preferred coordinate system"
                ar=Numeric.array
                dot=Numeric.dot
                tr=Numeric.transpose
                
                cm=dot(optic.matrix_to_local, self.matrix_to_global)
                cm2=ar(cm[0:2,0:2])
                a,b,c,d=tuple(cm2.flat)
                cm2inv=ar(((d,-b),(-c,a)))/(a*d-b*c)
                self.q.transform(cm2inv)        
                self.polarization=dot(cm2inv, self.local_polarization)
                
                del self.local_x0, self.local_direction, self.localize_tensor_transform, self.local_polarization
                
        def transform(self, matrix):
                "transform the beam into a new coordinate system"
                ar=Numeric.array
                dot=Numeric.dot
                mat=dot(matrix, self.matrix_to_global)
                matl=[x/vec_mag(x) for x in mat] #make sure unit vectors stay that way!
                self.matrix_to_global=Numeric.array(matl)
                        
        def update_q(self, optic):
                "update our q parameter for a given optic.  See qtens.qw for more info"
                self.q.qw(optic)
                        
        def __str__(self):
                return "beam: x0=%s, dir=%s, %s" % (Numeric.array_str(self.x0, precision=3, suppress_small=1),
                                Numeric.array_str(self.direction(), precision=3, suppress_small=1),
                                str(self.q))

        def __repr__(self):
                return self.__str__()
        
        def clone(self):
                "make a complete clone of the beam"
                b=copy.copy(self)
                b.q=copy.copy(self.q) #copy q a little deeper
                return b
                
        def clone_no_marks(self):
                "make a clone of the beam without any marks.  This is used by the marks system to embed non-recursive snapshots of the beam into the marks array"
                marks=self.marks
                del self.marks
                q=self.clone()
                self.marks=marks
                return q
        
        def shift_lambda(self, delta):
                """reset the beam to a wavelength shifted by delta from the current wavelength.  
                Typically used on a cloned beam to prepare a set of beams with different wavelengths but otherwise identical for propagation
                """ 
                self.set_lambda(self.get_lambda()+delta)
                return self
        
        def x(self, optic):
                """apply an optic's tranform method to us, and return self for daisy chaining.  For example,
                        b.x(mylens).x(mygrating).x(mydrift) etc. causes the beam to be passed theough mylens, mygrating, and mydrift in that order.
                """
                optic.transform(self)
                return self #to make daisy-chains easy
        
        def mark(self, label=None): 
                "record an entry in the marks array as to what we look like here"
                if not self.marks.has_key(label):
                        self.marks[label]=[] #empty list for this optic
                        
                self.marks[label].append(self.clone_no_marks())
                self.marks["order"].append((label, len(self.marks[label])-1))

        def transformation_matrix_to_table(self, up):
                """find a best-effort transformation matrix which describes our current direction relative to the vector 'up'.
                        This is used to find a matrix which transforms the beam into a coordinate system which looks natural on the optics table.
                        Returns flag, matrix where flag is 0 if there is no obvious solution, and 1 if there is a pretty good solution.
                        If our direction is close to perpendicular to 'up', the matrix puts z in our propagation direction, x perpendicular to 'up' and y perpendicular to x & z.
                        If the beam is close to parallel to 'up', returns the identity matrix.
                        The result when the flag is true is a nice coordinate system in which x lies in the plane of the table, y lies nearly in the cirection of 'up'
                        and z is the beam direction.
                """
                ar=Numeric.array
                dot=Numeric.dot
                tr=Numeric.transpose
                
                dir=self.matrix_to_global
                z=dir[:,2]
                x=cross(up,z)
                xmag=sqrt(dot(x,x))
                if xmag < 0.1 : #z is not even close to perpendicular to up!
                        return 0, Numeric.identity(3).astype(numeric_float) #punt, return false and identity
                else:
                        x=x/xmag
                        y=cross(z,x) #may be tilted if the beam isn't completely level
                        direction=tr(ar((x,y,z)))
                        return 1, dot(tr(direction), dir) #coordinates are rational, return true and transform

        def transform_q_to_table(self, qi, up=(0,1,0)):
                "return qix, qiy (our inverse q parameter diagonal components) in a coordinate system relative to the direction 'up', if possible"
                dot=Numeric.dot
                tr=Numeric.transpose
                ok, matrix=self.transformation_matrix_to_table(up)
                if not ok : #z is not even close to perpendicular to up!
                        theta, qix, qiy=qi.qi_moments()
                        return qix, qiy #so just use principal moments  
                else:
                        xyt=matrix[0:2,0:2]
                        qiprime=dot(xyt, dot(qi.qit, tr(xyt)))
                        return qiprime[0,0], qiprime[1,1]

class general_optic(object):
        "general_optic a a class which provides coordinate-system and transport support for many 'atomic' optics types such as thin lenses, mirrors, and gratings"
        def __init__(self, name, center=(0,0,0), angle=0, **extras):
                "set up our name, center position, and angle, and any extra keyword, value pairs.  See general_optic.reset_angle for the meaning of the angle"
                self.init(name, center, angle, extras)
                
        def init(self, name, center, angle, extras):
                
                self.abcd=Numeric.identity(2).astype(numeric_float) #predefine this as a default abcd matrix (in 2 dimensions)
                self.driftlength=0.0
                
                #copy any extra information directly into the class dictionary
                for i in extras.keys():
                        setattr(self, i, extras[i])

                if len(center)==2: #2-d optics live in the x-z plane
                        center=(center[0], 0, center[1])
                
                self.center=Numeric.array(center, numeric_float)
                self.name=name
                
                self.reset_angle(angle)
                self.post_init()
        
        def post_init(self):
                """override post_init in subclasses to do computations after the construction, usually based on extra keywords.  
                This avoids the need for every general_optic to override the default constructor. 
                """
                pass
        
        def add_info(self, **keys):
                "copy extra keywrd-value pairs into our attributes"
                for i in keys.keys():
                        setattr(self, i, keys[i])
        
        def __str__(self):
                if self.name is not None:
                        return (self.name+" "+Numeric.array_str(self.center, precision=3, suppress_small=1) +
                                        " "+Numeric.array_str(self.cosines, precision=3, suppress_small=1))
                else:
                        return "Unnamed optic"
        
        def entrance_center(self):
                """return the coordiinate at which this optic's front/entrance surface is centered.  For 'atomic' optics, it is the center of the whole object'
                        override this for thick optics, etc.
                """
                return self.center
        def exit_center(self):
                """return the coordiinate at which this optic's back/exit surface is centered.  For 'atomic' optics, it is the center of the whole object'
                        override this for thick optics, etc.
                """
                return self.center

        def transform_into_local(self, direction):
                "take a vector in global coordinates, and express it in the local, preferred frame of this optic"
                return Numeric.dot(self.matrix_to_local, direction)
        
        def transform_into_global(self, local_direction):
                """take a vector in the local frame of the optic, and express it globally.  For example, transform_into_global((0,0,1)) 
                usually points in the global direction of forward propagation through the optic
                """
                return Numeric.dot(self.matrix_to_global, local_direction)
                
        def check_hit_optic(self):
                "check to make sure local coordinates are within bounds of optic: default always true"
                return 1
        
        def localize_tensor(self, tens):
                "compute what a tensor looks like in the coordinate system of self.beam "
                dot=Numeric.dot
                tr=Numeric.transpose
                return dot(self.beam.localize_tensor_transform, dot(tens, tr(self.beam.localize_tensor_transform)))
        
        def globalize_transform(self, transform):
                """express a transform which is represented in our local frame as a global transform.  Used typically to 
                express a rotation about a specific axis in our preferred frame globally
                """
                dot=Numeric.dot
                return dot(self.matrix_to_global, dot(transform, self.matrix_to_local))
                
        def transform(self, beam, backwards=0):
                "transform(beam, backwards) set up local coordinates, calls local_transform on the beam, and resets it to global coordinates.  Returns self for chaining."
                self.beam=beam
                self.backwards=backwards #in case anyone needs to know (e.g. dielectric interfaces)
                beam.localize(self)
                self.check_hit_optic()
                self.local_transform()
                beam.globalize(self)
                del self.beam, self.backwards #get it out of our dictionary so it is an error if not localized
                return self
                
        def local_transform(self):
                "by default, do abcd_transform on self.beam, assuming small angles"
                ar=Numeric.array
                dot=Numeric.dot
                tr=Numeric.transpose
                xp, yp, zp=tuple(self.beam.local_direction)  #it better be a small angle, so sin(theta)=theta for this to work
                dx, dy, dz=tuple(self.beam.local_x0) #dz should always be zero in these coordinates
                x1,xp1, y1, yp1 =self.abcd_transform((dx, xp, dy, yp))
                sx=-(xp1-xp) #this is sort of a sine of a rotation angle of x about y, with the right sign
                if abs(sx) > 0.25:
                        raise ValueError("x-angle is too big to by paraxial... %.3f" % sx)
                        
                cx=math.sqrt(1-sx*sx)
                sy=-(yp1-yp) #this is sort of a sine of a rotation angle of y about x, with the right sign
                if abs(sy) > 0.25:
                        raise ValueError("y-angle is too big to by paraxial... %.3f" % sy)
                cy=math.sqrt(1-sy*sy)
                rot=dot(ar(((cx, 0, -sx),(0,1,0),(sx,0,cx))),ar(((1,0,0),(0,cy,-sy),(0,sy,cy))))
                self.beam.transform(self.globalize_transform(rot))
                self.q_transform()
                
        def intersect(self, from_point, from_direction):
                "find the intersection of a beam coming from from_point, going in from_direction, with our center. Raise an exception if beam won't hit center going that way."
                a,x  =  planesolve(from_point, from_direction, self.center, self.cosines)  
                
                if a < -1e-9:
                        raise OpticDirectionError, "Optic found on backwards side of beam: "+str(self)+" incoming (x,y,z)="+\
                        Numeric.array_str(from_point, precision=3, suppress_small=1)+" cosines="+\
                        Numeric.array_str(from_direction, precision=3, suppress_small=1) + \
                        (" distance = %.3f, point=(%.3f %.3f %.3f)" % (a, x[0], x[1], x[2]))
                return a, x

        def transport_to_here(self, beam):
                "transport beam from wherever it is to our center"
                distance, x=self.intersect(beam.x0, beam.direction())
                beam.free_drift(distance)
                return self
                
        def format_geometry(self):
                return ("(x,y,z)=(%.3f, %.3f, %.3f) "%tuple(self.center))+str(self.euler)
        
        def reset_angle(self, angle):
                """set the angle of the optic.  If angle is a scalar, it is an absolute rotation about the y axis.
                Otherwise, angle should be a triple Euler angles theta (yaw), eta (roll around absolute z), phi(roll around local z)            
                """
                if type(angle) != types.TupleType: #convert conventional angle to rotation about y only
                        self.euler=euler(angle, 0, 0)
                        theta=angle
                else: #this should be a triple angles theta (yaw), eta (roll around absolute z), phi(roll around local z)                       
                        self.euler=euler(angle[0], angle[1], angle[2])
                        theta=angle[0]

                self.matrix_to_global=self.euler.mat
                self.matrix_to_local=Numeric.transpose(self.euler.mat)
                self.cosines=self.transform_into_global(Numeric.array((0,0,1)))
        
        def old_rotate_in_local_frame(self, matrix_to_global):
                self.matrix_to_global=Numeric.dot(self.matrix_to_global, matrix_to_global)
                self.matrix_to_local=Numeric.transpose(self.matrix_to_global)
                self.cosines=self.transform_into_global(Numeric.array((0,0,1)))
                
        def rotate_in_local_frame(self, matrix_to_global):
                """Apply an incremental change to our global direction, expressed in local coordinates.  For example, this makes it easy to 
                        roll an optic around its local z axis or turn it off center around its local y axis, even after it has already been set in its global frame
                """
                self.update_coordinates(self.center, self.center, self.globalize_transform(matrix_to_global))

        def update_coordinates(self, parent_center=None, reference_coordinate=None, matrix_to_global=None):
                """do a complete transform of our angular coordinates and positions to a new frame.  
                Our rotation is adjusted from its current value by matrix_to_global.
                Our center is moved to parent_center+rotated value of (self.center-reference_coordinate).  
                This is used when we are embedded in a composite optic, and the whole composite optic is moved or rotated.
                """
                if parent_center is None:
                        parent_center=self.center
                if reference_coordinate is None:
                        reference_coordinate=self.center
                if matrix_to_global is not None:                                
                        self.matrix_to_global=Numeric.dot(matrix_to_global, self.matrix_to_global)
                        self.matrix_to_local=Numeric.transpose(self.matrix_to_global)
                self.center=parent_center+Numeric.dot(matrix_to_global, self.center-reference_coordinate)
                self.cosines=self.transform_into_global(Numeric.array((0,0,1)))
                self.euler=None
                return self
                
        def polygon(self):
                "return a polygonal boundary for the object.  By default it is just the bounding box"
                try:
                        
                        face_centered=hasattr(self,"face_centered")
                                
                        if hasattr(self,"justify"):
                                justify=self.justify
                        else:
                                justify="center"
                                                
                        if justify=="left":
                                left=0
                                right=-self.width
                        elif justify=="right":
                                left=self.width
                                right=0
                        else:
                                try:
                                        # a fraction of 1 top justifies, 0 center justifies, and -1 bottom justifies
                                        fraction=(float(justify)+1)*0.5
                                        left=self.width*(1-fraction)
                                        right=-self.width*fraction
                                except:
                                        left=self.width/2.0
                                        right=-left
                        
                        if hasattr(self,"height"):
                                height=self.height
                        else:
                                height=self.width       
                                                        
                        top=height/2.0
                        bottom=-height/2.0
                        
                        if(face_centered):
                                front=0
                                back=self.thickness
                        else:
                                front=-self.thickness/2.0
                                back=-front
                                                        
                        baserect=Numeric.array((
                                        (left, right, right, left, left, left, right, right, left, left, right, right), 
                                        (top, top, bottom, bottom, top, top, top, bottom, bottom, top, bottom, bottom),
                                        (front, front, front, front, front, back, back, back, back, back, back, front)))
                        return Numeric.transpose(Numeric.dot(self.matrix_to_global, baserect))+self.center
                        
                except:
                        return None
        
        def polygon_list(self):
                "return a list of polygons which might be used to draw this object.  In this case, it is a single item."
                return [self.polygon()] #for simple optics, the list has one item
        
        def place_between(self, from_obj, to_obj, distance):
                "place_between(from, to, distance, set_info) puts the optic between object or coordinate 'from' and 'to' and rotates it to the specified axis."
                if isinstance(from_obj, general_optic):
                        fc=from_obj.exit_center()
                        fn=from_obj.name
                else:
                        fc=Numeric.array(from_obj) #assume is is a tuple or array
                        fn=Numeric.array_str(fc, precision=3, suppress_small=1)
                if isinstance(to_obj, general_optic):
                        tc=to_obj.entrance_center()
                        tn=to_obj.name
                else:
                        tc=Numeric.array(to_obj) #assume is is a tuple or array
                        tn=Numeric.array_str(tc, precision=3, suppress_small=1)
                
                dx1=tc-fc
                dx1hat=dx1/vec_mag(dx1)
                if distance > 0.0:
                        self.center=fc+distance*dx1hat
                else:
                        self.center=tc+distance*dx1hat
                        
                x,y,z=tuple(dx1.flat)
                rho=math.sqrt(x*x+y*y)
                theta=math.atan2(rho,z)/deg
                eta=math.atan2(y,x)/deg
                self.reset_angle((theta, eta, 0))               
                return self #make daisy-chaining easy!

        def set_direction(self, from_obj, to_obj):
                "set_direction(from, to, set_info) points a mirror from object or coordinate 'from' to 'to'"
                if isinstance(from_obj, general_optic):
                        fc=from_obj.exit_center()
                        fn=from_obj.name
                else:
                        fc=Numeric.array(from_obj) #assume is is a tuple or array
                        fn=Numeric.array_str(fc, precision=3, suppress_small=1)
                if isinstance(to_obj, general_optic):
                        tc=to_obj.entrance_center()
                        tn=to_obj.name
                else:
                        tc=Numeric.array(to_obj) #assume is is a tuple or array
                        tn=Numeric.array_str(tc, precision=3, suppress_small=1)
                
                self.looking_from_name=fn
                self.looking_to_name=tn
                self.looking_from_obj=from_obj
                self.looking_to_obj=to_obj
                
                dx1=fc-self.center
                dx2=tc-self.center
                dx1hat=dx1/vec_mag(dx1)
                dx2hat=dx2/vec_mag(dx2)
                halfway=(dx1hat+dx2hat)/vec_mag(dx1hat+dx2hat)
                x,y,z=tuple(halfway.flat)
                rho=math.sqrt(x*x+y*y)
                theta=math.atan2(rho,z)/deg
                eta=math.atan2(y,x)/deg
                self.reset_angle((180+theta, eta, 0))   
                self.perp=Numeric.array((dx1hat[1]*dx2hat[2]-dx1hat[2]*dx2hat[1],
                                dx1hat[2]*dx2hat[0]-dx1hat[0]*dx2hat[2],
                                dx1hat[0]*dx2hat[1]-dx1hat[1]*dx2hat[0]))  #cross product perpendicular to plane of incidence, for reference
                return self #make daisy-chaining easy

        def rotate_axis(self, axis_theta):
                self.rotate_in_local_frame(matrix_to_global=eulermat(0.0, 0.0, axis_theta))
                return self

        def tilt_off_axis(self, angle):
                if type(angle) is not types.TupleType:
                        theta=angle
                        eta=0.0
                else:
                        theta=angle[0]
                        eta=angle[1]
                self.rotate_in_local_frame(matrix_to_global=eulermat(theta, eta, 0.0))
                return self
                
        def clone(self, newname=None):
                a=copy.copy(self)
                if newname is not None:
                        a.name=newname
                return a
                
        def format_name(self):
                if self.name is None:
                        return ""
                else:
                        return self.name + ": "
        
class base_reflector:
        "reflector is a class for mirror-like objects... the default is a mirror"
        def local_transform(self):
                "a mirror just reverse the z-component of the motion of the beam"
                self.beam.transform(self.globalize_transform(Numeric.array(((1.0,0,0),(0,1.0,0),(0,0,-1.0)))))
        
        def post_init(self):
                self.reflector_info=self.format_geometry()

class base_lens:
        """a base_lens handles simple thin lenses with either a scalar or vector (diagonal) focal length or strength specified.  To put it off axis,
                        apply a rotation after the object has been initialized.
        """
        def post_init(self):
                f=self.f
                if type(f)==types.TupleType:
                        f1, f2 = f
                        if f1 is not None:
                                d1=-1.0/f1
                        else:
                                d1=0.0
                        if f2 is not None:
                                d2=-1.0/f2
                        else:
                                d2=0.0
                else:
                        if f is not Infinity:
                                d1=d2=-1.0/f
                        else:
                                d1=d2=0.0
                
                self.d1=d1
                self.d2=d2
                self.strength=Numeric.array(((d1,0),(0,d2)))
                self.info_str()
                
        def mat2(self):
                "get an abcd matrix, if we look like a spherical lens"
                if self.d1==self.d2:
                        return Numeric.array(((1.0,0.),(self.d1,1)))
                else:
                        raise "Attempt to get 2x2 matrix of non-spherical lens" 

        def mat4(self):
                "get a full abcd tensor for this lens, as needed to transform q"
                mxx, mxy, myx, myy=[Numeric.array(((1.,0.),(d,1.))) for d in self.strength.flat]
                return Numeric.array(((mxx,mxy),(myx,myy)))
        
        def rotate_axis(self, axis_theta):
                "rrotate our axis, and update our info string"
                general_optic.rotate_axis(self, axis_theta)
                self.info_str()
                return self
                
        def q_transform(self):
                "apply our q-transform to a localized beam"
                self.beam.q.focus(self.strength) #it's easy!
        
        def abcd_transform(self, vec):
                "apply our abcd matrix to a vector.  Used for propagating the center of a beam"
                x, xp, y, yp = tuple(vec)
                
                dxx,dxy,dyx,dyy=tuple(self.localize_tensor(self.strength).flat)
                return x, xp+dxx*x+dxy*y, y, yp+dyy*y+dyx*x
        
        def info_str(self): #short format string
                if self.d1==self.d2:
                        if self.d1 != 0:
                                self.base_lens_info=("f=%.1f"%(-1.0/self.d1))
                        else:
                                self.base_lens_info=("f= Infinity")

                else:
                        if self.d1==0:
                                f1=""
                        else:
                                f1="f1=%.1f " % (-1.0/self.d1)
                        if self.d2==0:
                                f2=""
                        else:
                                f2="f2=%.1f " % (-1.0/self.d2)
                        self.base_lens_info=f1+f2+("axis theta=%.1f"%(self.axis_theta))

        def __str__(self):
                return self.format_name()+self.base_lens_info

class reflector(general_optic, base_reflector):
        "reflector is a class for mirror-like objects... the default is a mirror.  Like a base_reflector, but with size and drawing info set up"
                
        def post_init(self):
                if not hasattr(self,"face_centered"):
                        self.face_centered=1
                if not hasattr(self,"width"):
                        self.width=0.0254
                if not hasattr(self,"height"):
                        self.height=self.width
                if not hasattr(self,"thickness"):
                        self.thickness=0.01
                base_reflector.post_init(self)
                
        def __str__(self):
                return self.format_name()+self.reflector_info
                
        def local_transform(self):
                base_reflector.local_transform(self)
        
        def q_transform(self):
                pass
                
        def set_direction(self, from_obj, to_obj, set_info=1):
                "set_direction(from, to, set_info) points the mirror from object or coordinate 'from' to 'to' and updates the info string"
                general_optic.set_direction(self, from_obj, to_obj)
                
                if set_info:
                        self.reflector_info=("looking from %s to %s " % 
                                        (self.looking_from_name, self.looking_to_name))+str(self.euler)
                return self #make daisy-chaining easy
                
class null_optic(general_optic):
        "null_optic is drawable, but has no effect on the beam except the beam will be transported to it... useful for markers in an optical system"
        def post_init(self):
                if not hasattr(self,"width"):
                        self.width=0.0254
                if not hasattr(self,"thickness"):
                        self.thickness=0.01
                        
        def abcd_transform(self, vec):
                return vec

        def q_transform(self):
                pass

class marker_optic(null_optic):
        "marker_optic is drawable, but has no effect on the beam at all... useful for markers in an optical system"
        def transport_to_here(self, beam):
                "transport beam from wherever it is to our center"
                return self

class lens(general_optic, base_lens):
        "lens is like a base_lens, but has geometry information"
        def post_init(self):
                base_lens.post_init(self)
                #default lens draws as 1" diameter x 5 mm thick
                if not hasattr(self,'thickness'): self.thickness=0.005
                if not hasattr(self,'width'): self.width=0.0254
                if not hasattr(self,'height'): self.height=self.width

        def __str__(self):
                return base_lens.__str__(self)+" "+self.format_geometry()       

class dielectric_interface(general_optic, base_lens):
        """ warning... as of 9/24/2002, this is not even close to done. Do not use"""
        
        def post_init(self):
                #raise "Warning!", "dielectric_interface is not ready to use! Do not try this."
                self.last_lambda=0.0 
                if not hasattr(self, "external_index"):
                        self.external_index=get_ambient_index
                
        def local_transform(self):
                
                dot=Numeric.dot
                
                self.update_strength()
                
                kx, ky, kz=self.beam.local_direction
                
                #must rotate by the appropriate refraction angle _in the plane of incidence_ 
                sin_theta_in=math.sqrt(kx*kx+ky*ky) #incoming k had better be a unit vector!
                if abs(sin_theta_in) < 1e-6: return
                cphi, sphi = kx / sin_theta_in, ky/sin_theta_in
                
                n1=self.ambient_index
                n2=self.medium_index
                                
                if kz < 0.0:
                        n1, n2 = n2, n1 #we're going backwards through the interface
                        sin_theta_in=-sin_theta_in
                
                self.final_index=n2
                
                sin_theta_out= n1/n2*sin_theta_in
                dtheta=math.asin(sin_theta_out)-math.asin(sin_theta_in)
                c,s = math.cos(dtheta), math.sin(dtheta)
                phimat= Numeric.array(((cphi,-sphi, 0),( sphi, cphi, 0),(0,0,1.)))
                phimati=Numeric.array(((cphi, sphi, 0),(-sphi, cphi, 0),(0,0,1.)))
                
                #this matrix is a rotation by by phi to put the incident beam on x, rotate about x-z by dtheta, then undo the phi
                self.beam.transform(self.globalize_transform(dot(phimat,dot(Numeric.array(((c,0,s),(0,1,0),(-s,0,c))), phimati))))
                self.q_transform()
                

        def update_strength(self):
                oldlambda=self.beam.get_lambda()
                if oldlambda==self.last_lambda: return
                
                if type(self.external_index) is types.FunctionType:
                        self.ambient_index=self.external_index(oldlambda)
                else:
                        self.ambient_index=self.external_index
                n1=self.ambient_index
                
                if type(self.index) is types.FunctionType:
                        self.medium_index=self.index(oldlambda)
                else:
                        self.medium_index=self.index
                        
                n2=self.medium_index
                
                if hasattr(self, "radius"):
                        raise "Warning...", "Curved dielectric interfaces don't work yet! try again later"
                        if type(self.radius) is not types.TupleType:
                                rx=ry=self.radius
                        else:
                                rx,ry=self.radius
                        if rx is not Infinity:
                                cx=(n1-n2)/(rx*n2)
                        else:
                                cx=0.0
                        if ry is not Infinity:
                                cy=(n1-n2)/(ry*n2)
                        else:
                                cy=0.0
                        self.d_scalar=n1/n2     #always diagonal, for scalar media, so we don't have to localize        
                        self.strength=Numeric.array(((cx,0),(0,cy)))
                else:
                        self.strength=Numeric.array(((0.,0.),(0.,0.)))
                        
                self.last_lambda=oldlambda
                
        def q_transform(self):
                self.beam.set_medium_index(self.final_index)
                kx, ky, kz=self.beam.local_direction
                if kz > 0.0:
                        self.beam.q.focus(self.strength)
                else: #going the wrong way!
                        self.beam.q.focus(self.strength*(-self.medium_index/self.ambient_index))
                        

class paraxial_spherical_mirror(reflector, base_lens):
        """spherical_mirror is a reflector which focuses.  
        This is a paraxial approximation, and only makes sense for flairly 'flat' mirrors, for which the intersection can be computed by planar geometry.
        Since base_lens (q.v.) also handles optics with different x&y strengths, this can represent cylinders and ellipses, too.
        """
        def post_init(self):
                base_reflector.post_init(self)
                base_lens.post_init(self)
                #default lens draws as 1" diameter x 5 mm thick
                if not hasattr(self,'thickness'): self.thickness=0.005
                if not hasattr(self,'width'): self.width=0.0254
                if not hasattr(self,'height'): self.height=0.0254
                
        def local_transform(self):
                general_optic.local_transform(self) #pick up our abcd transform for the lens
                base_reflector.local_transform(self) #and do the reflection

        def q_transform(self):
                "apply our q-transform to a localized beam, making sure this is found at the right level by general_optic"
                self.beam.q.focus(self.strength) #it's easy!
        
        def __str__(self):
                return self.format_name()+self.reflector_info+" "+self.base_lens_info+" "+self.format_geometry()

class spherical_mirror(reflector, base_lens):
        """spherical_mirror is a reflector which focuses.  This solves the exact intersection of a beam with the spherical surface, and is right even
                for tilted mirrors and strong curvature.  For these mirrors, the width and height are assumed to be the same, and are important
                since the decision about where the beam hits the mirror depends on these.  This logic is not fully implemented yet...
                This is also a useful base class for other highly curved surfaces, since transform() handles dynamic geometry.
        """
        def post_init(self):
                base_lens.post_init(self)
                #default lens draws as 1" diameter x 5 mm thick
                if not hasattr(self,'thickness'): self.thickness=0.005
                if not hasattr(self,'width'): self.width=0.0254
                if not hasattr(self,'height'): self.height=0.0254
                
        def __str__(self):
                return self.format_name()+self.reflector_info+" "+self.base_lens_info+" "+self.format_geometry()

        def intersect(self, from_point, from_direction):
                """find the intersection of a beam coming from from_point, going in from_direction, with our center. Raise an exception if beam won't hit center going that way."""
                
                # t=-(a,b,c).(x1,y1,z1) +- sqrt( ( (a,b,c).(x1,y1,z1) )^2 - (x1,y1,z1)^2 + r^2 ) from Mathematica for line (a,b,c)*t+(x1,y1,z1) and sphere of radius r at origin
                #the center of curvature of the mirror is derived from the apex position (our location) and the rotation matrix
                                
                radius=self.f*2.0 #radius of curvature
                
                centerpos=self.center-self.matrix_to_global[:,2]*radius #position of center of sphere           
                from0=from_point-centerpos
                abcxyz=Numeric.dot(from0, from_direction)
                disc=abcxyz*abcxyz - Numeric.dot(from0, from0) + radius*radius
                if disc < 0:
                        raise OpticDirectionError, ("beam misses sphere: "+str(self)+" incoming (x,y,z)="+
                                Numeric.array_str(from_point, precision=3, suppress_small=1)+" cosines="+
                                Numeric.array_str(from_direction, precision=3, suppress_small=1) )
                                        
                tvals =[ t for t in (-abcxyz - math.sqrt(disc), -abcxyz + math.sqrt(disc)) if t > 1e-9] #select only forward solutions

                if not tvals:
                        raise OpticDirectionError, ( "Optic found on backwards side of beam: "+str(self)+" incoming (x,y,z)="+
                        Numeric.array_str(from_point, precision=3, suppress_small=1)+" cosines="+
                        Numeric.array_str(from_direction, precision=3, suppress_small=1)  )
                        
                solns = [ (t, from_point+from_direction*t) for t in tvals]
                
                solns=[ (t,xx) for t,xx in solns if Numeric.dot(xx-centerpos, from_direction)*radius > 0] #pick solution with surface pointing the right way
                #there will always only be one of the solutions which passes this test, at most

                if not solns:
                        raise OpticDirectionError, ( "Only interaction with spherical mirror is on wrong side: "+str(self)+" incoming (x,y,z)="+
                        Numeric.array_str(from_point, precision=3, suppress_small=1)+" cosines="+
                        Numeric.array_str(from_direction, precision=3, suppress_small=1)  )
        
                soln=solns[0]
                self.intersection_zhat=(soln[1]-centerpos)/radius  #unit surface normal in general direction of beam, useful later
                return soln #this is the only possible solution

        def transform(self, beam, backwards=0):
                "transform(beam, backwards) set up local coordinates, calls local_transform on the beam, and resets it to global coordinates.  Returns self for chaining."
                self.beam=beam
                self.backwards=backwards #in case anyone needs to know (e.g. dielectric interfaces)
                ml=self.matrix_to_local
                mg=self.matrix_to_global
                self.matrix_to_local=self.get_dynamic_matrix_to_local(beam.matrix_to_global) #do optics with exact local matrix
                self.matrix_to_global=Numeric.transpose(self.matrix_to_local) #do optics with exact local matrix
                beam.localize(self)
                self.check_hit_optic()
                self.local_transform()
                beam.globalize(self)
                self.matrix_to_local=ml
                self.matrix_to_global=mg
                del self.beam, self.backwards #get it out of our dictionary so it is an error if not localized
                return self

        def get_dynamic_matrix_to_local(self, matrix_to_global):
                """return the transformation to the exact coordinates for the intersection point last found by intersect() and optimizing based on beam's matrix.
                In this case, the beam matrix is not used, since our x,y are sensible choices since in the future, they are likely to be principal axes of an ellipsoid"""
                zhat=self.intersection_zhat
                xhat=cross(self.matrix_to_global[:,1], zhat) #use our real yhat x our zhat to generate xhat
                xmag=math.sqrt(Numeric.dot(xhat, xhat))
                if xmag < 0.707: #bad guess for basis... mirror normal is very close to our yhat, use our xhat instead (they can't BOTH be bad!)
                        yhat=cross( zhat, self.matrix_to_global[:,0]) #use our zhat x our real xhat to generate yhat (swapped to keep handedness)
                        ymag=math.sqrt(Numeric.dot(yhat, yhat))
                        yhat/=ymag
                        xhat=cross(yhat, zhat) #xhat is automatically a unit vector
                else:
                        xhat /= xmag
                        yhat=cross(zhat, xhat) #yhat is automatically a unit vector
                
                return Numeric.array((xhat,yhat,zhat))

        def local_transform(self):
                self.beam.transform(self.globalize_transform(Numeric.array(((1.0,0,0),(0,1.0,0),(0,0,-1.0))))) #reflect along local z axis
                self.beam.q.focus(self.strength) #it's easy!


if 0:
        print "\n\n****start mirror tests"
        mir1=reflector("reflector1", center=(0,0,1))
        mir2=reflector("reflector2", center=(0,1,1))
        mir1.set_direction((0,0,0), mir2)
        mir2.set_direction(mir1, (1,1,1))
        mybeam=beam((0,0,0), qtens(1.054e-6, r=Infinity, w=.002))
        mybeam.q.qit[0,0]*=0.25 
        for optic in (mir1, mir2):
                print optic.name
                optic.transport_to_here(mybeam)
                print mybeam
                optic.transform(mybeam)
                print mybeam

if 0:
        print "\n\n****start lens tests"
        optic=lens("reflector", center=(0,0,1), f=0.25)
        mybeam=beam((0,0,0), qtens(1.054e-6, r=Infinity, w=.002)) 
        print mybeam
        optic.transport_to_here(mybeam)
        print mybeam
        optic.transform(mybeam)
        print mybeam


class grating(reflector):
        "grating is a reflector which diffracts. The ruling is along the y axis.  It should be initialized with keywords order and pitch."
        
        def local_transform(self):
                dot=Numeric.dot
                tr=Numeric.transpose
                deg=math.pi/180.0
                
                #need to find basis set for rotation which is perp. to beam and grating rulings (yhat)
                kx, ky, kz = v2 = self.beam.local_direction
                v3 = cross((1,0,0), v2) #this is rotation axis (!) in grating frame 
                v3 /= vec_mag(v3)
                v1 = cross(v2, v3) #this is first basis vector for rotation 
                v1 /= vec_mag(v1)
                coord=Numeric.array((v1,v2,v3)) #matrix to convert coordinates in grating system into diffraction rotation system
                cinv=tr(coord) #matrix to convert diffraction basis vectors to grating basis i.e. cinv.(0,0,1) is rotation axis in grating system
                
                #print "**grating**"
                #print Numeric.array_str(coord, precision=4)
                
                theta=math.atan2(kx, math.sqrt(ky*ky+kz*kz))
                littrow, out=self.angles(theta, self.beam.get_lambda())
                #print littrow/deg, theta/deg, out/deg, (out+theta)/deg
                
                #remember, outgoing angle is _not_ outgoing direction... beam has changed from incoming to outgoing, too
                dtheta=out+theta
                s,c=-math.sin(dtheta), math.cos(dtheta)
                
                #this funny matrix is a rotation by dtheta, followed by a reflection in z
                rot1=dot(Numeric.array(((1,0,0),(0,1,0),(0,0,-1))), dot(cinv, dot(Numeric.array(((c,s,0),(-s,c,0),(0,0,1))), coord )))
                #print Numeric.array_str(rot1, precision=4)
                self.beam.transform(self.globalize_transform(rot1))

        def degree_angles(self, theta, lam):
                #return angle info for incoming and outgoing angles in degrees (for user convenience)
                litt, beta = self.angles(theta*deg, lam)
                return litt/deg, beta/deg
                
        def angles(self, theta, lam):
                #return angle info for incoming and outgoing angles in degrees (for user convenience)
                if theta<0:
                        sgn=-1
                else:
                        sgn=1
                gratparm=self.order*lam*self.pitch*sgn
                littrow=asin(gratparm/2.0)
                phi=(((theta + math.pi/2.0) % math.pi ) - math.pi/2.0) #always wrap to front of grating!
                beta0=asin(gratparm-sin(phi))
                self.parafocus_scale=math.cos(phi)/math.cos(beta0) #angular magnification along x
                #print "grating angles: ", lam, theta/deg, littrow/deg, beta0/deg
                return (littrow, beta0)
                
        def __str__(self):
                return reflector.__str__(self)+("pitch= %.3f" % self.pitch)

class key_tag:
        def __init__(self, key):
                self.key=key

class backwards(key_tag):
        pass

def get_tagged_key(object):
        if isinstance(object, key_tag):
                return object.key
        else:
                return object

class composite_optic(general_optic):
        "composite_optic is a container for a list of general_optics which can be rotated, etc. as a group"
        
        def __init__(self, name, optics_dict, optics_order, reference_coordinate=None,
                        center=(0,0,0), angle=0.0, **extras):
                        """create a composite_optics.  It is composed of a dictionary 'optics_dict' of named objects, and a list 'optics_order' of dictionary keys
                        which defines the order in which elements of this optic should be traversed.  A single element may appear multiple times in the list.
                        The reference_coordinate is the coordinate around which this optic will rotate, it is the reference_coordinate that is placed at the position 'center'.
                        If no reference_coordinate is specified, it is ssumed to be the entrance_center of the first optic in the optics_order list.
                        """
                        self.init( name, optics_dict, optics_order, reference_coordinate, center, angle, extras)
                
        def init(self, name, optics_dict, optics_order, reference_coordinate, center, angle, extras):
                
                if reference_coordinate is None: #refer all coordinates to first optic in list by default
                        reference_coordinate=optics_dict[optics_order[0]].entrance_center()
                        
                self.optics_dict={}
                self.optics_order=list(optics_order)

                for k in optics_order: #only pull out keys which are used, and let python eliminate duplicates
                        self.optics_dict[get_tagged_key(k)]=optics_dict[get_tagged_key(k)]
                                                
                general_optic.init(self, name, center=center, angle=angle, extras=extras)
                for k in self.optics_dict.keys():
                        self.optics_dict[k].update_coordinates(center, reference_coordinate, self.matrix_to_global)
        
        def exit_center(self):
                "return the position of the exit center of this optic"
                return self.optics_dict[self.exit_optics_tags()[1]].center
        
        def entrance_center(self):
                "return the position of the entrance center of this optic"
                return self.optics_dict[self.entrance_optics_tags()[0]].center
                                
        def update_coordinates(self, new_center, parent_reference, matrix_to_global):
                "move us to a new positin and/or angle.  See general_optic.update_coordinates"
                for k in self.optics_dict.keys():
                        self.optics_dict[k].update_coordinates(new_center, parent_reference, matrix_to_global)
                general_optic.update_coordinates(self, new_center, parent_reference, matrix_to_global) #update our top-level matrices, etc.
                
        def mark_label(self, opticname):
                "provide a default label for automatic marking of the beam as it passes though this optic"
                return (self,opticname)
                                
        def transform(self, beam, back=0):
                "track a beam through this optics, forwards or backwards, and mark the beam whenever it strikes an atomic optic"
                if back:
                        order=copy.copy(self.optics_order)
                        order.reverse()
                else:
                        order=self.optics_order
                
                for opticname in order:
                        optic=self.optics_dict[get_tagged_key(opticname)]
                        if not isinstance(optic, composite_optic): #only mark primitive optics
                                waist=beam.q.next_waist()
                                current_drift=beam.total_drift
                                optic.transport_to_here(beam)
                                distance=beam.total_drift-current_drift
                                if waist > 0 and waist < distance:
                                        beam.free_drift(waist-distance)
                                        beam.mark("waist")
                                        optic.transport_to_here(beam)
                        if isinstance(opticname, backwards):
                                optic.transform(beam, not back) #'backwards' must toggle the reversed flag, so backwards-backwards is forwards
                        else:
                                optic.transform(beam, back)
                                
                        if not isinstance(optic, composite_optic): #only mark primitive optics
                                beam.mark(self.mark_label(get_tagged_key(opticname)))
                        
        def polygon_list(self):
                "return a list of polygons which will draw this optic"
                l=[]
                for o in self.optics_dict.keys():
                        #use additions semantics to flatten nesting of lists
                        l=l+self.optics_dict[o].polygon_list()
                return [poly for poly in l if poly is not None] 
        
        def exit_optics_tags(self):
                "return the last two elements of this optic, to allow one to get an exit axis direction"
                return self.optics_order[-2], self.optics_order[-1]
        
        def entrance_optics_tags(self):
                "return the first two elements of this optic, to allow one to get an entrance axis direction"
                return self.optics_order[0], self.optics_order[1]

        def set_exit_direction(self, look_to):
                "make the last optic of this look from the second-to-last optic to a final look_to point.  Useful if the last optic is a mirror"
                l=self.optics_dict
                e1, e2 = self.exit_optics_tags()
                l[e2].set_direction(l[e1], look_to)

        def set_entrance_direction(self, look_from):
                "make the first optic of this look from a look_from point to the second optic.  Useful if the first optic is a mirror"
                l=self.optics_dict
                e1, e2 = self.entrance_optics_tags()
                l[e1].set_direction(look_from, l[e2])

        def rotate_to_axis(self, from_obj):
                "rotate this object by an angle that makes it look at from_obj, assuming it started out looking along the z axis"
                if isinstance(from_obj, general_optic):
                        fc=from_obj.exit_center()
                        fn=from_obj.name
                else:
                        fc=Numeric.array(from_obj) #assume is is a tuple or array
                        fn=Numeric.array_str(fc, precision=3, suppress_small=1)
                
                dx1=self.center-fc
                x,y,z=tuple(dx1)
                rho=math.sqrt(x*x+y*y)
                theta=math.atan2(rho,z)/deg
                eta=math.atan2(y,x)/deg
                if abs(eta)>90: #prefer signed theta and unsigned eta
                        eta=180-eta
                        theta=-theta
                self.update_coordinates(self.center, self.center, euler(theta, eta, 0).mat)     
                return self #make daisy-chaining easy

        def __getitem__(self, tag):
                "get an optic from our list by its identifier.  If a mark is passed in of the form (self, item), use the item"
                if type(tag) is types.TupleType and tag[0] is self:
                        return self.optics_dict[tag[1]] #in case the tag had our object identifier attached
                else:
                        return self.optics_dict[tag]

        def __len__(self):
                return len(self.optics_order)
                
if 0:
        print "testing grating"
        optic=grating("grating", pitch=1.5e6, angle=38.0, order=1)
        mybeam=beam((0,0,0), qtens(1.054e-6, r=Infinity, w=.002)) 
        print mybeam
        optic.transport_to_here(mybeam)
        print mybeam
        optic.transform(mybeam)
        print mybeam
        print math.atan2(mybeam.direction()[0], mybeam.direction()[2])/(math.pi/180.0)
        
class optics_trace:
        def __init__(self, marks, color=None, **extras):
                self.color=color
                self.marks=marks
                #copy any extra information directly into the class dictionary
                for i in extras.keys():
                        setattr(self, i, extras[i])
        
        def __getitem__(self, index):
                if type(index) is types.IntType:
                        tag, n = self.marks["order"][index]
                        return self.marks[tag][n]
                else:
                        return self.marks[index[0]][index[1]]

        def __len__(self):
                return len(self.marks["order"])
        
def trace_path(optics_system, beam):
        """tracks a beam through a composite_optic, and returns an optics_trace wrapper around the marks which were created.
                If an error is encountered which throws an exception, the exception is printed, and the partial trace returned.
                This makes it very easy to find a problem optic (e.g. a grating which is diffracting a beam away from the next item,
                or a mirror which isn't steered right).
        """
        beam.total_drift=0.0            
        try:
                optics_system.transform(beam)   
        except:
                traceback.print_exc()
                pass #just return an incomplete trace if something goes wrong!
        return optics_trace(beam.marks)

class phase_plate(null_optic):
        def post_init(self):
                theta=self.phase_angle*math.pi/180.0
                self.x_phase_shift=complex(math.cos(theta), math.sin(theta))
        
        def local_transform(self):
                self.beam.local_polarization[1]*=self.x_phase_shift
        
        def info_str(self):
                return "Phase plate: x shift = %.1f" % self.phase_angle
                
class halfwave_plate(phase_plate):
        def post_init(self):
                self.phase_angle=180.0
                phase_plate.post_init(self)

class quarterwave_plate(phase_plate):
        def post_init(self):
                self.phase_angle=90
                phase_plate.post_init(self)
        
class faraday_rotator(null_optic):
        def post_init(self):
                pass

        def info_str(self):
                return "Faraday Rotator: rotation = %.1f" % self.rotation

        def local_transform(self):
                theta=self.rotation*self.beam.local_direction[2]
                s,c=sincosdeg(theta)
                #if beam is going forward, shift (+), if backwards, shift (-)
                #where forward/backwards comes from the local z-component of the beam direction
                self.beam.local_polarization=Numeric.dot(Numeric.array(((c,-s),(s,c))), self.beam.local_polarization)

class dielectric_trapezoid(composite_optic):
        ENTRANCE='entrance'
        CENTER='center'
        EXIT='exit'
        def __init__(self, name, entrance_face_angle=0.0, exit_face_angle=0.0, thickness=0.05, width=0.025, index=None, center=(0.,0.,0.), angle=0.0, **extras):
                
                if index is None:
                        raise "No index of refraction (scalar or function) given as index=foo creating dielectric trapezoid"
                
                my=dielectric_trapezoid
                self.thickness=thickness
                self.width=width
                
                self.front_face_offset=math.tan(entrance_face_angle*deg)*width*0.5
                self.back_face_offset=math.tan(exit_face_angle*deg)*width*0.5
                
                optics={}
                optics[my.ENTRANCE]=dielectric_interface("entrance face", angle=entrance_face_angle, index=index,
                                center=(0,0,-0.5*thickness))
                optics[my.CENTER]=null_optic("trapezoid center", center=(0,0,0), width=width*0.05, thickness=width*0.05)
                optics[my.EXIT]=dielectric_interface("exit face", angle=exit_face_angle+180.0, index=index,
                                center=(0,0,0.5*thickness) )
                order=[my.ENTRANCE, my.CENTER, my.EXIT]
                
                #specify reference as (0,0,0) to make our coordinates referenced to (0,0,0)
                composite_optic.init(self, name, optics, order, (0,0,0), center, angle, extras=extras )
                
        def polygon(self):
                if hasattr(self,"height"):
                        height=self.height
                else:
                        height=self.width       
                                                
                top=height/2.0
                bottom=-height/2.0
                
                front=-self.thickness/2.0
                back=-front
                
                fo=self.front_face_offset
                bo=self.back_face_offset
                
                left=0.5*self.width
                right=-left
                
                baserect=Numeric.array((
                                (left, right, right, left, left, left, right, right, left, left, right, right), 
                                (top, top, bottom, bottom, top, top, top, bottom, bottom, top, bottom, bottom),
                                (front-fo, front+fo, front+fo, front-fo, front-fo, back-bo, back+bo, back+bo, back-bo, back-bo, back+bo, front+fo)))
                return Numeric.transpose(Numeric.dot(self.matrix_to_global, baserect))+self.center

        def polygon_list(self):
                my=dielectric_trapezoid
                return [self.polygon(), self.optics_dict[my.CENTER].polygon()] 


if 0:
        print "\n\n****start phase plate tests"
        optic=halfwave_plate("phase", center=(0,0,1)).rotate_axis(30)
        mybeam=beam((0,0,0), qtens(1.054e-6, r=Infinity, w=.002)) 
        print mybeam
        optic.transport_to_here(mybeam)
        print mybeam, mybeam.polarization
        optic.transform(mybeam)
        print mybeam, mybeam.polarization
