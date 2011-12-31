#!/usr/bin/env python

import sys
from PyQt4 import Qt
import PyQt4.Qwt5 as Qwt
from PyQt4.Qwt5.anynumpy import *


# from scipy.pilutil
def bytescale(data, cmin=None, cmax=None, high=255, low=0):
    if ((hasattr(data, 'dtype') and data.dtype.char == UInt8)
        or (hasattr(data, 'typecode') and data.typecode == UInt8)
        ):
        return data
    high = high - low
    if cmin is None:
        cmin = min(ravel(data))
    if cmax is None:
        cmax = max(ravel(data))
    scale = high * 1.0 / (cmax-cmin or 1)
    bytedata = ((data*1.0-cmin)*scale + 0.4999).astype(UInt8)
    return bytedata + asarray(low).astype(UInt8)

# bytescale()


def square(n, min, max):
    t = arange(min, max, float(max-min)/(n-1))
    #return outer(cos(t), sin(t))
    return cos(t)*sin(t)[:,NewAxis]

# square()
    

class ImagePlot(Qwt.QwtPlotItem):
    '''
    This class was taken (stolen?) from the pyQwt example files.
    It can plot 2D images
    '''

    def __init__(self, title = Qwt.QwtText()):
        Qwt.QwtPlotItem.__init__(self)
        if not isinstance(title, Qwt.QwtText):
            self.title = Qwt.QwtText(str(title))
        else:
            self.title = title
        self.setItemAttribute(Qwt.QwtPlotItem.Legend);
        self.xyzs = None

    # __init__()
    
    def setData(self, xyzs, xRange = None, yRange = None):
        self.xyzs = xyzs
        shape = xyzs.shape
        if not xRange:
            xRange = (0, shape[0])
        if not yRange:
            yRange = (0, shape[1])

        self.xMap = Qwt.QwtScaleMap(0, xyzs.shape[0], *xRange)
        self.plot().setAxisScale(Qwt.QwtPlot.xBottom, *xRange)
        self.yMap = Qwt.QwtScaleMap(0, xyzs.shape[1], *yRange)
        self.plot().setAxisScale(Qwt.QwtPlot.yLeft, *yRange)

        self.image = Qwt.toQImage(bytescale(self.xyzs)).mirrored(False, True)
        for i in range(0, 256):
            self.image.setColor(i, Qt.qRgb(i, i, i))

    # setData()    

    def updateLegend(self, legend):
        Qwt.QwtPlotItem.updateLegend(self, legend)
        legend.find(self).setText(self.title)

    # updateLegend()

    def draw(self, painter, xMap, yMap, rect):
        """Paint image zoomed to xMap, yMap

        Calculate (x1, y1, x2, y2) so that it contains at least 1 pixel,
        and copy the visible region to scale it to the canvas.
        """
        assert(isinstance(self.plot(), Qwt.QwtPlot))
        
        # calculate y1, y2
        # the scanline order (index y) is inverted with respect to the y-axis
        y1 = y2 = self.image.height()
        y1 *= (self.yMap.s2() - yMap.s2())
        y1 /= (self.yMap.s2() - self.yMap.s1())
        y1 = max(0, int(y1-0.5))
        y2 *= (self.yMap.s2() - yMap.s1())
        y2 /= (self.yMap.s2() - self.yMap.s1())
        y2 = min(self.image.height(), int(y2+0.5))
        # calculate x1, x2 -- the pixel order (index x) is normal
        x1 = x2 = self.image.width()
        x1 *= (xMap.s1() - self.xMap.s1())
        x1 /= (self.xMap.s2() - self.xMap.s1())
        x1 = max(0, int(x1-0.5))
        x2 *= (xMap.s2() - self.xMap.s1())
        x2 /= (self.xMap.s2() - self.xMap.s1())
        x2 = min(self.image.width(), int(x2+0.5))
        # copy
        image = self.image.copy(x1, y1, x2-x1, y2-y1)
        # zoom
        image = image.scaled(xMap.p2()-xMap.p1()+1, yMap.p1()-yMap.p2()+1)
        # draw
        painter.drawImage(xMap.p1(), yMap.p2(), image)

    # drawImage()

# class ImagePlot
