#! /usr/bin/python

import numpy as np

from pdb import set_trace as bp #DEBUGGIN

class FileProcessor:

  def __init__(self):
    #instance variables
    self.plotsUsed = [1] #let the GUI know to reserve this plot space


  def load(self, filesList):
    '''I am being lazy here and simply rereading all the files.
    If your files are large and this starts taking a long time you should make sure this method
    only reads in the new data and not all the data
    '''
    self.filesList = filesList
    self.processedData = [{}]
    self.displayData = []
    self.tableData = []
    self.cube = []

    self.processFiles()
    self.prepareDataForDisplay()
    self.prepareTableData()


  def processFiles(self):
    '''This method builds self.processedData
    '''
    #leave open the possiblility to process more than 1 file, but for now only 1 works
    #if more than one file is presented, only the last file gets displayed
    #this code assumes the lines are in in temporal order
    for filename in self.filesList:
      boardNumber = 10
      registerNumber = 17
      
      f = open(filename)
      lines = f.readlines()
      lines = lines[2:] #Remove putty log lines before processing
      f.close()
      #This will hold all the timestamps in order
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
            #if there is no previous value to compare to, simply add in the current value
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
    '''This method should build self.displayData
    '''
    for i in range(len(self.processedData)):
      if i is 0:
        self.displayData.append(['All Registers'])
      else:
        self.displayData.append(['Register '+str(i)])
        

  def prepareTableData(self):
    '''This method should build self.tableData
    '''
    for i in range(len(self.processedData)):
      self.tableData.append([]) #New list for each plot item
      self.tableData[-1].append(['Board', 'Count']) #append the header list
      self.tableData[-1].append(range(1,11)) #append the board number
      if i is 0:
        #the list of total error count (over all registers) in each board
        self.tableData[-1].append(sum(np.transpose(self.cube[-1,:,:])))
      else:
        self.tableData[-1].append(self.cube[-1,:,i-1])

