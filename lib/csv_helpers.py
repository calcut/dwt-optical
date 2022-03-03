from curses import meta
import pandas as pd
import os
import re
import shutil
from IPython.display import display
import logging

logging.basicConfig(level=logging.INFO)


default_metadata = {
    # Column              Datatype
    'index'             : 'string',
    'date'              : 'datetime64[ns]',
    'instrument'        : 'string',
    'sensor'            : 'string',
    'element'           : 'string',
    'chemistry'         : 'string',
    'fluid'             : 'string',
    'repeats'           : 'Int64',
    'hidden'            : 'boolean',
    'comment'           : 'string',
}

# Must be able to uniquely identify measurements
# Any measurements with matching primary metadata are treated as repeats
primary_metadata = [
    'instrument',
    'fluid',
    'element',
]

instrument = {
    'name'              : 'instrument01',
    'sensor'            : 'DUM01',
    'element_map'       : { 'A01': 'Barium',
                            'A02': 'Bromine',
                            'A03': 'Lanthanum',
                            'A04': 'Titanium',
                            'B01': 'Chromium',
                            'B02': 'Arsenic',
                            'B03': 'Krypton',
                            'B04': 'Nitrogen',
                            'C01': 'Fluorine',
                            'C02': 'Manganese',
                            'C03': 'Cadmium',
                            'C04': 'Arsenic',
                            'D01': 'Argon',
                            'D02': 'Copper',
                            'D03': 'Aluminium',
                            'D04': 'Selenium',
                            },
    'light Source'      : 'Stellarnet LED White',
    'spectrometer'      : 'Stellarnet BlueWave VIS-25',
}

setup = {
    'output_dir'        : './dummydata',
    'fluids'            : ['water', 'beer1', 'beer2'],
    'elements'          : 'all',
    'repeats'           : 3,
    'wavelength_range'  : [400, 420, 0.5], #start, stop, step
    'primary_metadata'  : ['instrument', 'element', 'fluid'],
}

def store(df, metadata, path='./raw', primary_keys=None):

    if not os.path.exists(path):
        os.makedirs(path)

    metapath = os.path.join(path, "index.txt")
    if os.path.isfile(metapath):
        meta_df = read_metadata(metapath)
    else:
        cols = default_metadata.keys()
        meta_df = pd.DataFrame(columns=cols)
        meta_df.index.name = "index"

    try:
        date_obj = pd.Timestamp.fromtimestamp(metadata['timestamp'])
    except KeyError:
        date_obj = pd.Timestamp.utcnow()

    metadata['date'] = date_obj.strftime('%Y-%m-%d')


    d = metadata['date']
    s = metadata['sensor']
    f = metadata['fluid']
    e = metadata['element']

    # Allows overriding of default Primary Metadata as used for file naming
    if primary_keys: 
        meas_id = ''
        for k in primary_keys:
            meas_id += f'{metadata[k]}-'
        meas_id = meas_id[:-1]

    #Default Primary Metadata
    else:
        meas_id = F"{d}-{s}-{f}-{e}"

    datapath = os.path.join(path, f, f'{meas_id}.txt')

    os.makedirs(os.path.dirname(datapath), exist_ok=True)

    # Check if the file exists, then write the data 
    if not os.path.isfile(datapath):
        logging.info(f'Saving data into new file {meas_id}.txt')
        with open(datapath, 'w') as f:
            df.to_csv(f, index=False, sep='\t', mode='w')

    # If file exists, read it, merge, then rewrite the data
    else:
        logging.warning(f'Merging new data into existing file {meas_id}.txt')

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

    metadata['repeats'] = len(df.columns) - 1
    metadata.pop('timestamp', None)

# Update the Metadata Index File
    try:
        new_row= pd.Series(data=metadata, name=meas_id)
        meta_df = meta_df.append(new_row, ignore_index=False, verify_integrity=True)
        # break
    except ValueError as err:
        # print(f"Warning, {meas_id} already exists in {metapath}, "
        #     + f"updating rep count to {metadata['repeats']}")
        meta_df.at[meas_id, 'repeats'] = metadata['repeats']

    meta_df.to_csv(f'{metapath}', index=True, sep='\t', na_rep='', date_format='%Y-%m-%d')
    return datapath


