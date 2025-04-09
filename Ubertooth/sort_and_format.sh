#!/bin/bash

if [ $# -eq 0 ]; then
    echo "Usage: $0 <filename>"
    exit 1
fi

input="$1"
uap="${input}_UAP"
lap="${input}_LAP"

> "$uap"  # Clear output files
> "$lap"

while IFS= read -r line; do
    if [[ $line =~ ^([0-9A-Fa-f]{2}|\?\?)(:([0-9A-Fa-f]{2}|\?\?)){5}$ ]]; then
        IFS=':' read -ra parts <<< "$line"
        count=0
        visible_parts=()
        for part in "${parts[@]}"; do
            if [[ "$part" != "??" ]]; then
                ((count++))
                visible_parts+=("$part")
            fi
        done
        
        if [ $count -eq 4 ]; then
            # Replace first two octets with 00:00
            modified="00:00:${parts[2]}:${parts[3]}:${parts[4]}:${parts[5]}"
            echo "$modified" >> "$uap"
        elif [ $count -eq 3 ]; then
            # Only write the lower three octets
            echo "${visible_parts[0]}:${visible_parts[1]}:${visible_parts[2]}" >> "$lap"
        fi
    fi
done < "$input"

