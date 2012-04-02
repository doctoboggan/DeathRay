# THie file suppose to able to add new modules (not edit them).


import shutil 
import datetime
import re

# delete "result"
# delete all "info"s
# add "input required" for each device.
# add "kind of input" for each device. 

class add():

  def __init__(self, checkk = True , nameofnewmdoule = 'dafult', module_name = '', module_person = '', module_goal = '', module_device_one = '', module_device_two = '', module_device_three = '', module_device_four = '', module_device_five = '', module_device_one_scpi = '', module_device_two_scpi = '', module_device_three_scpi = '', module_device_four_scpi = '', module_device_five_scpi = '', module_device_one_scpi_input = '', module_device_two_scpi_input = '', module_device_three_scpi_input = '', module_device_four_scpi_input = '', module_device_five_scpi_input = '', firstint = False, secondint = False, thirdint = False, fourthint = False, fifthint = False, firstf = False, secondf = False, thirdf = False, fourthf = False, fifthf = False, firststr = True, secondstr = True, thirdstr = True, forthstr = True, fifthstr = True, oneex = '', secondex = ''. threeex = '', fourex = '', fiveex = ''):

    self.name = nameofnewmdoule
    self.replace_dic = {}
    self.replace_dic_one = {}
    self.replace_dic_sone = {}
    self.replace_dic_stwo = {}
    self.replace_dic_sthree = {}
    self.replace_dic_sfour = {}
    self.replace_dic_sfive = {}
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
    self.i = module_device_one_scpi   # here, we have to divide it if it contains extra info (channels,...)
    self.j = module_device_two_scpi
    self.k = module_device_three_scpi
    self.l = module_device_four_scpi
    self.m = module_device_five_scpi
    self.ii = module_device_one_scpi_input
    self.jj = module_device_two_scpi_input
    self.kk = module_device_three_scpi_input
    self.ll = module_device_four_scpi_input
    self.mm = module_device_five_scpi_input
    self.iii = oneex
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
    self.n = firstint
    self.nn = secondint
    self.nnn = thirdint
    self.nnnn = forthint
    self.nnnnn = fifthint
    self.o = firstf
    self.oo = secondf
    self.ooo = thirdf
    self.oooo = forthf
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

  def checkscpi(self):
    
    # uselss for now

    try:
      self.i.split()[1]
      self.listing_scpi_inputs[0] = '1'
      self.inputs[0] = self.i.split()[1]
    except IndexError:
      pass

  
    try:
      self.j.split()[1]
      self.listing_scpi_inputs[1] = '1'
      self.inputs[1] = self.j.split()[1]
    except IndexError:
      pass

    try:
      self.k.split()[1]
      self.listing_scpi_inputs[2] = '1'
      self.inputs[2] = self.k.split()[1]
    except IndexError:
      pass

    try:
      self.l.split()[1]
      self.listing_scpi_inputs[3] = '1'
      self.inputs[3] = self.l.split()[1]
    except IndexError:
      pass

    try:
      self.m.split()[1]
      self.listing_scpi_inputs[4] = '1'
      self.inputs[4] = self.m.split()[1]
    except IndexError:
      pass

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
    if self.jj = '':
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

  def selfness (self):

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

    if self.ii != '':
      if self.n == True:
        if self.o == True:
          self.bi = "if type("+self.si+") is int or type("+self.si+") is float:\n  (one tap) try:\n     "+self.si+" = float("+self.si+")"
        else:
          self.bi = "if type("+self.si+") is int:\n  (one tap) try:\n     "+self.sj+" = int("+self.sj+")"
      elif self.o == True:
        self.bi = "if type("+self.si+") is float:\n  (one tap) try:\n     "+self.si+" = float("+self.si+")"
      elif self.p == True: 
        self.bi = "if type("+self.si+") is str:
      else:
        print "WHY YOU CHOOSE AN INPUT WHILE YOU DO NOT TELL ME THE TYPE!! I AM NOT SMART... BECAUSE OF THAT I AM GOING TO CRY BY STOPING THE TOOL AND CRASH"
        break
    else
      self.bi = ''



    if self.jj != '':
      if self.nn == True:
        if self.oo == True:
          self.bj = "if type("+self.sj+") is int or type("+self.sj+") is float:\n  (one tap) try:\n     "+self.sj+" = float("+self.sj+")"
        else:
          self.bj = "if type("+self.si+") is int:\n  (one tap) try:\n     "+self.sj+" = int("+self.sj+")"
      elif self.oo == True:
        self.bi = "if type("+self.si+") is float:\n  (one tap) try:\n     "+self.sj+" = float("+self.sj+")"
      elif self.pp == True: 
        self.bj = "if type("+self.sj+") is str:
      else:
        print "WHY YOU CHOOSE AN INPUT WHILE YOU DO NOT TELL ME THE TYPE!! I AM NOT SMART... BECAUSE OF THAT I AM GOING TO CRY BY STOPING THE TOOL AND CRASH"
        break
    else:
      self.bj = ''



    if self.kk != ''
      if self.nnn == True:
        if self.ooo == True:
          self.bk = "if type("+self.sk+") is int or type("+self.sk+") is float:\n  (one tap) try:\n     "+self.sk+" = float("+self.sk+")"
        else:
          self.bj = "if type("+self.sk+") is int:\n  (one tap) try:\n     "+self.sk+" = int("+self.sk+")"
      elif self.ooo == True:
        self.bk = "if type("+self.sk+") is float:\n  (one tap) try:\n     "+self.sk+" = float("+self.sk+")"
      elif self.ppp == True: 
        self.bk = "if type("+self.sk+") is str:
      else:
        print "WHY YOU CHOOSE AN INPUT WHILE YOU DO NOT TELL ME THE TYPE!! I AM NOT SMART... BECAUSE OF THAT I AM GOING TO CRY BY STOPING THE TOOL AND CRASH"
        break
    else:
      self.bk = ''



    if self.ll != '':
      if self.nnnn == True:
        if self.oooo == True:
          self.bl = "if type("+self.sl+") is int or type("+self.sl+") is float:\n  (one tap) try:\n     "+self.sl+" = float("+self.sl+")"
        else:
          self.bl = "if type("+self.sl+") is int:\n  (one tap) try:\n     "+self.sj+" = int("+self.sl+")"
      elif self.oooo == True:
        self.bl = "if type("+self.sl+") is float:\n  (one tap) try:\n     "+self.sl+" = float("+self.sl+")"
      elif self.pppp == True: 
        self.bl = "if type("+self.sl+") is str:
      else:
        print "WHY YOU CHOOSE AN INPUT WHILE YOU DO NOT TELL ME THE TYPE!! I AM NOT SMART... BECAUSE OF THAT I AM GOING TO CRY BY STOPING THE TOOL AND CRASH"
        break
    else:
      self.bl = ''



    if self.mm != '':
      if self.nnnnn == True:
        if self.ooooo == True:
          self.bm = "if type("+self.sm+") is int or type("+self.sm+") is float:\n  (one tap) try:\n     "+self.sm+" = float("+self.sm+")"
        else:
          self.bm = "if type("+self.sm+") is int:\n  (one tap) try:\n     "+self.sj+" = int("+self.sm+")"
      elif self.ooooo == True:
        self.bl = "if type("+self.sm+") is float:\n  (one tap) try:\n     "+self.sm+" = float("+self.sm+")"
      elif self.ppppp == True: 
        self.bm = "if type("+self.sm+") is str:
      else:
        print "WHY YOU CHOOSE AN INPUT WHILE YOU DO NOT TELL ME THE TYPE!! I AM NOT SMART... BECAUSE OF THAT I AM GOING TO CRY BY STOPING THE TOOL AND CRASH"
        break
    else:
      self.bm = ''


