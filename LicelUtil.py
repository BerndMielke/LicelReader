import numpy as np
import os



def offset_correction(physData, start, stop):
      arr = physData[start:stop] 
      return physData - np.mean(arr)

def smoothed_signal(data,filterWidth): 
      """ return a smoothed array based on the data input 
        Parameters
        ----------
        data : numpy array
        filterWidth : int
            The width of the filtering the larger the number the stronger the
            filtering
        """
      kernel_size = filterWidth
      kernel = np.ones(kernel_size) / kernel_size
      return np.convolve(data, kernel, mode='same')

