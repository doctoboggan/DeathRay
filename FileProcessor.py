#! /usr/bin/python

import os
import numpy as np

class FileProcessor:
  '''
  This class takes a list of files to open

  .processedData - returns a list of dicts (one for each file) with the labeled processed data
  .plotType - returns the suggested plot type for the processed data
  .displayData - list of lists with data formated to be displayed by the treeWidget

  This will ultimately be the class that has to be written for each experimental setup
  '''

  def __init__(self, filesList):
    #instance variables
    self.filesList = filesList
    self.processedData = [{}]
    self.plotType = 'histogram'
    self.plotTitle = 'Frequency of detected pulse widths'
    self.xAxis = 'Pulse Width (picoseconds)'
    self.yAxis = 'Frequency'

    #process the files and then prepare the data for display
    self.processFiles()
    self.prepareDataForDisplay()


  def processFiles(self):
    #initialize the first dictionary to be the total of all the runs
    self.processedData[0] = {'filename': 'All Runs',
                              'Decoder': '',
                              'AutoMea': '',
                       'pulsewidthList': [],
                            'dataCount': 0,
                          'doublePulse': [],
                        'invalidString': []}

    for filepath in self.filesList:
      #place a dictionary in the list for each run of the experiment
      self.processedData.append({})
      self.processedData[-1] = {'filename': os.path.basename(filepath),
                                'Decoder': '',
                                'AutoMea': '',
                         'pulsewidthList': [],
                              'dataCount': 0,
                            'doublePulse': [],
                          'invalidString': []}

      #open the current file and loop over each line
      currentFile = open(filepath)
      lineNumber = 0
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
    for run in self.processedData:
      self.displayData.append([])
      self.displayData[-1].append(run['filename'])

      if run['Decoder'] != '':
        decoderType = ['DIRECT_INPUT',
                      'inv_1x_avt_fb',
                      'inv_1x_rvt',
                      '24576_inv_1x_rvt',
                      'OR_Tree_rvt',
                      'inv_1x_rvt_bt',
                      'OR_Tree_bt',
                      'nhit_rvt',
                      'phit_bt',
                      'nhit_bt',
                      'inv_1x_to_bt',
                      'inv_5x_s_rvt',
                      'inv_1x_to',
                      'OR_Tree_to',
                      'phit_rvt,'
                      'inv_5x_f_rvt']
        decNum = run['Decoder']
        self.displayData[-1].append('Decoder ' + decNum + ': ' + decoderType[int(decNum, 16)])
      
      if run['AutoMea'] != '':
        autoMeaType = ['30%',
                      '49%',
                      '56%',
                      '70%',
                      '80%',
                      'OVERFLOW',
                      'NOT VALID',
                      'NOT VALID']
        autoNum = run['AutoMea']
        self.displayData[-1].append('AutoMea ' + autoNum + ': ' + autoMeaType[int(autoNum)])
      
      if run['dataCount'] != 0:
        self.displayData[-1].append('Data points: ' + str(run['dataCount']))

      if run['invalidString'] != []:
        self.displayData[-1].append('Invalid lines: ' + str(run['invalidString']))

      if run['doublePulse'] != []:
        self.displayData[-1].append('Double pulse lines: ' + str(run['doublePulse']))


