# Cerulean Companion

<a href="https://ceruleansonar.com/">
<img src="https://avatars2.githubusercontent.com/u/57329052?v=3&s=200" align="left" hspace="10" vspace="6">
</a>


Companion app to enable Cerulean Sonar devices to share their data with other hosts and services, such as QGroundControl or a BlueROV2.


<br/>
<br/>
<br/>
<br/>
<br/>
<br/>


## Installing a Release

Head over to [Releases](https://github.com/CeruleanSonar/Cerulean-Companion/releases) and download the appropriate version for your OS.

For now, the app is CLI only. Use terminal on Linux/Mac and CMD on Windows to execute the program. Follow the help prompt to set the flags appropriately for your configuration.

For Linux, you'll need to enable execution of the file with your file manager, or by running `chmod +x cerulean-companion` . In Windows 10, you may need to approve a SmartScreen dialog.

```
$ ./cerulean-companion
usage: cerulean-companion [-h] [-u /dev/ttyUSB#] [-g /dev/ttyXXX#] [-e localhost:port]
                  [-m host:port] [--log level]

```

## Getting ROVL and GPS data into QGroundControl on a BlueROV2

### Requirements

* ROVL Receiver and Transmitter
* USB GPS [Such as this](https://smile.amazon.com/HiLetgo-G-Mouse-GLONASS-Receiver-Windows/dp/B01MTU9KTF/ref=sr_1_4?keywords=usb+gps&qid=1572829299&sr=8-4)
* QGroundControl >= 3.5.2
* BlueROV2 with a recent version of Companion [How to Update](https://discuss.bluerobotics.com/t/software-updates/1128)

### Start and Configure QGroundControl

Because of the way QGroundControl handles USB devices, we'll have to disable its auto-connect functionality for everything except UDP. If we don't do this, the Cerulean Companion (or anything else) will be unable to interact with serial ports while QGroundControl is open. This won't have any effect on the way a BlueROV2 operates.

We also want to switch the NMEA GPS Device to "UDP Port" and leave it on 14401.

You can find these settings in the Q Menu of QGroundControl, and your settings should look like this:

![qgc_settings](https://raw.githubusercontent.com/CeruleanSonar/Cerulean-Companion/master/docs/images/qgc_settings.png "QGC Settings")

### Plug Everything In

* ROVL Receiver
* USB GPS
* Power on ROV

### Determine the Correct Ports

You'll need to figure out the correct ports for the ROVL Receiver and GPS on your system. This can be accomplished a few ways:

* Run `cerulean-companion` in a terminal with no settings, and it will attempt to help you find your ports
* Use Device Manager on Windows

At this point, you may want to allow your GPS some time to acquire a lock, and pivot the ROVL Receiver around so it can initialize.

### Sync the ROVL Receiver and Transmitter

This is a good time to sync the ROVL Receiver and Transmitter using the supplied software, or by sending it `D0` when the devices are touching.

On Linux:
```
$ sudo -s
# echo 'D0' > /dev/ttyUSB0
```

### Run the app

Run `cerulean-companion` in a terminal with the settings you determined in the previous step, it should look something like this:

```
$ ./cerulean-companion -u /dev/ttyUSB0 -g /dev/ttyACM0 -e localhost:14401 -m 192.168.2.2:27000
```

If all has gone well, you should see your location as well as your ROV in QGroundControl's map display:

![qgc_map](https://raw.githubusercontent.com/CeruleanSonar/Cerulean-Companion/master/docs/images/qgc_rov.jpg "QGC Map")


If you have issues, check the output of `cerulean-companion` in the terminal



## Advanced Usage

### Installing From PIP

With python3.6 or later, the following command will install all dependencies locally:
```
pip3 install --user --force-reinstall git+https://github.com/CeruleanSonar/Cerulean-Companion.git
```
Note the `--force-reinstall` flag. This is required if you already have `pynmea2` installed to get our custom modified branch.

You should then be able to run the command:
```
$ cerulean-companion
usage: cerulean-companion [-h] [-u /dev/ttyUSB#] [-g /dev/ttyXXX#] [-e localhost:port]
                  [-m host:port] [--log level]
cerulean-companion: error: GPS and USBL devices must be specified

Serial devices detected:
  /dev/cu.Bluetooth-Incoming-Port - n/a
  /dev/cu.DansCans-SPPDev - n/a
```


### Building for distribution:

To package it up for consumption on another machine:
```
git clone https://github.com/CeruleanSonar/Cerulean-Companion.git
cd Cerulean-Companion
pip3 install pyinstaller ./ -t build
env PYTHONPATH="build" python3 -m PyInstaller cerulean-companion.spec
```
You will find the executable file in the `dist` subfolder.
