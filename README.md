# filamentation_data_proc
Basic functions for experimental data processing for data obtained in experiments on femtosecond laser filamentation conducted in Relativistic Laser Plasma laboratory, ILC MSU. Includes auxiliary functions for data reading, plotting, searching plot parameters for better plot quality, some values and parameters conversions, and for correct energy retriving from the energy detector waveform. Also includes basic functions for data samples and pulse energy matching.

## Dependencies
To use the module you will need installed python3 on your machine.

The module uses functions from numpy, matplolib, os, sys, shutil and struct modules, so you will need to have this modules installed as well.

## Installing
To install the module on linux you need to run 'setup.py' script:
```
sudo python3 setup.py install
```

## Uninstalling
To uninstall run 'uninstall.sh':
```
sudo sh uninstall.sh
```

## Project contents
### ./data_proc/data_proc_basics_script
Functions for:
- acoustics ('.bin') and ('.dat') energies data files reading;
- converting date and time information from data file to seconds;
- select x-range for optoacoustic pulse energy meter waveform averaging;
- find maximum values for experimental data (max value for acoustic waveform and interference data and sum within user-defined area for luminescence and mode data);
- preparing of a properly sorted data list for mathcing with energies data;

### ./data_proc/lumin_proc
Functions for:
- luminescence and modes ('.dat') data files reading and saving;
- image rotation;
- reading and acounting for the CCD beakdowns map;
- 1d and 2d running average;
- searching limits for data plotting.

### ./data_proc/plotters
Functions for:
- plot waveforms from oscilloscope ('.bin' data);
- modes and luminescence ('heat map') plotter (with and without latex).

### ./compare_ac_with_en
Functions for:
- matching data with energies accounting for lost shots in data and file with energies for data obtained on different computers (for user or program-defined time shift between the data);
- matching data with energies for data obtained at the same computer;
- checking if there were 'lost' strobs;
- some auxiliary funcrions for data mathcing.
