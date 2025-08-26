import sqlite3
import json
import sys
import os
import subprocess
import argparse
from sqlite3 import Error

def create_connection(db_file):
    """Create a database connection to the SQLite database specified by db_file"""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(f"Successfully connected to {db_file}")
        return conn
    except Error as e:
        print(e)
    return conn

def extract_devices_json(conn):
    """Extract JSON data from the 'devices' table"""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT device FROM devices")
        rows = cursor.fetchall()

        devices_list = []
        for row in rows:
            try:
                device_json = json.loads(row[0])
                devices_list.append(device_json)
            except json.JSONDecodeError:
                print(f"Error decoding JSON for device: {row[0][:50]}...")  # Print first 50 chars of problematic data

        print(f"\nExtracted JSON data for {len(devices_list)} devices")
        return devices_list

    except Error as e:
        print("Error querying 'devices' table:", e)
        return []

def generate_intermediate_files(btedr_macs, btle_macs, client_macs, ap_macs, sensor_macs, advertised_ssids, probed_ssids):
    """Generate intermediate files like KismetParse.py does"""
    # Write files with unique entries
    with open("BTEDR.txt", "w") as f:
        f.write("\n".join(set(btedr_macs)))

    with open("BTLE.txt", "w") as f:
        f.write("\n".join(set(btle_macs)))
    
    with open("CLIENT.txt", "w") as f:
        f.write("\n".join(set(client_macs)))
    
    with open("SSID.txt", "w") as f:
        f.write("\n".join(set(advertised_ssids)))

    with open("ProbedSSID.txt", "w") as f:
        f.write("\n".join(set(probed_ssids)))

    with open("AP.txt", "w") as f:
        f.write("\n".join(set(ap_macs))) 
    
    with open("SENSORS.txt", "w") as f:
        f.write("\n".join(set(sensor_macs)))

    print("Intermediate files created with extracted SSIDs and MAC addresses")

def generate_target_alerts_from_files():
    """Generate Kismet target alert configuration from existing files (add_targets.sh functionality)"""
    config_dirs = ["/etc/kismet", "/usr/local/etc"]
    mac_sources = ["AP.txt", "BTEDR.txt", "BTLE.txt", "CLIENT.txt", "SENSORS.txt"]
    ssid_sources = ["SSID.txt", "ProbedSSID.txt"]
    processed_dirs = 0

    for config_dir in config_dirs:
        alerts_conf = os.path.join(config_dir, "kismet_alerts.conf")
        target_conf = os.path.join(config_dir, "kismet_target_alerts.conf")
        
        # Verify config directory and alerts file exist
        if os.path.isdir(config_dir) and os.path.isfile(alerts_conf):
            include_line = f"opt_include={target_conf}"
            
            # Add include directive if missing
            with open(alerts_conf, "r+") as f:
                content = f.read()
                if include_line not in content:
                    f.write(f"\n{include_line}\n")
            
            # Create fresh target file
            with open(target_conf, "w") as f:
                # Process SSIDs from all sources
                for ssid_file in ssid_sources:
                    if os.path.isfile(ssid_file):
                        with open(ssid_file, "r") as sf:
                            for line in sf:
                                ssid = line.strip()
                                if ssid:
                                    f.write(f'ssidcanary="{ssid}":ssid="{ssid}"\n')
                    else:
                        print(f"\033[33mWarning: {ssid_file} not found - skipping SSID alerts\033[0m")
                
                # Process MAC addresses from all sources
                for source in mac_sources:
                    if os.path.isfile(source):
                        with open(source, "r") as sf:
                            for line in sf:
                                mac = line.strip().replace('-', '')
                                if mac:
                                    f.write(f'devicefound={mac}\n')
                    else:
                        print(f"\033[33mWarning: {source} not found - skipping\033[0m")
            
            print(f"\033[32mConfiguration updated in {config_dir}\033[0m")
            processed_dirs += 1
    
    if processed_dirs == 0:
        print("\033[31mError: No valid Kismet configuration directories found\033[0m")
        sys.exit(1)

