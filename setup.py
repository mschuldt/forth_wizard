#!/usr/bin/env python3

from distutils.core import setup, Extension

setup(name='forthwiz',
      version='1.0',
      author='Michael Schuldt',
      author_email='mbschuldt@gmail.com',
      ext_modules=[Extension('forthwiz', ['forthwiz.c'])])
