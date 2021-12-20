# WeeSAP

This script is a Linux command-line tool used to set the Bluetooth
MAC address of a host to which a USB-connected PS3 Sixaxis controller
will connect via Bluetooth. It does the same job as SixaxisPairTool.

If no argument is supplied, the current host Bluetooth MAC
address is displayed. (This is distinct from the MAC address of
the PS3 controller itself.)

Setting a new host Bluetooth MAC address on a PS3 controller
will allow a microcontroller such as an ESP32-WROOM using the
PS3 Controller Host library to accept a connection from a PS3
controller.

A standard HID library (package "python3-hid") is used to send
the 8-byte packet that does the magic. Though sudo will likely
be needed to execute this script, no change to security policies
is required. (When using sudo, the full path to this script may
be required, since root's PATH variable is usually not the same
as that if the user.)
