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

Configure custom Serial and reduce Logging to a Minimum:
```
sudo ./configure.py --executable ./ms-tools/cli/cli --serial 0123456789 --log-level=2
```

Configure using random Serial and reduce Logging to a Minimum:
```
sudo ./configure.py --executable ./ms-tools/cli/cli --log-level=2
```

Configure using random Serial and reduce Logging to a Minimum and skip Backup:
```
sudo ./configure.py --executable=./ms-tools/cli/cli --serial=0123456789 --log-level=2 --no-backup
```



# References
- https://github.com/BertoldVdb/ms-tools
- https://github.com/ultrasemier/ms213x_community
- https://github.com/steve-m/ms2130_patcher
