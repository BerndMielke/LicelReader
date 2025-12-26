import numpy as np
import re
from dataclasses import dataclass, field
from typing import List, IO
from numpy.typing import NDArray


@dataclass
class GlobalInfo:
    """The measurement situation is described in this class.

    Field names intentionally match the Licel spec (section 9.2).
    """
    filename: str = ''
    Location: str = ''
    StartTime: str = ''
    StopTime: str = ''
    Height: float = 0
    Longitude: float = 0.0
    Latitude: float = 0.0
    Zenith: float = 0.0
    Azimuth: float = 0.0
    Custom: str = ''
    numShotsL0: int = 0
    repRateL0: int = 0
    numShotsL1: int = 0
    repRateL1: int = 0
    numShotsL2: int = 0
    repRateL2: int = 0
    numDataSets: int = 0

    def getDescString(self) -> str:
        return (
            f"{self.filename}\n"
            f"datasets: {self.numDataSets}\n"
            f"start:    {self.StartTime}\n"
            f"stop:     {self.StopTime}\n"
            f"Shots L0: {self.numShotsL0}\n"
            f"Shots L1: {self.numShotsL1}"
        )


@dataclass
class dataSet:
    """Dataset description — field names kept to match the Licel spec."""
    active: int = 0
    dataType: int = 0
    laserSource: int = 0
    numBins: int = 0
    laserPolarization: int = 0
    highVoltage: int = 0
    binWidth: float = 0.0
    wavelength: int = 0
    Polarization: str = 'o'
    binshift: int = 0
    binshiftPart: int = 0
    ADCBits: int = 0
    numShots: int = 0
    inputRange: float = 0.5
    discriminator: float = 0.003
    descriptor: str = ''
    comment: str = ''
    rawData: NDArray[np.uint32] = field(default_factory=lambda: np.zeros(0, dtype=np.uint32))
    physData: NDArray[np.float64] = field(default_factory=lambda: np.zeros(0, dtype=np.float64))

    def __init__(self, stringIn: str):
        splitted = stringIn.split()
        if len(splitted) < 16:
            raise ValueError(f"Invalid dataset descriptor line: '{stringIn.strip()}'")
        try:
            self.active = int(splitted[0])
            self.dataType = int(splitted[1])
            self.laserSource = int(splitted[2])
            self.numBins = int(splitted[3])
            self.laserPolarization = int(splitted[4])
            self.highVoltage = int(splitted[5])
            self.binWidth = float(splitted[6])
            wl_field = splitted[7]
            if '.' in wl_field:
                wlsplit = wl_field.split('.', 1)
                self.wavelength = int(wlsplit[0]) if wlsplit[0] else 0
                self.Polarization = wlsplit[1] if len(wlsplit) > 1 else 'o'
            else:
                self.wavelength = int(wl_field) if wl_field.isdigit() else 0
                self.Polarization = 'o'
            self.binshift = int(splitted[8])
            # fields 9..11 exist in some formats — ignore if not needed
            self.binshiftPart = int(splitted[9]) if len(splitted) > 9 and splitted[9].isdigit() else 0
            # ADCBits at index 12
            self.ADCBits = int(splitted[12])
            self.numShots = int(splitted[13])
            if (self.dataType == 0) or (self.dataType == 2):
                self.inputRange = float(splitted[14])
            else:
                self.discriminator = float(splitted[14])
            self.descriptor = splitted[15]
            if len(splitted) > 16:
                self.comment = ' '.join(splitted[16:])
        except Exception as e:
            raise ValueError(f"Failed to parse dataset descriptor: '{stringIn.strip()}': {e}")

    def getDescString(self) -> str:
        max_disc_mV = 25.0
        match self.dataType:
            case 0:
                desc = (
                    f"wavelength: {self.wavelength} nm\n"
                    f"Analog Bins: {self.numBins}\n"
                    f"binWidth:    {self.binWidth}\n"
                    f"Shots:       {self.numShots}\n"
                    f"ADC:         {self.ADCBits}\n"
                    f"Input:       {self.inputRange * 1000}mV"
                )
            case 1:          
                desc = (
                    f"wavelength: {self.wavelength} nm\n"
                    f"Photon Bins: {self.numBins}\n"
                    f"binWidth:    {self.binWidth}\n"
                    f"Shots:       {self.numShots}\n"
                    f"discr:       {int(round(63 * self.discriminator / max_disc_mV))}"
                )
            case 2:
                desc = (
                    f"wavelength: {self.wavelength} nm\n"
                    f"Analog  Square Bins: {self.numBins}\n"
                    f"binWidth:    {self.binWidth}\n"
                    f"Shots:       {self.numShots}\n"
                    f"ADC:         {self.ADCBits}\n"
                    f"Input:       {self.inputRange * 1000}mV"
                )
            case 3:
                desc = (
                    f"wavelength: {self.wavelength} nm\n"
                    f"Photon Square Bins: {self.numBins}\n"
                    f"binWidth:    {self.binWidth}\n"
                    f"Shots:       {self.numShots}\n"
                    f"discr:       {int(round(63 * self.discriminator / max_disc_mV))}"
                )
            case 4:
                desc = f"Powermeter shots: {self.numBins}"
            case 5:
                desc = f"Analog Overflow: {self.numBins}"
            case _:
                desc = (
                    f"wavelength: {self.wavelength} nm\n"
                    f"Analog Bins: {self.numBins}\n"
                    f"binWidth:    {self.binWidth}\n"
                    f"Shots:       {self.numShots}\n"
                    f"ADC:         {self.ADCBits}\n"
                    f"Input:       {self.inputRange * 1000}mV"
                )
        if self.dataType < 4:
            desc += f"\nHV:          {self.highVoltage}V\nPol.:        {self.Polarization}\nID: {self.descriptor} {self.comment}"
        return desc

    def getShortDescr(self) -> str:
        if self.wavelength > 0:
            desc = f"{self.wavelength} nm "
        else:
            spl = re.split('(?<=\\D)(?=\\d)|(?<=\\d)(?=\\D)', self.descriptor)
            desc = f"TR{spl[-1]} " if spl else self.descriptor
        match self.dataType:
            case 0:
                desc += "A"
            case 1:
                desc += "PC"
            case 2:
                desc += "ASQR"
            case 3:
                desc += "PCSQR"
            case _:
                pass
        if self.dataType < 4 and self.Polarization != 'o':
            desc += f" {self.Polarization}"
        return desc

    def x_axis_m(self) -> NDArray[np.float64]:
        return np.asarray(np.arange(self.numBins, dtype=np.float64) * self.binWidth, dtype=np.float64)

    def x_axis_us(self) -> NDArray[np.float64]:
        lidar_range_factor = 150.0  # m/us  
        return np.asarray(np.arange(self.numBins, dtype=np.float64) * self.binWidth /
                           lidar_range_factor, dtype=np.float64)


