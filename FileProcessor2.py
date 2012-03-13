#! /usr/bin/python

import os
import numpy as np

from pdb import set_trace as bp

class FileProcessor:
  '''
  This class takes a list of files to open

  .processedData - returns a list of dicts (one for each file) with the labeled processed data
  .displayData - list of lists with data formated to be displayed by the treeWidget

  This will ultimately be the class that has to be written for each experimental setup
  '''

  def __init__(self, filesList):
    #instance variables
    self.filesList = filesList
    self.processedData = [{}]
    self.cube = []

    #process the files and then prepare the data for display
    self.processFiles()
    self.prepareDataForDisplay()
    self.prepareTableData()


  def processFiles(self):

    #leave open the possiblility to process more than 1 file, but for now only 1 works
    for filename in self.filesList:
      boardNumber = 10
      registerNumber = 17
      
      f = open(filename)
      lines = f.readlines()
      lines = lines[2:] #Remove putty log lines before processing
      f.close()
      #This will hold all the timestamps in order for each file
      timestampVector = []
      #This matrix counts how many times each register has rolled over
      rollOverCount = np.zeros([boardNumber, registerNumber], dtype=int)

      #timeCube will be a 3d array to hold all the data
      #Dim  0       1        2
      #Val  time    board    register
      timeCube = []
      for line in lines:
        timestampVector.append(int(line[0:9].strip(), 16))
        boardCodes = line[11:].strip()
        boardMat = []
        for b in range(boardNumber):
          #will hold all the values of the registers on the current board
          regVector = []
          for r in range(registerNumber):
            pointer = b*34+2*r
            regValue = int(boardCodes[pointer:pointer+2], 16)
            #if there is no previous value to compare to, simple add in the current value
            if len(timeCube) is 0:
              regVector.append(regValue)
            else: #if there is a value, check to see if it is lower than the previous (rollover)
              if timeCube[-1][b][r] <= regValue:
                regVector.append(regValue + 256*rollOverCount[b,r])
              else:
                rollOverCount[b,r] += 1
                regVector.append(regValue + 256*rollOverCount[b,r])
          boardMat.append(regVector)
        timeCube.append(boardMat)
      self.cube = np.array(timeCube)
    

    #add in first plot data which is simply each register and total count
    self.processedData[0]['plotType'] = 'sticks'
    self.processedData[0]['x-axis'] = 'Register Number'
    self.processedData[0]['y-axis'] = 'Total Error Count'
    self.processedData[0]['x-vector'] = np.arange(1,18)
    self.processedData[0]['y-vector'] = sum(self.cube[-1,:,:])

    
    #Iterate over each register and pull out the data vector from the cube
    for r in range(17):
      self.processedData.append({})
      self.processedData[r+1]['plotType'] = 'step'
      self.processedData[r+1]['x-axis'] = 'Timestamp'
      self.processedData[r+1]['y-axis'] = 'Total Error Count'
      self.processedData[r+1]['x-vector'] = timestampVector
      self.processedData[r+1]['y-vector'] = sum(np.transpose(self.cube[:,:,r]))



  def prepareDataForDisplay(self):
    '''
    Prepare a list of lists for display in the treeWidget. Each sublist contains only strings
    The first string is the run name that will be displayed on the top level
    All the following strings will be displayed as sub items when the arrow is dropped down

    ex: ['title', 'drop down 1', 'drop down 2', 'drop down 3'] will display as

    >title
      drop down 1
      drop down 2
      drop down 3
    '''

    self.displayData = []
    for item in self.processedData:
      self.displayData.append('yup')

  def prepareTableData(self):
    '''
    Prepare a list of lists of lists (yes) for display in the table. The outermost list contains one element
    for each run. When a run is selected in the treeWidget, the corresponding list is displayed in the table
    
    Each list inside that outermost list also contains lists representing the columns in the table from
    left to right. However the first list is a list of the column headers. Maybe an example will help

    [
      [
        ['first header 1', 'first header 2'],
        [1,2,3,4,5],
        ['a','b','c','d','e']
      ],
      [
        ['second header 1', 'second header 2'],
        [6,7,8,9,0],
        ['f','g','h','i','j']
      ]
    ]

    When the first item in the tree widget is selected the table will display:
    
            first header 1    first header 2
            1                  a
            2                  b
            3                  c
            4                  d
            5                  e

    and likewise when the second item is selected.

    Store this data in the variable self.tableData and it will be displayed.
    '''
    self.tableData = []

