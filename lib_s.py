"""
Distutils setup script.
Created on Mar 12, 2012
@author: Anas Alfuntukh
"""

from distutils.core import setup

setup(name='DeathRay',
      version='0.1',
      description='A GUI program with its plugin for controlling and analyzing FPGA and Gpib devices',
      author='Jack Minardi, Nadiah Husseini Zainol Abidin and Anas Khalid Alfuntukh',
      author_email='jack@minardi.org, nadiah.husseini.zainol.abidin@vanderbilt.edu and anas.alfuntukh@vanderbilt.edu',
      packages=['DRscripts'],
      package_dir={'DRscripts': 'DRscripts'},
      requires=['data_acquisition','numpy'],
      provides=['DeathRay']
     )
