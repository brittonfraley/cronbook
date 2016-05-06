Read Me
=======

Purpose
-------
Cronbook is a command line tool and library for writing time series data to delimited, plain text files. It was designed to provide a way to record monitoring data within shell scripts, similar to the way one might use a logging library within an application.  Data is passed as inline JSON or a JSON file. As such, cronbook should be viewed as a low-end alternative to a formal time-series database system that is more appropriate for lightweight and older systems, or corporate environments that restrict root and network access. 

Strengths vs Time-Series Database System:

* Single-file program
* Traditional UNIX tools can be used with the data store
* Easy installation and configuration
* Minimal dependencies--python v2.7 and the standard library
* Customizable with light programming knowledge

Strengths vs Traditional stdout/stderr Log Files:

* Data is organized within a file like a database, which facilitates processing
* Data files are rotated, which prevents disk storage saturation
* Unix and human-readable timestamps are written for each entry
* Control characters are escaped and non UTF-8 characters are stripped

Adding a record is as simple as:

    cronbook.py -a '{ "dataset" : "test", "keys" : [ "key_1" ], "values" : [ [ "value_1" ] ] }'

which will create a file named "test" with the content:

    unixtime|timestamp|key_1
    1459807807736918|2016-04-04 17:10:07.736918|value_1


To Do
-----
* unit test - rotation
* integration test - expand to include large JSON documents and other functions


Limitations
-----------
* not a high performance data store
* no "key", and rows not necessarily ordered by timestamp
* non-compressed storage


Concerns
--------
* local time is used for auto-generation of timestamps, not UTC


Contact
-------
brittonfraley@gmail.com or @brittonfraley on Twitter
