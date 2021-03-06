# vtkxml-builder

[![Build Status](https://travis-ci.org/glesica/vtkxml-builder.png?branch=master)](https://travis-ci.org/glesica/vtkxml-builder)

## Author

George Lesica <george@lesica.com>

## Description

A Python module for constructing VTK XML files for use with
ParaView and other data visualization software.

The code was inspired by
<https://github.com/cfinch/Shocksolution_Examples/blob/master/Visualization/vtktools.py>
though it has been completely rewritten.

## Documentation

The documentation can be compiled by entering the "docs" directory and issuing
the following:

    make html

This will build the documentation in a directory called "build".

Documentation can also be found online at
https://vtkxml-builder.readthedocs.org/en/latest/

## Tests

Right now there are only a few doctests designed to catch major bugs. They can
be run with Nose:

    nosetests --with-doctest
