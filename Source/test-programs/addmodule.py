# THie file suppose to able to add new modules (not edit them).


import shutil 
import datetime
import re
import sys

import pdb # for debuging 

# delete "result"
# delete all "info"s
# add "input required" for each device.
# add "kind of input" for each device. 

class add():

  def __init__(self, checkk = True ,
                     nameofnewmdoule = 'dafult',
                     module_name = '',
                     module_person = '',
                     module_goal = '',
                     module_device_one = '', # name of first device.
                     module_device_two = '',  # name of second device
                     module_device_three = '',  # name of third device
                     module_device_four = '', # name of forth device
                     module_device_five = '', # name of fifth device
                     module_device_one_scpi = '', # the first device's SCPI command (without input)
                     module_device_two_scpi = '', #  the second device's SCPI command (without input)
                     module_device_three_scpi = '', #  the third device's SCPI command (without input)
                     module_device_four_scpi = '', #  the forth device's SCPI command (without input)
                     module_device_five_scpi = '', #  the fifth device's SCPI command (without input)
                     module_device_one_scpi_input = '', # the first device's SCPI command input.
                     module_device_two_scpi_input = '', # the second device's SCPI command input.
                     module_device_three_scpi_input = '', # the third device's SCPI command input.
                     module_device_four_scpi_input = '', # the forth device's SCPI command input.
                     module_device_five_scpi_input = '', # the fifth device's SCPI command input.
                     firstint = False, # True if the first SCPI input is "int"
                     secondint = False, # True if the second SCPI input is "int"
                     thirdint = False, # True if the third SCPI input is "int"
                     fourthint = False, # True if the forth SCPI input is "int"
                     fifthint = False, # True if the fifth SCPI input is "int"
                     firstf = False, # True if the first SCPI input is "float"
                     secondf = False, # True if the second SCPI input is "float"
                     thirdf = False, # True if the third SCPI input is "float"
                     fourthf = False, # True if the forth SCPI input is "float"
                     fifthf = False, # True if the fifth SCPI input is "float"
                     firststr = True, # True if the first SCPI input is "str"
                     secondstr = True, # True if the second SCPI input is "str"
                     thirdstr = True, # True if the third SCPI input is "str"
                     forthstr = True, # True if the forth SCPI input is "str"
                     fifthstr = True, # True if the fifth SCPI input is "str"
                     oneex = '', # an example input (dafult value) for first SCPI's iput
                     twoex = '', # an example input (dafult value) for second SCPI's iput
                     threeex = '', # an example input (dafult value) for third SCPI's iput
                     fourex = '', # an example input (dafult value) for forth SCPI's iput
                     fiveex = ''): # an example input (dafult value) for fifth SCPI's iput

    self.name = nameofnewmdoule
    self.replace_dic = {}
    self.replace_dic_one = {}
    self.timenow = str(datetime.datetime.now())    # to now the time of creating the new module
    self.nowfile = None
    self.reading = None
    self.listing_scpi_inputs = ['0','0','0','0','0']  # Assume all scpi commands doe not required any extra stuff (0 - not required, 1 - does required)
    self.inputs = []
    self.getset = checkk    # here, we are going to know if it is "set" or "get". If it is"set". it  is False, If it is "get", it is true.
    self.a = module_name
    self.b = module_person
    self.c = module_goal
    self.d = module_device_one
    self.e = module_device_two
    self.f = module_device_three
    self.g = module_device_four
    self.h = module_device_five
    self.i = module_device_one_scpi   # here, the first part of SCPI command
    self.j = module_device_two_scpi
    self.k = module_device_three_scpi
    self.l = module_device_four_scpi
    self.m = module_device_five_scpi
    self.ii = module_device_one_scpi_input    # a name of the input  (second part of second command)
    self.jj = module_device_two_scpi_input
    self.kk = module_device_three_scpi_input
    self.ll = module_device_four_scpi_input
    self.mm = module_device_five_scpi_input
    self.iii = oneex  # a dafult example forunputs
    self.jjj = twoex
    self.kkk = threeex
    self.lll = fourex
    self.mmm = fiveex
    self.iiii = '' # this is the first input phase in the __init__ requirement.
    self.jjjj = ''
    self.kkkk = ''
    self.llll = ''
    self.mmmm = ''
    self.si = ''  # this save the first "self" phase.
    self.sj = ''
    self.sk = ''
    self.sl = ''
    self.sm = ''
    self.bi = ''  # this saves first check input (beginging)
    self.bj = ''
    self.bk = ''
    self.bl = ''
    self.bm = ''
    self.ei = ''  # this saves the fiest check input (end)
    self.ej = ''
    self.ek = ''
    self.el = ''
    self.em = ''
    self.ci = ''  # these are for saving the final shape of 
    self.cj = ''
    self.ck = ''
    self.cl = ''
    self.cm = ''
    self.ai = ''    # these are for saving the final output comment
    self.aj = ''
    self.ak = ''
    self.al = ''
    self.am = ''
    self.ti = ''  # the self.xxx = xxx in def __init__ will be created here.
    self.tj = ''
    self.tk = ''
    self.tl = ''
    self.tm = ''
    self.n = firstint
    self.nn = secondint
    self.nnn = thirdint
    self.nnnn = fourthint
    self.nnnnn = fifthint
    self.o = firstf
    self.oo = secondf
    self.ooo = thirdf
    self.oooo = self
    self.ooooo = fifthf
    self.p = firststr
    self.pp = secondstr
    self.ppp = thirdstr
    self.pppp = forthstr
    self.ppppp = fifthstr


  def copythetamp(self):
    
    if self.getset == True:
      self.name = 'get' + self.name
      shutil.copy2('./tamp.py','../gpib_commands/'+self.name+'.py')
    else:
      self.name = 'set' + self.name
      shutil.copy2('./tamp.py','../gpib_commands/'+self.name+'.py')
    

  def readnewfile(self):

    self.copythetamp()
    self.newfile = open('../gpib_commands/'+self.name+'.py',"r")
    self.reading = self.newfile.read()
    self.newfile.close


  def replacing_function(self, text, word_dic):
    """
    take a text and replace words that match a key in a dictionary with
    the associated value, return the changed text
    """
    rc = re.compile('|'.join(map(re.escape, word_dic)))
    def translate(match):
        return word_dic[match.group(0)]
    return rc.sub(translate, text)
  
  def dafultinput(self):

    if self.ii != '':
      self.iiii = self.ii+' = "'+self.iii+'",'
    else:
      self.iiii = ''
    if self.jj != '':
      self.jjjj = self.jj+' = "'+self.jjj+'",'
    else:
      self.jjjj = ''
    if self.kk != '':
      self.kkkk = self.kk+' = "'+self.kkk+'",'
    else:
      self.kkkk = ''
    if self.ll != '':
      self.llll = self.ll+' = "'+self.lll+'",'
    else:
      self.llll = ''
    if self.mm != '':
      self.mmmm = self.mm+' = "'+self.mmm+'",'
    else:
      self.mmmm = ''

  def selfness(self): # Here, we generate the self.xxx name.

    if self.ii != '':
      self.si = "self."+self.ii
    else:
      self.si = ''
    if self.jj != '':
      self.sj = "self."+self.jj
    else:
      self.sj = ''
    if self.kk != '':
      self.sk = "self."+self.kk
    else:
      self.sk = ''
    if self.ll != '':
      self.sl = "self."+self.ll
    else:
      self.sl = ''
    if self.mm != '':
      self.sm = "self."+self.mm
    else:
      self.sm = '' 

  def basicinputcheck(self):

    self.selfness()

    if self.ii != '':
      if self.n == True:
        if self.o == True:
          self.bi = "if type("+self.si+") is int or type("+self.si+") is float:\n\n              try:\n\n                  "+self.si+" = float("+self.si+")"
        else:
          self.bi = "if type("+self.si+") is int:\n\n              try:\n\n                "+self.si+" = int("+self.si+")"
      elif self.o == True:
        self.bi = "if type("+self.si+") is float:\n\n              try:\n\n                "+self.si+" = float("+self.si+")"
      elif self.p == True: 
        self.bi = "if type("+self.si+") is str:"
      else:
        print "WHY YOU CHOOSE AN INPUT WHILE YOU DO NOT TELL ME THE TYPE!! I AM NOT SMART... BECAUSE OF THAT I AM GOING TO CRY BY STOPING THE TOOL AND CRASH"
        
    else:
      self.bi = ''



    if self.jj != '':
      if self.nn == True:
        if self.oo == True:
          self.bj = "if type("+self.sj+") is int or type("+self.sj+") is float:\n\n              try:\n\n                  "+self.sj+" = float("+self.sj+")"
        else:
          self.bj = "if type("+self.si+") is int:\n\n              try:\n\n                  "+self.sj+" = int("+self.sj+")"
      elif self.oo == True:
        self.bi = "if type("+self.si+") is float:\n\n              try:\n\n                  "+self.sj+" = float("+self.sj+")"
      elif self.pp == True: 
        self.bj = "if type("+self.sj+") is str:"
      else:
        print "WHY YOU CHOOSE AN INPUT WHILE YOU DO NOT TELL ME THE TYPE!! I AM NOT SMART... BECAUSE OF THAT I AM GOING TO CRY BY STOPING THE TOOL AND CRASH"
        sys.exit()
    else:
      self.bj = ''



    if self.kk != '':
      if self.nnn == True:
        if self.ooo == True:
          self.bk = "if type("+self.sk+") is int or type("+self.sk+") is float:\n\n              try:\n\n                  "+self.sk+" = float("+self.sk+")"
        else:
          self.bj = "if type("+self.sk+") is int:\n\n              try:\n\n                  "+self.sk+" = int("+self.sk+")"
      elif self.ooo == True:
        self.bk = "if type("+self.sk+") is float:\n\n              try:\n\n                  "+self.sk+" = float("+self.sk+")"
      elif self.ppp == True: 
        self.bk = "if type("+self.sk+") is str:"
      else:
        print "WHY YOU CHOOSE AN INPUT WHILE YOU DO NOT TELL ME THE TYPE!! I AM NOT SMART... BECAUSE OF THAT I AM GOING TO CRY BY STOPING THE TOOL AND CRASH"
        sys.exit()
    else:
      self.bk = ''



    if self.ll != '':
      if self.nnnn == True:
        if self.oooo == True:
          self.bl = "if type("+self.sl+") is int or type("+self.sl+") is float:\n\n              try:\n\n                  "+self.sl+" = float("+self.sl+")"
        else: 
          self.bl = "if type("+self.sl+") is int:\n\n              try:\n\n                  "+self.sj+" = int("+self.sl+")"
      elif self.oooo == True:
        self.bl = "if type("+self.sl+") is float:\n\n              try:\n\n                  "+self.sl+" = float("+self.sl+")"
      elif self.pppp == True: 
        self.bl = "if type("+self.sl+") is str:"
      else:
        print "WHY YOU CHOOSE AN INPUT WHILE YOU DO NOT TELL ME THE TYPE!! I AM NOT SMART... BECAUSE OF THAT I AM GOING TO CRY BY STOPING THE TOOL AND CRASH"
        sys.exit()
    else:
      self.bl = ''



    if self.mm != '':
      if self.nnnnn == True:
        if self.ooooo == True:
          self.bm = "if type("+self.sm+") is int or type("+self.sm+") is float:\n\n              try:\n\n                  "+self.sm+" = float("+self.sm+")"
        else:
          self.bm = "if type("+self.sm+") is int:\n\n              try:\n\n                  "+self.sj+" = int("+self.sm+")"
      elif self.ooooo == True:
        self.bl = "if type("+self.sm+") is float:\n\n              try:\n\n                  "+self.sm+" = float("+self.sm+")"
      elif self.ppppp == True: 
        self.bm = "if type("+self.sm+") is str:"
      else:
        print "WHY YOU CHOOSE AN INPUT WHILE YOU DO NOT TELL ME THE TYPE!! I AM NOT SMART... BECAUSE OF THAT I AM GOING TO CRY BY STOPING THE TOOL AND CRASH"
        sys.exit()
    else:
      self.bm = ''