#----------------00000000000000000000000000000000000000000000------------------
#----------------00000000000000000000000000000000000000000000------------------

    if self.ii != '':
      if self.n == True:
        if self.o == True:
          self.ei = """            except ValueError:

              print "the input is not real number (can not be converted to a numbder) !!"

              return False, 'n'"""


        else:
          self.ei = """            except ValueError:

              print "the input is not real number (can not be converted to a numbder) !!"

              return False, 'n'"""

      elif self.o == True:
        self.ei = """            except ValueError:

              print "the input is not real number (can not be converted to a numbder) !!"

              return False, 'n'"""
      elif self.p == True: 
        self.ei ="""            print "The input"""+self.ii+""" is not string. I know it should not be string. However, the input number has to have string type... sorry"  # For debug purpose
            return False, 's'"""
      else:
        print "WHY YOU CHOOSE AN INPUT WHILE YOU DO NOT TELL ME THE TYPE!! I AM NOT SMART... BECAUSE OF THAT I AM GOING TO CRY BY STOPING THE TOOL AND CRASH"
        break
    else
      self.ei = ''



    if self.jj != '':
      if self.nn == True:
        if self.oo == True:
          self.ej ="""            except ValueError:

              print "the input is not real number (can not be converted to a numbder) !!"

              return False, 'n'"""
        else:
          self.ej ="""            except ValueError:

              print "the input is not real number (can not be converted to a numbder) !!"

              return False, 'n'"""
      elif self.oo == True:
        self.ei ="""            except ValueError:

              print "the input is not real number (can not be converted to a numbder) !!"

              return False, 'n'"""
      elif self.pp == True: 
        self.ej ="""            print "The input"""+self.jj+""" is not string. I know it should not be string. However, the input number has to have string type... sorry"  # For debug purpose
            return False, 's'"""
      else:
        print "WHY YOU CHOOSE AN INPUT WHILE YOU DO NOT TELL ME THE TYPE!! I AM NOT SMART... BECAUSE OF THAT I AM GOING TO CRY BY STOPING THE TOOL AND CRASH"
        break
    else:
      self.ej = ''



    if self.kk != ''
      if self.nnn == True:
        if self.ooo == True:
          self.ek ="""            except ValueError:

              print "the input is not real number (can not be converted to a numbder) !!"

              return False, 'n'"""
        else:
          self.ej ="""            except ValueError:

              print "the input is not real number (can not be converted to a numbder) !!"

              return False, 'n'"""
      elif self.ooo == True:
        self.ek ="""            except ValueError:

              print "the input is not real number (can not be converted to a numbder) !!"

              return False, 'n'"""
      elif self.ppp == True: 
        self.ek ="""            print "The input"""+self.kk+""" is not string. I know it should not be string. However, the input number has to have string type... sorry"  # For debug purpose
            return False, 's'"""
      else:
        print "WHY YOU CHOOSE AN INPUT WHILE YOU DO NOT TELL ME THE TYPE!! I AM NOT SMART... BECAUSE OF THAT I AM GOING TO CRY BY STOPING THE TOOL AND CRASH"
        break
    else:
      self.ek = ''



    if self.ll != '':
      if self.nnnn == True:
        if self.oooo == True:
          self.el ="""            except ValueError:

              print "the input is not real number (can not be converted to a numbder) !!"

              return False, 'n'"""
        else:
          self.el ="""            except ValueError:

              print "the input is not real number (can not be converted to a numbder) !!"

              return False, 'n'"""
      elif self.oooo == True:
        self.el ="""            except ValueError:

              print "the input is not real number (can not be converted to a numbder) !!"

              return False, 'n'"""
      elif self.pppp == True: 
        self.el ="""            print "The input"""+self.ll+""" is not string. I know it should not be string. However, the input number has to have string type... sorry"  # For debug purpose
            return False, 's'"""
      else:
        print "WHY YOU CHOOSE AN INPUT WHILE YOU DO NOT TELL ME THE TYPE!! I AM NOT SMART... BECAUSE OF THAT I AM GOING TO CRY BY STOPING THE TOOL AND CRASH"
        break
    else:
      self.el = ''



    if self.mm != '':
      if self.nnnnn == True:
        if self.ooooo == True:
          self.em ="""            except ValueError:

              print "the input is not real number (can not be converted to a numbder) !!"

              return False, 'n'"""
        else:
          self.em ="""            except ValueError:

              print "the input is not real number (can not be converted to a numbder) !!"

              return False, 'n'"""
      elif self.ooooo == True:
        self.el ="""            except ValueError:

              print "the input is not real number (can not be converted to a numbder) !!"

              return False, 'n'"""
      elif self.ppppp == True: 
        self.em ="""            print "The input"""+self.mm+""" is not string. I know it should not be string. However, the input number has to have string type... sorry"  # For debug purpose
            return False, 's'"""
      else:
        print "WHY YOU CHOOSE AN INPUT WHILE YOU DO NOT TELL ME THE TYPE!! I AM NOT SMART... BECAUSE OF THAT I AM GOING TO CRY BY STOPING THE TOOL AND CRASH"
        break
    else:
      self.el = ''



  def repl(self):

    self.dafultinput()
    self.selfness()
    self.basicinputcheck()

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
    'module_device_one_scpi': "'"+self.i+"'",
    'module_device_two_scpi': "'"+self.j+"'",
    'module_device_three_scpi': "'"+self.k+"'",
    'module_device_four_scpi': "'"+self.l+"'",
    'module_device_five_scpi': "'"+self.m+"'",
    'firstinput' : self.iiii,
    'secondinput' : self.jjjj,
    'thirdinput' : self.kkkk,
    'forthinput' : self.llll,
    'fifthinput' : self.mmmm,
    '#selfone' : self.si,
    '#selftwo' : self.sj,
    '#selfthree' : self.sk,
    '#selffour' : self.sl,
    '#selffive' : self.sm,
    'module_device_one_scpi_input' : "'"+self.ii+' "+'+self.si,
    'module_device_two_scpi_input' : "'"+self.jj+' "+'+self.sj,
    'module_device_three_scpi_input' : "+"self.kk+' "'+self.sk,
    'module_device_four_scpi_input' : "+"self.ll+' "'+self.sl,
    'module_device_one_scpi_input' : "+"self.mm+' "'+self.sm,
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

      
    '''
    try: 
      self.replace_dic_sone = {
      'main_scpi_one' : "'"+self.i.split()[0]+"'"}
    except:
       self.replace_dic_sone = {
      'main_scpi_one' : "'"+self.i+"'"}   # because self.i in this case is just empty string.
    try: 
      self.replace_dic_stwo = {
      'main_scpi_two' : "'"+self.j.split()[0]+"'"}
    except:
      self.replace_dic_stwo = {
      'main_scpi_two' : "'"+self.j+"'"}
    try:
      self.replace_dic_sthree = {
      'main_scpi_three' : "'"+self.k.split()[0]+"'"}
    except:
      self.replace_dic_sthree = {
      'main_scpi_self' : "'"+self.k+"'"}
    try:
      self.replace_dic_sfour = {
      'main_scpi_four' : "'"+self.l.split()[0]+"'"}
    except:
      self.replace_dic_sfour = {
      'main_scpi_four' : "'"+self.l+"'"}
    try:
      self.replace_dic_sfive = {
      'main_scpi_five' : "'"+self.m.split()[0]+"'"}
    except:
      self.replace_dic_sfive = {
      'main_scpi_five' : "'"+self.m+"'"}
      '''


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


      

























