#!/usr/bin/env python
##############
##Given a file and two angle records, this will load the file
##using "decrypt_sdr" and then use the angle records to produce
##the 2-space location of the point those angles intersect at
##Software by: Richard Barnes (barn0357@umn.edu) "http://finog.org"
##############

import sys

if len(sys.argv)!=3:
  print "Syntax: interpolate <SDR File> <Obs Pair File>"
  print "SDRFile must be an unreduced SDR file"
  print " "
  print "The ObsPairFile must consist of a list of points such as:"
  print "1001 1003"
  print "1003 1004"
  print "..."
  print " "
  print "Where each point is an observed angle to an object of interest"
  print "And each pair of points corresponds to two different stations' observation of this point"
  sys.exit(0)

import decrypt_sdr

sdrfile=decrypt_sdr.SDRFile(sys.argv[1])
sdrfile.print_stations()
sdrfile.print_points()

with open(sys.argv[2],'r') as fin:
  for line in fin:
    if line[0]=="#":
      continue
    elif len(line[0].strip())==0:
      continue
    else:
      line=line.split()
      sdrfile.interpolate_angles(int(line[0]),int(line[1]))
