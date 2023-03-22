tooltips = {
    "setup" : {
        "name" : "Switch to editing a different setup file", 
        "category" : "Read-only tag identifying where in the setup heirarchy this file is",
        "metafile" : "Select the metadata Index file, a record of which measurements have been made.\nTypically 'index.txt'",
        "datadir"  : "Select the working directory (containing the metadata index file)",
        "subdirs"  : "subdirectory structure (within datadir) used to store measurement data\ne.g. ['Sensor', 'fluid'] becomes datadir/<sensor>/<fluid>/",
        "primary_metadata" : "Select the metadata fields used to name measurement files."
                            +"\nMeasurements with matching primary_metadata will be combined into a single file"
                            +"\ne.g. ['sensor', 'element', 'fluid'] becomes <sensor>-<element>-<fluid>.txt",
        "instrument" : "select the instrument metadata (not really used by code, for future reference only)",
        "sensor" : "select the sensor (slide) parameters",
        "input_config" : "select the parameters for capturing data",
        "output_config" : "select the defaults for processing and exporting the data",
    },
    "input_config" : {
        "name" : "Name of this input_config, will be added to dropdown list at the 'setup' level\nand saved as a .json file in rootdir/setup/input_config",
        "category" : "Read-only tag identifying where in the setup heirarchy this file is",
        "fluids"   : "A list of fluids expected to be used\n"
                    +"For convenience this populates the drop down menus on the 'Measure' tabs\n"
                    +"Can be blank, or a list e.g. ['Air', 'Water']",
        "elements" : "A list of elements to iterate through during batch measurements\n"
                    +"Can be 'all' or a list e.g. ['A01', 'A02']\n"
                    +"list elements must exist in the sensor layout map",
        "repeats"  : "How many consecutive measurements to do on each element",
        "grid_shape" : "To run additional measurements on each element in a grid pattern (small offsets from the centre)\n"
                      +"Valid settings are '3x3_grid' or 'cross'",
        "wavelength_range" : "Spectrophotometer wavelengths to capture, in nanometres. [start, stop, step] e.g. [450, 900, 0.5]\n"
                             +"NB 'step' is used for dummy measurements, not stellarnet Bluewave)",
        "integration_time" : "Spectrophotometer integration time in milliseconds (see Stellarnet Documentation)",
        "scans_to_avg"     : "Spectrophotometer number of scans to be averaged (see Stellarnet Documentation)",
        "x_timing"     : "Spectrophotometer XTiming Rate (see Stellarnet Documentation)",
        "x_smooth"     : "Spectrophotometer boxcar smoothing window size (see Stellarnet Documentation)",
        "lightref_offset_x" : "If capturing regular light references (with lightref_interval), this is the x direction offset in mm from the current sensor element",
        "lightref_interval" : "To update the light reference every [n]th element, can be 0 to disable",
        "delay_between_reps" : "Optional delay between repeats in seconds. Typically used to capture episodic data on a single element",
    },
    "output_config" : {
        "name" : "Name of this output_config, will be added to dropdown list at the 'setup' level\nand saved as a .json file in rootdir/setup/output_config",
        "category" : "Read-only tag identifying where in the setup heirarchy this file is", 
        "wavelength_range" : "Processing settings for Export Tab. format is: [True/False, wl_min, wl_max]",
        "smooth" : "Processing settings for Export Tab. format is: [True/False, smoothpoints]",
        "interpolate" : "Processing settings for Export Tab. format is: [True/False, samplerate]",
        "normalise" : "Processing settings for Export Tab. format is: [True/False]",
        "round" : "Processing settings for Export Tab. format is: [True/False, decimalplaces]",
        "average_repeats" : "Processing settings for Export Tab. format is: [True/False]",
        "outfile" : "Filename to export to, e.g. 'exported_data.txt', or can be None",
    },
    "sensor" : {
        "name" : "Name of this sensor, will be added to dropdown list at the 'setup' level\nand saved as a .json file in rootdir/setup/sensor",
        "category" : "Read-only tag identifying where in the setup heirarchy this file is",
        "layout"   : "Select the physical layout of the elements on this sensor, used to move the stage to correct position",
        "structure_map" : "Select a mapping of nanostructures to elements on this sensor. Mainly for future reference",
        "surface_map" : "Select a mapping of surface chemistries to elements on this sensor. Mainly for future reference",
    }

}
    