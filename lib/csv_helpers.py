import pandas as pd
import numpy as np
import os
from io import StringIO
import re
import json
import shutil
import copy
from IPython.display import display
import logging
import time
import math

import lib.json_setup as json_setup

logging.basicConfig(level=logging.INFO)


def get_default_setup():
    new_setup = copy.deepcopy(json_setup.default_setup)
    return new_setup

def dummy_measurement(setup, row):
    
    #For a real instrument, may wish to adjust/move based on row['element']

    dummywavelength = list(np.arange(setup['input_config']['wavelength_range'][0], #start
                                    setup['input_config']['wavelength_range'][1],  #stop
                                    setup['input_config']['wavelength_range'][2])) #step

    size = len(dummywavelength)
    dummydata = list(np.random.random_sample(size))
    dummycsv = {'wavelength' : dummywavelength, 'transmission' : dummydata}
    df = pd.DataFrame(data=dummycsv, dtype=np.float32)
    df.set_index("wavelength", inplace=True)

    timestamp = pd.Timestamp.utcnow().timestamp()
    df.rename(columns={"transmission" : timestamp }, inplace=True)
    time.sleep(0.5)
    return df

def simple_measurement(setup, element, fluid, measure_func, merge=True, comment=''):

    run_dict = {
        'date'          : pd.Timestamp.utcnow().strftime('%Y-%m-%d'),
        'instrument'    : setup['instrument']['name'],
        'sensor'        : setup['sensor']['name'],
        'element'       : element,
        'structure'     : setup['sensor']['structure_map']['map'][element][0],
        'surface'       : setup['sensor']['surface_map']['map'][element][0],
        'fluid'         : fluid,
        'repeats'       : 1,
        'comment'       : comment
    }
    index = '-'.join(run_dict[p] for p in setup['primary_metadata'])
    run_dict['index'] = index

    for col in run_dict.keys():
        # dtypes are not specified here, they get assigned when during read_metadata()
        run_dict[col] = pd.Series([run_dict[col]])

    run_df = pd.DataFrame(run_dict)
    run_df.set_index('index', inplace=True)

    run_measure(setup, run_df, measure_func, merge=merge)

    datapath = find_datapath(setup, run_df, index)
    df = pd.read_csv(datapath, sep='\t', index_col='wavelength')
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
    datapath = os.path.join(setup['datadir'], subdir, f'{row_index}.txt')
    return datapath


def merge_dataframes(setup, meta_df, posixtime_from=None, posixtime_until=None):
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
        df = pd.read_csv(datapath, sep='\t', index_col='wavelength')

        # Select only the columns that are within the specified time range
        if posixtime_from is not None:
            df = df.loc[:, df.columns.astype(float) >= posixtime_from]
        if posixtime_until is not None:
            df = df.loc[:, df.columns.astype(float) <= posixtime_until]

        # Name the output columns based on metadata
        col_names = []
        n=0
        for col in df.columns:
            n += 1
            # Convert the timestamp to a human-readable format
            # Possibly bad practice to hard code time zone, but at least it has the UTC offset included
            timestamp = pd.to_datetime(col,unit='s', utc=True)
            timestamp = timestamp.tz_convert('Europe/London').strftime('%Y-%m-%d_%H:%M:%S%z')

            if len(individual_meta) > 0:
                name = '_'.join(meta_df.loc[row][i] for i in individual_meta)
                col_names.append(f'{name}_rep{n:02d}_{timestamp}')
            else:
                col_names.append(f'rep{n:02d}_{timestamp}')
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

