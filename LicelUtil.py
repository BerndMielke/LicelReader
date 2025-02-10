import numpy as np
import os



def offset_correction(physData: np.ndarray, start: int,
                       stop : int) ->  np.ndarray:
      """ 
      return an offset corrected array based on the data input
      
      Parameters
      ----------
      physData: np.ndarray
            Data in MHz or mV
      start: int
            Start index for the background region
      stop: int
            Stop index for the background region
      
      Returns
      -------
      np.ndarray:
            offset corrected numpy array
      """
      arr = physData[start:stop] 
      return physData - np.mean(arr)

def smoothed_signal(data: np.ndarray, filterWidth: int) -> np.ndarray :
      """ return a smoothed array based on the data input 

      Parameters
      ----------
      data : np.ndarray
            input array to be filtered
      filterWidth : int
            The width of the filtering the larger the number the stronger the
            filtering

      Returns
      -------
      np.ndarray :
            smoothed numpy array
      """
      kernel_size = filterWidth
      kernel = np.ones(kernel_size) / kernel_size
      return np.convolve(data, kernel, mode='same')
def downsampling(data: np.ndarray, exponent: int) -> np.ndarray :
      """
      accumulating the array in steps of 0  no accumulation, 1 add two bins
      2 add 4 bins...
      Parameters
      ----------
      data : np.ndarray
            data input array 
      exponent: int
            how many accumulation steps are needed
      Returns
      -------
      np.ndarray :
            downsampled array
      """
      oversampling_Factor = 1 << exponent
      max_size = data.size
      pieces = np.floor_divide(max_size, oversampling_Factor)
      new_size = pieces * oversampling_Factor
      y = np.split(data[0:new_size], pieces)
      return np.sum(y, axis = 1)

