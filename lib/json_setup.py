import os
import json
import logging

default_instrument = { 
    'name'              : 'default_instrument',
    'light Source'      : 'Stellarnet LED White',
    'spectrometer'      : 'Stellarnet BlueWave VIS-25',
}

default_layout = {
    'name'  : 'default_layout',
    'A01'   : [0.1, 0.1],
    'A02'   : [0.1, 0.2],
    'B01'   : [0.2, 0.1],
    'B02'   : [0.2, 0.2],
    'C01'   : [0.3, 0.1],
    'C02'   : [0.3, 0.2],
}

default_element_map ={
    'name'          : 'default_element_array',
    'valid_layout'  : 'default_layout',

    #Element : [material, detail]
    'A01'    : ['Al', '100nm x 100nm x 50 squares, 300 nm pitch'],
    'A02'    : ['Au', '100nm x 100nm x 50 squares, 300 nm pitch'],
    'B01'    : ['Al', '100nm x 100nm x 50 squares, 300 nm pitch'],
    'B02'    : ['Au', '100nm x 100nm x 50 squares, 300 nm pitch'],
    'C01'    : ['Al', '100nm x 100nm x 50 squares, 300 nm pitch'],
    'C02'    : ['Au', '100nm x 100nm x 50 squares, 300 nm pitch'],
    }

default_surface_map ={
    'name'          : 'default_surface_map',
    'valid_layout'  : 'default_layout',

    #Element : [surface, detail]
    'A01'    : None,
    'A02'    : None,
    'B01'    : ['HMDS', 'Hexamethyldisilazane'],
    'B02'    : ['DT',   '1-decanethiol'],
    'C01'    : ['PEG',  '2-[methoxy(polyethyleneoxy)6-9propyl] trimethoxysilane'],
    'C02'    : ['PFDT', 'perfluoro-1-decanethiol'],
    }

default_sensor = {
    'name'          : 'default_sensor',
    'layout'        : default_layout,
    'element_map'   : default_element_map,
    'surface_map'   : default_surface_map,
}

default_input_config = {
    'name'              : 'default_input_config',
    'fluids'            : ['waterA', 'waterB', 'waterC'],
    'elements'          : 'all',
    'repeats'           : 3,
    'wavelength_range'  : [400, 420, 0.5], #start, stop, step
    'integration_time'  : 10,
    'scans_to_avg'      : 1,
    'x_smooth'          : 0,
    'x_timing'          : 1,   
}

default_output_config = {
    'name'               : 'default_output_config',
                           #Enabled, parameters
    'wavelength_range'   : [True, 540, 730], # wl_min = 540, wl_max = 730
    'smooth'             : [True, 3], # smooth_points = 3
    'interpolate'        : [True, 1],  # sample_rate = 1
    'normalise'          : [True],
    'round'              : [True, 3], 
    'outfile'            : None,
}

default_metadata_columns = {
    'name'              : 'default_metadata_columns',
    # Column            : #Datatype
    'index'             : 'string',
    'date'              : 'datetime64[ns]',
    'instrument'        : 'string',
    'sensor'            : 'string',
    'element'           : 'string',
    'surface'           : 'string',
    'fluid'             : 'string',
    'repeats'           : 'Int64',
    'comment'           : 'string',
}

# Example of a setup data structure
default_setup = {
    'name'              : 'default_setup',
    'metafile'          : 'index.txt',
    'path'              : 'dummydata',
    'subdirs'           : ['sensor', 'fluid'], #Directory structure for data.txt files
    'primary_metadata'  : ['sensor', 'element', 'fluid'], #Determines data filenames
    'instrument'        : default_instrument,
    'sensor'            : default_sensor,
    'input_config'      : default_input_config,
    'output_config'     : default_output_config,
}

def setup_to_flat(dictionary):

    dictionary_list = [dictionary]

    for key, setting in dictionary.items():
        if type(setting) == dict:

            # Replace the subdictionary with just its name
            dictionary[key] = setting['name']
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

            # Replace the subdictionary with just its name
            dictionary[key] = setting['name']
            subpath = os.path.join(path, f'{key}s')
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
        subpath = os.path.join(os.path.dirname(filepath), key+'s')
        
        if os.path.exists(subpath):

            sub_json = os.path.join(subpath, setting+'.json')
            logging.debug(f'Populating {key}:')
            
            # Recursively call this function to populate the sub-dictionary
            dictionary[key] = json_to_dict(sub_json)

    return dictionary
        
    
if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO)


    path = "/Users/calum/spectrometer/testing/setup"
    dict_to_json(default_setup, path, overwrite=True)

    d = json_to_dict("/Users/calum/spectrometer/testing/setup/default_setup.json")
    print(json.dumps(d, indent=3))

    d = setup_to_flat(default_setup)

    for dict in d:
        print(dict)
        print("")