def export_stats(setup, dp, meta_df=None, outfile=None, std_deviation=True):

    if isinstance(meta_df, pd.DataFrame):
        pass
    else:
        meta_df = read_metadata(setup)

    exportstats = pd.DataFrame()
    if dp.apply_avg_repeats:
        std_dev = True
    else:
        std_dev = False

    for row in meta_df.index:

        stats_df = get_stats_single(setup, dp, meta_df, row, std_deviation=std_dev)

        # Accumulate the dataframes in a large 'result' dataframe
        exportstats = pd.concat([exportstats, stats_df], axis=0)

    exportstats.sort_values(by=['element'], inplace=True)
    exportstats.reset_index(drop=True, inplace=True)

    if outfile:
        logging.info(f"Writing to {outfile} ...")
        exportstats.to_csv(outfile, sep='\t', na_rep='NA')
        logging.info(f"Done")
    return exportstats

def get_stats_single(setup, dp, meta_df, row, peak_type='Min', std_deviation=True):

    # locate the datafile and read it in
    datapath = find_datapath(setup, meta_df, row)
    df = pd.read_csv(datapath, sep='\t', index_col='wavelength')

    # Name the output columns (extract timestamps and leave columns named rep01 etc.)
    col_names = []
    timestamps = []
    n=0
    for col in df.columns:
        n += 1
        col_names.append(f'{row}_rep{n:02d}')
        timestamps.append(pd.to_datetime(col,unit='s').strftime('%Y-%m-%d_%H:%M:%S'))
    df.columns = col_names

    if std_deviation:
        dp.apply_avg_repeats = False

    df = dp.process_dataframe(df)

    if dp.apply_round:
        round_digits = dp.round_decimals
    else:
        round_digits = 6

    stats_df = dp.get_stats(df, peak_type, round_digits=round_digits, std_deviation=std_deviation) 

    if std_deviation:
        row_info = pd.DataFrame(index=[f"{row}_avg"])
        stats_df.rename({"averaged" : f"{row}_avg"}, axis=0, inplace=True)
    else:
        row_info = pd.DataFrame(index=df.columns)
        if not dp.apply_avg_repeats:
            row_info['timestamp'] = timestamps

    row_info['element'] = meta_df.loc[row]['element']
    row_info['surface'] = meta_df.loc[row]['surface']
    row_info['fluid'] = meta_df.loc[row]['fluid']

    stats_df = pd.concat([row_info, stats_df], axis=1)
    return stats_df

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
        header_rows= [[f'{surface}'],[F'{e}'], element_df.columns]
        col_ix = pd.MultiIndex.from_product(header_rows, names = header_row_names)

        element_df.columns = col_ix
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
    setup{} dictionary
    '''

    if not os.path.exists(input_dir):
        logging.error('import folder not found')
        return

    for subdir, dirs, files in os.walk(input_dir):
        for filename in files:
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
                run_dict['sensor'] = setup['sensor']['name']

            if 'element' not in run_dict: # This will be unusual
                element = setup['input_config']['elements']
                if type(element) == list:
                    element = element[0]
                run_dict['element'] = element
                logging.warning('The REGEX should typically identify which element is used')
                logging.warning(f"Using {element} as a default")

            if 'structure' not in run_dict:
                run_dict['structure'] = setup['sensor']['structure_map']['map'][run_dict['element']][0]

            if 'surface' not in run_dict:
                run_dict['surface'] = setup['sensor']['structure_map']['map'][run_dict['element']][0]

            if 'fluid' not in run_dict:
                run_dict['fluid'] = setup['input_config']['fluids'][0]

            run_dict['repeats'] = pd.NA #Will be modified in write_meta_df_txt()

            index = '-'.join(run_dict[p] for p in setup['primary_metadata'])

            run_dict['index'] = index
            run_dict['date'] = pd.Timestamp.utcnow().strftime('%Y-%m-%d')

            for col in run_dict.keys():
                # dtypes are not specified here, they get assigned when during read_metadata()
                run_dict[col] = pd.Series([run_dict[col]])
            run_df = pd.DataFrame(run_dict)
            run_df.set_index('index', inplace=True)

            # Read the file contents into a dataframe
            df = pd.read_csv(os.path.join(input_dir, subdir, filename), sep=separator)
            
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

            # Note, this function reads and writes the full metadata file
            # each time, so room for improvement here.

def read_metadata(setup=json_setup.default_setup, filebuffer=None):

    if filebuffer:
        # Optionally read in from a memory buffer.
        # Used by write_meta_df_txt() function for merging.
        metapath = filebuffer
    else:
        # Normally read in from the metafile specified in setup{}
        metapath = os.path.join(setup['datadir'], setup['metafile'])
        if not os.path.isfile(metapath):
            logging.warning(f'{metapath} not found')
            return

    # Import the metadata and apply the appropriate datatypes 
    # 'date' needs to be treated separately using parse_dates
    dtypes = json_setup.default_metadata_columns.copy()
    dtypes.pop('date')
    dtypes.pop('name')

    meta_df = pd.read_csv(metapath,
                    sep='\t',
                    index_col='index',
                    parse_dates=['date'],
                    dtype=dtypes,
                    )

    if not filebuffer:
        logging.debug(f'Loaded Metadata Index from {metapath}')
       
    return meta_df

# def apply_surface_map(setup):

#     meta_df = read_metadata(setup)

#     map = setup['instrument']['structure_map']

#     for index, row in meta_df.iterrows():
#         try:
#             surface = map[row['element']]
#             meta_df.at[index, 'surface'] = surface
#             logging.info(f'Applying: {surface} to {index}')
#         except KeyError:
#             logging.error(f"Element {row['element']} not found in surface map")
    
#     metapath = os.path.join(setup['datadir'], setup['metafile'])
#     meta_df.to_csv(metapath, index=True, sep='\t', na_rep='', date_format='%Y-%m-%d')

def generate_run_df(setup, fluid=None):
    '''
    For doing a bulk run of measurements.
    This generates a list (dataframe) of metadata describing the measuremnts

    Measurement rows are generated for all permutations of fluids and
    elements provided in the setup{}
    '''

    # Create a blank table (really a dict of lists) with default headers
    # NB It is bad practice to append to Dataframes, so will convert to
    # dataframe at the end
    run_list = json_setup.default_metadata_columns.copy()
    run_list.pop('name')

    for col in run_list.keys():
        run_list[col] = []

    # List of elements can be specified in the setup{}, or can use 'all'.
    if setup['input_config']['elements'] == 'all':
        elements = setup['sensor']['layout']['map'].keys()
    else:
        elements = setup['input_config']['elements']

    # Build the run list, row by row
    for e in elements:
        row = {}
        row['date'] = pd.NaT
        row['instrument'] = setup['instrument']['name']
        row['sensor'] = setup['sensor']['name']
        row['element'] = e
        row['structure'] = setup['sensor']['structure_map']['map'][e][0]
        row['surface'] = setup['sensor']['surface_map']['map'][e][0]
        if fluid:
            row['fluid'] = fluid
        else:
            row['fluid'] = setup['input_config']['fluids'][0]
        row['repeats'] = setup['input_config']['repeats']
        row['comment'] = ''

        # Build the index as a string based on primary metadata
        row['index'] = '-'.join(row[p] for p in setup['primary_metadata'])

        for col in row.keys():
            run_list[col].append(row[col])

    # Convert the lists into pandas series
    for col in run_list.keys():
        # run_list[col] = pd.Series(run_list[col], dtype=json_setup.default_metadata_columns[col])
        run_list[col] = pd.Series(run_list[col])

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
        df.to_csv(datapath, sep='\t', mode='w')

    # If file exists, read it, merge, then rewrite the data
    else:
        if merge:
            logging.info(f'Merging into existing {datapath}')

            with open(datapath, 'r+', newline='') as f:
                existing_df = pd.read_csv(f, sep='\t', index_col='wavelength')

                df = pd.merge(existing_df, df, how='outer', on='wavelength', sort=True)

                #relabel columns  -  Unless they are timestamped
                col_names = []
                n=0
                for col in df.columns:
                    n += 1
                    try:
                        pd.Timestamp(float(col), unit='s')
                        col_names.append(col)
                    except ValueError:
                        col_names.append(f"rep{n:02d}")
                df.columns = col_names
                    
                f.seek(0,0)
                df.to_csv(f, sep='\t', mode='w')
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
    metapath = os.path.join(setup['datadir'], setup['metafile'])

    if not os.path.isfile(metapath):
        logging.info(f'Saving into new file {metapath}')

    # If file exists, read it, merge, then rewrite the data
    else:
        if not merge:
            logging.warning(f'{metapath} exists, and merge=False, did not write')
            return
        else:
            logging.info(f'Merging into existing {metapath}')

            # Before merging we need to ensure the datatypes and NA values
            # match exactly. The most robust way of doing that seems to be
            # writing out the meta_df, then reading both back using the same function.
            buffer = StringIO()
            meta_df.to_csv(buffer, index=True, sep='\t', na_rep='', date_format='%Y-%m-%d')
            buffer.seek(0)

            meta_df = read_metadata(filebuffer=buffer)
            existing_df = read_metadata(setup)
                
            for row in meta_df.index:

                # zero out the repeat count for a clean merge, will restore later
                meta_df.at[row, 'repeats'] = pd.NA
                if row in existing_df.index:
                    existing_df.at[row, 'repeats'] = pd.NA

                # Also set the date modified to 'now'
                date = pd.Timestamp.utcnow().strftime('%Y-%m-%d')
                meta_df.at[row, 'date'] = date
                if row in existing_df.index:
                    existing_df.at[row, 'date'] = date
                    
            meta_df = pd.concat([existing_df, meta_df])
            
            # It is OK to drop duplicates (that match in every column),
            # NB, the repeat and date columns have been dealt with already
            meta_df.drop_duplicates(inplace=True)

            dup_count = 0
            for dup in meta_df[meta_df.index.duplicated()].index:
                dup_count += 1
                logging.warning(f'Index Conflict: {meta_df.loc[dup]}')

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
                    df = pd.read_csv(d, sep='\t', index_col='wavelength')
                reps = len(df.columns)
                meta_df.at[row, 'repeats'] = reps
        
    meta_df.to_csv(metapath, index=True, sep='\t', na_rep='', date_format='%Y-%m-%d')

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
                df = pd.read_csv(f, sep='\t', index_col='wavelength')
            write_df_txt(df, datapath_out, merge=merge_out)

        except FileNotFoundError as e:
            logging.error(f"{e}"
                +"\nRow will be removed from output metadata file"
                +"\nCheck that setup_in['subdirs'] is set correctly")
            meta_df.drop(index=row, inplace=True)
    
    write_meta_df_txt(setup_out, meta_df, merge=merge_out)

    if delete_input:
        shutil.rmtree(setup_in['path'])


def export_slide_rotation_csv(rotation_deg, pos_map, filepath):

    corr_map = pos_map.copy()
    # python uses radians by default
    rads = math.radians(rotation_deg)

    for element, coords in  pos_map.items():
        x=coords[0]
        y=coords[1]
        # # correct for rotation
        x = round(x*math.cos(rads) - y*math.sin(rads), 2)
        y = round(y*math.cos(rads) + x*math.sin(rads), 2)

        corr_map[element] = [x, y]

    with open(filepath, 'w') as f:
        f.write(f'Angle = {rotation_deg} degrees\n')

        f.write(f'Element,X Orig,Y Orig,X Corrected,Y Corrected, X Adjustment,Y Adjustment\n')
        for key in pos_map.keys():
            x_orig = pos_map[key][0]
            y_orig = pos_map[key][1]
            x_corr = corr_map[key][0]
            y_corr = corr_map[key][1]
            x_adj = round(x_corr - x_orig, 5)
            y_adj = round(y_corr - y_orig, 5)
            f.write(f'{key},{x_orig},{y_orig},{x_corr},{y_corr},{x_adj},{y_adj}\n')