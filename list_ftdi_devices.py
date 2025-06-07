from pyftdi.ftdi import Ftdi

print("Scanning for FTDI devices...")
devices = list(Ftdi.list_devices())
if not devices:
    print("No FTDI devices found.")
else:
    for i, dev in enumerate(devices):
        print(f"{i}: {dev}")