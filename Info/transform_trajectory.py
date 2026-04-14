#!/usr/bin/env python3
import yaml

input_file = "trajectory_stb.txt"
output_file = "trajectory_stb_new.txt"

with open(input_file, 'r') as f, open(output_file, 'w') as out:
    data = yaml.safe_load_all(f)

    for entry in data:
        if entry is None:
            continue

        sec = entry['header']['stamp']['sec']
        nsec = entry['header']['stamp']['nanosec']
        t = sec + nsec * 1e-9

        pos = entry['pose']['pose']['position']
        ori = entry['pose']['pose']['orientation']

        line = f"{t} {pos['x']} {pos['y']} 0.0 {ori['x']} {ori['y']} {ori['z']} {ori['w']}\n"
        out.write(line)
