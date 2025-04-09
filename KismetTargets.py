import sqlite3
import json
import sys
import os
import subprocess
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

def generate_target_alerts(bt_macs, client_macs, ap_macs, sensor_macs, ssid_list):
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
                    'bt': bt_macs,
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

def sort_and_configure_devices(devices_list):
    """Process devices and configure Kismet alerts directly"""
    bt_macs = []
    client_macs = []
    ssid_list = []
    ap_macs = []
    sensor_macs = []

    for device in devices_list:
        dev_type = device.get("kismet.device.base.type")
        mac = device.get("kismet.device.base.macaddr")

        # Handle Bluetooth devices
        if dev_type == "BR/EDR":
            if mac:
                bt_macs.append(mac)

        # Handle Bluetooth Low Energy devices
        if dev_type == "BTLE":
            if mac and (device.get("kismet.device.base.macaddr") != device.get("kismet.device.base.commonname") or 
                        device.get("kismet.device.base.manuf") != "Unknown"):
                bt_macs.append(mac)
        
        # Handle Wi-Fi Clients and their probed SSIDs
        elif dev_type in ["Wi-Fi Client", "Wi-Fi WDS", "Wi-Fi Ad-Hoc"]:
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
                ssid_list.extend(ssids)  # Store unique SSIDs for later use
            except:
                pass
        
        # Handle Wi-Fi APs and their advertised SSIDs
        elif dev_type in ["Wi-Fi AP","Wi-Fi WDS AP"]:
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
                ssid_list.extend(ssids)
            except:
                pass
            
        # Handle Sensors
        elif dev_type == "Sensor" and mac:
            sensor_macs.append(mac)
    # Generate alerts directly without intermediate files
    generate_target_alerts(bt_macs, client_macs, ap_macs, sensor_macs, ssid_list)

def check_privileges():
    """Check and escalate privileges if needed"""
    if os.geteuid() != 0:
        print("\033[31mPermission Error: Restarting with sudo...\033[0m")
        subprocess.call(['sudo', sys.executable] + sys.argv)
        sys.exit()

def main():
    if len(sys.argv) != 2:
        print("Usage: python KismetParse.py <kismet_database>")
        sys.exit(1)
    
    check_privileges()
    database = sys.argv[1]
    
    conn = create_connection(database)
    if conn is not None:
        devices_list = extract_devices_json(conn)
        conn.close()
        
        if devices_list:
            sort_and_configure_devices(devices_list)
        else:
            print("No devices found")
    else:
        print("Database connection failed")

if __name__ == '__main__':
    main()
