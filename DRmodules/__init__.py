from getvoltageDC import getvoltageDC 
from getvoltageAC import getvoltageAC 
from getcurrentDC import getcurrentDC
from setcurrentDC import setcurrentDC
from Displayscreen import Displayscreen
from getIDN import getIDN
from setvoltageDC import setvoltageDC
from getcurrentAC import getcurrentAC
command = {
    'getvoltageDC': getvoltageDC,
    'getvoltageAC': getvoltageAC,
    'getcurrentDC': getcurrentDC,
    'setcurrentDC': setcurrentDC,
    'Displayscreen': Displayscreen,
    'getIDN': getIDN,
    'setvoltageDC': setvoltageDC,
    'getcurrentAC': getcurrentAC
    }
# never ever have an empty line inside this file !! (the program will crash!!)
# because of the "command" dic.We have to get use to how to import stuff from DRmodules (not the same way as DRscripts and other stuff because of different in __init__ method )