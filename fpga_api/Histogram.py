from PyQt4 import Qt
import PyQt4.Qwt5 as Qwt

class HistogramItem(Qwt.QwtPlotItem):
    '''
    This class was taken from the PyQwt5.2 example files. It is simply a class that can
    draw histograms.
    '''

    Auto = 0
    Xfy = 1
    
    def __init__(self, *args):
        Qwt.QwtPlotItem.__init__(self, *args)
        self.__attributes = HistogramItem.Auto
        self.__data = Qwt.QwtIntervalData()
        self.__color = Qt.QColor()
        self.__reference = 0.0
        self.setItemAttribute(Qwt.QwtPlotItem.AutoScale, True)
        self.setItemAttribute(Qwt.QwtPlotItem.Legend, True)
        self.setZ(20.0)

    # __init__()

    def setData(self, data):
        self.__data = data
        self.itemChanged()

    # setData()

    def data(self):
        return self.__data

    # data()

    def setColor(self, color):
        if self.__color != color:
            self.__color = color
            self.itemChanged()

    # setColor()

    def color(self):
        return self.__color

    # color()

    def boundingRect(self):
        result = self.__data.boundingRect()
        if not result.isvalid():
            return result
        if self.testHistogramAttribute(HistogramItem.Xfy):
            result = Qwt.QwtDoubleRect(result.y(), result.x(),
                                       result.height(), result.width())
            if result.left() > self.baseline():
                result.setLeft(self.baseline())
            elif result.right() < self.baseline():
                result.setRight(self.baseline())
        else:
            if result.bottom() < self.baseline():
                result.setBottom(self.baseline())
            elif result.top() > self.baseline():
                result.setTop(self.baseline())
        return result

    # boundingRect()

    def rtti(self):
        return Qwt.QwtPlotItem.PlotHistogram

    # rtti()

    def draw(self, painter, xMap, yMap, rect):
        iData = self.data()
        painter.setPen(self.color())
        x0 = xMap.transform(self.baseline())
        y0 = yMap.transform(self.baseline())
        for i in range(iData.size()):
            if self.testHistogramAttribute(HistogramItem.Xfy):
                x2 = xMap.transform(iData.value(i))
                if x2 == x0:
                    continue

                y1 = yMap.transform(iData.interval(i).minValue())
                y2 = yMap.transform(iData.interval(i).maxValue())

                if y1 > y2:
                    y1, y2 = y2, y1
                    
                if  i < iData.size()-2:
                    yy1 = yMap.transform(iData.interval(i+1).minValue())
                    yy2 = yMap.transform(iData.interval(i+1).maxValue())

                    if y2 == min(yy1, yy2):
                        xx2 = xMap.transform(iData.interval(i+1).minValue())
                        if xx2 != x0 and ((xx2 < x0 and x2 < x0)
                                          or (xx2 > x0 and x2 > x0)):
                            # One pixel distance between neighboured bars
                            y2 += 1

                self.drawBar(
                    painter, Qt.Qt.Horizontal, Qt.QRect(x0, y1, x2-x0, y2-y1))
            else:
                y2 = yMap.transform(iData.value(i))
                if y2 == y0:
                    continue

                x1 = xMap.transform(iData.interval(i).minValue())
                x2 = xMap.transform(iData.interval(i).maxValue())

                if x1 > x2:
                    x1, x2 = x2, x1

                if i < iData.size()-2:
                    xx1 = xMap.transform(iData.interval(i+1).minValue())
                    xx2 = xMap.transform(iData.interval(i+1).maxValue())
                    x2 = min(xx1, xx2)
                    yy2 = yMap.transform(iData.value(i+1))
                    if x2 == min(xx1, xx2):
                        if yy2 != 0 and (( yy2 < y0 and y2 < y0)
                                         or (yy2 > y0 and y2 > y0)):
                            # One pixel distance between neighboured bars
                            x2 -= 1
                
                self.drawBar(
                    painter, Qt.Qt.Vertical, Qt.QRect(x1, y0, x2-x1, y2-y0))

    # draw()

    def setBaseline(self, reference):
        if self.baseline() != reference:
            self.__reference = reference
            self.itemChanged()

    # setBaseLine()
    
    def baseline(self,):
        return self.__reference

    # baseline()

    def setHistogramAttribute(self, attribute, on = True):
        if self.testHistogramAttribute(attribute):
            return

        if on:
            self.__attributes |= attribute
        else:
            self.__attributes &= ~attribute

        self.itemChanged()
    
    # setHistogramAttribute()

    def testHistogramAttribute(self, attribute):
        return bool(self.__attributes & attribute) 

    # testHistogramAttribute()

    def drawBar(self, painter, orientation, rect):
        painter.save()
        color = painter.pen().color()
        r = rect.normalized()
        factor = 125;
        light = color.light(factor)
        dark = color.dark(factor)

        painter.setBrush(color)
        painter.setPen(Qt.Qt.NoPen)
        Qwt.QwtPainter.drawRect(painter, r.x()+1, r.y()+1,
                                r.width()-2, r.height()-2)

        painter.setBrush(Qt.Qt.NoBrush)

        painter.setPen(Qt.QPen(light, 2))
        Qwt.QwtPainter.drawLine(
            painter, r.left()+1, r.top()+2, r.right()+1, r.top()+2)

        painter.setPen(Qt.QPen(dark, 2))
        Qwt.QwtPainter.drawLine(
            painter, r.left()+1, r.bottom(), r.right()+1, r.bottom())

        painter.setPen(Qt.QPen(light, 1))
        Qwt.QwtPainter.drawLine(
            painter, r.left(), r.top() + 1, r.left(), r.bottom())
        Qwt.QwtPainter.drawLine(
            painter, r.left()+1, r.top()+2, r.left()+1, r.bottom()-1)

        painter.setPen(Qt.QPen(dark, 1))
        Qwt.QwtPainter.drawLine(
            painter, r.right()+1, r.top()+1, r.right()+1, r.bottom())
        Qwt.QwtPainter.drawLine(
            painter, r.right(), r.top()+2, r.right(), r.bottom()-1)

        painter.restore()

    # drawBar()

# class HistogramItem
