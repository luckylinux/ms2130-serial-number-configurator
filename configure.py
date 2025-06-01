#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import Libraries
import argparse
import pprint
import re
from secrets import choice
import string
from pathlib import Path
import subprocess
import sys
from datetime import datetime
from copy import copy


# Generate a random Serial Number
def generate_random_serial(length: int = 8):
    return ''.join([choice(string.ascii_uppercase + string.digits) for _ in range(0, length)])


# Flatten List
# https://discuss.python.org/t/why-cant-iterable-unpacking-be-used-in-comprehension/15622/7
# def flatten(a):
#     return [c for b in a for c in flatten(b)] if hasattr(a, '__iter__') else [a]
def flatten(lists):
    flat = []
    for item in lists:
        if type(item) is type([]):
            flat += flatten(item)
        else:
            flat += [item]
    return flat


# Number of Bytes per Character
# UNICODE = 16 bits / 2 Bytes per ASCII Character
character_num_bytes = 2

# Store Serial Length
store_serial_length: bool = False

# Fixed Length Serial Number
serial_fixed_length = 16

# Main
if __name__ == "__main__":
    # Declare Arguments Parser
    parser = argparse.ArgumentParser(description='Configure new MS2310 Device.')

    parser.add_argument('-s', '--serial', dest="serial", default=None,
                        help='Use a custom Serial Number (if NOT set, a random Serial Number will be generated)')

    parser.add_argument('-n', '--serial-length', dest="serial_length", required=False, type=int, default=8,
                        help='Serial Number Length')

    parser.add_argument('-f', '--file', '--data-file', '--file-data', dest="data_file", required=False, default=None,
                        help='Data File to compute Checksum from')

    parser.add_argument('-e', '--executable', dest="executable", required=True,
                        help='Path to ms-tools <cli> Executable')

    parser.add_argument('-b', '--base-path', dest="base_path", required=False, default=Path().cwd().joinpath("devices"),
                        help='Basepath where to save Stuff (<basepath>/<serial> will contain each Device Configuration & Firmware)')

    parser.add_argument('-l', '--log-level', dest="log_level", required=False, default="7",
                        help='Log Level (0 ... 7)')

    parser.add_argument('--backup', dest="backup", required=False, default=True,
                        help='Backup current Flash/EEPROM as well as the Flash/EEPROM after Modification', action=argparse.BooleanOptionalAction)

    parser.add_argument('--dry-run', dest="dry_run", required=False, default=False,
                        help='Perform a Dry Run (do NOT flash / patch)', action="store_true")

    parser.add_argument('--verify', dest="verify", required=False, default=True,
                        help='Verify that the Serial Number is correct after Flashing (requires Power Cycle)', action="store_true")

    # Generate Timestamp for Backups
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d-%H-%M-%S")

    # Parse Arguments
    parsed = parser.parse_args()

    if parsed.serial is None:
        # Serial Length
        serial_length = parsed.serial_length

        # Generate Random Serial Number
        serial_number = generate_random_serial(length=serial_length)
    else:
        # Get Serial Number
        serial_number = parsed.serial

        # Get Length of Serial Number
        # This Corresponds to the first Byte (uint8) at the Offset Position to be changed
        serial_length = len(serial_number)

    # Data File
    data_file = parsed.data_file

    # LOG Level
    log_level = parsed.log_level

    # Dry Run
    dry_run = parsed.dry_run

    # Verify
    verify = parsed.verify

    # CLI Executable
    executable = parsed.executable

    # Backup
    backup = parsed.backup

    # Base Path where to save old and new Firmware / Configuration
    base_path = Path(parsed.base_path)

    # Full Path
    device_path = base_path.joinpath(serial_number)

    # Sanity Check
    if serial_length < 2:
       print("ERROR: Serial Number must have at least 2 Characters")
       sys.exit(1)
    elif serial_length > serial_fixed_length:
       print(f"ERROR: Serial Number must have at most {serial_fixed_length} Characters")
       sys.exit(2)

    # Save Variable without padding
    serial_number_nonpadded = serial_number

    # Add Padding to the End of the Serial Number
    # padding_character = chr(255)
    padding_character = chr(000)
    serial_number = serial_number + "".join([padding_character for x in range(serial_length, serial_fixed_length)])

    # Define Start Addresses for the Serial in Hex
    # Does NOT seem to work
    address_SerialnumString_hex = "0x00189F"
    address_U2SerialnumString_hex = "0x0018E3"
    # address_SerialnumString_hex = "0x00FB50"
    # address_U2SerialnumString_hex = "0x00FB70"
    # address_SerialnumString_hex = "0x00FB20"
    # address_U2SerialnumString_hex = "0x00FB40"

    # Convert Addresses to Decimal
    address_SerialnumString_dec = int(address_SerialnumString_hex, 0)
    address_U2SerialnumString_dec = int(address_U2SerialnumString_hex, 0)

    # Debug
    # print(f"Serial Number: {serial_number} (Length: {len(serial_number)})")

    # Generate Serial String in Decimal Format (inverse ASCII Table using "ord")
    if store_serial_length is True:
        serial_inverse_ascii_dec_array = ["%02d" % serial_length]
        start_index = 2
    else:
        serial_inverse_ascii_dec_array = []
        start_index = 0

    if character_num_bytes == 2:
        serial_inverse_ascii_dec_array.extend(flatten([['%03d' % ord(x) , "000"]  for x in serial_number]))
    else:
        serial_inverse_ascii_dec_array.extend(['%03d' % ord(x) for x in serial_number])

    serial_inverse_ascii_dec = ''.join(serial_inverse_ascii_dec_array)

    serial_inverse_ascii_dec_readable = ""
    if store_serial_length is True:
        serial_inverse_ascii_dec_readable = serial_inverse_ascii_dec[0:start_index] + '-'

    serial_inverse_ascii_dec_readable = serial_inverse_ascii_dec_readable + '-'.join(re.findall('...?', serial_inverse_ascii_dec[start_index:None]))

    # Debug
    # print(serial_inverse_ascii_dec_readable)

    # Generate Serial String in Binary Format (inverse ASCII Table using "ord")
    if store_serial_length is True:
        serial_inverse_ascii_bin_array = ["%08d" % int(bin(serial_length).removeprefix("0b"))]
        start_index = 8
    else:
        serial_inverse_ascii_bin_array = []
        start_index = 0

    if character_num_bytes == 2:
        serial_inverse_ascii_bin_array.extend(flatten([[('%08d' % int(bin(ord(x)).removeprefix("0b"))) , "00000000"] for x in serial_number]))
    else:
        serial_inverse_ascii_bin_array.extend(['%08d' % int(bin(ord(x)).removeprefix("0b")) for x in serial_number])

    serial_inverse_ascii_bin = ''.join(serial_inverse_ascii_bin_array)

    serial_inverse_ascii_bin_readable = ""
    if store_serial_length is True:
        serial_inverse_ascii_bin_readable = serial_inverse_ascii_bin[0:start_index] + '-'

    serial_inverse_ascii_bin_readable = serial_inverse_ascii_bin_readable + '-'.join(re.findall('........?', serial_inverse_ascii_bin[start_index:None]))


    # Generate Serial String in Hex Format (inverse ASCII Table using "ord")
    if store_serial_length is True:
        serial_inverse_ascii_hex_array = [str(hex(serial_length).removeprefix("0x"))]
        start_index = 1
    else:
        serial_inverse_ascii_hex_array = []
        start_index = 0

    if character_num_bytes == 2:
        serial_inverse_ascii_hex_array.extend(flatten([[str(hex(ord(x)).removeprefix("0x")) , "00"] for x in serial_number]))
    else:
        serial_inverse_ascii_hex_array.extend([str(hex(ord(x)).removeprefix("0x")) for x in serial_number])

    serial_inverse_ascii_hex = ''.join(serial_inverse_ascii_hex_array)

    serial_inverse_ascii_hex_readable = ""
    if store_serial_length is True:
        serial_inverse_ascii_hex_readable = serial_inverse_ascii_hex[0] + '-'

    serial_inverse_ascii_hex_readable = serial_inverse_ascii_hex_readable + '-'.join(re.findall('..?', serial_inverse_ascii_hex[start_index:None]))

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

    # Read a few Bytes from the Device
    # This seems to make the entire Procedure much more Reliable.
    # Previously (without this) there would be a lot of Timeout generated and the USB would drop out after a while.
    subprocess.run([executable, f"--log-level=0", "--no-patch", "read", "FLASH", "0", "1024"], shell=False, check=True, capture_output=True)

    if backup:
        if dry_run is False:
            # Echo
            print("Backup current Firmware from FLASH and EEPROM")

            # Backup current Firmware
            ##### cmd_read = [executable, "--log-level=7", "read", "FLASH", "0", f"--filename={device_path}/ms2130.original.flash.bin"]
            ##### print(f"Executing BACKUP: {cmd_read}")
            subprocess.run([executable, f"--log-level={log_level}", "--no-patch", "read", "FLASH", "0", f"--filename={device_path}/ms2130.original.flash.{timestamp}.bin"], shell=False, check=True)

            # Backup current EEPROM
            subprocess.run([executable, f"--log-level={log_level}", "--no-patch", "read", "EEPROM", "0", f"--filename={device_path}/ms2130.original.eeprom.{timestamp}.bin"], shell=False, check=True)
        else:
            # Echo
            print("Dry Run: Backup Firmware")

    # Perform Modification (one go)
    # ### subprocess.run([executable, "--log-level=7", "write", "FLASH", address_SerialnumString_hex, ], shell=True, check=True)
    # ### subprocess.run([executable, "--log-level=7", "write", "FLASH", address_U2SerialnumString_hex, ], shell=True, check=True)

    # Perform Modification (Byte by Byte)
    # ###for index, value in enumerate(serial_inverse_ascii_dec_array):
    # ####    subprocess.run([executable, f"--log-level={log_level}", "write", "FLASH", hex(address_SerialnumString_dec + index), str(value)], shell=False, check=True)
    # ####    subprocess.run([executable, f"--log-level={log_level}", "write", "FLASH", hex(address_U2SerialnumString_dec + index), str(value)], shell=False, check=True)

    if dry_run is False:
        # Echo
        print("Write new Serial Number to FLASH / EEPROM")
    else:
        # Echo
        print("Dry Run: Perform Operations")

    if dry_run is False:
        for index, value in enumerate(serial_inverse_ascii_hex_array):
            # Echo
            print(f"Write {str(value)} at Address {hex(address_SerialnumString_dec + index)}")

            # Perform Operation
            subprocess.run([executable, f"--log-level={log_level}", "--no-patch", "write", "FLASH", hex(address_SerialnumString_dec + index), "0x" + str(value)], shell=False, check=True)

            # Echo
            print(f"Write {str(value)} at Address {hex(address_U2SerialnumString_dec + index)}")

            # Perform Operation
            subprocess.run([executable, f"--log-level={log_level}", "--no-patch", "write", "FLASH", hex(address_U2SerialnumString_dec + index), "0x" + str(value)], shell=False, check=True)

    # Echo
    print("Backup updated Firmware from FLASH and EEPROM - Need to do so in order to compute Checksum-16")


    if dry_run is False and data_file is None:
        # Backup Firmware after Modification
        subprocess.run([executable, f"--log-level={log_level}", "--no-patch", "read", "FLASH", "0", f"--filename={device_path}/ms2130.modified.flash.{timestamp}.bin"], shell=False, check=True)

        # Backup EEPROM after Modification
        subprocess.run([executable, f"--log-level={log_level}", "--no-patch", "read", "EEPROM", "0", f"--filename={device_path}/ms2130.modified.eeprom.{timestamp}.bin"], shell=False, check=True)

    # Compute Checksum-16
    checksum_data_start_address_hex = "0x0030"
    checksum_data_end_address_hex = "0xFBCF"
    # checksum_data_end_address_hex = "0xFBDF"

    checksum_data_start_address_dec = int(checksum_data_start_address_hex, 0)
    checksum_data_end_address_dec = int(checksum_data_end_address_hex, 0)

    checksum_value_start_address_hex = "0xFBD2"
    checksum_value_end_address_hex = "0xFBD3"

    checksum_value_start_address_dec = int(checksum_value_start_address_hex, 0)
    checksum_value_end_address_dec = int(checksum_value_end_address_hex, 0)

    # byte = int(sys.argv[3], 0)

    if data_file is None:
        data_file = f"{device_path}/ms2130.modified.flash.{timestamp}.bin"
    else:
        # Try Relative Path first
        data_file = Path(data_file)

        if data_file.exists() is False:
            # Fall Back to use Filename inside Device Folder
            data_file = f"{device_path}/{data_file.as_posix()}"

    # Echo
    print(f"Using Data File {data_file}")

    # file_contents = None
    with open(data_file, "r+b") as fh:
        # Read File Contents in Binary Format
        file_contents_bytes = fh.read()

        # Split into Array
        file_contents_split = [file_contents_bytes[i] for i in range (0, len(file_contents_bytes))]

        # Copy Variable
        file_contents_split_original = copy(file_contents_split)

        # Overwrite specific Positions for Serial Number
        # This Way the File does NOT need to be generated AFTER Serial Number Configuration and the Stock Firmware Dump can be used instead
        for index, value in enumerate(serial_inverse_ascii_dec_array):
            # Echo
            print(f"Overwrite at Address {hex(address_SerialnumString_dec + index)} in Array with Value {value}")

            # Perform Operation
            file_contents_split[address_SerialnumString_dec + index] = int(value)

            # Echo
            print(f"Overwrite at Address {hex(address_U2SerialnumString_dec + index)} in Array with Value {value}")

            # Perform Operation
            file_contents_split[address_U2SerialnumString_dec + index] = int(value)

        # Debug
        # pprint.pprint(file_contents_split)

        # Get Checksum Data Range
        checksum_data_range = file_contents_split[checksum_data_start_address_dec:checksum_data_end_address_dec+1]

        # Calculate Sum
        checksum_data_sum = sum(checksum_data_range)

        # Calculate Modulo 65535
        checksum_data_result_dec = checksum_data_sum % 65536

        # Calculate in HEX
        checksum_data_result_hex = hex(checksum_data_result_dec).removeprefix("0x")

        # Debug
        print(f"Using File {data_file} for Checksum Analysis")
        print(f"Checksum Data Start Address: {checksum_data_start_address_hex}")
        print(f"Checksum Data End Address: {checksum_data_end_address_hex}")
        print(f"Checksum Data Number of Elements: {len(checksum_data_range)}")
        print(f"Checksum Data Initial Values: {[hex(checksum_data_range[i]) for i in range(0, 16)]}")
        print(f"Checksum Data Final Values: {[hex(checksum_data_range[i]) for i in range(len(checksum_data_range) - 1 - 16, len(checksum_data_range) - 1, 1)]}")
        print(f"Row after last Checksum Data: {[hex(file_contents_split[i]) for i in range(checksum_data_end_address_dec + 1, checksum_data_end_address_dec + 16, 1)]}")
        print(f"Checksum Data Sum: {checksum_data_sum}")
        print(f"Checksum Data Result Decimal: {checksum_data_result_dec}")
        print(f"Checksum Data Result Hex: 0x{checksum_data_result_hex}")

        if dry_run is False:
            # Write new Checksum
            subprocess.run([executable, f"--log-level={log_level}", "--no-patch", "write", "FLASH", hex(checksum_value_start_address_dec), "0x" + str(checksum_data_result_hex[0:2])], shell=False, check=True)
            subprocess.run([executable, f"--log-level={log_level}", "--no-patch", "write", "FLASH", hex(checksum_value_end_address_dec), "0x" + str(checksum_data_result_hex[2:4])], shell=False, check=True)

        # ### Convert that to String
        # ### file_contents_str = file_contents_bytes.decode("utf-16")

        # ### Convert to Numeric Values
        # ### file_contents_int = [int.from_bytes(file_contents_split[i], byteorder="big", signed=True) for i in range (0, len(file_contents_bytes))]

        # ### pprint.pprint(file_contents_int)

    if dry_run is False:
        # Echo
        print("Read Serial Number Value at Address after Operations")

        # Read Final Value
        subprocess.run([executable, f"--log-level={log_level}", "--no-patch", "read", "FLASH", hex(address_SerialnumString_dec), "32"], shell=False, check=True)
        subprocess.run([executable, f"--log-level={log_level}", "--no-patch", "read", "FLASH", hex(address_U2SerialnumString_dec), "32"], shell=False, check=True)

        # Echo
        print("Read Serial Number Checksum Value at Address after Operations")
        subprocess.run([executable, f"--log-level={log_level}", "--no-patch", "read", "FLASH", hex(checksum_value_start_address_dec), "1"], shell=False, check=True)
        subprocess.run([executable, f"--log-level={log_level}", "--no-patch", "read", "FLASH", hex(checksum_value_end_address_dec), "1"], shell=False, check=True)
    else:
        # Echo
        print("Dry Run: read Serial Number Value at Address after Operations")


    if verify:
        # Reset Device
        x = input("Disconnect & Reconnect MS2130 Device (Power Cycle) and press [ENTER]: ")

        # Get Serial Number via lsusb
        result = subprocess.run(["/usr/bin/lsusb", "-vvv", "-d", "345f:2130"], shell=False, check=False, capture_output=True)

        output = result.stdout.decode()

        for line in output.splitlines():
            # Debug
            # print(f"Processing Line: {line}")

            if "iSerial" in line:
                items = line.split()
                serial = items[-1]

                # Echo
                print(f"Serial Number on Device: {serial}")

                # Check against what was supposed to be there
                if serial == serial_number_nonpadded:
                    print(f"Serial Number matches UNPADDED Serial Number")
                elif serial == serial_number:
                    print(f"Serial Number matches PADDED Serial Number")
                else:
                    print(f"ERROR: Serial Number on Device ({serial}) does NOT match UNPADDED ({serial_number_nonpadded}) nor PADDED ({serial_number}) Serial Numbers !!!")

