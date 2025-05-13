# Script-Shop

## Introduction
The Script Shop™ is your one stop shop to find all the scripts you desire.

# Kismet

## KismetParse.py

Kismet Parse is a tool for extracting captured device information from a kismet database. The tool reads over the database and generates 7 sorted output files:

- **BTEDR.txt** : A list of targetable Bluetooth Classic Addresses.
- **BTLE** A list of targetable BTLE Addresses that have a specified name or manufacturer.
- **CLIENT.txt**: A list of all the WiFi Client MAC addresses that are not random in nature.
- **ProbedSSID.txt**: A list of all SSIDs probed for by a client device.
- **SSID.txt**: A list of all SSIDs prodcued from a beacon frame.
- **AP.txt**: A list of all of the WiFi access point MAC addresses.
- **SENSORS.txt**: A list of all of the RF sensor addresses.

### Usage
```bash
python KismetParse.py <your_capture.kismet>
```

## add_targets.sh

Add Targets is a tool for adding kismet alerts to a new alerts configuration file that are generated from the resulst of Kismet Parse. **KISMETPARSE.PY MUST BE RAN FIRST**. 

The script will add the configuration file to the kismet configuration directory. For a package install, this will be `/etc/kismet/`, and for a build from source, this will be `/usr/local/etc/`. The alert file will be written as `kismet_target_alerts.conf`, and deleting this file means the alerts will get removed again.


### Usage
```bash
chmod +x add_targets.sh
./add_targets.sh
```

## KismetTargets.py

Kismet Targets marries the above two scripts into one script making it possible to generate the target alerts without having to generate intermediate files. It will preform the exact function of running both scripts back to back, but no extra files will be generated in the process.


### Usage
```bash
python KismetParse.py <your_capture.kismet>
```

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
