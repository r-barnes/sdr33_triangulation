#!/usr/bin/env python
###################
##Decrypts/reduces (partially) SDR-33 data files
##The data files are assumed to have been read using the ProLink software
##And saved to a non-reduced format (which I can't remember right now)
##Software by: Richard Barnes (barn0357@umn.edu). "http://finog.org"
###################

#Derivation codes:
#CL: Collimation Program
#CP: Setting of correction parameter
#FC: Feature code note
#F1: Uncorrected observation measured with face 1
#F2: Uncorrected observation measured with face 2
#IN: Inverse Program
#KI: Keyboard input
#KM: Kinematic data (low accuracy)
#KP: Kinematic processed data (high accuracy)
#MC: Measurement corrected for instrumental and environmental factors
#MD: Multiple distance readings
#NM: Not measured
#OS: Offset reading note
#RE: Remote elevation program
#RO: Roading program
#RS: Resection program
#SC: Set collection
#SO: Setting out program
#TP: Topography program
#TS: Automatic time stamp note
#TV: Traverse program

import sys
from math import *

def atan_in_circle(x,y):
  #Assumes original angle is taken from the northing
  #Returns tangent angle [0,360) 
  if x>0 and y==0:
    return 90
  elif x<0 and y==0:
    return 270

  t=abs(atan(x/y))*180/pi #'cause we work in degrees
  if x>0 and y>0:
    return t
  elif x>0 and y<0:
    return 180-t
  elif x<0 and y<0:
    return 180+t
  elif x<0 and y>0:
    return 360-t

def ang_in_circle(ang):
  while ang<360:
    ang+=360
  while ang>360:
    ang-=360
  return ang

def ang_in_hemicircle(ang):
  ang=ang_in_circle(ang)
  if ang>180:
    ang=360-ang
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
    print " "
    print "Station " + str(ptnum) + " Details"
    print "---------------"
    print "Northing:\t\t"        + str(self.northing)
    print "Easting:\t\t"         + str(self.easting)
    print "Elevation:\t\t"       + str(self.elevation)
    print "Theodolite Height:\t" + str(self.theodheight)
    print "Desc: \t" + desc
    print " "

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

    if len(slope.replace(" ","")): #Todo: Trim command
      self.slope=float(slope)
    else:
      self.slope=False

    self.vertobs=float(vertobs)
    self.horzobs=float(horzobs)
    self.desc=desc
    self.bkb_azimuth=float(bkb_azimuth)
    self.bkb_horzobs=float(bkb_horzobs)
#    self.display()

  def display(self):
    print "OBS:\t" + str(self.sourcept) + "-" + str(self.targetpt) + ",\t" + str(self.slope) + "S,\t" + str(self.vertobs) + "V,\t" + str(self.getH()) + "H,\t" + self.desc

  def getcH(self):
    __out=self.horzobs
    #The following transforms all angles to be relative to the northing line with negative values (0,-180) westing and positive values (0,180) easting
    __out=__out+float(self.bkb_azimuth)-float(self.bkb_horzobs) #Correction applied to horziontal angle (may not be done as this is an "uncorrected observation")
    if __out>180:
      __out-=360
    if __out<-180:
      __out+=360
    if __out>360:
      __out-=360
    return __out

  def getH(self): #Get the 360 H
    __out=self.horzobs
    #The following transforms all angles to be relative to the northing line with negative values (0,-180) westing and positive values (0,180) easting
    __out=__out+float(self.bkb_azimuth)-float(self.bkb_horzobs) #Correction applied to horziontal angle (may not be done as this is an "uncorrected observation")
    if __out<0:
      __out+=360
    if __out>=360:
      __out-=360
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

  def interpolate(self,stations,target1,target2):
    t1=self.find(target1)
    t2=self.find(target2)
    if not (t1 and t2):
      print "Target point not found!"
      return False
    s1=stations.get(t1.getSource())
    s2=stations.get(t2.getSource())
    if not (s1 and s2):
      print "Station not found!"
      return False

#    print "Using points (" + str(t1.getTarget()) + "," + str(t2.getTarget()) + ") with stations (" + str(s1.getStation()) + "," + str(s2.getStation()) + ")"

    xd=s2.getEasting()-s1.getEasting()
    yd=s2.getNorthing()-s1.getNorthing()
    dist=sqrt(xd**2+yd**2)
    s1_s2=atan_in_circle(xd,yd)
    ts1=ang_in_hemicircle(t1.getH()-s1_s2)
    ts2=ang_in_hemicircle(t2.getH()-ang_in_circle(180+s1_s2))
    inta=180-ts1-ts2
#    print "Station Angle:\t" + str(s1_s2) + ", Dist:\t" + str(dist)
#    print "Target 1:\t" + str(t1.getH()) + ", Interior 1:\t" + str(ts1)
#    print "Target 2:\t" + str(t2.getH()) + ", Interior 2:\t" + str(ts2)
#    print "Unknown:\t" + str(inta)
    ts1d=sin(ts2*pi/180)/sin(inta*pi/180)*dist
    ts2d=sin(ts1*pi/180)/sin(inta*pi/180)*dist
