DeathRay is an application to display and control
radiation experiments in real time. It was built for
the 2012 Senior Design Project at Vanderbilt University.

To launch, simply run deathray.py with no arguments. 
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
    Prints the help message

For more information, see the README in the fpga_scripts folder or
the documentation in the docs folder.


What you need to run this application:
Python (http://www.python.org/)
PyQt (http://www.riverbankcomputing.co.uk/software/pyqt/download)
PyQwt (http://pyqwt.sourceforge.net/home.html)
Numpy (http://numpy.scipy.org/)
data_acquisition  (installed with this program)
pyaudio (http://people.csail.mit.edu/hubert/pyaudio)


Authors are:
Nadiah Husseini Zainol Abidin
Anas Alfuntukh
Jack Minardi

Installation: 
sudo ./deathray.py install

Project Sponsor:
ISDE (http://www.isde.vanderbilt.edu/)
