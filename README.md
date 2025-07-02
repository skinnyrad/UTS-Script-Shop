# Script-Shop

## Introduction
The Script Shop™ is your one stop shop to find all the scripts you desire.

# Kismet

## KismetParse.py

Kismet Parse is a comprehensive tool for extracting captured device information from a Kismet database and managing target alerts. The tool can generate intermediate files and/or directly configure Kismet target alerts with various options.

The tool generates up to 7 sorted output files:

- **BTEDR.txt**: A list of targetable Bluetooth Classic Addresses.
- **BTLE.txt**: A list of targetable BTLE Addresses that have a specified name or manufacturer.
- **CLIENT.txt**: A list of all the WiFi Client MAC addresses that are not random in nature.
- **ProbedSSID.txt**: A list of all SSIDs probed for by a client device.
- **SSID.txt**: A list of all SSIDs produced from a beacon frame.
- **AP.txt**: A list of all of the WiFi access point MAC addresses.
- **SENSORS.txt**: A list of all of the RF sensor addresses.

### Usage
```bash
# Basic usage - generates intermediate files only (no target alerts)
python KismetParse.py <your_capture.kismet>

# Generate target alerts directly without intermediate files (requires sudo)
sudo python KismetParse.py -e <your_capture.kismet>

# Add targets from existing intermediate files (requires sudo)
sudo python KismetParse.py -a

# Clean up intermediate files
python KismetParse.py -c

# Combine flags - clean files after processing
python KismetParse.py -c <your_capture.kismet>
```

### Flags
- **-e, --exclude-files**: Generate target alerts directly without creating intermediate files
- **-a, --add-targets**: Add targets from existing intermediate files (replaces add_targets.sh)
- **-c, --clean**: Clean up intermediate files

### Target Alert Generation
By default, the script only generates intermediate files and does **not** create Kismet target alerts. To generate target alerts, you must use either:
- **-a** flag to generate alerts from existing intermediate files
- **-e** flag to generate alerts directly from the database without creating intermediate files

Both target alert generation modes require sudo privileges as they modify Kismet configuration files.

### Note on Tool Consolidation
The functionality of `add_targets.sh` and `KismetTargets.py` has been consolidated into the main `KismetParse.py` script. The old separate scripts are no longer needed - all functionality is now available through the unified interface with command-line flags.

# Ubertooth

## sort_and_format.sh

Sort and Format is a tool for sorting the output of the ubertooths survey mode. The script will create two files from the input, appended with _LAP and _UAP respectively. The LAP file will simply be all the LAPs found by the ubertooth excluding those with UAPs. The UAP file will contain all of the UAP/LAP pairs, filling the NAP with 00:00.


### Usage
First run ubertooth-rx in survey mode, writing the result to a file:
```bash
ubertooth-rx -z > <your_file>
```
Then run the utility with:
```bash
chmod +x sort_and_format.sh
./sort_and_format.sh
```