def clean_intermediate_files():
    """Clean up intermediate files"""
    files_to_clean = ["BTEDR.txt", "BTLE.txt", "CLIENT.txt", "SSID.txt", "ProbedSSID.txt", "AP.txt", "SENSORS.txt"]
    cleaned_files = []
    
    for file_name in files_to_clean:
        if os.path.exists(file_name):
            os.remove(file_name)
            cleaned_files.append(file_name)
    
    if cleaned_files:
        print(f"\033[32mCleaned up files: {', '.join(cleaned_files)}\033[0m")
    else:
        print("\033[33mNo intermediate files found to clean\033[0m")

def delete_target_configuration():
    """Delete target configuration file and include statement from Kismet configuration"""
    config_dirs = ["/etc/kismet", "/usr/local/etc"]
    processed_dirs = 0

    for config_dir in config_dirs:
        alerts_conf = os.path.join(config_dir, "kismet_alerts.conf")
        target_conf = os.path.join(config_dir, "kismet_target_alerts.conf")
        
        # Verify config directory and alerts file exist
        if os.path.isdir(config_dir) and os.path.isfile(alerts_conf):
            include_line = f"opt_include={target_conf}"
            
            # Remove include directive if present
            try:
                with open(alerts_conf, "r") as f:
                    content = f.read()
                
                if include_line in content:
                    # Remove the include line and any extra newlines around it
                    updated_content = content.replace(f"\n{include_line}\n", "\n")
                    updated_content = updated_content.replace(f"{include_line}\n", "")
                    updated_content = updated_content.replace(f"\n{include_line}", "")
                    updated_content = updated_content.replace(include_line, "")
                    
                    with open(alerts_conf, "w") as f:
                        f.write(updated_content)
                    
                    print(f"\033[32mRemoved include directive from {alerts_conf}\033[0m")
                else:
                    print(f"\033[33mInclude directive not found in {alerts_conf}\033[0m")
            except Exception as e:
                print(f"\033[31mError modifying {alerts_conf}: {e}\033[0m")
            
            # Remove target configuration file if it exists
            if os.path.isfile(target_conf):
                try:
                    os.remove(target_conf)
                    print(f"\033[32mDeleted target configuration file: {target_conf}\033[0m")
                except Exception as e:
                    print(f"\033[31mError deleting {target_conf}: {e}\033[0m")
            else:
                print(f"\033[33mTarget configuration file not found: {target_conf}\033[0m")
            
            processed_dirs += 1
    
    if processed_dirs == 0:
        print("\033[31mError: No valid Kismet configuration directories found\033[0m")
        sys.exit(1)
    else:
        print(f"\033[32mTarget configuration cleanup completed for {processed_dirs} directory(ies)\033[0m")

def generate_target_alerts(btedr_macs, btle_macs, client_macs, ap_macs, sensor_macs, ssid_list):
    """Generate Kismet target alert configuration from extracted data"""
    config_dirs = ["/etc/kismet", "/usr/local/etc"]
    target_config = "kismet_target_alerts.conf"
    processed = False

    for config_dir in config_dirs:
        alerts_conf = os.path.join(config_dir, "kismet_alerts.conf")
        target_path = os.path.join(config_dir, target_config)
        
        if os.path.isdir(config_dir) and os.path.isfile(alerts_conf):
            include_line = f"opt_include={target_path}"
            
            # Add include directive if missing
            with open(alerts_conf, "r+") as f:
                content = f.read()
                if include_line not in content:
                    f.write(f"\n{include_line}\n")
            
            # Generate target configuration
            with open(target_path, "w") as f:
                # Write SSID alerts
                for ssid in set(ssid_list):
                    if ssid:
                        f.write(f'ssidcanary="{ssid}":ssid="{ssid}"\n')
                
                # Write MAC alerts
                mac_sources = {
                    'btedr': btedr_macs,
                    'btle': btle_macs,
                    'client': client_macs,
                    'ap': ap_macs,
                    'sensor': sensor_macs
                }
                
                for mac_type, macs in mac_sources.items():
                    for mac in set(macs):
                        cleaned_mac = mac.strip().replace('-', '')
                        if cleaned_mac:
                            f.write(f'devicefound={cleaned_mac}\n')
            
            print(f"\033[32mConfiguration updated in {config_dir}\033[0m")
            processed = True
            break
    
    if not processed:
        print("\033[31mError: No valid Kismet configuration directories found\033[0m")
        sys.exit(1)

