"""
Distutils setup script.
Created on Mar 12, 2012
@author: Anas Alfuntukh
"""

from distutils.core import setup

setup(name='DeathRay',
      version='0.20',
      description='interface library',
      author='Jack Minardi, Nadiah Husseini Zainol Abidin and Anas Khalid Alfuntukh',
      author_email='jack@minardi.org, nadiah.husseini.zainol.abidin@vanderbilt.edu and anas.alfuntukh@vanderbilt.edu',
      packages=['interfaces'],
      package_dir={'interfaces': './interfaces'},   # Here, the path only works when the user run setup file. If the user tries to install it from here, it will fail.
      requires=['data_acquisition','numpy'],
      provides=['DeathRay']
     )
