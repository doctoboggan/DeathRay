# THie file suppose to able to add new modules (not edit them).


import shutil 
import datetime
import re


class add():

  def __init__(self, checkk = True , nameofnewmdoule = 'dafult', module_name = '', module_person = '', module_goal = '', module_device_one = '', module_device_two = '', module_device_three = '', module_device_four = '', module_device_five = '', module_device_one_scpi = '', module_device_two_scpi = '', module_device_three_scpi = '', module_device_four_scpi = '', module_device_five_scpi = '', module_result = '', class_info = '', init_info = '', check_info = '', do_info = ''):

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
    self.n = module_result
    self.o = class_info
    self.p = init_info
    self.q = check_info
    self.r = do_info


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
  

  def repl(self):

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
    'module_device_one_scpi': self.i,
    'module_device_two_scpi': self.j,
    'module_device_three_scpi': self.k,
    'module_device_four_scpi': self.l,
    'module_device_five_scpi':self.m,
    'module_result': self.n,
    'class_info' : self.o,
    'init_info' : self.p,
    'check_info' : self.q,
    'do_info' : self.r}

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
    self.reading = self.replacing_function(self.reading, self.replace_dic_sone)
    self.reading = self.replacing_function(self.reading, self.replace_dic_stwo)
    self.reading = self.replacing_function(self.reading, self.replace_dic_sthree)
    self.reading = self.replacing_function(self.reading, self.replace_dic_sfour)
    self.reading = self.replacing_function(self.reading, self.replace_dic_sfive)

  def applying(self):

    self.runreplacment()
    fileout = open('../gpib_commands/'+self.name+'.py', 'w')
    fileout.write(self.reading)
    fileout.close()


      

























