## Welcome to HVAnalysis!
### Table of contents
* [Introduction](#introduction)
* [Setup](#setup)
* [Usage](#usage)

### Introduction
This is the codebase for the IRIS-HEP Fellowship project:
Data Reduction for the ProtoDUNE Detector Control System

### Setup
Check out the code:
```
$ ssh://git@gitlab.cern.ch:7999/ligerlac/HVAnalysis.git
$ cd HVAnalysis/
```
Create a virtual environment, activate it and install dependencies
```
$ python -m venv venv/
$ . venv/bin/activate
$ pip install -r requirements.txt
```

### Usage
Use the following command to make a plot of the resistance:
```
$ python HVAnalysis/make_resistance_plot.py --datelist 2018-09-14 --loglvl 1
```
If ```datelist``` is not specified, all data in the input folder will be considered.

### To-Dos
* Make separate plots of current, voltage, and resistance vs time for all of Run-1
* Make separate histograms for current, voltage, and resistance for all of Run-1