def sort_devices_to_files(devices_list, generate_files=True, generate_targets=False):
    btedr_macs = []
    btle_macs = []
    client_macs = []
    advertised_ssids = []
    probed_ssids = []
    ap_macs = []
    sensor_macs = []

    for device in devices_list:
        dev_type = device.get("kismet.device.base.type")
        mac = device.get("kismet.device.base.macaddr")

        # Handle Bluetooth devices
        if dev_type == "BR/EDR":
            if mac:
                btedr_macs.append(mac)

        # Handle Bluetooth Low Energy devices
        if dev_type == "BTLE":
            if mac and (device.get("kismet.device.base.macaddr") != device.get("kismet.device.base.commonname") or 
                        device.get("kismet.device.base.manuf") != "Unknown"):
                btle_macs.append(mac)
        
        # Handle Wi-Fi Clients and their probed SSIDs
        elif dev_type in ["Wi-Fi Client", "Wi-Fi Ad-Hoc","Wi-Fi Device","Wi-Fi Bridged"]:
            if mac and device.get("kismet.device.base.manuf") != "Unknown":
                client_macs.append(mac)

            # Extract probed SSIDs 
            try:
                ssids = []
                ssid_map = device.get("dot11.device").get("dot11.device.probed_ssid_map")
                for map in ssid_map:
                    ssid = map.get("dot11.probedssid.ssid")
                    if ssid != "":
                        ssids.append(ssid)
                probed_ssids.extend(ssids)  # Store unique SSIDs for later use
            except:
                pass
        
        # Handle Wi-Fi APs and their advertised SSIDs
        elif dev_type in ["Wi-Fi AP","Wi-Fi WDS AP","WiFi WDS"]:
            if mac:
                ap_macs.append(mac)

            # Extract advertised SSIDs 
            try:
                ssids = []
                ssid_map = device.get("dot11.device").get("dot11.device.advertised_ssid_map")
                for map in ssid_map:
                    ssid = map.get("dot11.advertisedssid.ssid")
                    if ssid:
                        ssids.append(ssid)
                advertised_ssids.extend(ssids)
            except:
                pass
            
        # Handle Sensors
        elif dev_type == "Sensor" and mac:
            sensor_macs.append(mac)

    if generate_files:
        # Generate intermediate files only
        generate_intermediate_files(btedr_macs, btle_macs, client_macs, ap_macs, sensor_macs, advertised_ssids, probed_ssids)
    
    if generate_targets:
        # Generate alerts directly without intermediate files (when -e flag is used)
        generate_target_alerts(btedr_macs, btle_macs, client_macs, ap_macs, sensor_macs, probed_ssids)

    return btedr_macs, btle_macs, client_macs, ap_macs, sensor_macs, advertised_ssids, probed_ssids

