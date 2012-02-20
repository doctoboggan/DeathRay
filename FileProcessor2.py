#! /usr/bin/python

import os
import numpy as np

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
    self.plotType = 'histogram'
    self.plotTitle = 'Frequency of detected pulse widths'
    self.xAxis = 'Pulse Width (picoseconds)'
    self.yAxis = 'Frequency'

    #process the files and then prepare the data for display
    self.processFiles()
    self.prepareDataForDisplay()
    self.prepareTableData()


  def processFiles(self):

    currentDecoder = '' #initiailze variables
    currentAutoMea = ''

    #initialize the first dictionary to be the total of all the runs
    self.processedData[0] = {'filename': 'All Runs',
                              'Decoder': '',
                              'AutoMea': '',
                       'pulsewidthList': [],
                            'dataCount': 0,
                          'doublePulse': [],
                        'invalidString': []}

    #loop over each file in the file list
    for filepath in self.filesList:
      #place a dictionary in the list for each run of the experiment
      self.processedData.append({})
      self.processedData[-1] = {'filename': os.path.basename(filepath).split('.')[0],
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
          currentDecoder = fixedLine[10]
        self.processedData[-1]['Decoder'] = currentDecoder
        if 'AutoMea' in line:
          currentAutoMea = fixedLine[10]
        self.processedData[-1]['AutoMea'] = currentAutoMea
        if '0000000' in line:
          #if there is an invalid string (non hex char) the rawPulse creation will fail
          try:
            rawPulse = filter(None, bin(int(fixedLine[11:] ,16))[2:].split('0'))
            #if more than one pulse is detected set the flag to true
            if len(rawPulse) > 1:
              self.processedData[-1]['doublePulse'].append(lineNumber)
            #if no pulse listed, it is the smallest pulse detected
            if len(rawPulse) == 0:
              self.processedData[-1]['pulsewidthList'].append(15)
              self.processedData[0]['pulsewidthList'].append(15)
              self.processedData[-1]['dataCount'] += 1
              self.processedData[0]['dataCount'] += 1
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
        self.displayData[-1].append('AutoMeasure ' + autoNum + ': ' + autoMeaType[int(autoNum)])
      
      if run['dataCount'] != 0:
        self.displayData[-1].append('Data points: ' + str(run['dataCount']))

      if run['invalidString'] != []:
        self.displayData[-1].append('Invalid lines: ' + str(run['invalidString']))

      if run['doublePulse'] != []:
        self.displayData[-1].append('Double pulse lines: ' + str(run['doublePulse']))


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
    for run in self.processedData:
      if run['filename'] == 'All Runs':
        self.tableData = [[['Run', 'Decoder', 'AutoMea', 'Count'], [], [], [], []]]
        for run2 in self.processedData:
          if run2['filename'] != 'All Runs':
              self.tableData[0][1].append(run2['filename'])
              self.tableData[0][2].append(run2['Decoder'])
              self.tableData[0][3].append(run2['AutoMea'])
              self.tableData[0][4].append(run2['dataCount'])
      else:
        self.tableData.append([['Pulsewidths', 'Avg', 'Max', 'Min', 'Stdv'], [], [], [], [], []])
        self.tableData[-1][1] = run['pulsewidthList']
        self.tableData[-1][2].append(np.around(np.mean(run['pulsewidthList'])))
        self.tableData[-1][3].append(max(run['pulsewidthList']))
        self.tableData[-1][4].append(min(run['pulsewidthList']))
        self.tableData[-1][5].append(np.around(np.std(run['pulsewidthList'])))
    print self.tableData


