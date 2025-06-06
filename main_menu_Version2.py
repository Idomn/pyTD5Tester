@@
-import serial
+from pyftdi.serialext import serial_for_url
@@
-import msvcrt
-from pyftdi.ftdi import Ftdi
+from pyftdi.ftdi import Ftdi
@@
-serial_port = 'COM3'
+FTDI_URL = 'ftdi://ftdi:232h/1'  # Adjust for your FTDI device, see pyftdi docs
@@
-ser=0
+ser=0
@@
-def fast_init():
-    ser = serial.Serial(serial_port, 360, timeout=0.1) #CP210x is configured for 300 being 360
-    #ser = serial.Serial(serial_port, 300, timeout=0.1)
-    command=b"\x00"
-    ser.write(command) #Send a 25ms pulse
-    time.sleep(0.025)
-    ser.close()
+def fast_init():
+    global ser
+    ser = serial_for_url(FTDI_URL, baudrate=360, timeout=0.1)
+    command=b"\x00"
+    ser.write(command) #Send a 25ms pulse
+    time.sleep(0.025)
+    ser.close()
@@
-def send_packet(data,res_size):
-    global debug
-    time.sleep(interframe_delay)
-    
-    lendata=len(data)
-    modulo=0
-    for i in range(0,lendata):
-        modulo = modulo + data[i]
-    modulo = modulo % 256
-    to_send=data+chr(modulo).encode('latin1')
-    ser.write(to_send)
-    time.sleep(interframe_delay)
-
-    ignore=len(to_send)
-    read_val = ser.read(len(to_send)+res_size)
-
-    read_val_s = read_val[0:ignore]
-    if debug > 2:    
-        print(("Data Sent: %s." % binascii.b2a_hex(read_val_s)))
-    read_val_r = read_val[ignore:]
-    if debug > 2: 
-        print(("Data Received: %s." % binascii.b2a_hex(read_val_r)))
-    
-    modulo=0
-    for i in range(0,len(read_val_r)-1):
-        modulo = modulo + read_val_r[i] 
-    modulo = modulo % 256
-    
-    if (len(read_val_r)>2):
-        if (modulo!=read_val_r[len(read_val_r)-1]): #Checksum error
-            read_val_r=""
-            if debug > 1:
-                print ("Checksum ERROR")
-       
-    return read_val_r
+def send_packet(data,res_size):
+    global ser, debug
+    time.sleep(interframe_delay)
+    lendata = len(data)
+    modulo = sum(data) % 256
+    to_send = data + bytes([modulo])
+    ser.write(to_send)
+    time.sleep(interframe_delay)
+    ignore = len(to_send)
+    read_val = ser.read(ignore + res_size)
+    read_val_s = read_val[0:ignore]
+    if debug > 2:
+        print("Data Sent: %s." % binascii.b2a_hex(read_val_s))
+    read_val_r = read_val[ignore:]
+    if debug > 2:
+        print("Data Received: %s." % binascii.b2a_hex(read_val_r))
+    if len(read_val_r) > 2:
+        modulo = sum(read_val_r[:-1]) % 256
+        if modulo != read_val_r[-1]:
+            if debug > 1:
+                print("Checksum ERROR")
+            return b""
+    return read_val_r
@@
-def initialize():
-    global ser
-    fast_init()
-
-    ser = serial.Serial(serial_port, 10400, timeout=0.1)    #CP210x must be configured for 
-
-    time.sleep(0.1)
-    response=send_packet(b"\x81\x13\xF7\x81",5)             #Init Frame
-    time.sleep(0.1)
-    response=send_packet(b"\x02\x10\xA0",3)             #Start Diagnostics
-    time.sleep(0.1)
-    response=send_packet(b"\x02\x27\x01",6)             #Seed Request
-
-    if (len(response)==6):
-        key_ans=seed_key(response)
-        response=send_packet(key_ans,4)             #Seed Request
-
-    time.sleep(0.2)
+def initialize():
+    global ser
+    fast_init()
+    ser = serial_for_url(FTDI_URL, baudrate=10400, timeout=0.1)
+    time.sleep(0.1)
+    send_packet(b"\x81\x13\xF7\x81",5)
+    time.sleep(0.1)
+    send_packet(b"\x02\x10\xA0",3)
+    time.sleep(0.1)
+    response = send_packet(b"\x02\x27\x01",6)
+    if len(response) == 6:
+        key_ans = seed_key(response)
+        send_packet(key_ans,4)
+    time.sleep(0.2)
@@
-while (True):
-    time.sleep(0.01)
-    os.system("cls")
-    print("-------------------------------------------------------------------------------")
-    print("|                Land Rover Td5 Motorren Azterketa Programa                   |")
-    print("-------------------------------------------------------------------------------")
-    print("|                                                                             |", end="\r")
-    print("| COM Port: %s - Map: %s - Fuel: %s - Homol: %s"% (serial_port,map_variant,fuel_variant,homologation))
-    print("|                                                                             |", end="\r")    
-    print("| VIN: %s - ECU Model: %s"% (VIN,ecu_type))
-    print("-------------------------------------------------------------------------------")
-    print("| 1. Fuelling - 2. Inputs - 3. Outputs - 4. Settings - 5. Faults - 6. Map     |")
-    print("-------------------------------------------------------------------------------")                                       
-    if (menu_code==0):
-        print("\n Land Rover Td5 Motorren Azterketa Programa")
-        print("\t\t Ongi Etorri")
-        print("")
-        print(" BSD 2-Clause License")
-        print(" Egilea: EA2EGA - Garmen - xabiergarmendia@gmail.com")
-        print(" Erabilitako kodea:")
-        print("\thttps://github.com/pajacobson/td5keygen")
-        print("\t\tpaul@discotd5.com")
-        print("\thttp://stackoverflow.com/questions/12090503")
-        print("\t\thttp://stackoverflow.com/users/300783/thomas")
-        print("\n")
-        print(" Serie Portu erabilgarriak:")
-
-        import serial.tools.list_ports
-        ports = list(serial.tools.list_ports.comports())
-        for p in ports:
-            print(("  "+str(p)))
-        if len(ports)==1:
-            print(("\n "+str(ports[0]).split(' ')[0]+" Portua Aukeratua"))
-            serial_port=str(ports[0]).split(' ')[0]
-        elif len(ports)>1:
-            sarrera=input("\n Aukeratu Serie Portua: ")
-            print(sarrera)
-        else:
-            print("\n Ez da serie porturik topatu sisteman :(")
-            print(" Programa amaitzen")
-            #exit()
-        
-        initialize()
-        time.sleep(0.1)
-        response=send_packet(b"\x02\x3e\x01",3)             #Start outputs
-        current_mode=4
-        time.sleep(0.5)
-        
-        get_setting()
-        
-        response=send_packet(b"\x01\x20",3)             
-        response=send_packet(b"\x01\x82",3)
-        ser.close()  
-        current_mode=0
-        time.sleep(logout_sleep)
-        
-        time.sleep(0.5)
-        
-        menu_code=1
-        continue
+while (True):
+    time.sleep(0.01)
+    os.system("cls")
+    print("-------------------------------------------------------------------------------")
+    print("|                Land Rover Td5 Motorren Azterketa Programa                   |")
+    print("-------------------------------------------------------------------------------")
+    print("|                                                                             |", end="\r")
+    print("| FTDI Port: %s - Map: %s - Fuel: %s - Homol: %s"% (FTDI_URL,map_variant,fuel_variant,homologation))
+    print("|                                                                             |", end="\r")    
+    print("| VIN: %s - ECU Model: %s"% (VIN,ecu_type))
+    print("-------------------------------------------------------------------------------")
+    print("| 1. Fuelling - 2. Inputs - 3. Outputs - 4. Settings - 5. Faults - 6. Map     |")
+    print("-------------------------------------------------------------------------------")
+    if (menu_code==0):
+        print("\n Land Rover Td5 Motorren Azterketa Programa")
+        print("\t\t Ongi Etorri")
+        print("")
+        print(" BSD 2-Clause License")
+        print(" Egilea: EA2EGA - Garmen - xabiergarmendia@gmail.com")
+        print(" Erabilitako kodea:")
+        print("\thttps://github.com/pajacobson/td5keygen")
+        print("\t\tpaul@discotd5.com")
+        print("\thttp://stackoverflow.com/questions/12090503")
+        print("\t\thttp://stackoverflow.com/users/300783/thomas")
+        print("\n")
+        print(" FTDI gailuak erabilgarriak:")
+        devices = list(Ftdi.list_devices())
+        for i, dev in enumerate(devices):
+            print(f"  {i}: {dev}")
+        if len(devices) == 0:
+            print("\n Ez da FTDI gailurik topatu sisteman :(")
+            print(" Programa amaitzen")
+            break
+        elif len(devices) > 1:
+            print("\n FTDI URL lehenetsia: %s" % FTDI_URL)
+            # Optionally prompt user for FTDI URL selection
+        else:
+            print(f"\n FTDI gailu bakarra: {FTDI_URL}")
+        initialize()
+        time.sleep(0.1)
+        response=send_packet(b"\x02\x3e\x01",3)             #Start outputs
+        current_mode=4
+        time.sleep(0.5)
+        get_setting()
+        response=send_packet(b"\x01\x20",3)
+        response=send_packet(b"\x01\x82",3)
+        ser.close()
+        current_mode=0
+        time.sleep(logout_sleep)
+        time.sleep(0.5)
+        menu_code=1
+        continue
@@
-        if msvcrt.kbhit():
-            menu_code = int(msvcrt.getch())
-            time.sleep(0.1)
-            if (menu_code != current_mode):                     #Logout
-                if(ser.isOpen()):
-                    response=send_packet(b"\x01\x20",3)             
-                    response=send_packet(b"\x01\x82",3)
-                    ser.close() 
-                current_mode=0
-                if debug > 2:              
-                    print ("Logging out")
-                time.sleep(logout_sleep)
-                os.system("cls")
-                continue
+        sel = input("Press Enter to refresh (or type menu number to change): ").strip()
+        if sel.isdigit():
+            menu_code = int(sel)
+            if (menu_code != current_mode):                     #Logout
+                if ser and ser.is_open:
+                    response=send_packet(b"\x01\x20",3)
+                    response=send_packet(b"\x01\x82",3)
+                    ser.close()
+                current_mode=0
+                if debug > 2:
+                    print ("Logging out")
+                time.sleep(logout_sleep)
+                os.system("cls")
+                continue
@@
-        if msvcrt.kbhit():
-            menu_code = int(msvcrt.getch())
-            time.sleep(0.1)
-            if (menu_code != current_mode):                     #Logout
-                if(ser.isOpen()):
-                    response=send_packet(b"\x01\x20",3)             
-                    response=send_packet(b"\x01\x82",3)
-                    ser.close()  
-                current_mode=0
-                if debug > 2:
-                    print ("Logging out")
-                time.sleep(logout_sleep)
-                os.system("cls")
-                continue
+        sel = input("Press Enter to refresh (or type menu number to change): ").strip()
+        if sel.isdigit():
+            menu_code = int(sel)
+            if (menu_code != current_mode):                     #Logout
+                if ser and ser.is_open:
+                    response=send_packet(b"\x01\x20",3)
+                    response=send_packet(b"\x01\x82",3)
+                    ser.close()
+                current_mode=0
+                if debug > 2:
+                    print ("Logging out")
+                time.sleep(logout_sleep)
+                os.system("cls")
+                continue
@@
-        while(True):
-            time.sleep(0.1)
-            response=send_packet(b"\x02\x3e\x01",3)
-            if msvcrt.kbhit():
-                if (msvcrt.getch()=="a" or msvcrt.getch()=="A"):
-                    response=send_packet(b"\x03\x30\xa3\xff",4)
-                    print("\n   Testing AC Clutch")
-                    time.sleep(2)
-                    break
-                elif (msvcrt.getch()=="b" or msvcrt.getch()=="B"):
-                    response=send_packet(b"\x03\x30\xa4\xff",4)
-                    print("\n   Testing AC FAN")
-                    time.sleep(2)
-                    break
-                elif (msvcrt.getch()=="c" or msvcrt.getch()=="C"):
-                    response=send_packet(b"\x03\x30\xa2\xff",4)
-                    print("\n   Testing MIL Lamp")
-                    time.sleep(2)
-                    break
-                elif (msvcrt.getch()=="d" or msvcrt.getch()=="D"):
-                    response=send_packet(b"\x03\x30\xa1\xff",4)
-                    print("\n   Testing Fuel Pump")
-                    time.sleep(2)
-                    break
-                elif (msvcrt.getch()=="e" or msvcrt.getch()=="E"):
-                    response=send_packet(b"\x03\x30\xb3\xff",4)
-                    print("\n   Testing Glow Plugs")
-                    time.sleep(2)
-                    break
-                elif (msvcrt.getch()=="f" or msvcrt.getch()=="F"):
-                    response=send_packet(b"\x03\x30\xb7\xff",4)
-                    print("\n   Testing Pulse Rev Counter")
-                    time.sleep(2)
-                    break
-                elif (msvcrt.getch()=="g" or msvcrt.getch()=="G"):
-                    response=send_packet(b"\x07\x30\xbe\xff\x00\x0a\x13\x88",4)
-                    print("\n   Testing Turbo Wastegate Modulator")
-                    time.sleep(2)
-                    break
-                elif (msvcrt.getch()=="h" or msvcrt.getch()=="H"):
-                    response=send_packet(b"\x03\x30\xba\xff",4)
-                    print("\n   Testing Temperature Gauge")
-                    time.sleep(2)
-                    break
-                elif (msvcrt.getch()=="i" or msvcrt.getch()=="I"):
-                    response=send_packet(b"\x07\x30\xbd\xff\x00\xfa\x13\x88",4)
-                    print("\n   Testing EGR Inlet Modulator")
-                    time.sleep(2)
-                    break
-                elif (msvcrt.getch()=="j" or msvcrt.getch()=="J"):
-                    response=send_packet(b"\x03\x31\xc2\x01",4)
-                    print("\n   Testing Injector 1")
-                    time.sleep(2)
-                    break
-                elif (msvcrt.getch()=="k" or msvcrt.getch()=="K"):
-                    response=send_packet(b"\x03\x31\xc2\x02",4)
-                    print("\n   Testing Injector 2")
-                    time.sleep(2)
-                    break
-                elif (msvcrt.getch()=="l" or msvcrt.getch()=="L"):
-                    response=send_packet(b"\x03\x31\xc2\x03",4)
-                    print("\n   Testing Injector 3")
-                    time.sleep(2)
-                    break
-                elif (msvcrt.getch()=="m" or msvcrt.getch()=="M"):
-                    response=send_packet(b"\x03\x31\xc2\x04",4)
-                    print("\n   Testing Injector 4")
-                    time.sleep(2)
-                    break
-                elif (msvcrt.getch()=="n" or msvcrt.getch()=="N"):
-                    response=send_packet(b"\x03\x31\xc2\x05",4)
-                    print("\n   Testing Injector 5")
-                    time.sleep(2)
-                    break                    
-                entrada=msvcrt.getch()
-                try:
-                    menu_code = int(entrada)
-                except:
-                    donothing=0
-                time.sleep(0.1)
-                if (menu_code != current_mode):                     #Logout
-                    if(ser.isOpen()):
-                        response=send_packet(b"\x01\x20",3)             
-                        response=send_packet(b"\x01\x82",3)
-                        ser.close()  
-                    current_mode=0
-                    if debug > 2:
-                        print ("Logging out")
-                    time.sleep(logout_sleep)
-                    os.system("cls")
-                    break
+        while(True):
+            time.sleep(0.1)
+            response=send_packet(b"\x02\x3e\x01",3)
+            sel = input("Enter A-N for test (or menu number to exit): ").strip().upper()
+            if sel == "A":
+                response=send_packet(b"\x03\x30\xa3\xff",4)
+                print("\n   Testing AC Clutch")
+                time.sleep(2)
+                break
+            elif sel == "B":
+                response=send_packet(b"\x03\x30\xa4\xff",4)
+                print("\n   Testing AC FAN")
+                time.sleep(2)
+                break
+            elif sel == "C":
+                response=send_packet(b"\x03\x30\xa2\xff",4)
+                print("\n   Testing MIL Lamp")
+                time.sleep(2)
+                break
+            elif sel == "D":
+                response=send_packet(b"\x03\x30\xa1\xff",4)
+                print("\n   Testing Fuel Pump")
+                time.sleep(2)
+                break
+            elif sel == "E":
+                response=send_packet(b"\x03\x30\xb3\xff",4)
+                print("\n   Testing Glow Plugs")
+                time.sleep(2)
+                break
+            elif sel == "F":
+                response=send_packet(b"\x03\x30\xb7\xff",4)
+                print("\n   Testing Pulse Rev Counter")
+                time.sleep(2)
+                break
+            elif sel == "G":
+                response=send_packet(b"\x07\x30\xbe\xff\x00\x0a\x13\x88",4)
+                print("\n   Testing Turbo Wastegate Modulator")
+                time.sleep(2)
+                break
+            elif sel == "H":
+                response=send_packet(b"\x03\x30\xba\xff",4)
+                print("\n   Testing Temperature Gauge")
+                time.sleep(2)
+                break
+            elif sel == "I":
+                response=send_packet(b"\x07\x30\xbd\xff\x00\xfa\x13\x88",4)
+                print("\n   Testing EGR Inlet Modulator")
+                time.sleep(2)
+                break
+            elif sel == "J":
+                response=send_packet(b"\x03\x31\xc2\x01",4)
+                print("\n   Testing Injector 1")
+                time.sleep(2)
+                break
+            elif sel == "K":
+                response=send_packet(b"\x03\x31\xc2\x02",4)
+                print("\n   Testing Injector 2")
+                time.sleep(2)
+                break
+            elif sel == "L":
+                response=send_packet(b"\x03\x31\xc2\x03",4)
+                print("\n   Testing Injector 3")
+                time.sleep(2)
+                break
+            elif sel == "M":
+                response=send_packet(b"\x03\x31\xc2\x04",4)
+                print("\n   Testing Injector 4")
+                time.sleep(2)
+                break
+            elif sel == "N":
+                response=send_packet(b"\x03\x31\xc2\x05",4)
+                print("\n   Testing Injector 5")
+                time.sleep(2)
+                break
+            elif sel.isdigit():
+                menu_code = int(sel)
+                if (menu_code != current_mode):                     #Logout
+                    if ser and ser.is_open:
+                        response=send_packet(b"\x01\x20",3)
+                        response=send_packet(b"\x01\x82",3)
+                        ser.close()
+                    current_mode=0
+                    if debug > 2:
+                        print ("Logging out")
+                    time.sleep(logout_sleep)
+                    os.system("cls")
+                    break
@@
-        while(True):
-            time.sleep(1)
-            response=send_packet(b"\x02\x3e\x01",3)
-            if msvcrt.kbhit():
-                if (msvcrt.getch()=="5"): #Refresh
-                    break
-                if (msvcrt.getch()=="C" or msvcrt.getch()=="c"): #Clear Faults
-                    response=send_packet(b"\x14\x31\xdd\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",4)
-                    print("|Clearing Faults|")
-                    break
-                entrada=msvcrt.getch()
-                try:
-                    menu_code = int(entrada)
-                except:
-                    donothing=0
-                time.sleep(0.1)
-                if (menu_code != current_mode):                     #Logout
-                    if(ser.isOpen()):
-                        response=send_packet(b"\x01\x20",3)             
-                        response=send_packet(b"\x01\x82",3)
-                        ser.close()  
-                    current_mode=0
-                    if debug > 2:
-                        print ("Logging out")
-                    time.sleep(logout_sleep)
-                    os.system("cls")
-                    break
+        while(True):
+            time.sleep(1)
+            response=send_packet(b"\x02\x3e\x01",3)
+            sel = input("Type 5 to refresh, C to clear faults, or menu number to exit: ").strip().upper()
+            if sel == "5":
+                break
+            if sel == "C":
+                response=send_packet(b"\x14\x31\xdd\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",4)
+                print("|Clearing Faults|")
+                break
+            if sel.isdigit():
+                menu_code = int(sel)
+                if (menu_code != current_mode):                     #Logout
+                    if ser and ser.is_open:
+                        response=send_packet(b"\x01\x20",3)
+                        response=send_packet(b"\x01\x82",3)
+                        ser.close()
+                    current_mode=0
+                    if debug > 2:
+                        print ("Logging out")
+                    time.sleep(logout_sleep)
+                    os.system("cls")
+                    break
@@
-        while (1):
-            if msvcrt.kbhit():
-                entrada=msvcrt.getch()
-                if (entrada.decode('latin1')=="R" or entrada.decode('latin1')=="r"): #Clear Faults
-                    print("|                                                                             |", end="\r")
-                    print("|     Reading Map - ", end="")
-                    name = input("Write filename to save: ")
-                    f=open(name, 'wb')
-                    
-                    initialize()
-                    time.sleep(0.2)
-                    byte1=0x11
-                    byte2=0x00
-                    byte3=0x00
-                    while (1):
-
-                        percent=((byte1-0x11)*256*256+byte2*256+byte3)/(3*256*256)
-                        address=bytes([byte1])+bytes([byte2])+bytes([byte3])
-                        print("|                                                                             |", end="\r")
-                        print("|\tReading Address: %s - %s Complete" % (binascii.b2a_hex(address),'{:.1%}'.format(percent)), end="\r")
-
-                        if (byte1==0x13 and byte2==0xff):
-                            response=send_packet(b"\x05\x23"+bytes([byte1])+bytes([byte2])+bytes([byte3])+b"\x10",20)
-                            while (len(response)<19):
-                                response=send_packet(b"\x05\x23"+bytes([byte1])+bytes([byte2])+bytes([byte3])+b"\x10",20)
-                            f.write(response[3:19])
-                        else:
-                            response=send_packet(b"\x05\x23"+bytes([byte1])+bytes([byte2])+bytes([byte3])+b"\x40",68)
-                            while (len(response)<67):
-                                response=send_packet(b"\x05\x23"+bytes([byte1])+bytes([byte2])+bytes([byte3])+b"\x40",68)
-                            f.write(response[3:67])
-                        
-                        if (byte1==0x13 and byte2==0xff and byte3==0xe0):
-                            break
-
-                        if (byte1==0x13 and byte2==0xff):
-                            byte3=byte3+0x10
-                        else:
-                            byte3=byte3+0x40
-                            
-                        if byte3==256:
-                            byte2=byte2+1
-                            byte3=0
-                            if byte2==256:
-                                byte1=byte1+1
-                                byte2=0
-
-                    f.close()
-                    break
-                try:
-                    menu_code = int(entrada)
-                except:
-                    donothing=0
-            time.sleep(0.1)
+        while (1):
+            sel = input("Type R to read map, or menu number to exit: ").strip().upper()
+            if sel == "R":
+                print("|                                                                             |", end="\r")
+                print("|     Reading Map - ", end="")
+                name = input("Write filename to save: ")
+                f=open(name, 'wb')
+                initialize()
+                time.sleep(0.2)
+                byte1=0x11
+                byte2=0x00
+                byte3=0x00
+                while (1):
+                    percent=((byte1-0x11)*256*256+byte2*256+byte3)/(3*256*256)
+                    address=bytes([byte1])+bytes([byte2])+bytes([byte3])
+                    print("|                                                                             |", end="\r")
+                    print("|\tReading Address: %s - %s Complete" % (binascii.b2a_hex(address),'{:.1%}'.format(percent)), end="\r")
+                    if (byte1==0x13 and byte2==0xff):
+                        response=send_packet(b"\x05\x23"+bytes([byte1])+bytes([byte2])+bytes([byte3])+b"\x10",20)
+                        while (len(response)<19):
+                            response=send_packet(b"\x05\x23"+bytes([byte1])+bytes([byte2])+bytes([byte3])+b"\x10",20)
+                        f.write(response[3:19])
+                    else:
+                        response=send_packet(b"\x05\x23"+bytes([byte1])+bytes([byte2])+bytes([byte3])+b"\x40",68)
+                        while (len(response)<67):
+                            response=send_packet(b"\x05\x23"+bytes([byte1])+bytes([byte2])+bytes([byte3])+b"\x40",68)
+                        f.write(response[3:67])
+                    if (byte1==0x13 and byte2==0xff and byte3==0xe0):
+                        break
+                    if (byte1==0x13 and byte2==0xff):
+                        byte3=byte3+0x10
+                    else:
+                        byte3=byte3+0x40
+                    if byte3==256:
+                        byte2=byte2+1
+                        byte3=0
+                        if byte2==256:
+                            byte1=byte1+1
+                            byte2=0
+                f.close()
+                break
+            if sel.isdigit():
+                menu_code = int(sel)
+            time.sleep(0.1)