def subtract_baseline(new_data, baseline_data):
    """
    Subtract baseline MACs/SSIDs/etc. from new data
    Returns the filtered version of (btedr, btle, client, ap, sensor, adv_ssids, probed_ssids)
    """
    new_btedr, new_btle, new_client, new_ap, new_sensor, new_adv_ssids, new_probed_ssids = new_data
    base_btedr, base_btle, base_client, base_ap, base_sensor, base_adv_ssids, base_probed_ssids = baseline_data

    return (
        list(set(new_btedr) - set(base_btedr)),
        list(set(new_btle) - set(base_btle)),
        list(set(new_client) - set(base_client)),
        list(set(new_ap) - set(base_ap)),
        list(set(new_sensor) - set(base_sensor)),
        list(set(new_adv_ssids) - set(base_adv_ssids)),
        list(set(new_probed_ssids) - set(base_probed_ssids))
    )


def load_and_sort_devices(db_file):
    """Helper function: connect to DB, extract device JSON, sort into categories"""
    conn = create_connection(db_file)
    if conn is None:
        print(f"Database connection failed: {db_file}")
        return None
    devices = extract_devices_json(conn)
    conn.close()
    if not devices:
        return None
    return sort_devices_to_files(devices, generate_files=False, generate_targets=False)
    

def main():
    parser = argparse.ArgumentParser(description='Kismet device parser and target alert generator')
    parser.add_argument('database', nargs='?', help='Path to the Kismet database file')
    parser.add_argument('-a', '--add-targets', action='store_true', 
                        help='Add targets from existing intermediate files (add_targets.sh functionality)')
    parser.add_argument('-c', '--clean', action='store_true', 
                        help='Clean up intermediate files')
    parser.add_argument('-d', '--delete-targets', action='store_true',
                        help='Delete target configuration file and include statement')
    parser.add_argument('-e', '--exclude-files', action='store_true', 
                        help='Generate target alerts directly without creating intermediate files')
    parser.add_argument('-b', '--baseline', metavar="BASELINE_DB",
                        help='Path to baseline database file (devices in baseline will be excluded)')

    args = parser.parse_args()
    
    if args.clean:
        clean_intermediate_files()
        if not args.database and not args.add_targets and not args.delete_targets:
            return
    
    if args.delete_targets:
        if os.geteuid() != 0:
            print("\033[31mPermission Error: Restarting with sudo...\033[0m")
            subprocess.call(['sudo', sys.executable] + sys.argv)
            sys.exit()
        delete_target_configuration()
        return
    
    if args.add_targets:
        if os.geteuid() != 0:
            print("\033[31mPermission Error: Restarting with sudo...\033[0m")
            subprocess.call(['sudo', sys.executable] + sys.argv)
            sys.exit()
        generate_target_alerts_from_files()
        return
    
    if not args.database:
        parser.print_help()
        print("\nError: Database file is required unless using -a, -c, or -d flags")
        sys.exit(1)

    if args.exclude_files and os.geteuid() != 0:
        print("\033[31mPermission Error: Restarting with sudo...\033[0m")
        subprocess.call(['sudo', sys.executable] + sys.argv)
        sys.exit()
    
    # Load new database devices
    new_data = load_and_sort_devices(args.database)
    if new_data is None:
        print("No devices found in new database")
        sys.exit(1)

    # Load and subtract baseline if requested
    if args.baseline:
        base_data = load_and_sort_devices(args.baseline)
        if base_data is not None:
            print(f"Applying baseline filter using {args.baseline}")
            new_data = subtract_baseline(new_data, base_data)
        else:
            print("\033[33mWarning: Baseline database empty or invalid\033[0m")

    btedr_macs, btle_macs, client_macs, ap_macs, sensor_macs, advertised_ssids, probed_ssids = new_data

    # Write results
    if not args.exclude_files:
        # Default behavior: generate intermediate text files
        generate_intermediate_files(btedr_macs, btle_macs, client_macs, ap_macs, sensor_macs, advertised_ssids, probed_ssids)
    else:
        # Directly generate alerts without intermediate files
        generate_target_alerts(btedr_macs, btle_macs, client_macs, ap_macs, sensor_macs, probed_ssids)

if __name__ == '__main__':
    main()
