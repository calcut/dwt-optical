import numpy as np
import pandas as pd
import os
from datetime import datetime
import h5_helpers as h5
import csv_helpers as csv
import string
import shutil


instrument = {
    'name'              : 'Lab_setup_02',
    'sensor'            : 'DUM01',
    'element_rows'      : 4,
    'element_cols'      : 4,   
    'light Source'      : 'Stellarnet LED White',
    'spectrometer'      : 'Stellarnet BlueWave VIS-25'
}

# Set up parameters describing a run of measurements
# Affects how much data is generated in the dummy data function
defaults = {
    'filename'          : 'test.hdf5',
    'output_dir'        : './dummydata',
    'instrument'        : instrument,
    'fluid_list'        : ['water', 'beer1', 'beer2'],
    'wavelength_range'  : [400, 420, 0.5], #start, stop, step
    'elements'          : 'all', #Alternatively, a list of element names
    'repeats'           : 3,
}


# Returns a list of element indicies for a X by Y sensor array
# e.g. 2x2 would give [A01, A02, B01, B02]
# (This may be better as a method of a class called Instrument or Sensor)
def get_element_list(rows, cols):
	row_list = range(1, rows+1)
	col_list = list(string.ascii_uppercase[:cols])
	element_list = []
	for x, y in [(x,y) for x in col_list for y in row_list]:
		element_list.append(F"{x}{y:02d}")
	return element_list

def dummyMeasurement(run):
    dummywavelength = list(np.arange(run['wavelength_range'][0], #start
                                    run['wavelength_range'][1],  #stop
                                    run['wavelength_range'][2])) #step

    #Intentionally remove some data points from the end of the list
    missing_samples = np.random.randint(1,10)
    dummywavelength = dummywavelength[:-missing_samples]

    size = len(dummywavelength)
    dummydata = list(np.random.random_sample(size))
    dummycsv = {'wavelength' : dummywavelength, 'transmission' : dummydata}
    df = pd.DataFrame(data=dummycsv, dtype=np.float32)
    return df

def fill_hdf(run):
    #'run' is a dictionary of the same format as 'defaults'
    metadata = {}
    if os.path.exists(run['filename']):
        os.remove(run['filename'])

    if run['elements'] == 'all':
        elements = get_element_list(instrument['element_rows'],instrument['element_cols'])
    else:
        elements = run['elements']

    date = datetime.utcnow().strftime('%Y_%m_%d')
    run['measuredOn'] = date

    metadata['instrument'] = instrument['name']

    for f in run['fluid_list']:
        metadata['fluid'] = str(f)

        for e in elements:
            metadata['element_index'] = str(e)

            for r in range(run['repeats']):
                rep = r+1 # Start counting at 1 not 0
                metadata['repeat'] = str(rep)

                hdfkey = F"{instrument['name']}/_{date}/{f}/{e}_rep{rep}"
                df = dummyMeasurement(run)
                df.rename(columns={"transmission" : F"{f}_rep{rep}"}, inplace=True)
                metadata['timestamp'] = datetime.timestamp(datetime.now())
                h5.store(run['filename'], hdfkey, df, metadata)



def generate_tsv(run, append=True):
    #'run' is a dictionary of the same format as 'defaults'
    metadata = {}
    if not append:
        if os.path.exists(run['output_dir']):
            shutil.rmtree(run['output_dir'])

    if run['elements'] == 'all':
        elements = get_element_list(instrument['element_rows'],instrument['element_cols'])
    else:
        elements = run['elements']

    metadata['sensor'] = run['instrument']['sensor']
    metadata['instrument'] = run['instrument']['name']

    for f in run['fluid_list']:
        metadata['fluid'] = str(f)

        for e in elements:
            metadata['element'] = str(e)

            for r in range(run['repeats']):
                stamp = pd.Timestamp.utcnow().timestamp()
                metadata['timestamp'] = stamp
                df = dummyMeasurement(run)
                df.rename(columns={"transmission" : F"{stamp}"}, inplace=True)
                csv.store(df, metadata, path=run['output_dir'])