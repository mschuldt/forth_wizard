#!/usr/bin/env python3

from distutils.core import setup, Extension
import sys

version = '2.2' # also change in forthwiz.py

assert not sys.version_info.major < 3, 'The forth wizard requires python3'

setup(name='forthwiz',
      packages=['forthwiz'],
      version=version,
      description='Finds optimal forth code sequences for stack transformations',
      url='https://github.com/mschuldt/forth_wizard',
      download_url='https://github.com/mschuldt/forth_wizard/archive/{}.tar.gz'.format(version),
      author='Michael Schuldt',
      author_email='mbschuldt@gmail.com',
      ext_modules=[Extension('chuckmoore', ['forthwiz.c'] )],
      scripts=['test.py', 'solver.c'])