#    print "S1-Target Dist: " + str(ts1d)
#    print "S2-Target Dist: " + str(ts2d)
    s1x=s1.getEasting()+ts1d*sin(t1.getH()*pi/180)
    s1y=s1.getNorthing()+ts1d*cos(t1.getH()*pi/180)
    s2x=s2.getEasting()+ts2d*sin(t2.getH()*pi/180)
    s2y=s2.getNorthing()+ts2d*cos(t2.getH()*pi/180)
#    print "S1 Loc Projection: (" + str(s1x) + "," + str(s1y) + ")"
#    print "S2 Loc Projection: (" + str(s2x) + "," + str(s2y) + ")"
    print str(target1) + "," + str(target2) + "," + str(s1x) + "," + str(s1y)

#POS,  1000,  29.1755686N,  -4.0095257Ea,  0.00963371El,  FIT-TEST        
#OBS:  1-1001,  FalseS,  90.2166666V,  352.175H,  FIT-TEST        
#POS,  1002,  4.59433814N,  6.41467510Ea,  -0.4376595El,  FIT-TEST2       
#OBS:  1-1003,  FalseS,  94.0527777V,  54.388889H,  FIT-TEST2 

class stations_class:
  def __init__(self):
    self.stations=[]

  def add(self,ptnum,northing,easting,elevation,theodheight,desc):  #Todo: What if they return to the station?!
    self.stations += [ station(ptnum,northing,easting,elevation,theodheight,desc) ]

  def get(self,station):
    for i in self.stations:
      if i.getStation()==station:
        return i
    return False

class SDRFile:
  def __init__(self, fname):
    self.initialized=False
    self.angles  =angles_class()
    self.stations=stations_class()

    try:
      fin = open(fname,'r')
    except:
      sys.stderr.write("Failed to open file '" + fname + "'!\n")
      return -1

    for line in fin:
      dat=line.strip()
      header=dat[0:2]
      derv=dat[2:4]

      #Header record, units defined, serial number, version number (Header)
      if header=='00':
        version_number  =dat[ 4:20]
        serial_number   =dat[20:24]
        date            =dat[24:40]
        unit_angle      =dat[40]    #1=Degrees, 2=Gons, 3=Quadrant bearings, 4=Mils
        unit_dist       =dat[41]    #1=Meters, 2=Feet
        unit_pressure   =dat[42]    #1=mmHg, 2=Inches mercury, 3=mbar (Millibars)
        unit_temp       =dat[43]    #1=Celsius, 2=Fahrenheit
        unit_coor_prompt=dat[44]    #1=N-E-Elev, 2=E-N-Elev
        unit_always_one =dat[45]    #Why? No idea, it just is.

      #Instrument details (INSTR)
      elif header=='01':
        edm_type=dat[4]            #1=Manual, 4=DT4/5/5A/20, 6=SDM3E, 7=SDM3ER, 8=SDM3F, 9=SDM3FR, :=SET (older styles), ;=DT2/4, <=REDmini, ==SET with 2-way comms (newer style) and SET C series
        edm_desc         =dat[ 5:21]
        edm_serial       =dat[21:27]
        theodolite_desc  =dat[27:43]
        theodolite_serial=dat[43:49]
        mounting_type    =dat[49]        #1=Telescope, 2=Standards, 3=Not applicable
        vertical_angle_op=dat[50]        #1=Zenith (measured downards from upwards vertical, 2=Horiz (measured upwards from horizontal). Applies to all vertical observation in OBS records which have not had any coorections applied (deriv code of F1, F2 or MD)
        edm_offset       =dat[51:61]      #Distance
        reflector_offset =dat[61:71]      #Distance
        prism_const      =dat[71:81]      #mm

      #Station details (STN)
      elif header=='02':
        ptnum      =dat[ 4: 8]
        northing   =dat[ 8:18]        #Distance
        easting    =dat[18:28]        #Distance
        elevation  =dat[28:38]        #Distance
        theodheight=dat[38:48]        #+Distance
        desc       =dat[48:64]
        self.stations.add(ptnum,northing,easting,elevation,theodheight,desc)

      #Target (staff) details (TRGET)
      elif header=='03':
        targetheight=dat[4:14]

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
        print "POS,\t" + ptnum + ",\t" + northing + "N,\t" + easting + "Ea,\t" + elevation + "El,\t" + desc

      #Observation (OBS)
      elif header=='09' and (derv=='F1' or derv=='F2' or derv=='MD'):
        sourcept =dat[ 4: 8]
        targetpt =dat[ 8:12]
        slope    =dat[12:22]
        vertobs  =dat[22:32]
        horzobs  =dat[32:42]
        desc     =dat[42:58]
        self.angles.add(sourcept,targetpt,slope,vertobs,horzobs,desc,bkb_azimuth,bkb_horzobs)

      #Observation (OBS)
      elif header=='09' and derv=='MC':
        pass

      #Job identifier (JOB)
      elif header=='10':
        jobid=dat[4:20]

      #Note (NOTE)
      elif header=='13':
        note=dat[4:64]

    self.initialized=True

  def interpolate_angles(self, target1, target2):
    return self.angles.interpolate(self.stations,target1,target2)
