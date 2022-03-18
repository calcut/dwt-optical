from cProfile import run
from curses import meta
from sys import meta_path
import pandas as pd
import numpy as np
import os
import re
import json
import shutil
import copy
from IPython.display import display
import logging

logging.basicConfig(level=logging.INFO)


# Example of an instrument data structure
instrument = { 
    'name'              : 'instrument01',
    'sensor'            : 'DUM01',
    'element_map'       : { 
                        #Element : #Surface
                            'A01': 'Al',        # Aluminium
                            'A02': 'Au',        # Gold
                            'B01': 'Al-HMDS',   # Aluminium Hexamethyldisilazane
                            'B02': 'Au-DT',     # Gold 1-decanethiol
                            'C01': 'Al-PEG',    # Aluminium 2-[methoxy(polyethyleneoxy)6–9propyl] trimethoxysilane
                            'C02': 'Au-PFDT',   # Gold perfluoro-1-decanethiol
                            },
    'light Source'      : 'Stellarnet LED White',
    'spectrometer'      : 'Stellarnet BlueWave VIS-25',
}

# Example of a setup data structure
default_setup = {
    'metafile'          : 'index.txt',
    'path'              : 'dummydata',
    'subdirs'           : ['instrument', 'fluid'], #Directory structure for data.txt files
    'fluids'            : ['waterA', 'waterB', 'waterC'],
    'elements'          : 'all',
    'repeats'           : 3,
    'wavelength_range'  : [400, 420, 0.5], #start, stop, step
    'primary_metadata'  : ['instrument', 'element', 'fluid'],
    'comment'           : '', #To be added to the metadata
    'instrument'        : instrument,
}

