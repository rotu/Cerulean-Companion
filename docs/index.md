# Cerulean Companion

<a href="https://bluerobotics.com">
<img src="https://avatars2.githubusercontent.com/u/57329052?v=3&s=200" align="left" hspace="10" vspace="6">
</a>


Companion app to enable Cerulean Sonar devices to share their data with other hosts and services, such as QGroundControl or a BlueROV2.


<br/>
<br/>


## Installing:

With python3.6 or later, the following command will install all dependencies locally:
```
pip3 install --user --force-reinstall git+https://github.com/CeruleanSonar/Cerulean-Companion.git
```
Note the `--force-reinstall` flag. This is required if you already have `pynmea2` installed to get our custom modified branch.

You should then be able to run the command:
```
$ usbl_relay
usage: usbl_relay [-h] [-u /dev/ttyUSB#] [-g /dev/ttyXXX#] [-e localhost:port]
                  [-m host:port] [--log level]
usbl_relay: error: GPS and USBL devices must be specified

Serial devices detected:
  /dev/cu.Bluetooth-Incoming-Port - n/a
  /dev/cu.DansCans-SPPDev - n/a
```

## Building for distribution:

To package it up for consumption on another machine:
```
git clone https://github.com/CeruleanSonar/Cerulean-Companion.git
cd Cerulean-Companion
pip3 install pyinstaller git+https://github.com/CeruleanSonar/Cerulean-Companion.git -t build
env PYTHONPATH="build" python3 -m PyInstaller usbl_relay.spec
```
You will find the executable file in the `dist` subfolder.
