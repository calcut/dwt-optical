import pandas as pd
import os
import re
import shutil
from IPython.display import display
import logging

# logging.basicConfig(level=logging.INFO)


default_metadata = {
    'sensor'            : None,
    'element'           : None,
    'chemistry'         : None,
    'fluid'             : None,
    'repeats'           : None,
    'date'              : None,
    'hidden'            : False
}

primary_metadata = [
    'date',
    'sensor',
    'element',
    'fluid'
]

def store(df, metadata, path='./raw'):

    if not os.path.exists(path):
        os.makedirs(path)

    metapath = os.path.join(path, "index.tsv")
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

    meas_id = F"{d}-{s}-{f}-{e}"
    datapath = os.path.join(path, s, f'{meas_id}.tsv')

    os.makedirs(os.path.dirname(datapath), exist_ok=True)

    # Check if the file exists, then write the data 
    if not os.path.isfile(datapath):
        with open(datapath, 'w') as f:
            df.to_csv(f, index=False, sep='\t', mode='w')

    # If file exists, read it, merge, then rewrite the data
    else:
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

            
    meta_df.to_csv(f'{metapath}', index=True, sep='\t', na_rep='')
    return datapath


# Extracts dataframes from files and merges them into a single dataframe
# Requires a metadata frame to know which measurements to select
# Columns are renamed to show only the relevant metadata
# Outer join means that rows from all dataframes are preserved, and NaN is
# filled where needed
def merge_dataframes(meta_df, path='./raw'):
    result = []
    for row in meta_df.index:

        # locate the datafile and read it in
        subdir = meta_df.loc[row]['sensor']
        datapath = os.path.join(path, subdir, f'{row}.tsv') 
        df = pd.read_csv(datapath, sep='\t')

        # Name the output columns based on metadata
        col_names = ['wavelength']
        for col in df.columns[1:]:
            name = str()

            # Ignore metadata that is the same for measurements
            # i.e. only select columns with more than 1 unique value
            valid_meta = meta_df.columns[meta_df.nunique() > 1]

            # Ignore columns which aren't considered primary metadata
            # primary_metadata = ['date', 'sensor', 'fluid',' element']
            valid_meta = valid_meta.intersection(primary_metadata)

            for label in valid_meta:
                name += f'{meta_df.loc[row][label]}_'
            col_names.append(name[:-1])
        df.columns = col_names

        if len(result) > 0:
            result = pd.merge(result, df, how='outer', on='wavelength')
        else:
            result = df
    return result

def filter_by_metadata(metakey, metavalue, df, regex=False):
    
    try:
        df[metakey]
    except KeyError:
        logging.error(f'Key "{metakey}" not found in dataframe')
        return pd.DataFrame()

    if regex:
        logging.info(f'filtering by metadata "{metakey}" containing "{metavalue}"')
        regexdf = df[df[metakey].astype(str).str.contains(str(metavalue))]
        return(regexdf)
    else:
        logging.info(f'filtering by metadata "{metakey}" == "{metavalue}"')
        exactdf = df.loc[df[metakey].astype(str) == str(metavalue)]
        return(exactdf)


def export_dataframes(path='.', meta_df='index.tsv', outfile=None):

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
        selection = filter_by_metadata('element', e, input_df=meta_df)
        element_df = merge_dataframes(selection, path)
        element_df = element_df.transpose()

        chems = meta_df[meta_df['element'] == e]['chemistry'].drop_duplicates().tolist()
        chem = chems[0]
        if len(chems) > 1:
            logging.error(f'Error, multiple chemistries {chems} found for element {e}')
            return
        if pd.isnull(chem):
            chem = 'unknown chemistry'

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


def import_dir_to_csv(input_dir, regex, output_dir, separator='\t', append=False):

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
            # print(F"Warning regex not matched on filename: {filename}")
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

        # Shorthand for some metadata values, to be used in Fstrings
        s = metadata['sensor']
        f = metadata['fluid']
        e = metadata['element']

        # Read the file contents into a dataframe
        df = pd.read_csv(os.path.join(input_dir, filename), sep=separator)
        
        # Check how many repeats exist in the file and label them
        # Assumes the first column represents 'wavelength'
        reps = len(df.columns)-1
        col_names = ['wavelength']
        for r in range(reps):
            col_names.append(f'rep{r+1}')
        df.columns = col_names

        datapath = store(df, metadata, output_dir)
        logging.info(f'imported {filename} to {datapath}')

def read_metadata(metapath):
    if os.path.isfile(metapath):
        meta_df = pd.read_csv(metapath,
                        sep='\t',
                        index_col='index',
                        parse_dates=['date'],
                        dtype={'element' : str,
                               'chemistry' : str
                               }
                        )
    else:
        logging.error(f'{metapath} not found')
        return
    return meta_df

def apply_chem_map(chemistry_map, metapath):

    meta_df = read_metadata(metapath)

    for index, row in meta_df.iterrows():
        try:
            meta_df.at[index, 'chemistry'] = chemistry_map[row['element']]
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