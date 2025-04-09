import sqlite3
from sqlite3 import Error
import json
import sys

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
    
def sort_devices_to_files(devices_list):
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

    # Write files with unique entries
    with open("BT.txt", "w") as f:
        f.write("\n".join(set(bt_macs)))
    
    with open("CLIENT.txt", "w") as f:
        f.write("\n".join(set(client_macs)))
    
    with open("SSID.txt", "w") as f:
        f.write("\n".join(set(ssid_list)))

    with open("AP.txt", "w") as f:
        f.write("\n".join(set(ap_macs))) 
    
    with open("SENSORS.txt", "w") as f:
        f.write("\n".join(set(sensor_macs)))

    print("Files created with extracted SSIDs and MAC addresses")

def main():
    if len(sys.argv) != 2:
        print("Usage: python KismetParse.py <path_to_kismet_file>")
        sys.exit(1)
    
    database = sys.argv[1]  # Get the Kismet database file from command line argument
    
    # Create a database connection
    conn = create_connection(database)
    
    if conn is not None:
        devices_list = extract_devices_json(conn)
        conn.close()

        # Print the first device JSON as an example
        if devices_list:
            sort_devices_to_files(devices_list)
        else:
            print("No devices found or error occurred.")
    else:
        print("Error! Cannot create the database connection.")

if __name__ == '__main__':
    main()
