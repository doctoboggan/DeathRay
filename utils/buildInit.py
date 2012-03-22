#! /usr/bin/env python

# Name: buildInit.py
# Made by: Jack Minardi
# Date: 3/22/12
# Goal: Make sure the gpib_commands __init__.py file contains all the imports needed
# Result: new __init__.py file


import glob, os

initFile = open('./gpib_commands/__init__.py', 'w')
commandList = []

#find all the commands and append them to commandList
for pyFile in glob.glob('./gpib_commands/*.py'):
  command = os.path.split(pyFile)[1].split('.')[0]
  if '__init__' not in command:
    commandList.append(command)

#add the 'from command import command' lines
for command in commandList:
  initFile.write('from '+command+' import '+command+'\n')

#build the command dictionary
initFile.write('command = {\n')
for command in commandList:
  initFile.write("  '"+command+"': "+command+",\n")
initFile.write('}')

initFile.close()
