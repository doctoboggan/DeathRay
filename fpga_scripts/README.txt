This class takes as input a list of files to open.
It is designed to be imported by the main GUI window and to expose a few variables and
a method.

The methods you **MUST** build are:

  1) __init__(self, fpgaOutputFile)
    
      The __init__ method of this class must accept as a string the path to the FPGA output
      file. You must make sure all three of the variables listed below are initialized by
      the time this method returns, as DeathRay expects them.

  2) reloadData(self):

      This method must take no additional arguments. It will be called whenever a change is
      detected in the fpgaOutputFile. You should use this method to open the fpgaOutputFile,
      find the changes and then update the three variables below.


The variables you **MUST** build are:
  
  1) self.processedData

    This variable will hold the data to be plotted, and information about how to plot it
    It is a list of dictionaries, each dictionary corresponding to an item in the
    treeWidget (List on the left side of the window)
    Each dictionary must have the following keys (all of them are strings):
      'plotType'   : 'line', 'spline', 'steps', 'sticks', or 'scatter' (str)
      'x-axis'     : label for the x axis (str)
      'y-axis'     : label for the y axis (str)
      'x-vector'   : vector representing the x-values (list or np-array)
      'y-vector'   : vector representing the y-values (list or np-array)
    You can also store your own data in this dictionary under different keys
    If you want to plot in one of the other three regions, you may optionally build:
      self.processedData2, self.processedData3, or self.processedData4

  ********************************************************************************************
  2) self.displayData

    Prepare a list of lists for display in the treeWidget. Each sublist contains only strings
    The first string is the title that will be displayed on the top level
    All the following strings will be displayed as sub items when the arrow is dropped down

    ex: ['title', 'drop down 1', 'drop down 2', 'drop down 3'] will display as

    >title
      drop down 1
      drop down 2
      drop down 3

  ********************************************************************************************
  3) self.tableData

    Prepare a list of lists of lists (yes) for display in the table. The outermost list contains 
    one element for each item in the treeWidget. When an item is selected in the treeWidget, the
    corresponding list is displayed in the table
    
    Each list inside that outermost list also contains lists representing the columns in the
    table from left to right. However the first list is a list of the column headers. Maybe
    an example will help

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
  ********************************************************************************************


Optional variables

  1) self.processedData2
      Data in here will be displayed on the second plot
  2) self.processedData3
      Data in here will be displayed on the third plot
  3) self.processedData4
      Data in here will be displayed on the fourth plot
  4) self.plotsUsed
      Should be a list of plot indexes used, eg: [1,2] means plots 1 and 2 should be reserved.
      This is used to let the Device Control window disable plots. If it is not specified the variables
      above will take precedence over any device commands selected through the GUI. This variable must
      be specified on one line

