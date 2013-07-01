#!/usr/bin/env python
###################
# Decrypts/reduces (partially) SDR-33 data files
# The data files are assumed to have been read using the ProLink software
# And saved to a non-reduced format (which I can't remember right now)
# Software by: Richard Barnes (rbarnes@umn.edu). "http://rbarnes.org"
# The SDR33 assumes horizontal angles and azimuths are always measured opening
# to the right. 0.000 degrees azimuth is North
###################

import sys
import math

def atan2c(y,x):
  ang=math.atan2(y,x)   #Calculate atan2
  if (ang<0):           #Remap to the [0,2*Pi) range
    ang=2*math.pi+ang
  return ang

def ang_in_circle(ang):
  return math.fmod(abs(ang),360.0)

def ang_in_hemicircle(ang):
  ang=ang_in_circle(ang)
  if ang>math.pi:
    ang=2*math.pi-ang
  return ang

class station:
  def __init__(self,ptnum,northing,easting,elevation,theodheight,desc):
    self.ptnum      =int(ptnum)
    self.northing   =float(northing)
    self.easting    =float(easting)
    self.elevation  =float(elevation)
    self.theodheight=float(theodheight)
    self.desc       =desc

  def display(self):
    print "%f,%f,station" % (self.easting, self.northing)

  def getStation(self):
    return self.ptnum

  def getNorthing(self):
    return self.northing

  def getEasting(self):
    return self.easting

class angle:
  def __init__(self,sourcept,targetpt,slope,vertobs,horzobs,desc,bkb_azimuth,bkb_horzobs):
    self.sourcept=int(sourcept)
    self.targetpt=int(targetpt)

    if len(slope.strip()):
      self.slope=float(slope)
    else:
      self.slope=False

    self.vertobs=float(vertobs)
    self.horzobs=float(horzobs)
    self.desc=desc
    self.bkb_azimuth=float(bkb_azimuth)
    self.bkb_horzobs=float(bkb_horzobs)

  def getH(self): #Get the 360 H
    __out=self.horzobs*math.pi/180
    #The following transforms all angles to be relative to the northing line with negative values (0,-Pi) westing and positive values (0,Pi) easting
    __out=__out+(float(self.bkb_azimuth)-float(self.bkb_horzobs))*math.pi/180 #Correction applied to horziontal angle (may not be done as this is an "uncorrected observation")
    if __out<0:
      __out+=2*math.pi
    if __out>=2*math.pi:
      __out-=2*math.pi
    return __out

  def getTarget(self):
    return self.targetpt

  def getSource(self):
    return self.sourcept

class angles_class:
  def __init__(self):
    self.angles=[]

  def add(self,sourcept,targetpt,slope,vertobs,horzobs,desc,bkb_azimuth,bkb_horzobs):
    self.angles += [ angle(sourcept,targetpt,slope,vertobs,horzobs,desc,bkb_azimuth,bkb_horzobs) ]

  def find(self,ang):
    for i in self.angles:
      if i.getTarget()==ang:
        return i
    return False

class SDRFile:
  def __init__(self, fname):
    self.initialized=False
    self.angles  =angles_class()
    self.stations={}
    self.points = []

    try:
      fin = open(fname,'r')
    except:
      sys.stderr.write("Failed to open file '" + fname + "'!\n")
      return -1

    for line in fin:
      dat=line.strip()
      header=dat[0:2]
      derv=dat[2:4]

      #Station details (STN)
      if header=='02':
        ptnum      =dat[ 4: 8]
        northing   =dat[ 8:18]        #Distance
        easting    =dat[18:28]        #Distance
        elevation  =dat[28:38]        #Distance
        theodheight=dat[38:48]        #+Distance
        desc       =dat[48:64]
        self.stations[int(ptnum)] = station(ptnum,northing,easting,elevation,theodheight,desc)

      #Back bearing details (BKB)
      elif header=='07':
        sourcept   =dat[ 4: 8]
        targetpt   =dat[ 8:12]
        bkb_azimuth=dat[12:22]
        bkb_horzobs=dat[22:32]

      #Coordinates (a point) (POS)
      elif header=='08':
        ptnum    =dat[ 4: 8]
        northing =dat[ 8:18]
        easting  =dat[18:28]
        elevation=dat[28:38]
        desc     =dat[38:54]
        self.points.append("%s,%s,point" % (easting, northing))

      #Observation (OBS)
      elif header=='09' and (derv=='F1' or derv=='F2' or derv=='MD'):
        sourcept =dat[ 4: 8]
        targetpt =dat[ 8:12]
        slope    =dat[12:22]
        vertobs  =dat[22:32]
        horzobs  =dat[32:42]
        desc     =dat[42:58]
        self.angles.add(sourcept,targetpt,slope,vertobs,horzobs,desc,bkb_azimuth,bkb_horzobs)

    self.initialized=True

  def print_stations(self):
    for i in self.stations:
      self.stations[i].display()

  def print_points(self):
    for i in self.points:
      print i

  def interpolate_angles(self, target1, target2):
    t1=self.angles.find(target1)
    t2=self.angles.find(target2)
    if not (t1 and t2):
      print "Target point not found!"
      return False

    s1=self.stations[t1.getSource()]
    s2=self.stations[t2.getSource()]

    xd   =s2.getEasting() -s1.getEasting()      #Easting  distance between stations
    yd   =s2.getNorthing()-s1.getNorthing()     #Northing distance between stations
    dist =math.sqrt(xd**2+yd**2)                #Distance between stations

    s1_s2=atan2c(xd,yd)                         #Angle from station 1 to station 2 [0,2*Pi), 0 is North

    #Interior angle between line connecting stations (from s1) and line defined by observation angle from station 1
    ts1  =ang_in_hemicircle(t1.getH()-s1_s2)

    #Interior angle between line connecting stations (from s2) and line defined by observation angle from station 2
    ts2  =ang_in_hemicircle(t2.getH()-ang_in_circle(math.pi+s1_s2))

    #Third interior angle of the triangle formed by s1, s2, and the observed point
    inta =math.pi-ts1-ts2

    #Use the Law of Sines to determine distance from s1 to observed point
    ts1d =math.sin(ts2)/math.sin(inta)*dist
    #Use the Law of Sines to determine distance from s2 to observed point
    ts2d =math.sin(ts1)/math.sin(inta)*dist

    #Use segment length and angle to find location of observed point
    s1x  =s1.getEasting() +ts1d*math.sin(t1.getH())
    s1y  =s1.getNorthing()+ts1d*math.cos(t1.getH())
    s2x  =s2.getEasting() +ts2d*math.sin(t2.getH())
    s2y  =s2.getNorthing()+ts2d*math.cos(t2.getH())

    print "%f,%f,triangulated" % (s1x, s1y)
