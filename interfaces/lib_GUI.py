#!/usr/bin/env python

'''
Library for GUI code
'''

from distutils.core import setup

setup(name='DeathRay',
      version='0.15',
      description='A GUI files',
      author='Jack Minardi, Nadiah Husseini Zainol Abidin and Anas Khalid Alfuntukh',
      author_email='jack@minardi.org, nadiah.husseini.zainol.abidin@vanderbilt.edu and anas.alfuntukh@vanderbilt.edu',
      packages=['GUIfiles'],
      package_dir={'GUIfiles': './GUIfiles'},   # Here, the path only works when the user run setup file. If the user tries to install it from here, it will fail.
      requires=['data_acquisition','numpy'],
      provides=['DeathRay']
     )