# Extracts dataframes from files and merges them into a single dataframe
# Requires a metadata frame to know which measurements to select
# Columns are renamed to show only the relevant metadata
# Outer join means that rows from all dataframes are preserved, and NaN is
# filled where needed
def merge_dataframes(meta_df, path='./raw'):
    result = []

    # For re-labelling the merged dataframe:
    # Ignore metadata that is the same for measurements
    # i.e. only use columns with more than 1 unique value
    individual_meta = meta_df.columns[meta_df.nunique() > 1]

    # Ignore columns which aren't considered primary metadata
    # primary_metadata = ['date', 'sensor', 'fluid',' element']
    individual_meta = individual_meta.intersection(primary_metadata)

    # Identify primary metadata that is common for all measurements
    common_metadata = set(primary_metadata) - set(individual_meta)

    for row in meta_df.index:

        # locate the datafile and read it in
        subdir = meta_df.loc[row]['sensor']
        datapath = os.path.join(path, subdir, f'{row}.txt') 
        df = pd.read_csv(datapath, sep='\t')

        # Name the output columns based on metadata
        if len(individual_meta) > 0:
            col_names = ['wavelength']
            for col in df.columns[1:]:
                name = str()
                for label in individual_meta:
                    name += f'{meta_df.loc[row][label]}_'
                col_names.append(f'{name[:-1]}_{col}')
            df.columns = col_names

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

    if not isOnetoMany(meta_df, 'chemistry', 'element'):
        logging.info("At least 1 chemistry has multiple elements")

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

        chems = meta_df[meta_df['element'] == e]['chemistry'].drop_duplicates().tolist()
        chem = chems[0]
        if len(chems) > 1:
            logging.error(f'Error, multiple chemistries {chems} found for element {e}')
            return
        if pd.isnull(chem):
            chem = '-'

        header_row_names = ['Chemistry', 'Element', 'Wavelength']
        header_rows= [[f'{chem}'],[F'{e}'], element_df.loc['wavelength']]
        col_ix = pd.MultiIndex.from_product(header_rows, names = header_row_names)

        element_df.columns = col_ix
        element_df.drop('wavelength', inplace=True)
        frames.append(element_df)


    exportframe = pd.concat(frames, axis=1)
    if outfile:
        logging.info(f"Writing to {outfile} ...")
        exportframe.to_csv(outfile, sep='\t')
        logging.info(f"Done")
    return exportframe


def import_dir_to_csv(input_dir, regex, output_dir, separator='\t', append=False, primary_keys=None):

    if not os.path.exists(input_dir):
        logging.error('import folder not found')
        # print("Error, import folder not found")
        return

    if not append:
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)

    for filename in sorted(os.listdir(input_dir)):
        
        match = re.search(regex, filename)
        if not match:
            logging.warning(F"regex not matched on filename: {filename}")
            continue

        # Create a metadata dictionary with info extracted from filename
        metadata = match.groupdict()

        # If the element looks like an integer,
        # convert to a string with zero padding
        try: 
            e = int(metadata['element'])
            metadata['element'] = F"{e:02d}"
        except ValueError:
            #Otherwise, don't modify it
            pass

        # Read the file contents into a dataframe
        df = pd.read_csv(os.path.join(input_dir, filename), sep=separator)
        
        # Check how many repeats exist in the file and label them
        # Assumes the first column represents 'wavelength'
        reps = len(df.columns)-1
        col_names = ['wavelength']
        for r in range(reps):
            col_names.append(f'rep{r+1}')
        df.columns = col_names

        # TODO, the 'store' function reads and writes the full metadata file
        # each time, so room for improvement here.
        datapath = store(df, metadata, output_dir, primary_keys)
        logging.info(f'imported {filename} to {datapath}')

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

def apply_chem_map(chemistry_map, metapath):

    meta_df = read_metadata(metapath)
    if isinstance(chemistry_map, pd.DataFrame):
        chemistry_map = dict(chemistry_map.values)

    for index, row in meta_df.iterrows():
        try:
            chem = chemistry_map[row['element']]
            meta_df.at[index, 'chemistry'] = chem
            logging.info(f'Applying: {chem} to {index}')
        except KeyError:
            logging.error(f"Element {row['element']} not found in chemistry map")
    
    meta_df.to_csv(metapath, index=True, sep='\t', na_rep='')

# Check if there is a 1:1 relationship between 2 columns
# For example to check elements and chemistries match before export
def isOnetoOne(df, col1, col2):
    first = df.drop_duplicates([col1, col2]).groupby(col1)[col2].count().max()
    second = df.drop_duplicates([col1, col2]).groupby(col2)[col1].count().max()
    # Essentially this removes duplicates, then checks how many elements exist
    # for each chemistry, and vice versa. If both results are 1, there is a 1:1
    # relationship

    return first + second == 2

