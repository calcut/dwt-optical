import os
import json

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

def save_setup(setup):

    setup["path"] = "/Users/calum/spectrometer/testing"

    setup_path = os.path.join(setup['path'],'setup')

    dict_to_json(setup, setup_path)

    # for key, config in setup.items():
    #     if type(config) == dict:
    #         path = os.path.join(setup_path, f'{key}s')
    #         os.makedirs(path, exist_ok=True)
    #         print(f'dir {path}')

    #         for subkey, subconfig in config.items():
    #             if type(subconfig) == dict:
    #                 config[subkey] = subconfig['name']
    #                 subpath = os.path.join(path, f'{subkey}s')
    #                 os.makedirs(subpath, exist_ok=True)
    #                 print(f'dir {subpath}')
    #                 json_path = os.path.join(subpath, f"{subconfig['name']}.json")
    #                 with open(json_path, 'w') as f:
    #                     json.dump(subconfig, f, ensure_ascii=False, indent=3)

    #         json_path = os.path.join(path, f"{config['name']}.json")
    #         with open(json_path, 'w') as f:
    #             json.dump(config, f, ensure_ascii=False, indent=3)

def dict_to_json(dictionary, path):
    print(f'making dir {path}')
    os.makedirs(path, exist_ok=True)
    for key, config in dictionary.items():
        if type(config) == dict:
            dictionary[key] = config['name']
            subpath = os.path.join(path, f'{key}s')
            dict_to_json(config, subpath)

        json_path = os.path.join(path, f"{dictionary['name']}.json")
        with open(json_path, 'w') as f:
            json.dump(dictionary, f, ensure_ascii=False, indent=3)


    
    # instrument_path = os.path.join(setup_path,'instruments')
    # input_config_path = os.path.join(setup_path,'input_configs')
    # output_config_path = os.path.join(setup_path,'output_configs')
    # sensor_path = os.path.join(setup_path,'sensors')
    # surface_map_path = os.path.join(sensor_path,'layouts')
    # surface_map_path = os.path.join(sensor_path,'element_maps')
    # surface_map_path = os.path.join(sensor_path,'surface_maps')





    # os.makedirs(os.path.dirname(setup_path), exist_ok=True)

    # if not os.path.isfile(setup_path):
    #     with open(setup_path, 'w') as f:
    #         json.dump(setup_mod, f, ensure_ascii=False, indent=3)
    # else:
    #     logging.warning('File exists, did not write')
    



if __name__ == "__main__":
    save_setup(default_setup)