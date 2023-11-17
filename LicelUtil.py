import numpy as np
import os

def offset_correction(physData, start, stop):
      arr = physData[start:stop] 
      return physData - np.mean(arr) 
