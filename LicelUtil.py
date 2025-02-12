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

def deadtime_correction(pc_MHz: np.ndarray, deadtime_ns : float) -> np.ndarray :
      """ return the dead time corrected photon counting data using the non paralyzable model  

      Parameters
      ----------
      pc_MHz : np.ndarray
            photon counting array as observed in MHz
      deadtime_ns : float
            The dead time of the detection system, typical values are 3.08 ns

      Returns
      -------
      np.ndarray :
            dead time corrected photon counting data in MHz
      """
      max_count_rate = np.max(pc_MHz)
      if (max_count_rate * deadtime_ns * 0.001 >= 1) :
            raise ValueError('dead time too large')
      return pc_MHz /(1 - pc_MHz  * deadtime_ns * 0.001)

def analog_to_pc_scale(analog: np.ndarray, pc_MHz: np.ndarray, start : int, stop : int) -> list[float] :
      """ find the scaling coefficients to match the analog array to the photon counting array between the start and the stop index
      Parameters
      ----------
      analog: np.array
            array of the analog data
      pc_MHz : np.ndarray
            photon counting array as observed in MHz, this should be the dead time corrected values
      start: int
            Start index for the scaling region
      stop: int
            Stop index for the scaling region
      Returns
      -------
      list[float] :
            fit coefficients, scale is at index 0, offset at index 1
      """
      m, b = np.polyfit(analog[start:stop], pc_MHz[start:stop], deg=1)
      return([m,b])
def binshift(analog: np.ndarray, pc_MHz: np.ndarray, 
             binshift : int) -> list[np.ndarray]:
      """
      shift the analog data versus the photon counting data
      Parameters
      ----------
      analog: np.array
            array of the analog data
      pc_MHz : np.ndarray
            photon counting array as observed in MHz, this should be the dead time corrected values
      binshift: int
            if binshift is larger than 0 the first binshift bins will be removed from  the analog data and the last bisnhift bins will be removed from the photon counting so that both are reduced equally in size.
            if the binshift is negative the first bins will be removed from the photon counting
            if the binshift is negative both arrays will be  unchanged.
      Returns
      -------
      list[np.ndarray] :
            realigned arrays [analog, pc]
      """
def skip_first_bins(analog: np.ndarray, pc_MHz: np.ndarray, 
             skip_bins : int) -> list[np.ndarray]:
      """
      skip the first bins that might disturb the gluing process due to analog noise.
      Parameters
      ----------
      analog: np.array
            array of the analog data
      pc_MHz : np.ndarray
            photon counting array as observed in MHz, this should be the dead time corrected values
      skip_bin: int
            if binshift is larger than 0 the first binshift bins will be removed from  the analog data photon counting 
            if the binshift is negative or 0 both arrays will be  unchanged.
      Returns
      -------
      list[np.ndarray] :
            realigned arrays [analog, pc]
      """

