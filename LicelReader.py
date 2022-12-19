import numpy as np
import os

class GlobalInfo:
    filename = ''
    Location = ''
    StartTime = ''
    StopTime = ''
    Height = 0
    Longitude = 0.0
    Latitude = 0.0
    Zenith = 0.0
    Azimuth = 0.0
    Custom = ''
    numShotsL0 = 0
    repRateL0 = 0
    numShotsL1 = 0
    repRateL1 = 0
    numShotsL2 = 0
    repRateL2 = 0
    numDataSets = 0
class dataSet:
    active = 0
    dataType = 0
    laserSource = 0
    numBins = 0 
    laserPolarization = 0
    highVoltage = 0
    binWidth = 0.0
    LaserWavelength = 0.0
    Polarisation = 'o'
    binshift = 0
    binshiftPart = 0
    ADCBits = 0
    numShots = 0
    inputRange = 0.5
    discriminator = 0.003
    descriptor = ''
    rawData  = np.zeros((3,))
    physData = np.zeros((3,))
    def offset_correction(self, start, stop):
      arr = self.physData[start:stop] 
      return self.physData - np.mean(arr) 

  
    def __init__(self, stringIn):
      self.active = int(stringIn.split()[0]) 
      self.dataType = int(stringIn.split()[1])
      self.laserSource = int(stringIn.split()[2])
      self.numBins     = int(stringIn.split()[3])
      self.laserPolarization = int(stringIn.split()[4])
      self.highVoltage = int(stringIn.split()[5])
      self.binwidth = float(stringIn.split()[6])
      self.LaserWavelength = int(stringIn.split()[7].split('.')[0])
      self.binshift = int(stringIn.split()[8])
      self.ADCBits = int(stringIn.split()[12])
      self.numShots = int(stringIn.split()[13])
      if (self.dataType == 0):
        self.inputRange = float(stringIn.split()[14])
      else: 
        self.discriminator = float(stringIn.split()[14])
      self.descriptor = stringIn.split()[15]
    


class LicelFileReader:
  def __init__(self, filename):
     self.GlobalInfo = GlobalInfo
     self.dataSet = []
     fp = open(filename, 'rb')
     self.GlobalInfo.filename = str(fp.readline()).split()[0]
     encoding = 'utf-8'
     self.firstline = str(fp.readline(), encoding)
     self.secondline = str(fp.readline(), encoding)
     self.GlobalInfo.Location  = self.firstline.split()[0]
     self.GlobalInfo.StartTime = self.firstline.split()[1] + ' ' + self.firstline.split()[2]
     self.GlobalInfo.StopTime  =  self.firstline.split()[3] + ' ' + self.firstline.split()[4]
     self.GlobalInfo.Height = int(self.firstline.split()[5])
     self.GlobalInfo.Longitude = float(self.firstline.split()[6])
     self.GlobalInfo.Latitude = float(self.firstline.split()[7])
     self.GlobalInfo.Zenith = float(self.firstline.split()[8])
     if (len(self.firstline.split()) > 10): 
        self.GlobalInfo.Azimuth = float(self.firstline.split()[9])
        
     self.GlobalInfo.numShotsL0  = int(self.secondline.split()[0])
     self.GlobalInfo.repRateL0  = int(self.secondline.split()[1])
     self.GlobalInfo.numShotsL1  = int(self.secondline.split()[2])
     self.GlobalInfo.reprateL1  = int(self.secondline.split()[3])
     self.GlobalInfo.numDataSets   = int(self.secondline.split()[4])
     #self.GlobalInfo.numShotsL2  = int(self.secondline.split()[5])
     #self.GlobalInfo.repRateL2  = int(self.secondline.split()[6])
     for i in range(self.GlobalInfo.numDataSets):
       self.varline = str(fp.readline(), encoding)
       self.dataSet.append(dataSet(self.varline))
     fp.readline()
     for i in range(self.GlobalInfo.numDataSets):
       if (i > 0):
        fp.read(2)
       self.dataSet[i].rawData = np.fromfile(fp, dtype=int, count = self.dataSet[i].numBins)
       if (self.dataSet[i].dataType == 0):
         maxbits = (2 ** self.dataSet[i].ADCBits) - 1
         self.dataSet[i].physData = self.dataSet[i].inputRange * self.dataSet[i].rawData / (self.dataSet[i].numShots if self.dataSet[i].numShots > 0 else 1) /maxbits
       else :
         self.dataSet[i].physData = self.dataSet[i].rawData / (self.dataSet[i].numShots if self.dataSet[i].numShots > 0 else 1)
     fp.close()






