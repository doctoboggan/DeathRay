DeathRay is an application to display and control
radiation experiments in real time. It was built for
the 2012 Senior Design Project at Vanderbilt University.

To launch, simply run deathray.py with no arguments. 
The optional arguments are:

  install:
    Installs the gpib_commands and pythonlabtools modules on your system.
    This needs to be run once before you can run the program.
  uninstall:
    Removes the gpib_commands and pythonlabtools modules from your system.
  reload:
    Searches the fpga_scripts folder for new files and refreshes the list
    of scripts.
  help:
    Prints the help message

For more information, see the README in the fpga_scripts folder or
the documentation in the docs folder.


What you need to run this application:
OS X and Linux:
Python (Most likely already installed on your system)
Qt (http://qt.nokia.com/products/)
PyQt (http://www.riverbankcomputing.co.uk/software/pyqt/download)
PyQwt (http://pyqwt.sourceforge.net/home.html)
Numpy (http://numpy.scipy.org/)
data_acquisition  (installed with this program)

Windows:
You need the same programs as above, but you need to be using Python 2.6 instead.
The PyQwt developers nicely provide all the packages you need.
First download Qt from nokia (http://qt.nokia.com/products/) then head to the
PyQwt site (http://pyqwt.sourceforge.net/download.html) and download their version
of Python (2.6), Numpy (1.3.0), PyQt, and PyQwt. If you download all of the packages
from that website, everything should work nicely together. Make sure you install 
them in order. It is most likely possible to run DeathRay with Python 2.7 and
later versions of all the software, but you may need to do some compiling on
your own.


Authors are:
Nadiah Husseini Zainol Abidin
Anas Alfuntukh
Jack Minardi

Installation: 
sudo ./deathray.py install

Project Sponsor:
ISDE (http://www.isde.vanderbilt.edu/)
