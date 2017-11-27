#!/usr/bin/env python3

from distutils.core import setup, Extension

setup(name='forthwiz',
      packages=['forthwiz'],
      version='1.0',
      description='Finds optimal forth code sequences for stack transformations',
      url='https://github.com/mschuldt/forth_wizard',
      download_url='https://github.com/mschuldt/forth_wizard/archive/1.0.tar.gz',
      author='Michael Schuldt',
      author_email='mbschuldt@gmail.com',
      ext_modules=[Extension('chuckmoore', ['forthwiz.c'])])
