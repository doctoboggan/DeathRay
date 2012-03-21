# Name: Saves waveform to a source
# Made by: Nadiah Zainol Abidin
# Date: 02/20/12  (MM/DD/YY)
# Goal: set a DC voltage to a specific channel.
# Devices:  1) "dso6032a" 
# Modifiers:  None 



import data_acquisition

class saveFileWaveform (data_acquisition.vxi_11.vxi_11_connection,data_acquisition.gpib_utilities.gpib_device, data_acquisition.vxi_11.VXI_11_Error):	
  """
  :SAVE:PWD <path_name>

  <path_name> ::= quoted ASCII string
  The :SAVE:PWD command sets the present working directory for save
  operations.  

  The :SAVE:FILename command specifies the source for any SAVE
  operations.

  SAVE:WAVeform[:STARt] [<file_name>]
  <file_name> ::= quoted ASCII string
  The :SAVE:WAVeform[:STARt] command saves oscilloscope waveform data
  to a file.
  
  :SAVE:WAVeform:LENGth <length>
  <length> ::= 100 to max. length; an integer in NR1 format
  The :SAVE:WAVeform:LENGth command sets the waveform data length
  (that is, the number of points saved). <NR1> is a number from 0 to 255 that indicates the decimal value of the binary

  This class saves file using a base name and later
  saves in the directory requested by the user. 
  """

  def __init__(self, IPad = '127.0.0.1', Gpibad = "inst0", namdev = "Network Device", FileName = 'Experiment1', pointsInFile = 150, pathName, timeout = 500): 
'''
not sure how timeout works with saving files
def __init__(self, IPad = '127.0.0.1', Gpibad = "inst0", namdev = "Network Device", FileName = 'Experiment1', pointsInFile = 150, pathName, timeout = 500): 
'''
    self.ip_id = IPad
    self.gpib_id = Gpibad
    self.name_of_device = namdev
    self.rightDevice = ['dso6032a']
    self.baseName = FileName
    self.lengthOfFile = pointsInFile
    self.pathName = pathName
    self.nameOfFiles = [] #add in self.baseName if self.baseName is not the same name that exists in self.nameOfFiles. HOW? 
    rise_on_error = 0
    data_acquisition.vxi_11.vxi_11_connection.__init__(self,host=IPad,device=Gpibad,raise_on_err=rise_on_error,timeout=timeout,device_name=namdev)  
    #here we are feeding the data_acquisition library


  def check(self):


    if self.name_of_device in self.rightDevice:

      if type(self.timeout) is int or float:

        if self.timeout >= 500:      # hardcoded. Also, the number was choosen after several testing.

          if type(self.baseName) is str:
      
            if self.baseName not in self.nameOfFiles: #have to add agrument if baseName does not exist in directory already. 
            
              if type(self.pathName) is str:

                if type(self.lengOfFile) is int and self.lengthOfFile <= 255 and self.lengOfFile >= 100:

                  if self.name_of_device == 'dso6032a':
                    return True
              
                  else:
                    return False, 'wrong device'
              
                else: 
                  return False, 'File length error'
               
              else: 
                return False, 'path name error'

             
            else: 
              return False, 'file name already taken'

          else:
             return False, 'file name is not a string'
           
        else:
          print "The time-out is too short"   # For debug purpose
          return False, 'o'

      else: 

        print "timeout input is not acceptable"
        return False, 'q'

    else:
      print "the device is not in data base"    # For debug purpose
      return False, 'x'





  def get(self):		
    """
   
    """
 if self.check() is True:

      print "PASS check test"         # For debug purpose

      if self.name_of_device == 'dso6302a':

          fileName = self.transaction('SAVE:FIL '+self.baseName)      #First step
          directory = self.transaction('SAVE:PWD'+self.pathName+']')   #second step
          startSave = self.transaction('SAVE:WAV[:STAR] ['+self.baseName+']') #third
          endSave = self.transaction('SAVE:WAV:LENG'+self.lengthOfFile+']') #fourth
           

          print "DC voltage is "+set_voltageDC[2]    # For debug reasons.

          if startSave[0] == 0:             #check if it times out.

            print "It works !!"               # For debug reasons. 
            return True                # I have to considre this test here because I need to know the result. 

          else:
            print self.identify_vxi_11_error(startSave[0])      #print the error information.
            return False, startSave[0]  # It is going to return the error number. 

      
      else: 
        print "you should not be here at all. HOW DID YOU PASS THE CHECK TEST !!"       # here , we add new devices with new commands (using "elif" command). The user should not get here at all (hopefully).
        return False, 'w'


    else:
      return self.check()



'''
:SAVE:FILename <base_name>
<base_name> ::= quoted ASCII string
The :SAVE:FILename command specifies the source for any SAVE
operations.
Query Syntax :SAVE:FILename?
The :SAVE:FILename? query returns the current SAVE filename.
Return Format <base_name><NL>
<base_name> ::= quoted ASCII string
note --> This command specifies a file's base name only, without path information or an extension.

SAVE:IMAGe:FACTors <factors>
<factors> ::= {{OFF | 0} | {ON | 1}}
The :SAVE:IMAGe:FACTors command controls whether the oscilloscope
factors are output along with the image.
Query Syntax :SAVE:IMAGe:FACTors?
The :SAVE:IMAGe:FACTors? query returns a flag indicating whether
oscilloscope factors are output along with the image.
Return Format <factors><NL>
<factors> ::= {0 | 1}


SAVE:WAVeform[:STARt] [<file_name>]
<file_name> ::= quoted ASCII string
The :SAVE:WAVeform[:STARt] command saves oscilloscope waveform data
to a file.
note --> If a file extension is provided as part of a specified <file_name>,
and it does not match the extension expected by the format specified in :SAVE:WAVeform:FORMat,
the format will be changed if the extension is a valid waveform file extension.

:SAVE:IMAGe[:STARt] [<file_spec>]
<file_spec> ::= {<internal_loc> | <file_name>}
<internal_loc> ::= 0-9; an integer in NR1 format
<file_name> ::= quoted ASCII string
The :SAVE:IMAGe[:STARt] command saves an image.

:SAVE:WAVeform:LENGth <length>
<length> ::= 100 to max. length; an integer in NR1 format
The :SAVE:WAVeform:LENGth command sets the waveform data length
(that is, the number of points saved).

:SAVE:PWD <path_name>
<path_name> ::= quoted ASCII string
The :SAVE:PWD command sets the present working directory for save
operations.
