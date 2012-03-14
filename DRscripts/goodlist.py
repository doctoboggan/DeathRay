# Name: list module.
# Made by: Anas Alfuntukh
# Date: 3/4/12
# Goal: list module for mulitaple purposes. Specificlly, it focus in orginize names of files on a folder.
# Modifiers:  None (for now) 
# ------------- Note: ---------
# --> This is not module as itself. 
# --> It contains several functions.These functions can be used in other classes.
# --> Please, If you are going to use this file in other class within *DeathRay* program, please mention that in the dependancy section. 
# -----------------------------
# Dependancy: 1) checkinit.py
# Resullt: depned in each function.


import os     # It will be used in upcoming functions.

class goodlist(): # do not forget, if you are going to change the name of class, change too in the checkinit.py file.!!

  '''
  --> This class is for listing.
  --> This class requires "os" library. 
  '''

  def __init__(self, direct = '../DeathRay/DRmodules'):   # to accessble from the installed module. (works on linux so far...)
    '''
    Requirement: (direct path)
    Ex: goodlist.goodlist()
    Note: There is no need to feed it at all. 
    ____________
    --> Ask for path direction to list it. THE PATH ALAWYS IS "../modules". So, do not change it. 
    --> Defind some empty list, which will be used in the functions.
    --> Make these lists global to make them accessable for external purpose.
    --> The rightDevice list has to be there. It responsibles for flexibility of this file. Because this file is not related to any device, The list is going to be empty.
    '''


    self.direct = direct
    self.lis = [] 
    self.lise = []
    self.lisee = []
    self.finallist = []
    self.tolist = []
    self.rightDevice = ['']

  def scan(self):

    '''
    --> This function will scan the files in the given folder
    --> "self.lis" is a list. It has the name of files in the given path.
    '''

    for count in range(len(os.listdir(self.direct))):   # To count until reach the number of files in given path
      
      self.lis.append(count)    # creat the list (make it exist).
      print count       #debug
      self.lis[count] = os.listdir(self.direct)[count]    # take each file alone and store it in a list.
      print self.lis[count]   #debug

  def sep(self):

    '''
    --> This function will separate the name of file and its extension. 
    --> Ex: example.py ==> example and .py .
    --> The names of files will be in "self.lise" list.
    --> The extensions will be in "self.lisee" list.
    '''

    self.scan()   # call "self.scan()" to have "self.lis" list ready.
    for count in range(len(self.lis)):  # To count until reach the number of unites in "self.lis" list.
      print count   #debug
      self.lise.append(count)   # creat the list (make it exist).
      self.lisee.append(count)  # creat the list (make it exist).
      self.lise[count], self.lisee[count] = os.path.splitext(self.lis[count])   # Here, we spelt the names of files in: 1) only names. 2) only extensions.
      print self.lise[count]    #debug
      print self.lisee[count]   #debug
      

  def clee(self):

    '''
    --> This function's goal is make a list of only python files for the given path (folder).
    --> It will take both lists from "self.sep()". Then, it will only take the python files from these lists.
    --> The names of only python files will be in the "self.finallist"
    ''' 
    self.sep()  # call "self.sep()" to have both lists ready to be used.
    ncount = 0  # a counter. It will be used for counting the unites for "self.finallist" list.
    for count in range(len(self.lis)):   # To count until reach the number of unites in "self.lis" list (the real number of all files in the given path). 

        if self.lisee[count] == '.py':    # if we find a python file (by using the file extension).

          if self.lise[count] == '__init__':    # to make sure that, it does not read its self. Also, we can add any unwanted files here to be unscanned (for future purpose). {hidden tool}

            pass    # do nothing.

          else:   # for other files.
            self.finallist.append(ncount)   # creat the list (make it exist).
            self.finallist[ncount] = self.lise[count]   # take the name of the fileand store it in new list ("self.finallist").
            print ncount    #debug
            print count     #debug
            print self.finallist[ncount]   #debug
            ncount = ncount + 1   # prepare new place for upcoming new unite.

        else:   # if the file is not python extension.
          print "refused are here:"   #debug
          print count    #debug 
          print "next"    #debug
          pass

  def get(self):        # this is the one to run (do not worry about the others)

    '''
    --> This function is not that important (it was built for debug purpose).
    --> It give a quick result (not really).
    '''
    self.clee()   # call "self.clee()" to make "self.finallist" ready.
    print self.finallist  #debug
    return self.finallist #return the wanted list. 
        

  def together(self):     # The result of this function is to put the file kind and name of the file together 

    '''
    --> This function's goal is to put name of file and its extension together for one kind of ectension.
    --> The result will be in "self.tolist"list.
    ''' 
    self.sep()    # call "self.sep()" to have both lists ready to be used.
    ncount = 0    # a counter. It will be used for counting the unites for "self.tolist" list.
    for count in range(len(self.lis)):  # To count until reach the number of unites in "self.lis" list (the real number of all files in the given path).

        if self.lisee[count] == '.py':    # if the file is python file.
          self.tolist.append(ncount)    # creat the list (make it exist).
          self.tolist[ncount] = self.lise[count] + self.lisee[count]    # make the name and its ectension as one string and put as new unite in "self.tolist()"list.
          print ncount    #debug
          print count     #debug
          ncount = ncount + 1   # prepare new place for upcoming new unite.

        else:   # if the file is not python extension.
          print "refused are here:"   #debug
          print count    #debug 
          print "next"    #debug

    return  self.tolist   # return the new list to be used externally.


#Andrew Sternburg 
#Jeff kawppiln 
#listgood.list('/home/computer/DeathRay/modules').get()
# it works
# solve the bug (done). and improve the checkinit (not done) and speed up getIDN(done (but there is no must imporvement)). move the unnedded modules to script (done and add install way (done too)). and user arg standards (not done) 
# now, it alaways knows where the modules. There is no need to feed it. 
# I think now, there is new way of knowing the modules after we install them in the system. However, we will not use that way because it is not needed.
# The DeathRay folder must be in user folder (in linux, "/home/username/" to accessable from the installed module.

