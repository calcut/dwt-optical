# import numpy as np
import pandas as pd
import tables
from datetime import datetime
import os
import re


# Write dataframe and a metadata object (e.g. dictionary) to an hdf5 file
# Fixed format gives a much smaller file size 
# Table format would allow appending to individual tables, not needed.
def store(filename, hdfkey, df, metadata):
    store = pd.HDFStore(filename, mode='a')
    if hdfkey in store:
        store.close()
        raise ValueError(F'Error, node already exists in HDF5 file: {hdfkey}')
    else:
        store.put(hdfkey, df, format='fixed')
        store.get_storer(hdfkey).attrs.metadata = metadata
    store.close()

# Load a dataframe from an hdf5 file, also return associated metadata
def load(filename, hdfkey):
    store = pd.HDFStore(filename, mode='r')
    data = store[hdfkey]
    metadata = store.get_storer(hdfkey).attrs.metadata
    store.close()
    return data, metadata

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

# Returns a list of nodes with an attribute called metadata
# Intended as an initial filter to remove irrelevant nodes (or sub nodes)
def measurement_nodes(filename, hdfkey):
    with tables.open_file(filename, 'r') as f:
        nodelist = []
        for node in f.walk_nodes(hdfkey):
            if hasattr(node._v_attrs, 'metadata'):
                nodelist.append(node._v_pathname)
    return nodelist

# Checks each node in a list for a key/value pair in the metadata.
# Returns a filtered list containing only nodes with desired metadata.
# Can be called recursively to filter for more than one key
def filter_by_metadata(filename, key, value, nodelist):
    with tables.open_file(filename, 'r') as f:
        result = []
        for node in nodelist:
            node = f.get_node(node)
            try:
                if (node._v_attrs.metadata[key] == value ):
                    result.append(node._v_pathname)
            except Exception as e:
                pass
    return result

def inspect(filename):
    measurements = measurement_nodes(filename, '/')

    # measurements = filter_by_metadata(filename, 'element_index', "A00", measurements)
    # measurements = filter_by_metadata(filename, 'fluid', "water", measurements)

    num = len(measurements)
    fluids = set()
    elements = set()
    dates = set()
    data_lengths = set()
    reps = set()

    for node in measurements:
        data, metadata = load(filename, node)
        fluids.add(metadata['fluid'])
        elements.add(metadata['element_index'])
        reps.add(metadata['repeat'])
        try:
            time = datetime.fromtimestamp(metadata['timestamp'])
            dates.add(time.strftime('%Y_%m_%d'))
        except KeyError:
            #No timestamp in file
            pass

        transmission_col = data.columns[1]
        data_len = len(data[transmission_col])
        data_lengths.add(data_len)

        #Make sure each wavelength has a data point
        if data_len != len(data['wavelength']):
            print("Warning column/index length mismatch")

    #Expected number of measurements, assuming all permutations are present
    expected = len(fluids) * len(elements) * len(reps)

    print(F"Found {num} measurements out of {expected} expected permutations, including:\n"
        F"{len(fluids)} fluids {sorted(fluids)}\n"
        F"{len(elements)} elements {sorted(elements)}\n"
        F"{len(reps)} repeats {sorted(reps)}\n"
        F"{len(dates)} dates {sorted(dates)}\n"
        F"{len(data_lengths)} Data lengths {sorted(data_lengths)}")


def export_dataframes(h5file, outfile, nodelist):
    # measurements = measurement_nodes(h5file, '/')

    elements = set()
    with tables.open_file(h5file, 'r') as f:
        for node in nodelist:
            # data, metadata = load(h5file, node)
            n = f.get_node(node)
            try:
                elements.add(n._v_attrs.metadata['element_index'])
            except:
                print(F"Error, could not find 'element_index' in metadata for {node}")

    elements = sorted(elements)

    frames=[]
    for e in elements:
        selection = filter_by_metadata(h5file, 'element_index', e, nodelist)
        element_df = merge_dataframes(h5file, selection)
        element_df = element_df.transpose()
        iterables = [[F"Sensor {e}"], element_df.loc['wavelength']]
        col_ix = pd.MultiIndex.from_product(iterables)
        element_df.columns = col_ix
        frames.append(element_df)


    exportframe = pd.concat(frames, axis=1)
    exportframe.drop('wavelength', inplace=True)
    exportframe.to_csv(outfile)
    return exportframe


def import_dir_to_hdf(dir, regex, h5file, separator='\t', append=False):
    import_date = datetime.utcnow().strftime('%Y_%m_%d')

    if not os.path.exists(dir):
        print("Error, import folder not found")
        return

    if os.path.exists(h5file) and not append:
        os.remove(h5file)

    for filename in sorted(os.listdir(dir)):
        
        match = re.search(regex, filename)
        if not match:
            print(F"Warning regex not matched on filename: {filename}")
            continue

        # Create a metadata dictionary with info extracted from filename
        metadata = match.groupdict()

        # If the element looks like an integer,
        # convert to a string with zero padding
        try: 
            e = int(metadata['element_index'])
            metadata['element_index'] = F"{e:02d}"
        except ValueError:
            #Otherwise, don't modify it
            pass

        # Shorthand for some metadata values, to be used in Fstrings
        s = metadata['sensor']
        f = metadata['fluid']
        e = metadata['element_index']

        # Read the file contents into a dataframe
        df = pd.read_csv(os.path.join(dir, filename), sep=separator)
        
        # Check how many repeats exist in the file and label them
        # Assumes the first column represents 'wavelength'
        reps = len(df.columns)-1
        col_names = ['wavelength']
        for r in range(reps):
            col_names.append(str(r+1))
        df.columns = col_names

        # For every repeat in the file, create a new dataframe with only that data
        for r in range(reps):
            df_single = df.filter(['wavelength', str(r+1)])

            # update metadata to preserve info about the imported file
            if 'rotation' in metadata:
                metadata['imported_as'] = F"Rotation{metadata['rotation']}_{r+1}"
                metadata.pop('rotation', None)

            # This loop tries to save the dataframe and metadata to the hdf5
            # If the hdfkey already exists, the repeat number is incremented before
            # retrying
            hdf_r = r+1
            while True:
                try:
                    r_str = F"{hdf_r:02d}"
                    hdfkey = F"{s}/_{import_date}/{f}/_{e}_rep{r_str}"
                    df_single.columns=(['wavelength', F"{f}_rep{r_str}"])
                    metadata['repeat'] = r_str
                    store(h5file, hdfkey, df_single, metadata)
                    print(F"importing {filename} to {hdfkey}")
                    break
                except ValueError as err:
                    hdf_r += 1


