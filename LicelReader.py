import numpy as np
import os

class GlobalInfo:
    """ The measurement situation is described in this class
    """
    filename  : str  = '' #: name of the file when it was written
    Location  : str  = '' #: measurement site
    StartTime : str = ''  #: measurement start hh:mm:ss
    StopTime  : str = ''  #: measurement end hh:mm:ss
    Height : float = 0    #:altitude above sea level  
    Longitude : float = 0.0 #: longitude in degrees
    Latitude  : float = 0.0 #: latitude in degrees
    Zenith : float = 0.0    #: Zenith angle of the beam in degrees
    Azimuth : float = 0.0   #: Azimuth angle of the beam in degrees
    Custom : str = ''       #: optional custom information field
    numShotsL0 : int = 0 #: number of laser shots of the first laser
    repRateL0 : int  = 0 #: repetition rate of the first laser
    numShotsL1 : int = 0 #: number of laser shots of the second laser
    repRateL1 : int  = 0 #: repetition rate of the second laser
    numShotsL2 : int = 0 #: number of laser shots of the third laser
    repRateL2 : int  = 0 #: repetition rate of the third laser
    numDataSets : int = 0 #: number of variable datasets in the `dataset` array
    def getDescString(self): #: data file description string
        desc = str(self.filename) + \
              "\ndatasets: " + str(self.numDataSets) + \
              "\nstart:    " + str(self.StartTime) + \
              "\nstop:     " + str(self.StopTime) + \
              "\nShots L0: " + str(self.numShotsL0) + \
              "\nShots L1: " + str(self.numShotsL1)
        return desc
       
class dataSet:
    active :      int = 0 #: 1 for active data sets , 0 for skipped data sets
    dataType :    int = 0 
    """"
        0 Analog, 1 Photon Counting, 2 Analog squared, 
        3 Photon Counting squared,  4 Power Meter dataset, 5 Overflow dataset
    """
    laserSource : int = 0 #: which laser is the source, valid values 0, 1, 2
    numBins : int = 0 #: number of data points
    laserPolarization : int = 0 
    """
      the laser polarization 0 (none, vertical, horizontal, right circular, left circular) 0|1|2|3|4
    """
    highVoltage : int = 0 #: High voltage of the PM or APD in V 
    binWidth : float = 0.0 #: width of single bin in m
    wavelength : float = 0.0 #: detection wavelength in nm
    Polarization : str = 'o'
    """
      polarization status (none, parallel, crossed, right circular, left circular) o|p|s|r|l
    """
    binshift : int = 0
    """
      bin shift, whole-number (primary bins, integer rounded down, 2 digits, 00 if not supported or zero)
    """
    binshiftPart : int = 0
    """
      decimal places of the bin shift (3 digits, 000 if not supported or zero)
    """
    ADCBits : int = 0 #: the number of bits of the ADC
    numShots :int = 0 #: the number of accumulated shots
    inputRange : float = 0.5 
    """Analog input range in V valid values 0.02, 0.1, 0.5
    """
    discriminator : float = 0.003 #: photon counting discriminator level in V 
    descriptor : str = ''
    """
    device identificator
    BT 	analog dataset
    BC 	photon counting
    S2A  	s sqrt(N(N-1)) (analog, s sample standard deviation, N shots)
    S2P  	s sqrt(N(N-1)) (photon counting, s sample standard deviation, N shots)
    PD 	powermeter (photodiode)
    PM 	powermeter (powermeter)
    OF 	overflow
    """
    rawData : np.ndarray = np.zeros((3,)) #: binary raw sum 
    physData : np.ndarray = np.zeros((3,)) #: scaled to physical values
    
  
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
    def getDescString(self): #: data set description string
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
       self.dataSet[i].rawData = np.fromfile(fp, dtype=np.int32, count = self.dataSet[i].numBins)

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
     term = fp.read(2) #read the terminating CRLF
     if (term != '\r\n') :
       print('wrong termination')
     else :
       print ('file complete')
     fp.close()






