#! /usr/bin/python

import os
import numpy as np

class FileProcessor:
  '''
  This class takes a list of files to open

  .processedData - returns a list of dicts with the labeled processed data
  .plotType - returns the suggested plot type for the processed data
  '''

  def __init__(self, filesList):
    #instance variables
    self.filesList = filesList
    self.processedData = [{}]
    self.plotType = ''

    #process the files
    self.processFiles()

  def processFiles(self):

    #initialize the first dictionary to be the total of all the runs
    self.processedData[0]['filename'] = 'All Runs'
    self.processedData[0]['Decoder'] = ''
    self.processedData[0]['AutoMea'] = ''
    self.processedData[0]['pulsewidthList'] = []
    self.processedData[0]['dataCount'] = 0
    self.processedData[0]['doublePulse'] = []
    self.processedData[0]['invalidString'] = []

    for filepath in self.filesList:
      #place a dictionary in the list for each run of the experiment
      self.processedData.append({})
      self.processedData[-1]['filename'] = os.path.basename(filepath)
      self.processedData[-1]['pulsewidthList'] = []
      self.processedData[-1]['doublePulse'] = []
      self.processedData[-1]['invalidString'] = []
      self.processedData[-1]['Decoder'] = 'Not specified'
      self.processedData[-1]['AutoMea'] = 'Not specified'

      #open the current file and loop over each line
      currentFile = open(filepath)
      lineNumber = 0
      self.processedData[-1]['dataCount'] = 0
      for line in currentFile:
        fixedLine = line.strip()
        lineNumber += 1
        if 'Decoder' in line:
          self.processedData[-1]['Decoder'] = fixedLine[10]
        if 'AutoMea' in line:
          self.processedData[-1]['AutoMea'] = fixedLine[10]
        if '0000000' in line:
          #if there is an invalid string (non hex char) the rawPulse creation will fail
          try:
            rawPulse = filter(None, bin(int(fixedLine[11:] ,16))[2:].split('0'))
            #if more than one pulse is detected set the flag to true
            if len(rawPulse) > 1:
              self.processedData[-1]['doublePulse'].append(lineNumber)
            for pulse in rawPulse:
              pulsewidth = len(pulse)
              #store the pulsewidths in picoseconds. One '1' is equal to 30 ps
              self.processedData[-1]['pulsewidthList'].append(pulsewidth*30)
              self.processedData[0]['pulsewidthList'].append(pulsewidth*30)
              #increment the datacounts
              self.processedData[-1]['dataCount'] += 1
              self.processedData[0]['dataCount'] += 1
          except ValueError:
            self.processedData[-1]['invalidString'].append(lineNumber)


    #loop over each run and prepare the bins and counts for a histogram plot
    for i in range(len(self.processedData)):
      try:
        maxBinValue = max(self.processedData[i]['pulsewidthList'])
      except ValueError:
        maxBinValue = 0
      self.processedData[i]['binValues'] = np.arange(0,maxBinValue+1, 30)
      self.processedData[i]['binCounts'] = np.zeros(len(np.arange(0,maxBinValue+1, 30)))
      for pulsewidth in self.processedData[i]['pulsewidthList']:
        self.processedData[i]['binCounts'][int(pulsewidth/30)] += 1



