#import stellarnet_driver.so
import stellarnet_driver3 as sn

#function to get spectrum
def getSpectrum(spectrometer, wav):
    spectrum = sn.array_spectrum(spectrometer, wav)
    return spectrum
#function to set parameters
def setparam(spectrometer, wav, inttime, xtiming, scansavg, smooth):

    spectrometer['device'].set_config(
        int_time=inttime,
        x_timing=xtiming,
        scans_to_avg=scansavg,
        x_smooth=smooth)
    

#init spectrometer,0 represents 1st channel if multiple device connected you can select devices by
#changing argument
spectrometer,wav = sn.array_get_spec(0)
#wav = sn.wav_ret(0)
#Parameter to set, change values here        
inttime = 1000
scansavg = 3
smooth = 3
xtiming = 1

#call to set parameters
setparam(spectrometer, wav, inttime, xtiming, scansavg, smooth)
#call to get data
data = getSpectrum(spectrometer, wav)
print(data)