# import numpy as np
import pandas as pd
# from datetime import datetime
import os
import re
import shutil

# from pandas.core.reshape.merge import merge_asof

default_metadata = {
    'sensor'            : None,
    'element'           : None,
    'fluid'             : None,
    'repeats'           : None,
    'import_date'       : None,
}

def store(df, metadata, path='./raw'):

    if not os.path.exists(path):
        os.makedirs(path)

    metapath = os.path.join(path, "index.tsv")
    if os.path.isfile(metapath):
        meta_df = pd.read_csv(metapath, sep='\t', index_col='index')
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
            # print(F'Warning, file exists: {datapath}, appending columns')
            existing_df = pd.read_csv(f, sep='\t')
            df = pd.merge(df, existing_df, how='outer', on='wavelength')

            #relabel columns  -  Unless they are timestamped
            col_names = ['wavelength']
            n=0
            # print(df.columns[1:])
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


# Extracts dataframes from file and merges them into a single dataframe
# nodelist is a list of strings describing hdf paths
# Outer join means that rows from all dataframes are preserved, and NaN is
# filled where needed
def merge_dataframes(filename, nodelist):
    result = []
    for node in nodelist:
        df = pd.read_hdf(filename, node)
        if len(result) > 0:
            result = pd.merge(result, df, how='outer', on='wavelength')
        else:
            result = df
    return result

def filter_by_metadata(metakey, metavalue, path='./raw', input_df=None, regex=False):
   
    if isinstance(input_df, pd.DataFrame):
        df = input_df

    else:
        metapath = os.path.join(path, "index.tsv")
        if os.path.isfile(metapath):
            df = pd.read_csv(metapath,
                            sep='\t',
                            index_col='index',
                            parse_dates=['date', 'import_date'],
                            dtype={'element' : str}
                            )
        else:
            print('index.tsv file not found')
            return

    if regex:
        regexdf = df[df[metakey].str.match(metavalue)]
        return(regexdf)
    else:
        exactdf = df.loc[df[metakey] == metavalue]
        return(exactdf)





def export_dataframes(h5file, nodelist, outfile=None):
    # measurements = measurement_nodes(h5file, '/')
    elements = set()
    with h5py.File(h5file, 'r') as f:
        for node in nodelist:
            obj = f[node]
            try:
                elements.add(obj.attrs['element'])
            except Exception as e:
                print(node)
                print(e)

    elements = sorted(elements)

    frames=[]
    for e in elements:
        selection = filter_by_metadata(h5file, 'element', e, nodelist=nodelist)
        element_df = merge_dataframes(h5file, selection)
        element_df = element_df.transpose()
        iterables = [[F"Element {e}"], element_df.loc['wavelength']]
        col_ix = pd.MultiIndex.from_product(iterables)
        element_df.columns = col_ix
        frames.append(element_df)


    exportframe = pd.concat(frames, axis=1)
    exportframe.drop('wavelength', inplace=True)
    if outfile:
        exportframe.to_csv(outfile)
    return exportframe


def import_dir_to_csv(input_dir, regex, output_dir, separator='\t', append=False):

    if not os.path.exists(input_dir):
        print("Error, import folder not found")
        return

    if not append:
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)

    for filename in sorted(os.listdir(input_dir)):
        
        match = re.search(regex, filename)
        if not match:
            print(F"Warning regex not matched on filename: {filename}")
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
            col_names.append(str(r+1))
        df.columns = col_names

        store(df, metadata, output_dir)


