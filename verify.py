#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import pprint
import os
import sys

# Get Serial Number via lsusb
result = subprocess.run(["/usr/bin/lsusb", "-vvv", "-d", "345f:2130"], shell=False, check=False, capture_output=True)

output = result.stdout.decode()

for line in output.splitlines():
    # print(f"Processing Line: {line}")
    if "iSerial" in line:
        items = line.split()
        serial = items[-1]
        print(f"Serial: {serial}")
