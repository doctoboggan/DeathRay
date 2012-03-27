'''
Distutils setup class.

Created on Mar 19, 2010
@author: patend
'''

from distutils.core import setup

setup(name='pythonlabtools',
      version='20050805.1',
      description='Wrapper classes for control of laboratory equipment via GPIB and VXI-11',
      author='Marcus Mendenhall',
      author_email='marcus.h.mendenhall@Vanderbilt.Edu',
      packages=['data_acquisition'],
      package_dir={ 'data_acquisition': './interfaces/pythonlabtools/data_acquisition'},
      requires=['numeric'],
      provides=['data_acquisition']
     )
