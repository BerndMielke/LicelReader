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

