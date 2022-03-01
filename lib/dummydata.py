import numpy as np
import pandas as pd
import os
from datetime import datetime
import lib.csv_helpers as csv
import string
import shutil
import random


instrument = {
    'name'              : 'Lab_setup_02',
    'sensor'            : 'DUM01',
    'element_rows'      : 4,
    'element_cols'      : 4,
    'chemistry_map'     : None,
    'light Source'      : 'Stellarnet LED White',
    'spectrometer'      : 'Stellarnet BlueWave VIS-25'
}

# Set up parameters describing a run of measurements
# Affects how much data is generated in the dummy data function
defaults = {
    'output_dir'        : './dummydata',
    'instrument'        : instrument,
    'fluid_list'        : ['water', 'beer1', 'beer2'],
    'wavelength_range'  : [400, 420, 0.5], #start, stop, step
    'elements'          : 'all', #Alternatively, a list of element names
    'repeats'           : 3,
}

def dummyChemistry(run):
  
    chemistry_map = {}
    rows = run['instrument']['element_rows']
    cols = run['instrument']['element_rows']
    num_elements = rows * cols

    elements = get_element_list(rows,cols)

    for e in elements:
        chemistry_map[e] = random.choice(chemistries_list)
    return chemistry_map


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

def generate_tsv(run, append=False):
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
            metadata['chemistry'] = run['instrument']['chemistry_map'][str(e)]
            for r in range(run['repeats']):
                stamp = round(pd.Timestamp.utcnow().timestamp())
                metadata['timestamp'] = stamp
                df = dummyMeasurement(run)
                df.rename(columns={"transmission" : F"{stamp}"}, inplace=True)
                csv.store(df, metadata, path=run['output_dir'])

chemistries_list = [
 'Hydrogen',
 'Helium',
 'Lithium',
 'Beryllium',
 'Boron',
 'Carbon',
 'Nitrogen',
 'Oxygen',
 'Fluorine',
 'Neon',
 'Sodium',
 'Magnesium',
 'Aluminium',
 'Silicon',
 'Phosphorus',
 'Sulfur',
 'Chlorine',
 'Argon',
 'Potassium',
 'Calcium',
 'Scandium',
 'Titanium',
 'Vanadium',
 'Chromium',
 'Manganese',
 'Iron',
 'Cobalt',
 'Nickel',
 'Copper',
 'Zinc',
 'Gallium',
 'Germanium',
 'Arsenic',
 'Selenium',
 'Bromine',
 'Krypton',
 'Rubidium',
 'Strontium',
 'Yttrium',
 'Zirconium',
 'Niobium',
 'Molybdenum',
 'Technetium',
 'Ruthenium',
 'Rhodium',
 'Palladium',
 'Silver',
 'Cadmium',
 'Indium',
 'Tin',
 'Antimony',
 'Tellurium',
 'Iodine',
 'Xenon',
 'Cesium',
 'Barium',
 'Lanthanum',
 'Cerium',
 'Praseodymium',
 'Neodymium']