import numpy as np
import numpy.ma as ma
import os
from enum import Enum, auto




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

def pr2(physData: np.ndarray, t0 : int, start: int,
                       stop : int) ->  np.ndarray:
      """ 
      return an range corrected array based on the data input. Before t0 
      the input is multiplied by 1
      
      Parameters
      ----------
      physData: np.ndarray
            Data in MHz or mV
      t0: int
            index of the t0 point
      start: int
            Start index for the background region
      stop: int
            Stop index for the background region
      
      Returns
      -------
      np.ndarray:
            range corrected numpy array
      """
      range_array = np.arange(-t0, physData.size - t0)
      range_array = np.maximum(range_array, np.ones(physData.size))
      arr = physData[start:stop] 
      return (physData - np.mean(arr)) * range_array * range_array

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

def bin_shift(analog: np.ndarray, pc_MHz: np.ndarray, 
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
            if binshift is larger than 0 the first binshift bins will be removed from  the analog data and the last binshift bins will be removed from the photon counting so that both are reduced equally in size.
            if the binshift is negative the first bins will be removed from the photon counting
            if the binshift is negative both arrays will be  unchanged.
      
      Returns
      -------
      list[np.ndarray] :
            realigned arrays [analog, pc]
      """
      if binshift > 0 :
            analog_shifted = analog[binshift:]
            pc_shifted = pc_MHz[0 : pc_MHz.size - binshift]
      elif binshift < 0:
            analog_shifted = analog[0 : pc_MHz.size + binshift]
            pc_shifted = pc_MHz[-binshift:]
      else :
            analog_shifted = analog
            pc_shifted = pc_MHz
      return ([analog_shifted, pc_shifted])

      
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
      skip_bins: int
            if `skip_bins` is larger than 0 the first `skip_bins` bins will be removed from  the analog data  and photon counting 
            if the `skip_bins` is negative or 0 both arrays will be  unchanged.
      
      Returns
      -------
      list[np.ndarray] :
            realigned arrays [analog, pc]
      """
      if skip_bins < 0 :
         skip_bins = 0    
      analog_shifted = analog[skip_bins:]
      pc_shifted = pc_MHz[skip_bins]
      return ([analog_shifted, pc_shifted])

class GluingStrategy(Enum):
      """ Enum for the results of the gluing strategy check"""
      INVALID          = auto()  #: one of the inputs signals is invalid 
      SIGNAL_TOO_LARGE = auto()  
      """ The minimum  of the photon counting data  is larger than the  max_toggle rate, use the analog in this case
      """ 
      SIGNAL_TOO_WEAK  = auto() 
      """ the maximum of the photon counting data is smaller than the 
      the minimum toggle rate, use the the photon counting in this case
      """
      BACKGROUND       = auto()
      """ The minimum of the photon counting data does exceeds the min toggle rate, there will be no improvement for the dynamic range from the photon counting, use the analog in this case
      """
      GLUE_PROFILES    = auto() 
      """ both signals are valid and the minimum of the photon counting is below the minimum toggle rate and the maximum is above the max toggle 
      rate
      """
def check_gluing_strategy (analog: np.ndarray, pc_MHz: np.ndarray, 
                           min_toggle : float, max_toggle : float) -> GluingStrategy :
      """ check if the profiles can be glued

      Parameters
      ----------
      analog: np.array
            array of the analog data
      pc_MHz : np.ndarray
            photon counting array as observed in MHz, this should be the dead time corrected values
      min_toggle: float
            count rate in MHz values above or equal to the `min_toggle` will be used for computing the linear transfer coefficients between analog and photon counting. 
      max_toggle: float
            count rate in MHz values below or equal to the `max_toggle` will be used for computing the linear transfer coefficients between analog and photon counting. 
      
      Returns
      -------
      GluingStrategy :
            result of the gluing strategy check
      """
      if analog.size <= 0 :
            return GluingStrategy.INVALID
      if pc_MHz.size <= 0 :
            return GluingStrategy.INVALID
      pc_max = np.max(pc_MHz)
      pc_min = np.min(pc_MHz)
      if pc_max > 1000 :
            return GluingStrategy.INVALID
      if pc_min < 0 :
            return GluingStrategy.INVALID
      if pc_min > max_toggle :
            return GluingStrategy.SIGNAL_TOO_LARGE
      if pc_max < min_toggle :
            return GluingStrategy.SIGNAL_TOO_WEAK
      if pc_min > min_toggle :
            return GluingStrategy.BACKGROUND
      return GluingStrategy.GLUE_PROFILES

def mask_profiles(analog: np.ndarray, pc_MHz: np.ndarray, 
                  min_toggle : float, max_toggle : float, skip_bins: int = 0) -> list[np.ndarray] :
      """ mask in both profiles as Nan when the photon counting is outside 
      the min_toggle - max_toggle - range and compress the arrays so that only data points that are inside the range are returned

      Parameters
      ----------
      analog: np.array
            array of the analog data
      pc_MHz : np.ndarray
            photon counting array as observed in MHz, this should be the dead time corrected values
      min_toggle: float
            count rate in MHz values above or equal to the `min_toggle` will be used for computing the linear transfer coefficients between analog and photon counting. 
      max_toggle: float
            count rate in MHz values below or equal to the `max_toggle` will be used for computing the linear transfer coefficients between analog and photon counting. 
      skip_bins: int
            if `skip_bins` is larger than 0 the first `skip_bins` bins will be removed from  the analog data  and photon counting 
            if the `skip_bins` is negative or 0 both arrays will be  unchanged.
      
      Returns
      -------
      list[np.ndarray] :
            compressed  arrays [analog, pc]
      """
      pc_masked = ma.masked_outside(pc_MHz, min_toggle, max_toggle)
      pc_masked[0: skip_bins] = ma.masked
      analog_masked = ma.masked_where(pc_masked.mask, analog)
      pc_compressed = pc_masked.compressed()
      analog_compressed = analog_masked.compressed()
      return ([analog_compressed, pc_compressed])

def glue_profiles(analog: np.ndarray, pc_MHz: np.ndarray, 
                  min_toggle : float, max_toggle : float, skip_bins: int = 0) -> np.ndarray :
      """ get the glued profile

      Parameters
      ----------
      analog: np.array
            array of the analog data
      pc_MHz : np.ndarray
            photon counting array as observed in MHz, this should be the dead time corrected values
      min_toggle: float
            count rate in MHz values above or equal to the `min_toggle` will be used for computing the linear transfer coefficients between analog and photon counting. 
      max_toggle: float
            count rate in MHz values below or equal to the `max_toggle` will be used for computing the linear transfer coefficients between analog and photon counting. 
      skip_bins: int
            if `skip_bins` is larger than 0 the first `skip_bins` bins will be removed from  the analog data  and photon counting 
            if the `skip_bins` is negative or 0 both arrays will be  unchanged.
      
      Returns
      -------
      np.ndarray :
            glued profile in MHz
      """
      [analog_compressed, pc_compressed] = mask_profiles(analog, pc_MHz, min_toggle, max_toggle, skip_bins)
      [m,b] = analog_to_pc_scale(analog_compressed, pc_compressed, 0, pc_compressed.size)
      analog_scaled =  m * analog + b
      use_analog = 1 *  (pc_MHz > max_toggle)
      return use_analog * analog_scaled + (1 - use_analog) * pc_MHz

