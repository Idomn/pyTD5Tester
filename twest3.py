import usb.core
import usb.util

dev = usb.core.find()
if dev is None:
    print("No USB device found")
else:
    print("Found device:", dev)