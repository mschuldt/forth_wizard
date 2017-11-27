#!/usr/bin/env python3

from distutils.core import setup, Extension
import sys

assert not sys.version_info.major < 3, 'The forth wizard requires python3'

v='1.2'

setup(name='forthwiz',
      packages=['forthwiz'],
      version=v,
      description='Finds optimal forth code sequences for stack transformations',
      url='https://github.com/mschuldt/forth_wizard',
      download_url='https://github.com/mschuldt/forth_wizard/archive/{}.tar.gz'.format(v),
      author='Michael Schuldt',
      author_email='mbschuldt@gmail.com',
      ext_modules=[Extension('chuckmoore', ['forthwiz.c'] )],
      scripts=['test.py', 'solver.c'])
