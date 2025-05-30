# ms2130-serial-number-configurator
ms2130-serial-number-configurator

# Introduction
This Tool attempts to change the Serial Number of MS2130 Devices and Configures a Random Serial Number for each Device.

# Requirements
This Tool relies on downloading and installing [ms-tools](https://github.com/BertoldVdb/ms-tools).

Easy install (requires `go` to be installed on your System):
1. `git clone https://github.com/BertoldVdb/ms-tools.git`
2. `cd ms-tools/cli`
3. `go build`

# Using the Script
The `ms-tools` requires Super-User (`root` or `sudo`) Privileges in order to access the Device Memory.

First of all, it's reccomended to Dump the Stock Firmware FLASH once Manually and store it in a Safe Place:
```
./cli --log-level=7 read FLASH 0 --filename=firmware.stock.flash.bin
```

And the EEPROM as well, although it's apparently not being used on the MS2130:
```
./cli --log-level=7 read EEPROM 0 --filename=firmware.stock.eeprom.bin
```

# Usage Examples
Configure custom Serial and reduce Logging to a Minimum:
```
sudo ./configure.py --executable ./ms-tools/cli/cli --serial 0123456789 --log-level=2
```

Configure using random Serial and reduce Logging to a Minimum:
```
sudo ./configure.py --executable ./ms-tools/cli/cli --log-level=2
```

Configure using random Serial, reduce Logging ms2130.modified.flash.2025-05-30-07-08-35.bin

Faster Method - skip Backup before AND After Serial Number Customization (NOT reccomended):
```
sudo ./configure.py --executable=./ms-tools/cli/cli --serial=0123456789 --log-level=2 --no-backup --file=firmware.stock.flash.bin
```

# Verify Serial Number Change

# Testing Capture
720p:
```
ffplay -fflags nobuffer -input_format mjpeg -video_size 1280x720 -framerate 60 -color_range pc /dev/video3
```

1080p:
```
ffplay -fflags nobuffer -input_format mjpeg -video_size 1920x1024 -framerate 60 -color_range pc /dev/video3
```


# References
- https://github.com/BertoldVdb/ms-tools
- https://github.com/ultrasemier/ms213x_community
- https://github.com/steve-m/ms2130_patcher
