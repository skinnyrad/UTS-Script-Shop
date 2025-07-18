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

# Delete target configuration and remove all alerts (requires sudo)
sudo python KismetParse.py -d

# Clean up intermediate files
python KismetParse.py -c
```

### Flags

- **-h, --help**: Shows the help message
- **-e, --exclude-files**: Generate target alerts directly without creating intermediate files
- **-a, --add-targets**: Add targets from existing intermediate files
- **-c, --clean**: Clean up intermediate files
- **-d, --delete-targets**: Delete target configuration file and include statement (removes all alerts)

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
