#!/usr/bin/env python3

from distutils.core import setup, Extension

setup(name='forthwiz',
      packages=['forthwiz'],
      version='1.1',
      description='Finds optimal forth code sequences for stack transformations',
      url='https://github.com/mschuldt/forth_wizard',
      download_url='https://github.com/mschuldt/forth_wizard/archive/1.1.tar.gz',
      author='Michael Schuldt',
      author_email='mbschuldt@gmail.com',
      ext_modules=[Extension('chuckmoore', ['forthwiz.c'] )],
      scripts=['test.py', 'solver.c'])
