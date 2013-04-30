#!/usr/bin/env python

from distutils.core import setup

ver = open('VERSION', 'r').read().strip()

setup(
    name='vtkxml-builder',
    version=ver,
    description='VTK XML file writer',
    author='George Lesica',
    author_email='george@lesica.com',
    url='http://www.github.com/glesica/vtkxml-builder',
    packages=['vtkxml'],
)
