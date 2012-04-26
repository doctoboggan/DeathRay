=========> Information:
DeathRay is an application to display and control
radiation experiments in real time. It was built for
the 2012 Senior Design Project at Vanderbilt University.

There are pre-built packages intended for those who don't want to
modify anything, and then there is the source code and package-scripts
intended for those who need more control.

To rebuild the packaged software after you have made modifications run
either the wincompiler.bat or maccompiler.sh. The produced package
should be able to be distributed to users with no complications.


=========> For End users:
To run the program, you only need to download the binary zip file for your system:
----> Windows: 
1) download DeathRaywin.zip from binries_files folder.
2) unzip (extract) it anywhere you like.
3) double click on deathray.exe
4) that is it!!

----> Macintosh:
1) Download DeathRaymac.zip from binries_files folder.
2) unzip (extract) to have a deathray.app application.
3) double click on it
4) that is it!!

----> Linux:
1) There are no pre-packaged binaries for Linux.
   You should acquire the required packages and run from source

----> other OS:
Follow the developer method below.

=========> For developers:
===> What you need to run this application (pre-requirements):
----OS X and Linux:
Python (Most likely already installed on your system)
Qt (http://qt.nokia.com/products/)
PyQt (http://www.riverbankcomputing.co.uk/software/pyqt/download)
PyQwt (http://pyqwt.sourceforge.net/home.html)
Numpy (http://numpy.scipy.org/)
data_acquisition  (installed with this program)


----Linux (easy installation):
search for:
Python2.7.x
Qt
PyQt
PyQwt
Numpy
in your package manager
Then, install them from there.

----Windows:
You need the same programs as above, but you need to be using Python 2.6 instead.
The PyQwt developers nicely provide all the packages you need.
First download Qt from nokia (http://qt.nokia.com/products/) then head to the
PyQwt site (http://pyqwt.sourceforge.net/download.html) and download their version
of Python (2.6), Numpy (1.3.0), PyQt, and PyQwt. If you download all of the packages
from that website, everything should work nicely together. Make sure you install 
them in order. It is most likely possible to run DeathRay with Python 2.7 and
later versions of all the software, but you may need to do some compiling on
your own.

===> Installation (using the terminal or Windows command line):
This must be done before DeathRay can run properly.
cd into DeathRay/Source folder
sudo ./DeathRay.py install

===> To launch:
simply run DeathRay.py with no arguments via terminal 
(or just double click the file if you do not want to see the logs). 
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

===========> Authors are:
Nadiah Husseini Zainol Abidin
Anas Alfuntukh
Jack Minardi

============> Project Sponsor:
ISDE (http://www.isde.vanderbilt.edu/)