#----------------00000000000000000000000000000000000000000000------------------
#----------------00000000000000000000000000000000000000000000------------------

          # I will not check for each single case (which are 9 cases for each device): I am excepting the GUI layer will have right inputs. (I may write more later to explain) 


    if self.ii != '':
      if self.n == True:
        if self.o == True:
          self.ei ="""  except ValueError:

                print "the input is not real number (can not be converted to a numbder) !!"
                return False, 'n'"""


        else:
          self.ei = """  except ValueError:

                print "the input is not real number (can not be converted to a numbder) !!"
                return False, 'n'"""

      elif self.o == True:
        self.ei = """  except ValueError:

                print "the input is not real number (can not be converted to a numbder) !!"
                return False, 'n'"""

      elif self.p == True: 
        self.ei ="""else: 

                print "The input """+self.ii+""" is not string. I know it should not be string. However, the input number has to have string type... sorry"  # For debug purpose
                return False, 's'"""
      else:
        print "WHY YOU CHOOSE AN INPUT WHILE YOU DO NOT TELL ME THE TYPE!! I AM NOT SMART... BECAUSE OF THAT I AM GOING TO CRY BY STOPING THE TOOL AND CRASH"
        sys.exit()
    else:
      self.ei = ''



    if self.jj != '':
      if self.nn == True:
        if self.oo == True:
          self.ej ="""  except ValueError:

                print "the input is not real number (can not be converted to a numbder) !!"
                return False, 'n'"""

        else:
          self.ej ="""  except ValueError:

                print "the input is not real number (can not be converted to a numbder) !!"
                return False, 'n'"""

      elif self.oo == True:
        self.ei ="""  except ValueError:

                print "the input is not real number (can not be converted to a numbder) !!"
                return False, 'n'"""


      elif self.pp == True: 
        self.ej ="""except: 

                print "The input """+self.ii+""" is not string. I know it should not be string. However, the input number has to have string type... sorry"  # For debug purpose
                return False, 's'"""
      else:
        print "WHY YOU CHOOSE AN INPUT WHILE YOU DO NOT TELL ME THE TYPE!! I AM NOT SMART... BECAUSE OF THAT I AM GOING TO CRY BY STOPING THE TOOL AND CRASH"
        sys.exit()
    else:
      self.ej = ''



    if self.kk != '':
      if self.nnn == True:
        if self.ooo == True:
          self.ek ="""  except ValueError:

                print "the input is not real number (can not be converted to a numbder) !!"
                return False, 'n'"""


        else:
          self.ej ="""  except ValueError:

                print "the input is not real number (can not be converted to a numbder) !!"
                return False, 'n'"""


      elif self.ooo == True:
        self.ek ="""  except ValueError:

                print "the input is not real number (can not be converted to a numbder) !!"
                return False, 'n'"""

      elif self.ppp == True: 
        self.ek ="""else: 

                print "The input """+self.ii+""" is not string. I know it should not be string. However, the input number has to have string type... sorry"  # For debug purpose
                return False, 's'"""
      else:
        print "WHY YOU CHOOSE AN INPUT WHILE YOU DO NOT TELL ME THE TYPE!! I AM NOT SMART... BECAUSE OF THAT I AM GOING TO CRY BY STOPING THE TOOL AND CRASH"
        sys.exit()
    else:
      self.ek = ''



    if self.ll != '':
      if self.nnnn == True:
        if self.oooo == True:
          self.el ="""  except ValueError:

                print "the input is not real number (can not be converted to a numbder) !!"
                return False, 'n'"""


        else:
          self.el ="""  except ValueError:

                print "the input is not real number (can not be converted to a numbder) !!"
                return False, 'n'"""


      elif self.oooo == True:
        self.el ="""  except ValueError:

                print "the input is not real number (can not be converted to a numbder) !!"
                return False, 'n'"""


      elif self.pppp == True: 
        self.el ="""else: 

                print "The input """+self.ii+""" is not string. I know it should not be string. However, the input number has to have string type... sorry"  # For debug purpose
                return False, 's'"""
      else:
        print "WHY YOU CHOOSE AN INPUT WHILE YOU DO NOT TELL ME THE TYPE!! I AM NOT SMART... BECAUSE OF THAT I AM GOING TO CRY BY STOPING THE TOOL AND CRASH"
        sys.exit()
    else:
      self.el = ''



    if self.mm != '':
      if self.nnnnn == True:
        if self.ooooo == True:
          self.em ="""except ValueError:

                print "the input is not real number (can not be converted to a numbder) !!"
                return False, 'n'"""

        else:
          self.em ="""  except ValueError:

                print "the input is not real number (can not be converted to a numbder) !!"
                return False, 'n'"""


      elif self.ooooo == True:
        self.el ="""  except ValueError:

                print "the input is not real number (can not be converted to a numbder) !!"
                return False, 'n'"""


      elif self.ppppp == True: 
        self.em ="""else: 

                print "The input """+self.ii+""" is not string. I know it should not be string. However, the input number has to have string type... sorry"  # For debug purpose
                return False, 's'"""
      else:
        print "WHY YOU CHOOSE AN INPUT WHILE YOU DO NOT TELL ME THE TYPE!! I AM NOT SMART... BECAUSE OF THAT I AM GOING TO CRY BY STOPING THE TOOL AND CRASH"
        sys.exit()
    else:
      self.el = ''

  def finalscpi(self):    # to adjust the final scpi output (in case of an innput or not)

    if self.ii != '':
      self.ci = "'"+self.i+"' + "+self.si
    else:
      self.ci = "'"+self.i+"'"
    
    if self.jj != '':
      self.cj = "'"+self.j+"' + "+self.sj
    else:
      self.cj = "'"+self.j+"'"

    if self.kk != '':
      self.ck = "'"+self.k+"' + "+self.sk
    else:
      self.ck = "'"+self.k+"'"

    if self.ll != '':
      self.cl = "'"+self.l+"' + "+self.sl
    else:
      self.cl = "'"+self.l+"'"

    if self.mm != '':
      self.cm = "'"+self.m+"' + "+self.sm
    else:
      self.cm = "'"+self.m+"'"

  def scpicomment(self):    # for SCPI comment in the begining of the module doc

    if self.ii != '':
      self.ai = "'"+self.i+"' <"+self.ii+">"
    else:
      self.ai = "'"+self.i+"'"

    if self.jj != '':
      self.aj = "'"+self.j+"' <"+self.jj+">"
    else:
      self.aj = "'"+self.j+"'"

    if self.kk != '':
      self.ak = "'"+self.k+"' <"+self.kk+">"
    else:
      self.ak = "'"+self.k+"'"

    if self.ll != '':
      self.al = "'"+self.l+"' <"+self.ll+">"
    else:
      self.al = "'"+self.l+"'"

    if self.mm != '':
      self.am = "'"+self.m+"' <"+self.mm+">"
    else:
      self.am = "'"+self.m+"'"

  def selfinit(self): # Here, we add "self.xxx" in the "def __init__(self)" for inputs

    self.selfness()

    if self.ii != '':
      self.ti = self.si+" = "+self.ii
    else:
      self.ti = ''

    if self.jj != '':
      self.tj = self.sj+" = "+self.jj
    else:
      self.tj = ''

    if self.kk != '':
      self.tk = self.sk+" = "+self.kk
    else:
      self.tk = ''

    if self.ll != '':
      self.tl = self.sl+" = "+self.ll
    else:
      self.tl = ''

    if self.mm != '':
      self.tm = self.sm+" = "+self.mm
    else:
      self.tm = ''
    

  def repl(self):

    pdb.set_trace()
    self.dafultinput()
    self.selfness()
    self.basicinputcheck()
    self.finalscpi()
    self.scpicomment()
    self.selfinit()

    self.replace_dic = {
    'module_name': self.a,
    'module_person': self.b,
    'module_date' : self.timenow,
    'module_goal': self.c,
    'module_device_one': "'"+self.d+"'",
    'module_device_two': "'"+self.e+"'",
    'module_device_three': "'"+self.f+"'",
    'module_device_four': "'"+self.g+"'",
    'module_device_five': "'"+self.h+"'",
    'mdone_scpi': self.ai,
    'mdtwo_scpi': self.aj,
    'mdthree_scpi': self.ak,
    'mdfour_scpi': self.al,
    'mdfive_scpi': self.am,
    'firstinput' : self.iiii,
    'secondinput' : self.jjjj,
    'thirdinput' : self.kkkk,
    'forthinput' : self.llll,
    'fifthinput' : self.mmmm,
    '#selfone' : self.ti,
    '#selftwo' : self.tj,
    '#selfthree' : self.tk,
    '#selffour' : self.tl,
    '#selffive' : self.tm,
    'mdo_scpi_input' : self.ci,
    'mdt_scpi_input' : self.cj,
    'mdt_scpi_input' : self.ck,
    'mdf_scpi_input' : self.cl,
    'mdfi_scpi_input' : self.cm,
    '#first_check_start' : self.bi,
    '#second_check_start' : self.bj,
    '#third_check_start' : self.bk,
    '#forth_check_start' : self.bl,
    '#fifth_check_start' : self.bm,
    '#first_check_end' : self.ei,
    '#second_check_end' : self.ej,
    '#third_check_end' : self.ek,
    '#forth_check_end' : self.el,
    '#fifth_check_end' : self.em}


    if self.getset == True:
      self.replace_dic_one = {
      'nameofclass' : self.name}
       
    else:
      self.replace_dic_one = {
      'nameofclass' : self.name,
      'transaction': 'write',
      'return result[2]' : 'print "It works !!"\n           return True'}

  def runreplacment(self):

    self.readnewfile()
    self.repl()
    self.reading = self.replacing_function(self.reading, self.replace_dic )
    self.reading = self.replacing_function(self.reading, self.replace_dic_one)

  def applying(self):

    self.runreplacment()
    fileout = open('../gpib_commands/'+self.name+'.py', 'w')
    fileout.write(self.reading)
    fileout.close()


      

























