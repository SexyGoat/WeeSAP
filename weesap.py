#!/usr/bin/env python3

"""WeeSAP - Wee Sixaxis Pairing script

This script is a Linux command-line tool used to set the Bluetooth
MAC address of a host to which a USB-connected PS3 Sixaxis controller
will connect. It does the same job as SixaxisPairTool.

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

A minimal implementation would be

  import hid
  device = hid.device()
  device.open(0x054c, 0x0268)
  device.send_feature_report(b'\xF5\x00\xBA\xD4\xCA\xFE\xF0\x0D')
  device.close()

to set a PS3 controller's host address to BA:D4:CA:FE:F0:0D.
"""

import sys  # for access to command line arguments
import hid  # far access to the HDI API


# Vendor and product IDs for a Sony PS3 Sixaxis controller
VENDOR_ID = 0x054c
PRODUCT_ID = 0x0268


def bytes_to_mac_str(mac_bytes, sep=":"):
  return sep.join(("{:02x}".format(x) for x in mac_bytes))


def mac_str_to_bytes(mac_str):
  result = bytearray(6)
  failed = False
  seps = ''
  if len(mac_str) == 17:
    # 10:32:54:76:98:BA or 10-32-54-76-98-BA
    stride = 3
    fwidth = 2
    nfields = 6
    seps = mac_str[2 : : stride]
    failed = seps not in (":::::", "-----")
  elif len(mac_str) == 14:
    # 3210.7654.BA98
    stride = 5
    fwidth = 4
    nfields = 3
    seps = mac_str[4 : : stride]
    failed = seps not in ("..")
  elif len(mac_str) == 12:
    # 1032547698BA
    stride = 2
    fwidth = 2
    nfields = 6
  else:
    failed = True
  if not failed:
    ri = 0
    try:
      for fi in range(nfields):
        field = mac_str[stride * fi : stride * fi + fwidth]
        x = int(field, 16)
        for bi in range(fwidth >> 1):
          result[ri] = x & 255
          x >>= 8
          ri += 1
    except ValueError:
      failed = True
  return None if failed else result


def main():

  do_show_usage = False
  args = list(sys.argv)[1:]
  s = "--help"
  while s in args:
    print("{}: SixAxis Pairing PYthon script".format(sys.argv[0]))
    do_show_usage = True
    del args[args.index(s)]

  device = None
  rc = 0
  errmsg = ""
  vpstr = "{:04x}:{:04x}".format(VENDOR_ID, PRODUCT_ID)
  mb = None

  if len(args) > 1:
    rc = 1
    errmsg = "Too many arguments!"
    do_show_usage = True
  elif len(args) == 1:
    mb = mac_str_to_bytes(args[0])
    if mb is None:
      rc = 1
      errmsg = "Invalid MAC address"

  if rc == 0:
    try:
      device = hid.device()
      device.open(VENDOR_ID, PRODUCT_ID)
    except OSError:
      if device is None:
        rc = 2
        errmsg = "Could not access HID system."
      else:
        rc = 3
        errmsg = (f"Could not open HID device {vpstr}. "
                  "(Privileged access may be required.)")
      device = None

  if device:
    try:
      report = device.get_feature_report(0xF5, 8)
      host_mac_str = bytes_to_mac_str(report[2:8])
      if mb is not None:
        msg = bytearray([0xF5, 0x00]) + mb
        r = device.send_feature_report(msg)
        if r == 0:
          rc = 4
          errmsg = "Failed to set host address on controller."
      else:
        print(host_mac_str)
    except:
      rc = 5
      errmsg = "A mysterious error occurred."
    finally:
      device.close()

  if errmsg:
    print("{}: {}".format(sys.argv[0], errmsg), file=sys.stderr)
  if do_show_usage:
    print("Usage: {}".format(sys.argv[0]))
    print("       {} NEW_HOST_MAC".format(sys.argv[0]))
  return rc


if __name__ == '__main__':
  main()
