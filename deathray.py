#!/usr/bin/env python

import sys, os

helpmessage = '''DeathRay is an application to display and control
radiation experiments in real time.

To launch, simply run this program with no arguments. 
The optional arguments are:

  install:
    Installs the gpib_commands and pythonlabtools modules on your system.
    This needs to be run before you can run the program.
  uninstall:
    Removes the gpib_commands and pythonlabtoolds modules from your system.
  reload:
    Searches the fpga_scripts folder for new files and refreshes the list
    of scripts.
  help:
    Prints this message, but you already knew that.

For more information, see the README in this folder, the README in the
fpga_scripts folder or the documentation in the docs folder.
'''


if len(sys.argv) > 2:
  print 'usage: '+sys.argv[0]+' [install|uninstall|reload|help]'

if len(sys.argv) is 1:
  execfile('DeviceControl.py')

if len(sys.argv) is 2:
  arg = sys.argv[1]
  if arg == 'install':
    execfile('./utils/buildInit.py')
    execfile('./utils/reloadFPGA.py')
    os.system('python ./setup/lib_m.py install --record build_lib_m.txt')
    os.system(' python ./setup/pythonlabtools/lib_pythonlabtools.py install\
        --record build_lib_pythonlabtools.txt')

  if arg == 'uninstall':
    os.system('cat build_lib_m.txt | xargs rm -rf')
    os.system('rm build_lib_m.txt')
    os.system('cat build_lib_pythonlabtools.txt | xargs rm -rf')
    os.system('rm build_lib_pythonlabtools.txt')
    os.system('rm -r build')
    print 'uninstall successful'

  if arg == 'reload':
    execfile('./utils/reloadFPGA.py')
    print 'fpga scripts reloaded'
    
  if 'help' in arg:
    print helpmessage