metadata_columns = {
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

def get_default_setup():
    new_setup = copy.deepcopy(default_setup)
    return new_setup

def dummy_measurement(setup, row):
    
    #For a real instrument, may wish to adjust/move based on row['element']

    dummywavelength = list(np.arange(setup['wavelength_range'][0], #start
                                    setup['wavelength_range'][1],  #stop
                                    setup['wavelength_range'][2])) #step

    size = len(dummywavelength)
    dummydata = list(np.random.random_sample(size))
    dummycsv = {'wavelength' : dummywavelength, 'transmission' : dummydata}
    df = pd.DataFrame(data=dummycsv, dtype=np.float32)

    timestamp = pd.Timestamp.utcnow().timestamp()
    df.rename(columns={"transmission" : timestamp }, inplace=True)
    return df

def simple_measurement(setup, element, fluid, measure_func, merge=True, comment=pd.NA):

    #sanitise comment parameter
    if comment == '':
        comment = pd.NA
    
    run_dict = {
        'date'          : pd.Timestamp.utcnow().strftime('%Y-%m-%d'),
        'instrument'    : setup['instrument']['name'],
        'sensor'        : setup['instrument']['sensor'],
        'element'       : element,
        'surface'       : setup['instrument']['element_map'][element],
        'fluid'         : fluid,
        'repeats'       : 1,
        'comment'       : comment
    }
    index = '-'.join(run_dict[p] for p in setup['primary_metadata'])
    run_dict['index'] = index

    # Convert to pandas series, which allows datatype to be specified
    for col in run_dict.keys():
        run_dict[col] = pd.Series([run_dict[col]], dtype=metadata_columns[col])
        # run_dict[col] = pd.Series([run_dict[col]], dtype=str)
        
    # Convert to dataframe, this enables it to be concatenated with an existing
    # meta_df
    run_df = pd.DataFrame(run_dict)
    run_df.set_index('index', inplace=True)


    run_measure(setup, run_df, measure_func, merge=merge)

    datapath = find_datapath(setup, run_df, index)
    df = pd.read_csv(datapath, sep='\t')
    return df


def find_datapath(setup, meta_df, row_index):
    '''
    Extrapolates the path to the actual data file, using the subdirectories
    specified in setup{}
    '''
    subdir=[]
    for s in setup['subdirs']:
        subdir.append(meta_df.loc[row_index][s])
    subdir = os.path.join(*subdir)
    datapath = os.path.join(setup['path'], subdir, f'{row_index}.txt')
    return datapath


def merge_dataframes(setup, meta_df):
    '''
    Extracts dataframes from files and merges them into a single dataframe
    Requires a metadata frame to know which measurements to select
    Columns are renamed to show only the relevant metadata
    Outer join means that rows from all dataframes are preserved, and NaN is
    filled where needed
    '''
    result = []

    primary_meta = setup['primary_metadata']

    # For re-labelling the merged dataframe:
    # Ignore metadata that is the same for measurements
    # i.e. only use columns with more than 1 unique value
    individual_meta = meta_df.columns[meta_df.nunique() > 1]

    # Ignore columns which aren't considered primary metadata
    individual_meta = individual_meta.intersection(primary_meta)

    # Identify primary metadata that is common for all measurements
    common_metadata = set(primary_meta) - set(individual_meta)

    for row in meta_df.index:

        # locate the datafile and read it in
        datapath = find_datapath(setup, meta_df, row)
        df = pd.read_csv(datapath, sep='\t')

        # Name the output columns based on metadata
        col_names = ['wavelength']
        n=0
        for col in df.columns[1:]:
            n += 1
            if len(individual_meta) > 0:
                name = '_'.join(meta_df.loc[row][i] for i in individual_meta)
                col_names.append(f'{name}_rep{n:02d}')
            else:
                col_names.append(f'rep{n:02d}')
        df.columns = col_names

        # Accumulate the dataframes in a large 'result' dataframe
        if len(result) > 0:
            result = pd.merge(result, df, how='outer', on='wavelength')
        else:
            result = df

    title = str()
    for field in common_metadata:
        value = f'{meta_df.iloc[0][field]}'
        title += f'{field}: {value}\n'
    title = title[:-1]

    return result, title
    

def select_from_metadata(metakey, metavalue, meta_df, regex=False):
    
    try:
        meta_df[metakey]
    except KeyError:
        logging.error(f'Key "{metakey}" not found in dataframe')
        return pd.DataFrame()

    if regex:
        logging.info(f'filtering by metadata "{metakey}" containing "{metavalue}"')
        regexdf = meta_df[meta_df[metakey].astype(str).str.contains(str(metavalue))]
        return(regexdf)
    else:
        logging.info(f'filtering by metadata "{metakey}" == "{metavalue}"')
        exactdf = meta_df.loc[meta_df[metakey].astype(str) == str(metavalue)]
        return(exactdf)


def export_dataframes(setup, meta_df=None, outfile=None, dp=None):

    if isinstance(meta_df, pd.DataFrame):
        pass
    else:
        meta_df = read_metadata(setup)

    elements = sorted(meta_df['element'].unique())
    frames=[]
    for e in elements:
        logging.info(f'merging element {e}')
        selection = select_from_metadata('element', e, meta_df)
        element_df, title = merge_dataframes(setup, selection)

        #If a DataProcessor object has been provided, apply processing here.
        if dp:
            element_df = dp.process_dataframe(element_df)

        element_df = element_df.transpose()

        surfaces = meta_df[meta_df['element'] == e]['surface'].drop_duplicates().tolist()
        surface = surfaces[0]
        if len(surfaces) > 1:
            logging.error(f'Error, multiple surfaces {surfaces} found for element {e}')
            return

        header_row_names = ['Surface', 'Element', 'Wavelength']
        header_rows= [[f'{surface}'],[F'{e}'], element_df.loc['wavelength']]
        col_ix = pd.MultiIndex.from_product(header_rows, names = header_row_names)

        element_df.columns = col_ix
        element_df.drop('wavelength', inplace=True)
        frames.append(element_df)


    exportframe = pd.concat(frames, axis=1)
    if outfile:
        logging.info(f"Writing to {outfile} ...")
        exportframe.to_csv(outfile, sep='\t', na_rep='NA')
        logging.info(f"Done")
    return exportframe


def import_dir_to_csv(setup, input_dir, regex, separator='\t', merge=True):

    '''
    regex can optionally identify the following fields:
        'date'      
        'instrument'
        'sensor'    
        'element'   
        'surface'   
        'fluid'     
        'repeats'   
        'comment'   

    If they aren't identified by the regex, they should be present in the
    setup{} dictionary, e.g:

    setup{ 
        'metafile'          : 'index.txt',
        'path'              : 'dummydata',
        'subdirs'           : ['sensor', 'fluid'],
        'elements'          : ['xxx']
        'fluids'            : ['xxx']
        'primary_metadata'  : ['instrument', 'element', 'fluid'],
        'instrument'        : {
                                'name'  : 'xxxxx'
                                'sensor : 'xxxxx'
                                'element_map' : {'xxx' : 'surface-XX'}
                               }
        }
    '''

    if not os.path.exists(input_dir):
        logging.error('import folder not found')
        return

    for filename in sorted(os.listdir(input_dir)):
        
        match = re.search(regex, filename)
        if not match:
            logging.warning(F"regex not matched on filename: {filename}")
            continue

        # Create a metadata dictionary with info extracted from filename
        run_dict = match.groupdict()

        # If the element looks like an integer,
        # convert to a string with zero padding
        try: 
            e = int(run_dict['element'])
            run_dict['element'] = F"{e:02d}"
        except ValueError:
            #Otherwise, don't modify it
            pass

        if 'date' not in run_dict:
            run_dict['date'] = pd.Timestamp.utcnow().strftime('%Y-%m-%d')

        if 'instrument' not in run_dict:
            run_dict['instrument'] = setup['instrument']['name']

        if 'sensor' not in run_dict:
            run_dict['sensor'] = setup['instrument']['sensor']

        if 'element' not in run_dict:
            run_dict['element'] = setup['elements'][0]

        if 'surface' not in run_dict:
            run_dict['surface'] = setup['instrument']['element_map'][run_dict['element']]

        if 'fluid' not in run_dict:
            run_dict['fluid'] = setup['fluids'][0]

        run_dict['repeats'] = pd.NA #Will be modified in write_meta_df_txt()

        index = '-'.join(run_dict[p] for p in setup['primary_metadata'])
        run_dict['index'] = index
        run_dict['date'] = pd.Timestamp.utcnow().strftime('%Y-%m-%d')

        # Convert to pandas series, which allows dtype to be specified/forced as str
        for col in run_dict.keys():
            try:
                run_dict[col] = pd.Series([run_dict[col]], dtype=metadata_columns[col])
            except:
                run_dict[col] = pd.Series([run_dict[col]])
                logging.info(f'No dtype specified for {col}, using {run_dict[col].dtype}')

        # Convert to dataframe, this enables it to be concatenated with an existing
        # meta_df
        run_df = pd.DataFrame(run_dict)
        run_df.set_index('index', inplace=True)

        # Read the file contents into a dataframe
        df = pd.read_csv(os.path.join(input_dir, filename), sep=separator)
        
        # Check how many repeats exist in the file and label them
        # Assumes the first column represents 'wavelength'
        reps = len(df.columns)-1
        col_names = ['wavelength']
        for r in range(reps):
            col_names.append(f'rep{r+1:02d}')
        df.columns = col_names

        datapath = find_datapath(setup, run_df, index)

        write_df_txt(df, datapath, merge=merge)
        write_meta_df_txt(setup, run_df, merge=merge)

        # write_df_txt(df, )
        # # TODO, the 'store' function reads and writes the full metadata file
        # # each time, so room for improvement here.
        # datapath = store(df, metadata, output_dir, primary_keys)
        # logging.info(f'imported {filename} to {datapath}')
    # write_meta_df_txt(meta_df, )

def read_metadata(setup=default_setup):

    metapath = os.path.join(setup['path'], setup['metafile'])

    if os.path.isfile(metapath):

        # Import the metadata and apply the appropriate datatypes 
        # 'date' needs to be treated separately using parse_dates
        dtypes = metadata_columns.copy()
        dtypes.pop('date')

        meta_df = pd.read_csv(metapath,
                        sep='\t',
                        index_col='index',
                        parse_dates=['date'],
                        dtype=dtypes,
                        )
        logging.debug(f'Loaded Metadata Index from {metapath}')
    else:
        logging.warning(f'{metapath} not found')
        return
    return meta_df

def apply_surface_map(setup):

    meta_df = read_metadata(setup)

    map = setup['instrument']['element_map']

    for index, row in meta_df.iterrows():
        try:
            surface = map[row['element']]
            meta_df.at[index, 'surface'] = surface
            logging.info(f'Applying: {surface} to {index}')
        except KeyError:
            logging.error(f"Element {row['element']} not found in surface map")
    
    metapath = os.path.join(setup['path'], setup['metafile'])
    meta_df.to_csv(metapath, index=True, sep='\t', na_rep='', date_format='%Y-%m-%d')

def generate_run_df(setup):
    '''
    For doing a bulk run of measurements.
    This generates a list (dataframe) of metadata describing the measuremnts

    Measurement rows are generated for all permutations of fluids and
    elements provided in the setup{}
    '''

    # Create a blank table (really a dict of lists) with default headers
    # NB It is bad practice to append to Dataframes, so will convert to
    # dataframe at the end
    run_list = metadata_columns.copy()
    for col in run_list.keys():
        run_list[col] = []

    # List of elements can be specified in the setup{}, or can use 'all'.
    if setup['elements'] == 'all':
        elements = instrument['element_map'].keys()
    else:
        elements = setup['elements']

    # Build the run list, row by row
    for f in setup['fluids']:
        for e in elements:
                row = {}
                row['date'] = pd.NaT
                row['instrument'] = instrument['name']
                row['sensor'] = instrument['sensor']
                row['element'] = e
                row['surface'] = instrument['element_map'][e]
                row['fluid'] = f
                row['repeats'] = setup['repeats']
                row['comment'] = pd.NA

                # Build the index as a string based on primary metadata
                row['index'] = '-'.join(row[p] for p in setup['primary_metadata'])

                for col in row.keys():
                    run_list[col].append(row[col])

    # Convert the lists into pandas series with appropriate datatypes
    for col in run_list.keys():
        run_list[col] = pd.Series(run_list[col], dtype=metadata_columns[col])
        # run_list[col] = pd.Series(run_list[col], dtype=str)

    # Convert to dataframe now (avoids iteratively appending to the dataframe)
    run_df = pd.DataFrame(run_list)

    # Specify that the 'index' column should be treated as the index
    run_df.set_index('index', inplace=True)

    return run_df

def write_df_txt(df, datapath, merge=True):
    '''
    df is the new data frame to be saved / merged
    datapath should be the full path including the .txt filename
    '''

    os.makedirs(os.path.dirname(datapath), exist_ok=True)

    # Check if the file exists, then write the data 
    if not os.path.isfile(datapath):
        logging.info(f'Saving into new file {datapath}')
        df.to_csv(datapath, index=False, sep='\t', mode='w')

    # If file exists, read it, merge, then rewrite the data
    else:
        if merge:
            logging.info(f'Merging into existing {datapath}')

            with open(datapath, 'r+') as f:
                existing_df = pd.read_csv(f, sep='\t')

                df = pd.merge(existing_df, df, how='outer', on='wavelength', sort=True)

                #relabel columns  -  Unless they are timestamped
                col_names = ['wavelength']
                n=0
                for col in df.columns[1:]:
                    n += 1
                    try:
                        pd.Timestamp(float(col), unit='s')
                        col_names.append(col)
                    except ValueError:
                        # col_names.append(f'rep{col}')
                        col_names.append(f"rep{n:02d}")
                df.columns = col_names
                    
                f.seek(0,0)
                df.to_csv(f, index=False, sep='\t', mode='w')
        else:
            logging.warning(f'{datapath} exists, and merge=False, did not write')


def write_meta_df_txt(setup, meta_df, merge=True):
    '''
    Writes a meta_df to metapath (index.txt)
    If file exists will try to merge them. The merge will fail if 2 rows have
    identical index names, but different data in the columns. 

    An exception is for the 'repeats' column, where it opens the data files to
    check how many repeats are actually present.

    NB - To get the correct repeat count, any new data files must be
    written/merged before this function is run.
    '''
    metapath = os.path.join(setup['path'], setup['metafile'])

    if not os.path.isfile(metapath):
        logging.info(f'Saving into new file {metapath}')

    # If file exists, read it, merge, then rewrite the data
    else:
        if not merge:
            logging.warning(f'{metapath} exists, and merge=False, did not write')
            return
        else:
            logging.info(f'Merging into existing {metapath}')

            with open(metapath, 'r+') as f:
                existing_df = read_metadata(setup)
                
            for row in meta_df.index:
                if row in existing_df.index:
                    # zero out the repeat count for a clean merge, will restore later
                    meta_df.at[row, 'repeats'] = pd.NA
                    existing_df.at[row, 'repeats'] = pd.NA

                    # Also set the date modified to 'now'
                    date = pd.Timestamp.utcnow().strftime('%Y-%m-%d')
                    meta_df.at[row, 'date'] = date
                    existing_df.at[row, 'date'] = date
                    
            meta_df = pd.concat([existing_df, meta_df])
            
            # It is OK to drop duplicates (that match in every column),
            # NB, the repeat and date columns have been dealt with already
            meta_df.drop_duplicates(inplace=True)

            dup_count = 0
            for dup in meta_df[meta_df.index.duplicated()].index:
                dup_count += 1
                display(meta_df.loc[dup])

            if dup_count > 0:
                logging.warning(f'{dup_count} duplicate index values detected, cannot write metadata file')
                logging.warning("This is likely to occur if setup['primary_metadata'] can't uniquely identify measurements")
                return

            # Deal with NA 'repeat' counts by actually opening the data files
            # and counting the columns. Seems heavy handed but will
            # ensure they don't get out of sync.
            for row in meta_df[meta_df['repeats'].isnull()].index:
                datapath = find_datapath(setup, meta_df, row)
                with open(datapath, 'r') as d:
                    df = pd.read_csv(d, sep='\t')
                reps = len(df.columns) -1
                meta_df.at[row, 'repeats'] = reps
        
    meta_df.to_csv(metapath, index=True, sep='\t', na_rep='', date_format='%Y-%m-%d')

def write_setup_json(setup):

    #Don't need to save the full instrument data, just the name
    setup_mod = setup.copy()
    setup_mod['instrument'] = setup['instrument']['name']

    date = pd.Timestamp.utcnow().strftime('%Y-%m-%d_%H%M%S')
    setup_path = os.path.join('setups', f"{date}-setup.json")
    os.makedirs(os.path.dirname(setup_path), exist_ok=True)

    if not os.path.isfile(setup_path):
        with open(setup_path, 'w') as f:
            json.dump(setup_mod, f, ensure_ascii=False, indent=3)
    else:
        logging.warning('File exists, did not write')

def write_instrument_json(setup):

    instrument_path = os.path.join('setups', 'instruments', f"{setup['instrument']['name']}.json")
    os.makedirs(os.path.dirname(instrument_path), exist_ok=True)

    if not os.path.isfile(instrument_path):
        with open(instrument_path, 'w') as f:
            json.dump(setup['instrument'], f, ensure_ascii=False, indent=3)
    else:
        logging.warning('File exists, did not write')

def read_setup_json(path):

    with open(path) as setup_json:
        setup = json.load(setup_json)

    setupdir = os.path.dirname(path)
    instrument_path = os.path.join(setupdir, 'instruments', f"{setup['instrument']}.json")
    with open(instrument_path) as instrument_json:
        setup['instrument'] = json.load(instrument_json)    

    return setup


def run_measure(setup, run_df, measure_func, merge=True):
    '''
    For doing a batch run of measurements.
    This iterates through a run list (run_df), calling measure_func for each
    repeat of each row.

    Data is saved into .txt files named according the index of the row in the
    run_df. The output directory is defined in setup{}

    the date column in run_df is populated, and then saved as index.txt in the
    output directory
    '''
    # Duplicate the run_df so the original is not modified
    # Prevents unexpected behaviour if calling this function multiple times.
    run_df = run_df.copy()

    for row in run_df.index:
        df = pd.DataFrame()
        for rep in range(run_df.loc[row]['repeats']):
            # Construct the data path
            datapath = find_datapath(setup, run_df, row)
            # call the measure function to get data
            df = measure_func(setup, run_df.loc[row])

            # write the df to txt file
            write_df_txt(df, datapath, merge=merge)

        # Update the date column in the run_df
        run_df.at[row, 'date'] = pd.Timestamp.utcnow().strftime('%Y-%m-%d')
    
    write_meta_df_txt(setup, run_df, merge=merge)

def bulk_process(setup_in, setup_out, delete_input=False, merge_out=False):
    '''
    For doing a bulk copy/merge of one data directory to another.
    
    Also useful for modifying a folder structure from e.g. grouped by 'fluid'
    subdirectories to grouped by 'sensor' subdirectories

    Can be used to detect any missing data files

    This iterates through an input index.txt, reading in each datafile and
    writing it to the output directory structure, merging with existing files
    where appropriate.

    The output files can optionally be merged with an existing ones.

    TODO, add handling to deal with input and output root paths being the same
    TODO, add data processing option?
    '''

    meta_df = read_metadata(setup_in)

    for row in meta_df.index:
        datapath_in = find_datapath(setup_in, meta_df, row)
        datapath_out = find_datapath(setup_out, meta_df, row)

        try:
            with open(datapath_in, 'r') as f:
                df = pd.read_csv(f, sep='\t')
            write_df_txt(df, datapath_out, merge=merge_out)

        except FileNotFoundError as e:
            logging.error(f"{e}"
                +"\nRow will be removed from output metadata file"
                +"\nCheck that setup_in['subdirs'] is set correctly")
            meta_df.drop(index=row, inplace=True)
    
    write_meta_df_txt(setup_out, meta_df, merge=merge_out)

    if delete_input:
        shutil.rmtree(setup_in['path'])