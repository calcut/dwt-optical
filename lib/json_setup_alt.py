import os
import json
import logging
from pathlib import Path

from numpy import append

alt_instrument = { 
    'name'              : 'alt_instrument',
    'category'          : 'instrument',
    'light Source'      : 'Stellarnet LED White',
    'spectrometer'      : 'Stellarnet BlueWave VIS-25',
}

alt_layout = {
    'name'      : 'alt_layout',
    'category'  : 'layout',
    'map'       : {
            'A01'   : [0.1, 0.1],
            'A02'   : [0.1, 0.2],
            'B01'   : [0.2, 0.1],
            'B02'   : [0.2, 0.2],
            'C01'   : [0.3, 0.1],
            'C02'   : [0.3, 0.2],
    }
}

alt_structure_map ={
    'name'          : 'alt_structure_map',
    'category'      : 'structure_map',
    'valid_layout'  : 'alt_layout',
    'map' : {
        #Element : [material, detail]
        'A01'    : ['Al', '100nm x 100nm x 50 squares, 300 nm pitch'],
        'A02'    : ['Au', '100nm x 100nm x 50 squares, 300 nm pitch'],
        'B01'    : ['Al', '100nm x 100nm x 50 squares, 300 nm pitch'],
        'B02'    : ['Au', '100nm x 100nm x 50 squares, 300 nm pitch'],
        'C01'    : ['Al', '100nm x 100nm x 50 squares, 300 nm pitch'],
        'C02'    : ['Au', '100nm x 100nm x 50 squares, 300 nm pitch'],
    }
}

alt_surface_map ={
    'name'          : 'alt_surface_map',
    'category'      : 'surface_map',
    'valid_layout'  : 'alt_layout',
    'map' : {
        #Element : [surface, detail]
        'A01'    : ['None', ''],
        'A02'    : ['None', ''],
        'B01'    : ['HMDS', 'Hexamethyldisilazane'],
        'B02'    : ['DT',   '1-decanethiol'],
        'C01'    : ['PEG',  '2-[methoxy(polyethyleneoxy)6-9propyl] trimethoxysilane'],
        'C02'    : ['PFDT', 'perfluoro-1-decanethiol'],
    }
}

alt_sensor = {
    'name'          : 'alt_sensor',
    'category'      : 'sensor',
    'layout'        : alt_layout,
    'structure_map'   : alt_structure_map,
    'surface_map'   : alt_surface_map,
}

alt_input_config = {
    'name'              : 'alt_input_config',
    'category'          : 'input_config',
    'fluids'            : ['waterA', 'waterB', 'waterC'],
    'elements'          : 'all',
    'repeats'           : 3,
    'wavelength_range'  : [400, 420, 0.5], #start, stop, step
    'integration_time'  : 10,
    'scans_to_avg'      : 1,
    'x_smooth'          : 0,
    'x_timing'          : 1,   
}

alt_output_config = {
    'name'               : 'alt_output_config',
    'category'           : 'output_config',
                           #Enabled, parameters
    'wavelength_range'   : [True, 540, 730], # wl_min = 540, wl_max = 730
    'smooth'             : [True, 3], # smooth_points = 3
    'interpolate'        : [True, 1],  # sample_rate = 1
    'normalise'          : [True],
    'round'              : [True, 3], 
    'outfile'            : None,
}

alt_metadata_columns = {
    'name'              : 'alt_metadata_columns',
    # Column            : #Datatype
    'index'             : 'string',
    'date'              : 'datetime64[ns]',
    'instrument'        : 'string',
    'sensor'            : 'string',
    'element'           : 'string',
    'structure'         : 'string',
    'surface'           : 'string',
    'fluid'             : 'string',
    'repeats'           : 'Int64',
    'comment'           : 'string',
}

# Example of a setup data structure
alt_setup = {
    'name'              : 'alt_setup',
    'category'          : 'setup',
    'metafile'          : 'index.txt',
    'datadir'           : 'dummydata',
    'subdirs'           : ['sensor', 'fluid'], #Directory structure for data.txt files
    'primary_metadata'  : ['sensor', 'element', 'fluid'], #Determines data filenames
    'instrument'        : alt_instrument,
    'sensor'            : alt_sensor,
    'input_config'      : alt_input_config,
    'output_config'     : alt_output_config,
}



