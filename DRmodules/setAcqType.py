# Name: Sets the oscilloscope mode.
# Made by: Nadiah Zainol Abidin
# Date: 02/17/12  (MM/DD/YY)
# Goal: set the mode of the oscilloscope <type> ::= {NORMal | AVERage | HRESolution | PEAK}
# Devices:  1) dso6032a
# Modifiers:  None 
# SCPI command: 1) dso6032a ---> command to choose type ==> ACQuire:TYPE <type>
# ------------ <type> : -------------
# <type> ::= {NORMAL | AVERAGE | HERSOLUTION | PEAK}
# -----------------------------------
# Result: One string. it notifies the osc is set to the mode requested  

import data_acquisition

class AcqType(data_acquisition.vxi_11.vxi_11_connection,data_acquisition.gpib_utilities.gpib_device,data_acquisition.vxi_11.VXI_11_Error):		
  """
  This class sets the type of mode to operate the oscillscope
  """

  def __init__(self, IPad = '127.0.0.1', Gpibad = "inst0", namdev = "Network Device", setmode = "normal", timeout = 500): 
    """
    Requiremnt: ( IPad, Gpibad, namdev, input, channel='p25v', timeout=500)
    Ex of requirement: '129.59.93.179', 'gpib0,22', 'hpe3631a', '3' , channel='n25v', timeout=3000)
    ____________________________
    To store the given values from the user. 
    Note:
      --> IPad is the number of ip-address with quotation mark. 
      --> Gpibad is the number of Gpib address with quotation mark.
      --> namdev is the name of the device.
      --> setmode is the mode that the user wants the oscillscope to be in. The setmode can take in inputs - refer self.mode_type_dso 
      --> timeout is time duration of the operation. 
    Ex (for channel device) :   -----CvoltageDC('129.59.93.27', 'gpib0,10', 'hp34401a', '5', channel='p25v').get()
    Also, the definition has the devices list (hard-coded).
    Besdies that, you can control the time-out duration. The dafult time-out duration is 2500 msec. To change the time-out to 3000msec:
    Ex (for channel device with different time-out): ----- CvoltageDC('129.59.93.27', 'gpib0,10', 'hp34401a', '15', channel='p25v', timeout=3000).get()
    Becareful with time-out, it will cause crazy issues if the time-out is small (ex: 100msec).
    """

    self.ip_id = IPad
    self.gpib_id = Gpibad
    self.name_of_device = namdev.lower()    #lower case the input
    self.rightDevice = ['dso6032a']
    self.modetype_for_dso = ['normal', 'average', 'hresolution', 'peak']
    self.setmode = setmode.lower()          # It will convert it to lower case to consider how it will be written (from the user).
    self.timeout = timeout
    rise_on_error = 0
    data_acquisition.vxi_11.vxi_11_connection.__init__(self,host=IPad,device=Gpibad,raise_on_err=rise_on_error,timeout=timeout,device_name=namdev)  
                                            #here we are feeding the data_acquisition library


  def check(self):
    """
    To check if the given device will work with AcqType function (to avoid module from crashing).
    Also, it checks if the specified channel of certain device matches the data base of the names of channels in that device.
    it also checks to make sure the setmode entered by the user is valid for the device
    ALso, we take care of time-out minimum duration (to aviod run out of time).
    Also, we remind the user if the input channel is not required for the given device. 
    whatever that has been entered into setmode by the user, it is converted to lower case: so the only valid cases should be - refer self.modetype_for_dso
    """
    if self.name_of_device in self.rightDevice:

      if type(self.timeout) is int or float:

        if self.timeout >= 500:      # hardcoded. Also, the number was choosen after several testing.

          if type(self.setmode) is str: #setmode should only be a string type

            if self.name_of_device == 'dso6032a':

              if self.setmode not in self.modetype_for_dso: # for mode checking. very important to make sure mode 
                print "chosen mode does not exist !!"     # For debug purpose #also do not accept empty strings
                return False, 'c'
              
              else:
                return True

            else:
              print  "you probably got the wrong device.. how did you get here?" #for debug purposes
              return False, 'w'                                                                   #the user may add elif here if there exist another device that works with the command
              

          else:
            print "input mode is not a string!!"  # For debug purpose
            return False, 's'

        else:
          print "The time-out is too short"   # For debug purpose
          return False, 'o'

      else: 

        print "timeout input is not acceptable"
        return False, 'q'

    else:
      print "the device is not in data base"    # For debug purpose
      return False, 'x'
  



  def do(self):		
    """
    The main SCPI command. 
    First step:
    select the mode of the device. this is done using the SCPI command 
    ACQuire:TYPE <type>
    the type of mode can be selected from the following option:
    <type> ::= {NORMal | AVERage | HRESolution | PEAK}
    """

    if self.check() is True:

      print "PASS check test"         # For debug purpose

      if self.name_of_device == 'dso6032a':

          set_mode = self.transaction('ACQ:TYPE '+self.setmode)

          print "the mode selected is "+set_mode[2]    # For debug reasons. #######Nadiah: not really sure what this will return since this is not a query?

          if set_mode[0] == 0:             #check if it times out.

            print "It works !!"               # For debug reasons. 
            return True                # I have to consider this test here because I need to know the result. 

          else:
            print self.identify_vxi_11_error(set_mode[0])      #print the error information.
            return False, set_mode[0]  # It is going to return the error number. 

      
      else: 
        print "you should not be here at all. HOW DiD YOU PASS THE CHECK TEST !!"       
        # here , we add new devices with new commands (using "elif" command). The user should not get here at all (hopefully).
        return False, 'w'


    else:
      return self.check()


