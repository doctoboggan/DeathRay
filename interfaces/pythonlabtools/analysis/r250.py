"""
r-250 random number generator... VERY fast, high quality random bit strings and floats
implemented by Marcus Mendenhall, Vanderbilt University Free Electron Laser Center, nashville, TN USA
Public Domain
December, 2002

The code which follows is a pythonization of code derived from the following two sources:
    
DESCRIPTION:
Shift-register Random Number Generator.

Copyleft (c) 1987, 1992. Eugene I Levin, A.F.Ioffe institute,
                         St. Petersburg, Russia.
                         E-mail: Levin@lh.ioffe.rssi.ru

This is a public domain program and may be freely distributed under the
condition of remaining the original Copyleft information.

The author would appreciate to be informed about any improvements of
these functions, or their implementations for any other computer system.

and:
/* r250.c   the r250 uniform random number algorithm

        Kirkpatrick, S., and E. Stoll, 1981; "A Very Fast
        Shift-Register Sequence Random Number Generator",
        Journal of Computational Physics, V.40

        also:

        see W.L. Maier, DDJ May 1991



*/

REALIZATION NOTES:
This is a realization of standard shift-register algorithm for random
bit streams:
   x[n] = x[n-q] XOR x[n-p]                                        (1)
where p and q satisfy the condition that the polynomial x^p + x^q + 1
must be primitive on the GF(2) field. There are a few known pairs (p,
q), p = 250 and q = 103 has been used.

In order to generate float numbers independent bit streams (1) are used
for the each bit of mantissa.

Consecutive values of (1) are stored in array "buffer" of the length p.
The index of the n-th member of (1) in buffer is
   i = n mod p                                                     (2)
so that a new value x[n] always replaces x[n-p]. Substitution of Eq. (2)
into Eq. (1) yields to the algorithm:
   x[i] = x[i] XOR x[i - p]      when i >= p,                      (3a)
   x[i] = x[i] XOR x[i - p + q]  when i < p.                       (3b)

The operations have been extended to include r521 and r250_521, per the recommendations of
Heuer, Dunweg and Ferrenberg,
"Considerations on Correlations in Shift-Register Pseudorandom Number Generators and Their Removal"
by Marcus Mendenhall
                                                                
"""
_rcsid="$Id: r250.py 323 2011-04-06 19:10:03Z marcus $"

import random

try:
  import numpy as Numeric
  numeric_int32=Numeric.int32
  numeric_float=Numeric.float
except:
  import Numeric
  numeric_int32=Numeric.Int32
  numeric_float=Numeric.Float

import math

