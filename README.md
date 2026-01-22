# Script-Shop

## Introduction
The Script Shop™ is your one stop shop to find all the scripts you desire.

# Kismet

## KismetParse.py

Kismet Parse is a comprehensive tool for extracting, analyzing, and managing captured device information from a Kismet database and managing target alerts. The tool can generate intermediate files and/or directly configure Kismet target alerts with various options.

When executed in its most basic mode, the tool generates up to 7 sorted output files:

- **BTEDR.txt**: A list of targetable Bluetooth Classic Addresses.
- **BTLE.txt**: A list of targetable, nonrandom BTLE Addresses that have a specified name or manufacturer.
- **CLIENT.txt**: A list of all the WiFi Client MAC addresses that are not random in nature.
- **ProbedSSID.txt**: A list of all SSIDs probed for by a client device.
- **SSID.txt**: A list of all SSIDs produced from beacon frames.
- **AP.txt**: A list of all of the WiFi access point MAC addresses.
- **SENSORS.txt**: A list of all of the RF sensor addresses.

### Usage
```bash
# Basic usage - generates intermediate files only (no target alerts)
python KismetParse.py <target_capture.kismet>

# Generates Kismet alerts populated with targetable assests with producing output text files. (requires sudo)
sudo python KismetParse.py -e <target_capture.kismet>

# Add targets from existing intermediate files. All targets contain within files are used to create Kismet alerts. (requires sudo)
sudo python KismetParse.py -a

# Delete target Kismet configuration and remove all alerts (requires sudo)
sudo python KismetParse.py -d

# Clean up intermediate files by deleting them all
python KismetParse.py -c

# Use a baseline Kismet file to prevent anything captured in the baseline file from being tagged an a target in the Kismet file under scrutiny.
python -b <baseline_capture.kismet> <target_capture.kismet>

# Use a Kismet file to specify that only devices found in common with another Kismet file should be considered targetable.
python -i <intersect_capture.kismet> <target_capture.kismet>

# Create a clean kismet databaes file that only contains those devices that are considered targetable. Targetable assests must have already been generated.
python -k <new_kismet_file.kismet>
```

### Flags

- **-h, --help**: Shows the help message
- **-e, --exclude-files**: Generate target alerts directly without creating intermediate files
- **-a, --add-targets**: Add targets from existing intermediate files
- **-c, --clean**: Clean up intermediate files
- **-d, --delete-targets**: Delete target configuration file and include statement (removes all alerts)
- **-b BASELINE_DB, --baseline BASELINE_DB**: Specify a baseline file to remove any devices as targetable assets produces from the Kismet file under scrutiny. If the device exists in the baseline kismet file and the targeted kismet file, it is removed as a targetable asset in the intermediate target files.
- **-i INTERSECT_DB, --intersect INTERSECT_DB**: Specify a Kismet file, the intersect file, so that only devices that are in common with the Kismet file under scrutiny are output to the intermediate target files.
- **-k CLEAN_DB_NAME, --kismet-cleaned CLEAN_DB_NAME**: Creates a new kismet database file that only includes the extracted, targetable devices.

### Target Alert Generation
By default, the script only generates intermediate files and does **not** create Kismet target alerts. To generate target alerts, you must use either:
- **-a** flag to generate alerts from existing intermediate files
- **-e** flag to generate alerts directly from the database without creating intermediate files

Both target alert generation modes require sudo privileges as they modify Kismet configuration files.

To remove all target alerts, use the **-d** flag which will delete the target configuration file and remove the include statement from the main configuration. This also requires sudo privileges.

# Ubertooth

## ubersort.sh

UberSort is a tool for sorting the output of the ubertooths survey mode. The script will create two files from the input, appended with _LAP and _UAP respectively. The LAP file will simply be all the LAPs found by the ubertooth excluding those with UAPs. The UAP file will contain all of the UAP/LAP pairs, filling the NAP with 00:00.


### Usage
First run ubertooth-rx in survey mode, writing the result to a file:
```bash
ubertooth-rx -z > <your_file>
```
Then run the utility with:
```bash
chmod +x ubersort.sh
./ubersort.sh <your_file>
```
