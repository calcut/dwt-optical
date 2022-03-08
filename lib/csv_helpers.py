from cProfile import run
from curses import meta
from sys import meta_path
import pandas as pd
import numpy as np
import os
import re
import shutil
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
setup = {
    'metafile'          : 'index.txt',
    'path'              : 'dummydata',
    'subdirs'           : ['sensor', 'fluid'], #Directory structure for data.txt files
    'fluids'            : ['waterA', 'waterB', 'waterC'],
    'elements'          : 'all',
    'repeats'           : 3,
    'wavelength_range'  : [400, 420, 0.5], #start, stop, step
    'primary_metadata'  : ['instrument', 'element', 'fluid'],
    'comment'           : '', #To be added to the metadata
    'instrument'        : instrument,
}

default_metadata = {
    # Column            : #Datatype
    'index'             : 'string',
    'date'              : 'datetime64[ns]',
    'instrument'        : 'string',
    'sensor'            : 'string',
    'element'           : 'string',
    'surface'           : 'string',
    'fluid'             : 'string',
    'repeats'           : 'Int64',
    'hidden'            : 'boolean',
    'comment'           : 'string',
}

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

def simple_measurement(setup, element, fluid, measure_func):
    
    run_dict = {
        'date'          : pd.Timestamp.utcnow().strftime('%Y-%m-%d'),
        'instrument'    : setup['instrument']['name'],
        'sensor'        : setup['instrument']['sensor'],
        'element'       : element,
        'surface'       : setup['instrument']['element_map'][element],
        'fluid'         : fluid,
        'repeats'       : 1,
        'hidden'        : False,
        'comment'       : pd.NA,
    }
    index = '-'.join(run_dict[p] for p in setup['primary_metadata'])
    run_dict['index'] = index

    # Convert to pandas series, which allows datatype to be specified
    for col in run_dict.keys():
        run_dict[col] = pd.Series([run_dict[col]], dtype=default_metadata[col])
        
    # Convert to dataframe, this enables it to be concatenated with an existing
    # meta_df
    run_df = pd.DataFrame(run_dict)
    run_df.set_index('index', inplace=True)


    run_measure(setup, run_df, measure_func)


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
        if field == 'date':
            date = f"{meta_df.iloc[0][field].strftime('%Y-%m-%d')}"
        else:
            value = f'{meta_df.iloc[0][field]}'
            title += f'{field}: {value}\n'
   
    if date:
        title += date
    else:
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


def export_dataframes(path='.', meta_df='index.txt', outfile=None, dp=None):

    if isinstance(meta_df, pd.DataFrame):
        pass
    else:
        metapath = os.path.join(path, meta_df)
        meta_df = read_metadata(metapath)

    elements = sorted(meta_df['element'].unique())
    frames=[]
    for e in elements:
        logging.info(f'merging element {e}')
        selection = select_from_metadata('element', e, meta_df)
        element_df, title = merge_dataframes(selection, path)

        #If a DataProcessor object has been provided, apply processing here.
        if dp:
            element_df = dp.process_dataframe(element_df)

        element_df = element_df.transpose()

        surfaces = meta_df[meta_df['element'] == e]['surface'].drop_duplicates().tolist()
        surface = surfaces[0]
        if len(surfaces) > 1:
            logging.error(f'Error, multiple surfaces {surfaces} found for element {e}')
            return
        # if pd.isnull(surface):
        #     surface = 'NA'

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