class ran_shift(random.Random):
    "generate shift-register based high-quality randoms"    
    p,q = 250, 103
    def __init__(self, seed=None):
        self.floatscale=1.0/float(1L<<62)
        self.single_floatscale=1.0/float(1L<<31)
        self.seed(seed)
        self.mask32=Numeric.array(0x7ffffe00, numeric_int32)
        
    def seed(self, seed=None):
        "seed from the built in RNG python provides, and then scramble results a little"
        random.Random.seed(self, seed)
        seeds=[ 
            int( ((long(math.floor(random.random()*32768.0)) << 16) & 0x7fff0000) | long(math.floor(random.random()*65536.0))) for i in range(self.p)]
        self.ranbuf=Numeric.array(seeds, numeric_int32)
        
        for i in range(self.p): #scramble the dubious randoms from the default generator to start the system
            self.regenerate()
        
    def regenerate(self):
        "generate the next block of randoms, quickly"
        #the next two lines contain a slight subtlety:
        #the first line involves trivially non-overlapping operations (assuming q < p/2). 
        #the second line involves intentionally overlapped regions, so that the operation must be proceeding in 
        #place to make sure that the proper recursion is really happening. 
        self.ranbuf[:self.q]^=self.ranbuf[-self.q:]
        self.ranbuf[self.q:]^=self.ranbuf[:-self.q]
        self.counter=0

    def next(self):
        "return the next 31 bits from the random pool"
        v=self.ranbuf[self.counter]
        self.counter+=1
        if self.counter==self.p:
            self.regenerate()
        return v

    def getstate(self):
        return Numeric.array(self.ranbuf), self.counter #make sure we copy the array, not just return a reference
    
    def setstate(self, state):
        self.ranbuf=Numeric.array(state[0]) #make a copy here, too, so we can re-use the state as often as needed
        self.counter = state[1]
        
    def random(self):
        "return a _really good_ double precision (52 bits significant) random on [0,1) (upper included bound = (1 - 2^-52) )"
        q1, q2 = self.next(), self.next() #take 64 bits from the random pool
        return float( (long(q1) << 31) | ( long(q2) & 0x7ffffe00L) ) *self.floatscale

    def single_float_random(self):
        "return a good single-precision (32 bits significant) random on [0,1)  (upper included bound = (1 - 2^-32) )"
        q1 = self.next() #take 32 bits from the random pool
        return float(q1)*self.single_floatscale
            
    def fast_random_series(self, count):
        "return a series of 31-bit ints much more quickly than individual calls to next()."
        results=Numeric.zeros(count, numeric_int32)
        first=min(count, self.p-self.counter) #how many are already in the buffer that we want?
        results[:first]=self.ranbuf[self.counter:self.counter+first]
        #print self.ranbuf[self.counter], results.tolist()
        count-=first
        self.counter+=first
        if self.counter==self.p: #used up all in buffer, start generating more
            self.regenerate()
            for i in range(count//self.p):
                results[first:first+self.p]=self.ranbuf
                first+=self.p
                count-=self.p
                self.regenerate()
            if count:
                results[first:]=self.ranbuf[:count]
                self.counter=count
        return results

    def single_float_random_series(self, count):
        "return a series of good single-precision-quality (actually 31 bits embedded in double) randoms on [0,1).(upper included bound = (1 - 2^-31) )  \
                Note: conversion of this number to Float32 could result in rounding to exactly 1.0"

        #Warning! NumPy Unsigned-> Float is really signed!
        q1 = Numeric.array(self.fast_random_series(count), numeric_float) #take bits from the random pool. 
        q1*=self.single_floatscale
        return q1

    def double_float_random_series(self, count):
        "return a series of 52-bit significance double-precision randoms on [0,1)."
        q1 = self.fast_random_series(2*count) #take bits from the random pool
        q1[1::2] &= self.mask32#mask off low bits to prevent rounding when combined to 52-bit mantissas
        q1=q1*self.single_floatscale #convert results to doubles scaled on [0,1)        
        #now, for any generator with two-point correlations, or unknown bit lengths, this would fail horribly, but this class is safe.
        q1[1::2]*=self.single_floatscale #rescale LSBs 
        q1[0::2]+=q1[1::2] #and combine with MSBs
        return q1[::2]

class r250(ran_shift):
    "generate r250 based high-quality randoms"  
    p,q = 250, 103
            
class r521(ran_shift):
    "generate r521 based high-quality randoms"  
    p,q = 521, 168

class r250_521(r250):
    "generate super-quality r250/521 randoms per Heuer, Dunweg & Ferrenberg ca. 1995"
    def __init__(self, seed=None):
        r250.__init__(self, seed)
        self.r521=r521(seed) #give ourself a second generator
        
    def getstate(self):
        return r250.getstate(self), self.r521.getstate()
            
    def setstate(self, state):
        r250.setstate(self, state[0])
        self.r521.setstate(state[1])

    def next(self):
        return r250.next(self) ^ self.r521.next()
    
    def fast_random_series(self, count):
        return r250.fast_random_series(self, count) ^ self.r521.fast_random_series(count)
            
if __name__ == "__main__":
    r=r250_521()
    
    for i in range(20):
        print r.random(),
    print
    
    print 10*"%08lx "%tuple(r.fast_random_series(10).tolist())
    print

    state=r.getstate()
    
    print r.single_float_random_series(10)
    print
    
    print r.double_float_random_series(10)
    print

    r.setstate(state)
    print r.single_float_random_series(10)
    print

    r.setstate(state)
    print r.single_float_random_series(10)
    print

    import struct
    
    print "checking for uniformly filled bit in combined doubles"
    r.setstate(state)
    s=r.double_float_random_series(100).tostring()
    ss=struct.unpack("20L", s[:80])
    print (20*"%08lx ")%ss
    b1, b2 =0, 0
    for i,j in zip(ss[0::2], ss[1::2]):
        b1, b2 = b1 | i, b2 | j
    print "this should be 3fffffff ffffffff:", "%08lx %08lx" % (b1,b2)
    
    r.setstate(state)
    ranlistfast=r.fast_random_series(1000).tolist()
    r.setstate(state)
    ranlist=[r.next() for i in range(1000)]
    
    if ranlist != ranlistfast:
        print "fast series is not same as single randoms"
        print zip(ranlist, ranlistfast)
    else: print "fast series sequence is same as individual numbers"

    r.setstate(state)
    ranlistfast=r.single_float_random_series(1000).tolist()
    r.setstate(state)
    ranlist=[r.single_float_random() for i in range(1000)]
    
    if ranlist != ranlistfast:
        print "fast single series is not same as single randoms"
        print zip(ranlist, ranlistfast)
    else: print "fast single series sequence is same as individual numbers"

    r.setstate(state)
    ranlistfast=r.double_float_random_series(1000).tolist()
    r.setstate(state)
    ranlist=[r.random() for i in range(1000)]
    
    if ranlist != ranlistfast:
        print "fast double series is not same as single randoms"
        print zip(ranlist, ranlistfast)
    else: print "fast double series sequence is same as individual numbers"


    if 1:
        print "running pi-darts in 3d"
        cycles=100
        count=10000
        sum=0.0
        sum2=0.0
        for i in range(cycles):
            r1=r.single_float_random_series(3*count)
            r1*=r1
            insum=Numeric.sum(Numeric.less(r1[0::3]+r1[1::3]+r1[2::3], 1.0))
            pi=6.0*insum/count
            sum+=pi
            sum2+=pi*pi
            print pi, " ", 
        print
        print "pi estimate = %.6f +- %.6f" % (sum/cycles, math.sqrt(sum2/cycles-(sum/cycles)**2)/math.sqrt(cycles) )
        
