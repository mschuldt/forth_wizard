#!/usr/bin/env python3

from distutils.core import setup, Extension

setup(name='forthwiz',
      packages=['forthwiz'],
      version='1.0',
      author='Michael Schuldt',
      author_email='mbschuldt@gmail.com',
      ext_modules=[Extension('chuckmoore', ['forthwiz.c'])])
