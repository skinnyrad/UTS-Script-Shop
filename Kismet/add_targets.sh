#!/bin/sh

# Check privileges for system config directory
    if [ "$(id -u)" -ne 0 ]; then
        echo "\033[31mPermission Error: Must be run with sudo when configuring Kismet Alerts\033[0m"
        exit 1
    fi

# Potential config directories in priority order
CONFIG_DIRS="/etc/kismet /usr/local/etc"
MAC_SOURCES="AP.txt BTEDR.txt BTLE.txt CLIENT.txt SENSORS.txt"
SSID_SOURCES="ProbedSSID.txt"

processed_dirs=0

for CONFIG_DIR in $CONFIG_DIRS; do
    # Verify config directory and alerts file exist
    if [ -d "$CONFIG_DIR" ] && [ -f "${CONFIG_DIR}/kismet_alerts.conf" ]; then
        ALERTS_CONF="${CONFIG_DIR}/kismet_alerts.conf"
        TARGET_CONF="${CONFIG_DIR}/kismet_target_alerts.conf"
        INCLUDE_LINE="opt_include=${TARGET_CONF}"

        # Add include directive if missing
        if ! grep -qxF "$INCLUDE_LINE" "$ALERTS_CONF"; then
            echo "$INCLUDE_LINE" >> "$ALERTS_CONF"
        fi

        # Create fresh target file
        true > "$TARGET_CONF"

        # Process SSIDs from all sources
        for SSID_FILE in $SSID_SOURCES; do
            if [ -f "$SSID_FILE" ]; then
                while IFS= read -r ssid || [ -n "$ssid" ]; do
                    cleaned_ssid=$(echo "$ssid" | xargs)
                    [ -z "$cleaned_ssid" ] && continue
                    echo "ssidcanary=\"${cleaned_ssid}\":ssid=\"${cleaned_ssid}\"" >> "$TARGET_CONF"
                done < "$SSID_FILE"
            else
                echo "\033[33mWarning: $SSID_FILE not found - skipping SSID alerts\033[0m"
            fi
        done

        # Process MAC addresses from all sources
        for source in $MAC_SOURCES; do
            if [ -f "$source" ]; then
                while IFS= read -r mac || [ -n "$mac" ]; do
                    cleaned_mac=$(echo "$mac" | xargs | tr -d '-')
                    [ -z "$cleaned_mac" ] && continue
                    echo "devicefound=${cleaned_mac}" >> "$TARGET_CONF"
                done < "$source"
            else
                echo "\033[33mWarning: $source not found - skipping\033[0m"
            fi
        done

        echo "\033[32mConfiguration updated in ${CONFIG_DIR}\033[0m"
        processed_dirs=$((processed_dirs+1))
    fi
done

if [ "$processed_dirs" -eq 0 ]; then
    echo "\033[31mError: No valid Kismet configuration directories found\033[0m"
    exit 1
fi