def testing(dictionary, hierarchy=None):

    dictionary_list = [dictionary]

    if not hierarchy:
        hierarchy = []
    else:
        hierarchy.append(f'level {len(hierarchy)}')

    for key, setting in dictionary.items():
        if type(setting) == dict:
            # If any subdictionaries have their own 'name' field
            if 'name' in setting:
                # Replace the subdictionary with just its name
                dictionary[key] = setting['name']
                
                # Recursively call this function to split out any sub dictionaries
                sub_dicts = testing(setting)

                # concatenate dictionaries into the list
                dictionary_list += sub_dicts

    return dictionary_list, hierarchy


def setup_to_flat(dictionary):

    dictionary_list = [dictionary]

    for key, setting in dictionary.items():
        if type(setting) == dict:
            # If any subdictionaries have their own 'name' field
            if 'name' in setting:
                # Replace the subdictionary with its name and a * to indicate
                # it needs to be expanded
                dictionary[key] = '*'+setting['name']
                # Recursively call this function to split out any sub dictionaries
                sub_dicts = setup_to_flat(setting)

                # concatenate dictionaries into the list
                dictionary_list += sub_dicts

    return dictionary_list


def dict_to_json(dictionary, path, overwrite=False):

    # Copy to avoid modifying original dictionary
    dictionary = dictionary.copy()
    logging.debug(f'making dir {path}')
    os.makedirs(path, exist_ok=True)
    for key, setting in dictionary.items():
        if type(setting) == dict:
            # If any subdictionaries have their own 'name' field
            if 'name' in setting:
                # Replace the subdictionary with its name and a * to indicate
                # it needs to be expanded
                dictionary[key] = '*'+setting['name']
                subpath = os.path.join(path, key)
                # Recursively call this function to store the subdictionary
                dict_to_json(setting, subpath, overwrite=overwrite)

    # After any subdictionaries have been dealt with, store this dictionary
    json_path = os.path.join(path, f"{dictionary['name']}.json")
    if os.path.exists(json_path):
        if overwrite:
            logging.warning(f'File exists: {json_path}, overwriting')
        else:
            logging.warning(f'File exists: {json_path}, did not overwrite')
            return

        
    with open(json_path, 'w') as f:
        json.dump(dictionary, f, ensure_ascii=False, indent=3)


def json_to_dict(filepath):
        
    logging.debug(f'reading file {filepath}')
    try:
        with open(filepath, 'r') as f:
            dictionary = json.load(f)
    except FileNotFoundError as e:
        logging.error(f"{filepath} not found")
        return f"ERROR {filepath} not found"
        
    # Check if any of the dictionary settings are really sub-dictionaries
    # that need to be populated
    for key, setting in dictionary.items():
        if type(setting) == str:
            if setting[0] == '*':
                setting = setting[1:]
                subpath = os.path.join(os.path.dirname(filepath), key)
            # if os.path.exists(subpath):

                sub_json = os.path.join(subpath, setting+'.json')
                logging.debug(f'Populating {key}:')
                
                # Recursively call this function to populate the sub-dictionary
                dictionary[key] = json_to_dict(sub_json)

    return dictionary

def get_file_choice(path):
    choice_dict = {}
    for (dirpath, dirnames, filenames) in os.walk(path):
        basename = os.path.basename(dirpath)
        names = []

        # Remove the extension e.g .json
        for f in filenames:
            names.append(Path(f).stem)
        choice_dict[basename] = names  

    return choice_dict
        
    
if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO)


    path = "/Users/calum/spectrometer/setup"
    dict_to_json(alt_setup, path, overwrite=True)

    d = json_to_dict("/Users/calum/spectrometer/setup/alt_setup.json")
    print(json.dumps(d, indent=3))

    d = setup_to_flat(alt_setup)

    for dict in d:
        print(dict)
        print("")