
# Import the USB driver
import stellarnet_driver3 as sn
import time

# Import the logging module 
import logging
logging.basicConfig(format='%(asctime)s %(message)s')

# Function definition to get data
def getSpectrum(spectrometer, wav):
    logging.warning('requesting spectrum')
    spectrum = sn.array_spectrum(spectrometer, wav)
    logging.warning('received spectrum')
    return spectrum

# Function definition to set parameters
def setParam(spectrometer, wav, inttime, scansavg, smooth, xtiming):
	logging.warning('Setting Parameters----------------------------------------------------------------------------------')
	spectrometer['device'].set_config(int_time=inttime, scans_to_avg=scansavg, x_smooth=smooth, x_timing=xtiming)

# Function definition to reset hardware by using """Destructor. Release device resources."""  Make sure to call "spectrometer, wav = sn.array_get_spec(0)" to init spectrometer again
def reset(spectrometer):
	spectrometer['device'].__del__()

# Function definition to Enable or Disable Ext Trigger by Passing True or False. If pass True then Timeout function will be disabled. This allows the user to enable/disbale the timeout function.
# The recommended default setting is False unless an external trigger is being used. Alternatively, when using the hardware trigger, the setting should be True.
def external_trigger(spectrometer,trigger):
	sn.ext_trig(spectrometer,trigger)

# This resturns a Version number of compilation date of driver
version = sn.version()
print(version)	

# init Spectrometer
spectrometer, wav = sn.array_get_spec(0) # 0 for first channel and 1 for second channel , up to 127 spectrometers

# Device parameters to set       
inttime = 50
scansavg = 1
smooth = 0
xtiming = 3

# Get current device parameters
currentParam = spectrometer['device'].get_config() 

# Call to Enable or Disable External Trigger. Default is Disable=False
external_trigger(spectrometer,False)

# List of int_time for loop
int_time_l = [ 2, 4, 7, 15, 30, 60, 120, 240, 480]

# Loop through to save user time
for loopCnt in range(100):
    print('Test LoopCnt = ' + str(loopCnt))
    all_data = [ ]
    
    # Loop through several inttime settings
    for inttime in int_time_l:
        currentParam = spectrometer['device'].get_config()
        # Check to see any parameters change, id so call setParam
        if ((currentParam['int_time'] != inttime) or (currentParam['scans_to_avg'] != scansavg) or (currentParam['x_smooth'] != smooth) or (currentParam['x_timing'] != xtiming)):
            setParam(spectrometer, wav, inttime, scansavg, smooth, xtiming)
            
            # Only call this function on first call to get spectrum  and when you change any parameters i.e inttime, scansavg, smooth, also call
            # getSpectrum twice after this call as first time the data may not be true due to interruption of clock so we throw away the first scan.
            for i  in range (2): # Call getSpectrum twice and discard first one!
                data=getSpectrum(spectrometer, wav)   
        else:       	  
            data=getSpectrum(spectrometer, wav)# if no parameters change, just get data once

        # Wait for X seconds
        #time.sleep(0.4)

        # Increasing sleep time extends number of loops between errors.
        # 0 seconds observes errors within 10 loops in Pattern test system
        # 0.1 seconds will still observe errors, but varied between 5 and 71 loops in testing
        # 1 second allows all 100 loops to pass
        
        # Tested with the light cap on the spectrometer, bad samples will show values 0 through 64K.
        
        # Device must be fully reset to remove random noisy samples
        
        # Store data
        all_data.append(data.copy())
        
        
    # Print all data/spect
    maxOddCnt = 0
    for i in range(len(all_data)):
        oddCnt = sum(i[1] > 10000 for i in all_data[i])
        print('Data from int_time ' + str(int_time_l[i]) + ' us has ' + str(oddCnt) + ' data points > 10k')
        print(all_data[i][:512,1])#now you get 2048 data points for NIR inGaAs also but only first 512 pizels are valid rest are garbabge so croping them out 
        if (oddCnt > maxOddCnt):
            maxOddCnt = oddCnt
    
    if (maxOddCnt > 0):
        break
