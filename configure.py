#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import Libraries
import argparse
import re
from secrets import choice
import string
from pathlib import Path
import subprocess
import sys

# Generate a random Serial Number
def generate_random_serial(length: int = 31):
    return ''.join([choice(string.ascii_uppercase + string.digits) for _ in range(length)])

# Main
if __name__ == "__main__":
    # Declare Arguments Parser
    parser = argparse.ArgumentParser(description='Configure new MS2310 Device.')

    parser.add_argument('-s', '--serial', default=None,
                        help='Use a custom Serial Number (if NOT set, a random Serial Number will be generated)')

    parser.add_argument('-e', '--executable', required=True,
                        help='Path to ms-tools <cli> Executable')

    parser.add_argument('-b', '--base_path', required=False, default=Path().cwd().joinpath("devices"),
                        help='Basepath where to save Stuff (<basepath>/<serial> will contain each Device Configuration & Firmware)')

    parser.add_argument('-l', '--log_level', required=False, default="7",
                        help='Log Level (0 ... 7)')


    # Parse Arguments
    parsed = parser.parse_args()

    if parsed.serial is None:
        # Generate Random Serial Number
        serial_number = generate_random_serial()
    else:
        serial_number = parsed.serial

    # LOG Level
    log_level = parsed.log_level

    # CLI Executable
    executable = parsed.executable

    # Base Path where to save old and new Firmware / Configuration
    base_path = Path(parsed.base_path)

    # Full Path
    device_path = base_path.joinpath(serial_number)

    # Get Length of Serial Number
    # This Corresponds to the first Byte (uint8) at the Offset Position to be changed
    serial_length = len(serial_number)

    # Sanity Check
    if serial_length < 2:
       print("ERROR: Serial Number must have at least 2 Characters")
       sys.exit(1)
    elif serial_length > 31:
       print("ERROR: Serial Number must have at most 31 Characters")
       sys.exit(2)

    # Add Padding to the End of the Serial Number
    padding_character = chr(255)
    serial_number = serial_number + "".join([padding_character for x in range(serial_length, 31)])

    # Define Start Addresses for the Serial in Hex
    # Does NOT seem to work
    address_SerialnumString_hex = "0x00FB50"
    address_U2SerialnumString_hex = "0x00FB70"
    # address_SerialnumString_hex = "0x00FB20"
    # address_U2SerialnumString_hex = "0x00FB40"

    # Convert Addresses to Decimal
    address_SerialnumString_dec = int(address_SerialnumString_hex, 0)
    address_U2SerialnumString_dec = int(address_U2SerialnumString_hex, 0)

    # Generate Serial String in Decimal Format (inverse ASCII Table using "ord")
    serial_inverse_ascii_dec_array = ["%02d" % serial_length]
    serial_inverse_ascii_dec_array.extend(['%03d' % ord(x) for x in serial_number])
    serial_inverse_ascii_dec = "%02d" % serial_length + ''.join(['%03d' % ord(x) for x in serial_number])

    # Generate Serial String in Binary Format (inverse ASCII Table using "ord")
    serial_inverse_ascii_bin_array = ["%08d" % int(bin(serial_length).lstrip("0b"))]
    serial_inverse_ascii_bin_array.extend([('%08d' % int(bin(ord(x)).lstrip("0b"))) for x in serial_number])
    serial_inverse_ascii_bin = "%08d" % int(bin(serial_length).lstrip("0b"))  + ''.join([('%08d' % int(bin(ord(x)).lstrip("0b"))) for x in serial_number])

    # Generate Serial String in Hex Format (inverse ASCII Table using "ord")
    serial_inverse_ascii_hex_array = [str(hex(serial_length).lstrip("0x"))]
    serial_inverse_ascii_hex_array.extend([str(hex(ord(x)).lstrip("0x")) for x in serial_number])
    serial_inverse_ascii_hex = str(hex(serial_length).lstrip("0x")) + ''.join([str(hex(ord(x)).lstrip("0x")) for x in serial_number])

    # Convert in better Readable Representation
    serial_inverse_ascii_dec_readable = serial_inverse_ascii_dec[0:2] + '-' + '-'.join(re.findall('...?', serial_inverse_ascii_dec[2:None]))
    serial_inverse_ascii_bin_readable = serial_inverse_ascii_bin[0:8] + '-' + '-'.join(re.findall('........?', serial_inverse_ascii_bin[8:None]))
    serial_inverse_ascii_hex_readable = serial_inverse_ascii_hex[0] + '-' + '-'.join(re.findall('..?', serial_inverse_ascii_hex[1:None]))

    # Convert list of Bytes to Decimal
    # serial_number_value = 0
    # for bit in serial_inverse_ascii_bin:
    #     serial_number_value = (serial_number_value << 1) | int(bit)

    # Print
    print(f"Serial Number: {serial_number}")
    print(f"\tSerial Number Length: {serial_length}")
    print(f"MS Tools Executable: {executable}")
    print(f"Base Path where to save original Firmware prior to Flashing (and modified Firmware after Flashing): {base_path}")
    print(f"Full Path where to save original Firmware prior to Flashing (and modified Firmware after Flashing): {device_path}")
    print("================================================================================================================================")
    print(f"Serial Length + Serial Number Decimal Representation: {serial_inverse_ascii_dec_array}")
    print(f"Serial Length + Serial Number Decimal Representation: {serial_inverse_ascii_dec}")
    print(f"Serial Length + Serial Number Decimal Representation: {serial_inverse_ascii_dec_readable}")
    print("================================================================================================================================")
    print(f"Serial Length + Serial Number Hex Representation: {serial_inverse_ascii_hex_array}")
    print(f"Serial Length + Serial Number Hex Representation: {serial_inverse_ascii_hex}")
    print(f"Serial Length + Serial Number Hex Representation: {serial_inverse_ascii_hex_readable}")
    print("================================================================================================================================")
    print(f"Serial Length + Serial Number Bin Representation: {serial_inverse_ascii_bin_array}")
    print(f"Serial Length + Serial Number Bin Representation: {serial_inverse_ascii_bin}")
    print(f"Serial Length + Serial Number Bin Representation: {serial_inverse_ascii_bin_readable}")
    print("================================================================================================================================")
    # print(f"Serial Number overall Value: {serial_number_value}")

    # Abort for Debugging
    # sys.exit(5)

    # Create Folder Structure
    device_path.mkdir(exist_ok=True, parents=True)

    # Backup current Firmware
    ##### cmd_read = [executable, "--log-level=7", "read", "FLASH", "0", f"--filename={device_path}/ms2130.original.flash.bin"]
    ##### print(f"Executing BACKUP: {cmd_read}")
    #subprocess.run([executable, f"--log-level={log_level}", "read", "FLASH", "0", f"--filename={device_path}/ms2130.original.flash.bin"], shell=False, check=True)

    # Backup current EEPROM
    #subprocess.run([executable, f"--log-level={log_level}", "read", "EEPROM", "0", f"--filename={device_path}/ms2130.original.eeprom.bin"], shell=False, check=True)

    # Perform Modification (one go)
    #### subprocess.run([executable, "--log-level=7", "write", "FLASH", address_SerialnumString_hex, ], shell=True, check=True)
    #### subprocess.run([executable, "--log-level=7", "write", "FLASH", address_U2SerialnumString_hex, ], shell=True, check=True)

    # Perform Modification (Byte by Byte)
    ####for index, value in enumerate(serial_inverse_ascii_dec_array):
    #####    subprocess.run([executable, f"--log-level={log_level}", "write", "FLASH", hex(address_SerialnumString_dec + index), str(value)], shell=False, check=True)
    #####    subprocess.run([executable, f"--log-level={log_level}", "write", "FLASH", hex(address_U2SerialnumString_dec + index), str(value)], shell=False, check=True)

    for index, value in enumerate(serial_inverse_ascii_hex_array):
        subprocess.run([executable, f"--log-level={log_level}", "write", "FLASH", hex(address_SerialnumString_dec + index), "0x" + str(value)], shell=False, check=True)
        subprocess.run([executable, f"--log-level={log_level}", "write", "FLASH", hex(address_U2SerialnumString_dec + index), "0x" + str(value)], shell=False, check=True)


    # Backup Firmware after Modification
    #subprocess.run([executable, f"--log-level={log_level}", "read", "FLASH", "0", f"--filename={device_path}/ms2130.modified.flash.bin"], shell=False, check=True)

    # Backup EEPROM after Modification
    #subprocess.run([executable, f"--log-level={log_level}", "read", "EEPROM", "0", f"--filename={device_path}/ms2130.modified.eeprom.bin"], shell=False, check=True)

    # Read Final Value
    subprocess.run([executable, f"--log-level={log_level}", "read", "FLASH", hex(address_SerialnumString_dec), "32"], shell=False, check=True)
    subprocess.run([executable, f"--log-level={log_level}", "read", "FLASH", hex(address_U2SerialnumString_dec), "32"], shell=False, check=True)
