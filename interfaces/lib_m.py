"""
Distutils setup script.
Created on Mar 12, 2012
@author: Anas Alfuntukh
"""

from distutils.core import setup

setup(name='DeathRay',
      version='0.16',
      description='A GUI program with its plugin for controlling and analyzing FPGA and Gpib devices',
      author='Jack Minardi, Nadiah Husseini Zainol Abidin and Anas Khalid Alfuntukh',
      author_email='jack@minardi.org, nadiah.husseini.zainol.abidin@vanderbilt.edu and anas.alfuntukh@vanderbilt.edu',
      packages=['gpib_commands'],
      package_dir={'gpib_commands': './gpib_commands'},   # Here, the path only works when the user run setup file. If the user tries to install it from here, it will fail.
      requires=['data_acquisition','numpy'],
      provides=['DeathRay']
     )
