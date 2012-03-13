"""
Distutils setup script.
Created on Mar 12, 2012
@author: Anas Alfuntukh
"""

from distutils.core import setup

setup(name='DeathRay',
      version='0.12',
      description='A GUI program with its plugin for controlling and analyzing FPGA and Gpib devices',
      author='Jack Minardi, Nadiah Husseini Zainol Abidin and Anas Khalid Alfuntukh',
      author_email='jack@minardi.org, nadiah.husseini.zainol.abidin@vanderbilt.edu and anas.alfuntukh@vanderbilt.edu',
      packages=['DRm'],
      package_dir={'DRm': 'DRm'},
      requires=['data_acquisition','numpy'],
      provides=['Deathray']
     )