#example: "INST:SEL P25V" Select the +25V output
# Note:   ---> 'o' means time-out is too short.
#         ---> 's' means input setmode is not a string.
#         ---> 'c' means wrong channel input. 
#         ---> 'x' wrong name of device. 
#         ---> 'w' wired error (something wrong with code)
#         ---> 'z' out of range 
#         ---> 'q' timeout input is not number.
# CvoltageDC.CvoltageDC('129.59.93.179', 'gpib0,22', 'hpe3631a').get()
# check if input is negative or not for the negative or positive channels. 
# we have another douple check in the GUI level (the user input)
#--------------------------------------
# For error number, THe meaning is: 
#       1:"Syntax error", 3:"Device not accessible",
# 			4:"Invalid link identifier", 5:"Parameter error", 6:"Channel not established",
#				8:"Operation not supported", 9:"Out of resources", 11:"Device locked by another link",
#				12:"No lock held by this link", 15:"IO Timeout", 17:"IO Error",  21:"Invalid Address",
# 			23:"Abort", 29:"Channel already established" ,
#				"eof": "Cut off packet received in rpc.recvfrag()",
#				"sync":"stream sync lost",
#				"notconnected": "Device not connected"}
#---------------------------------------
# It works. However, the feedback says "it does not". ever, I after I read it by my self!! (need to fix)





#so far, sponsor requested to have the osc in normal mode. other modes have not been accounted for. refer details below
# ---------------Information: ------------
# page 208
# :ACQuire:TYPE <type>
# <type> ::= {NORMal | AVERage | HRESolution | PEAK}
#
# ---> The :ACQuire:TYPE NORMal command sets the oscilloscope in the
# normal mode.
# ---> The :ACQuire:TYPE AVERage command sets the oscilloscope in the
# averaging mode. You can set the count by sending the :ACQuire:COUNt
# command followed by the number of averages. In this mode, the value
# for averages is an integer from 1 to 65536. The COUNt value determines
# the number of averages that must be acquired.
# Setting the :ACQuire:TYPE to AVERage automatically sets
# :ACQuire:MODE to ETIMe (equivalent time sampling).
# The AVERage type is not available when in segmented memory mode
# (:ACQuire:MODE SEGMented).
# ---> The :ACQuire:TYPE HRESolution command sets the oscilloscope in the
# high- resolution mode (also known as smoothing). This mode is used to
# reduce noise at slower sweep speeds where the digitizer samples faster
# than needed to fill memory for the displayed time range.
# -------------------------------------
