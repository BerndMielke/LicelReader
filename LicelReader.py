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
    def getDescString(self):
        desc = str(self.filename) + \
              "\nstart:    " + str(self.StartTime) + \
              "\nstop:     " + str(self.StopTime) + \
              "\nShots L0: " + str(self.numShotsL0) + \
              "\nShots L1: " + str(self.numShotsL1)
        return desc
       
class dataSet:
    active = 0
    dataType = 0
    laserSource = 0
    numBins = 0 
    laserPolarization = 0
    highVoltage = 0
    binWidth = 0.0
    wavelength = 0.0
    Polarization = 'o'
    binshift = 0
    binshiftPart = 0
    ADCBits = 0
    numShots = 0
    inputRange = 0.5
    discriminator = 0.003
    descriptor = ''
    rawData  = np.zeros((3,))
    physData = np.zeros((3,))
    
  
    def __init__(self, stringIn):
      self.active = int(stringIn.split()[0]) 
      self.dataType = int(stringIn.split()[1])
      self.laserSource = int(stringIn.split()[2])
      self.numBins     = int(stringIn.split()[3])
      self.laserPolarization = int(stringIn.split()[4])
      self.highVoltage = int(stringIn.split()[5])
      (self.binWidth) = float(stringIn.split()[6])
      self.wavelength = int(stringIn.split()[7].split('.')[0])
      self.Polarization = stringIn.split()[7].split('.')[1]
      self.binshift = int(stringIn.split()[8])
      self.ADCBits = int(stringIn.split()[12])
      self.numShots = int(stringIn.split()[13])
      if ((self.dataType == 0) or (self.dataType == 2)):
        self.inputRange = float(stringIn.split()[14])
      else: 
        self.discriminator = float(stringIn.split()[14])
      self.descriptor = stringIn.split()[15]
    def getDescString(self):
      if (self.dataType == 1): 
        desc = "Photon Bins: " + str(self.numBins) + \
             "\nbinWidth:    " + str(self.binWidth) + \
             "\nShots:       " + str(self.numShots) + \
             "\ndiscr:       " + str(63 * self.discriminator/ 25.0)
      else:
        desc = "Analog Bins: " + str(self.numBins) + \
             "\nbinWidth:    " + str(self.binWidth) + \
             "\nShots:       " + str(self.numShots) + \
             "\nADC:         " + str(self.ADCBits) + \
             "\nInput:       " + str(self.inputRange * 1000) + "mV" 
      desc += "\nHV:          " + str(self.highVoltage) + "V" + \
              "\nPol.:        " + self.Polarization
      return desc


         


class LicelFileReader:
  def __init__(self, filename):
     self.GlobalInfo = GlobalInfo()
     self.dataSet = []
     fp = open(filename, 'rb')
     encoding = 'utf-8'
     self.GlobalInfo.filename = str(fp.readline(), encoding).split()[0];
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

       scale = 1.0 / (self.dataSet[i].numShots if self.dataSet[i].numShots > 0 else 1);
       if ((self.dataSet[i].dataType == 0) and (self.dataSet[i].ADCBits > 1)): #analog
         maxbits = (2 ** self.dataSet[i].ADCBits) - 1
         scale *= self.dataSet[i].inputRange / maxbits
         self.dataSet[i].physData = scale * self.dataSet[i].rawData
       elif (self.dataSet[i].dataType == 1): # pc
         scale *= (150 / self.dataSet[i].binWidth)
         self.dataSet[i].physData = scale * self.dataSet[i].rawData  
       elif (self.dataSet[i].dataType == 2): # analog sqr
         maxbits = (2 ** self.dataSet[i].ADCBits) - 1
         n = (self.dataSet[i].numShots if self.dataSet[i].numShots > 0 else 1)
         sq_n_1 = np.sqrt(self.dataSet[i].numShots -1) if (self.dataSet[i].numShots > 1) else 1
         scale = self.dataSet[i].inputRange /(n * sq_n_1) /maxbits 
         self.dataSet[i].physData = scale * self.dataSet[i].rawData 
       elif (self.dataSet[i].dataType == 3): # pc sqr
         scale *= (150 / self.dataSet[i].binWidth) / np.sqrt((self.dataSet[i].numShots -1) if self.dataSet[i].numShots > 1 else 1)
         self.dataSet[i].physData = scale * self.dataSet[i].rawData  
       else :
         self.dataSet[i].physData = scale * self.dataSet[i].rawData
     fp.close()






