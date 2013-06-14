#!/usr/bin/env python
##############
##Given a file and two angle records, this will load the file
##using "decrypt_sdr" and then use the angle records to produce
##the 2-space location of the point those angles intersect at
##Software by: Richard Barnes (barn0357@umn.edu) "http://finog.org"
##############

import sys

if len(sys.argv)!=4:
	print "Syntax: interpolate <FILE> <PT 1> <PT 2>"
	sys.exit(0)

import decrypt_sdr

sdrfile=decrypt_sdr.SDRFile(sys.argv[1])

sdrfile.interpolate_angles(int(sys.argv[2]),int(sys.argv[3]))