def import_dir_to_csv(setup, input_dir, regex, separator='\t'):

    '''
    regex can optionally identify the following fields:
        'date'      
        'instrument'
        'sensor'    
        'element'   
        'surface'   
        'fluid'     
        'repeats'   
        'hidden'    
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

    metapath = os.path.join(setup['path'], setup['metafile'])
    meta_df = read_metadata(metapath)

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

        index = '-'.join(run_dict[p] for p in setup['primary_metadata'])
        run_dict['index'] = index
        run_dict['date'] = pd.Timestamp.utcnow().strftime('%Y-%m-%d')

        # Convert to pandas series, which allows datatype to be specified
        for col in run_dict.keys():
            run_dict[col] = pd.Series([run_dict[col]], dtype=default_metadata[col])
            
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
        print(datapath)

        # write_df_txt(df, )
        # # TODO, the 'store' function reads and writes the full metadata file
        # # each time, so room for improvement here.
        # datapath = store(df, metadata, output_dir, primary_keys)
        # logging.info(f'imported {filename} to {datapath}')
    # write_meta_df_txt(meta_df, )

def read_metadata(metapath):
    if os.path.isfile(metapath):

        # Import the metadata and apply the appropriate datatypes 
        # 'date' needs to be treated separately using parse_dates
        dtypes = default_metadata.copy()
        dtypes.pop('date')

        meta_df = pd.read_csv(metapath,
                        sep='\t',
                        index_col='index',
                        parse_dates=['date'],
                        dtype=dtypes,
                        )
        logging.debug(f'Loaded Metadata Index from {metapath}')
    else:
        logging.error(f'{metapath} not found')
        return
    return meta_df

def apply_surface_map(setup):

    metapath = os.path.join(setup['path'], setup['metafile'])
    meta_df = read_metadata(metapath)

    map = setup['instrument']['element_map']

    for index, row in meta_df.iterrows():
        try:
            surface = map[row['element']]
            meta_df.at[index, 'surface'] = surface
            logging.info(f'Applying: {surface} to {index}')
        except KeyError:
            logging.error(f"Element {row['element']} not found in surface map")
    
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
    run_list = default_metadata.copy()
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
                row['hidden'] = False
                row['comment'] = pd.NA

                # Build the index as a string based on primary metadata
                row['index'] = '-'.join(row[p] for p in setup['primary_metadata'])

                for col in row.keys():
                    run_list[col].append(row[col])

    # Convert the lists into pandas series with appropriate datatypes
    for col in run_list.keys():
        run_list[col] = pd.Series(run_list[col], dtype=default_metadata[col])

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

                df = pd.merge(df, existing_df, how='outer', on='wavelength')

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
        meta_df.to_csv(metapath, index=True, sep='\t', na_rep='', date_format='%Y-%m-%d')

    # If file exists, read it, merge, then rewrite the data
    else:
        if merge:
            logging.info(f'Merging into existing {metapath}')

            with open(metapath, 'r+') as f:
                existing_df = read_metadata(metapath)

                # Deal with 'repeat' counts by actually opening the data files
                # and counting the columns. Seems heavy handed but will
                # ensure they don't get out of sync.
                path = os.path.dirname(metapath)
                for row in meta_df.index:
                    if row in existing_df.index:
                        datapath = find_datapath(setup, meta_df, row)
                        with open(datapath, 'r') as d:
                            df = pd.read_csv(d, sep='\t')
                        reps = len(df.columns) -1
                        meta_df.at[row, 'repeats'] = reps
                        existing_df.at[row, 'repeats'] = reps

                meta_df.reset_index(inplace=True)
                existing_df.reset_index(inplace=True)

                meta_df = pd.merge(meta_df, existing_df, how='outer') # TODO Change this to concat******************************

                # Specify that the 'index' column should be treated as the
                # index. If the merge has not worked correctly this will fail
                # due to duplicate index keys. Likely to happen if the primary
                # metadata is not enough to uniquely identify mesurements.
                try:
                    meta_df.set_index('index', verify_integrity=True, inplace=True)
                except ValueError as e:
                    logging.error('Could not merge meta_df')
                    logging.error(e.args)
                    display(meta_df)

                f.seek(0,0)
                meta_df.to_csv(f'{metapath}', index=True, sep='\t', na_rep='', date_format='%Y-%m-%d')
        else:
            logging.warning(f'{metapath} exists, and merge=False, did not write')

def run_measure(setup, run_df, measure_func):
    '''
    For doing a bulk run of measurements.
    This iterates through a run list (run_df), calling measure_func for each
    repeat of each row.

    Data is saved into .txt files named according the index of the row in the
    run_df. The output directory is defined in setup{}

    the date column in run_df is populated, and then saved as index.txt in the
    output directory
    '''
    for row in run_df.index:
        df = pd.DataFrame()
        for rep in range(run_df.loc[row]['repeats']):
            # Construct the data path
            datapath = find_datapath(setup, run_df, row)
            # call the measure function to get data
            df = measure_func(setup, run_df.loc[row])

            # write the df to txt file
            write_df_txt(df, datapath)

        # Update the date column in the run_df
        run_df.at[row, 'date'] = pd.Timestamp.utcnow().strftime('%Y-%m-%d')
    
    write_meta_df_txt(setup, run_df)

def bulk_merge(input_metapath, output_metapath, delete_input=False, 
                in_subdirs='fluid', out_subdirs='fluid'):
    '''
    For doing a bulk copy/merge of one data directory to another.
    
    Also useful for modifying a folder structure from e.g. grouped by 'fluid'
    subdirectories to grouped by 'sensor' subdirectories

    This iterates through an input index.txt, reading in each datafile and
    writing it to the output directory structure, merging with existing files
    where appropriate.

    The index.txt file is also written/merged with any existing one.
    '''

    input_path = os.path.dirname(input_metapath)
    output_path = os.path.dirname(output_metapath)

    meta_df = read_metadata(input_metapath)

    for row in meta_df.index:
        in_subdir = meta_df.loc[row][in_subdirs]
        out_subdir = meta_df.loc[row][out_subdirs]
        input_datapath = os.path.join(input_path, in_subdir, f'{row}.txt')
        output_datapath = os.path.join(output_path, out_subdir, f'{row}.txt')
        with open(input_datapath, 'r') as f:
            df = pd.read_csv(f, sep='\t')

        write_df_txt(df, output_datapath)
    
    write_meta_df_txt(meta_df, output_metapath)

    if delete_input:
        shutil.rmtree(input_path)