# Check if there is a 1:Many relationship between 2 columns
# For example to check elements and chemistries match before export
def isOnetoMany(df, col1, col_many):
    first = df.drop_duplicates([col1, col_many]).groupby(col1)[col_many].count().max()
    # Essentially this removes duplicates, then checks how many chemistries 
    # exist for each element, if the result is one, there is a 1:many (or 1:1)
    # relationship 

    return first == 1

def generate_run_list(setup, instrument):
    '''
    For doing a bulk run of measurements.
    This generates a list (dataframe) of metadata describing the measuremnts

    Takes dictionaries called setup{} and instrument{} in the example format
    provided. Measurement rows are generated for all permutations of fluids and
    elements.
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
                index = ''
                row['date'] = pd.NaT
                row['instrument'] = instrument['name']
                row['sensor'] = instrument['sensor']
                row['element'] = e
                row['chemistry'] = instrument['element_map'][e]
                row['fluid'] = f
                row['repeats'] = setup['repeats']
                row['hidden'] = False
                row['comment'] = pd.NA

                # Build the index as a string based on primary metadata
                for key in setup['primary_metadata']:
                    index += f'{row[key]}-'
                row['index'] = (index[:-1])

                for col in row.keys():
                    run_list[col].append(row[col])

    for col in run_list.keys():
        run_list[col] = pd.Series(run_list[col], dtype=default_metadata[col])

    # Convert to dataframe now (avoids iteratively appending to the dataframe)
    run_df = pd.DataFrame(run_list)

    # Specify that the 'index' column should be treated as the index
    run_df = run_df.set_index('index')

    return run_df

def write_df_txt(df, datapath, merge=True):
    '''
    df is the new data frame to be saved / merged in
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

def write_meta_df_txt(meta_df, metapath, merge=True, subdirs='fluid'):
    '''
    Writes a meta_df to metapath (index.txt)
    If file exists will try to merge them. The merge will fail if 2 rows have
    identical index names, but different data in the columns. 

    An exception is for the 'repeats' column, where it opens the data files to
    check how many repeats are actually present.

    NB - To get the correct repeat count, any new data files must be
    written/merged before this function is run.
    '''

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
                # ensure they don't get out of sync!
                path = os.path.dirname(metapath)
                for index in meta_df.index:
                    if index in existing_df.index:
                        subdir = meta_df.loc[index][subdirs] #Typically 'fluid'
                        datapath = os.path.join(path, subdir, f'{index}.txt')
                        with open(datapath, 'r') as d:
                            df = pd.read_csv(d, sep='\t')
                        reps = len(df.columns) -1
                        meta_df.at[index, 'repeats'] = reps
                        existing_df.at[index, 'repeats'] = reps

                meta_df.reset_index(inplace=True)
                existing_df.reset_index(inplace=True)

                meta_df = pd.merge(meta_df, existing_df, how='outer')

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

def bulk_measurement(setup, run_df, measure_func, subdirs='fluid'):
    '''
    For doing a bulk run of measurements.
    This iterates through a run list (run_df), calling measure_func for each
    repeat of each row.

    Data is saved into .txt files named according the index of the row in the
    run_df. The output directory is defined in setup{}

    the date column in run_df is populated, and then saved as index.txt in the
    output directory
    '''
    for index, row in run_df.iterrows():
        df = pd.DataFrame()
        for rep in range(row['repeats']):
            single_df = measure_func(setup, row)
            if len(df > 0):
                df = pd.merge(df, single_df, how='outer', on='wavelength')
            else:
                df = single_df

        datapath = os.path.join(setup['output_dir'], row[subdirs], f'{index}.txt')
        write_df_txt(df, datapath)

        # Update the date column in the run_df
        run_df.at[index, 'date'] = pd.Timestamp.utcnow().strftime('%Y-%m-%d')

    # Set date column to be correct time for merging with existing files
    # run_df['date'] = run_df['date'].astype('datetime64')
    metapath = os.path.join(setup['output_dir'], 'index.txt')
    
    write_meta_df_txt(run_df, metapath)

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

    for index in meta_df.index:
        in_subdir = meta_df.loc[index][in_subdirs]
        out_subdir = meta_df.loc[index][out_subdirs]
        input_datapath = os.path.join(input_path, in_subdir, f'{index}.txt')
        output_datapath = os.path.join(output_path, out_subdir, f'{index}.txt')
        with open(input_datapath, 'r') as f:
            df = pd.read_csv(f, sep='\t')

        write_df_txt(df, output_datapath)
    
    write_meta_df_txt(meta_df, output_metapath)

    if delete_input:
        shutil.rmtree(input_path)