class LicelFileReader:
    def __init__(self, filename: str):
        self.GlobalInfo = GlobalInfo()
        self.dataSet: List[dataSet] = []
        self.shortDescr: List[str] = []

        encoding = 'utf-8'
        try:
            with open(filename, 'rb') as fp:
                self._parse_header(fp, encoding)
                self._read_dataset_descriptors(fp, encoding)
                self._read_and_process_datasets(fp)
        except Exception:
            raise

    def _parse_header(self, fp: IO[bytes], encoding: str):
        """Parse the header lines and populate GlobalInfo."""
        # header lines — decode consistently
        first = fp.readline().decode(encoding)
        if not first:
            raise EOFError("Empty file or unable to read header")
        self.GlobalInfo.filename = first.split()[0]

        self.firstline = fp.readline().decode(encoding)
        self.secondline = fp.readline().decode(encoding)

        flsplit = self.firstline.split()
        if len(flsplit) < 9:
            raise ValueError(f"Invalid first header line: '{self.firstline.strip()}'")
        self.GlobalInfo.Location = flsplit[0]
        self.GlobalInfo.StartTime = flsplit[1] + ' ' + flsplit[2]
        self.GlobalInfo.StopTime = flsplit[3] + ' ' + flsplit[4]
        self.GlobalInfo.Height = int(flsplit[5])
        self.GlobalInfo.Longitude = float(flsplit[6])
        self.GlobalInfo.Latitude = float(flsplit[7])
        self.GlobalInfo.Zenith = float(flsplit[8])
        if len(flsplit) > 9:
            self.GlobalInfo.Azimuth = float(flsplit[9])

        slsplit = self.secondline.split()
        if len(slsplit) < 5:
            raise ValueError(f"Invalid second header line: '{self.secondline.strip()}'")
        self.GlobalInfo.numShotsL0 = int(slsplit[0])
        self.GlobalInfo.repRateL0 = int(slsplit[1])
        self.GlobalInfo.numShotsL1 = int(slsplit[2])
        self.GlobalInfo.repRateL1 = int(slsplit[3])
        self.GlobalInfo.numDataSets = int(slsplit[4])

    def _read_dataset_descriptors(self, fp: IO[bytes], encoding: str):
        """Read and parse dataset descriptor lines."""
        # read dataset descriptor lines
        for _ in range(self.GlobalInfo.numDataSets):
            varline = fp.readline().decode(encoding)
            if not varline:
                raise EOFError("Unexpected EOF while reading dataset descriptors")
            self.dataSet.append(dataSet(varline))

        # read blank/terminator line
        fp.readline()

    def _read_and_process_datasets(self, fp: IO[bytes]):
        """Read binary data and compute physical data for each dataset."""
        # read binary data for each dataset — safer: read exact bytes and use frombuffer
        for i in range(self.GlobalInfo.numDataSets):
            if i > 0:
                # separator CRLF between datasets (kept as bytes)
                fp.read(2)
            numBins = self.dataSet[i].numBins
            if numBins > 0:
                nbytes = int(numBins) * 4
                buf = fp.read(nbytes)
                if len(buf) != nbytes:
                    raise EOFError(f"Unexpected EOF reading dataset {i}: expected {nbytes} bytes, got {len(buf)}")
                arr = np.frombuffer(buf, dtype=np.uint32, count=numBins).copy()
            else:
                arr = np.zeros(0, dtype=np.uint32)
            self.dataSet[i].rawData = arr
            self.shortDescr.append(self.dataSet[i].getShortDescr())

            # compute physical scaling with guards
            shots = self.dataSet[i].numShots if self.dataSet[i].numShots > 0 else 1
            scale = 1.0 / shots

            if self.dataSet[i].dataType == 0 and self.dataSet[i].ADCBits > 0:
                maxbits = (2 ** int(self.dataSet[i].ADCBits)) - 1
                if maxbits > 0:
                    scale *= (self.dataSet[i].inputRange / maxbits)
                self.dataSet[i].physData = np.array(scale * self.dataSet[i].rawData, dtype=np.float64)
            elif self.dataSet[i].dataType == 1:
                # photon counting
                if self.dataSet[i].binWidth > 0:
                    scale *= (150.0 / self.dataSet[i].binWidth)
                self.dataSet[i].physData = np.array(scale * self.dataSet[i].rawData, dtype=np.float64)
            elif self.dataSet[i].dataType == 2:
                # analog squared
                maxbits = (2 ** int(self.dataSet[i].ADCBits)) - 1 if self.dataSet[i].ADCBits > 0 else 1
                n = shots
                sq_n_1 = np.sqrt(self.dataSet[i].numShots - 1) if (self.dataSet[i].numShots > 1) else 1.0
                denom = (n * sq_n_1 * maxbits) if maxbits > 0 else (n * sq_n_1)
                if denom != 0:
                    scale = self.dataSet[i].inputRange / denom
                else:
                    scale = 0.0
                self.dataSet[i].physData = np.array(scale * self.dataSet[i].rawData, dtype=np.float64)
            elif self.dataSet[i].dataType == 3:
                # photon counting squared
                denom = np.sqrt(self.dataSet[i].numShots - 1) if (self.dataSet[i].numShots > 1) else 1.0
                if self.dataSet[i].binWidth > 0 and denom != 0:
                    scale *= (150.0 / self.dataSet[i].binWidth) / denom
                else:
                    scale = 0.0
                self.dataSet[i].physData = np.array(scale * self.dataSet[i].rawData, dtype=np.float64)
            else:
                self.dataSet[i].physData = np.array(scale * self.dataSet[i].rawData, dtype=np.float64)

        _term = fp.read(2)
        # term is bytes, typically b'\r\n' — not fatal if different






