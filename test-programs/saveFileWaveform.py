# Name: Saves waveform to a source
# Made by: Nadiah Zainol Abidin
# Date: 02/20/12  (MM/DD/YY)
# Goal: set a DC voltage to a specific channel.
# Devices:  1) "dso6032a" 
# Modifiers:  None 

#right now it only has a name but not a directory. needs a lot of work to do. 
# did not use Anas's way because not familiar yet

import libgpib

class saveFileWaveform:  	
  """
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

  def __init__(self, IPad, Gpibad, namdev, FileName, pointsInFile, pathName): 

    self.ip_id = IPad
    self.gpib_id = Gpibad
    self.name_of_device = namdev
    self.rightDevice = ['dso6032a']
    self.baseName = FileName
    self.lengthOfFile = pointsInFile
    self.pathName = pathName

#note: how to check if file name already exists?


  def check(self):
    """
        
    """
    if self.name_of_device not in self.rightDevice:
      return False

    return True



  def get(self):		
    """
    The main SCPI command. It has ____ steps,
    
    Note: between each transaction, we have to disconnect the connection to aviod time-out errors. Also, to allow other connection to be established. 
    """
    m = eval('libgpib.'+ self.name_of_device+'(host="'+self.ip_id+'", device="'+self.gpib_id+'")')
    z , c , a = m.transaction('SAVE:FIL '+self.baseName) #SAVE:FILename <base_name>
    m.disconnect()
    z , c , d = m.transaction('SAVE:PWD'+self.pathName+']') #SAVE:PWD <path_name> 
    m.disconnect()
    z , c , b = m.transaction('SAVE:WAV[:STAR] ['+self.FileName+']') #SAVE:WAV[:STARt] [<file_name>]
    m.disconnect()
    z , c , e = m.transaction('SAVE:WAV:LENG'+self.lengthOfFile+']') #SAVE:WAVeform:LENGth <length>  
    m.disconnect()
    
    return 'Waveform is saved in file'+self.baseName+'and the length is'+self.lengthOfFile
    
#save image is done yet

''''
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
