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
Use the following commands to make a plot of the resistance:
```
(one day)
$ python HVAnalysis/start_main.py --datelist 2018-09-19 --loglvl 1

(period 2018-09-19 | 2018-10-04) 
$ python HVAnalysis/start_main.py --datelist 2018-09-19 2018-09-20 2018-09-21 2018-09-22 2018-09-23 2018-09-24 2018-09-25 2018-09-26 2018-09-27 2018-09-28 2018-09-29 2018-09-30 2018-10-01 2018-10-02 2018-10-03 2018-10-04  --loglvl 1
   
(period 2018-10-05 | 2018-10-16) 
$ python HVAnalysis/start_main.py --datelist 2018-10-05 2018-10-06 2018-10-07 2018-10-08 2018-10-09 2018-10-10 2018-10-11 2018-10-12 2018-10-13 2018-10-14 2018-10-15 2018-10-16  --loglvl 1

(period 2018-10-18 | 2018-11-12) 
$ python HVAnalysis/start_main.py --datelist 2018-10-18 2018-10-19 2018-10-20 2018-10-21 2018-10-22 2018-10-23 2018-10-24 2018-10-25 2018-10-26 2018-10-27 2018-10-28 2018-10-29 2018-10-30 2018-10-31 2018-11-01 2018-11-02 2018-11-03 2018-11-04 2018-11-05 2018-11-06 2018-11-07 2018-11-08 2018-11-09 2018-11-10 2018-11-11 2018-11-12 --loglvl 1

```
If ```datelist``` is not specified, all data in the input folder will be considered.

### To-Dos
* Make separate plots of current, voltage, and resistance vs time for all of Run-1
* Make separate histograms for current, voltage, and resistance for all of Run-1