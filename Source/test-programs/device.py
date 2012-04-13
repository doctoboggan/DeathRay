#! /usr/bin/env python

import libgpib

deviceList = []
for possibleDevice in dir(libgpib):
  try:
    if 'libgpib' in eval('libgpib.'+possibleDevice+'.__module__'):
      deviceList.append(possibleDevice)
  except AttributeError:
    pass



