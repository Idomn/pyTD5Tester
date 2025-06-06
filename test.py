from pyftdi.ftdi import Ftdi
import time
from collections import namedtuple
import msvcrt
import os

CAUTIOUS_READ           = False
READ_BUFFER_SIZE        = 127

MAX_ATTEMPTS            = 5
ATTEMPT_DELAY           = 3     # 2s
SEND_REQUEST_DELAY      = 0.2   # 0.055 # 55ms
READ_RESPONSE_TIMEOUT   = 0.1   # 100ms

Pid = namedtuple('Pid', ['request', 'response_len'])

fault_code_void="Unknown"
fault_code_01_01="1-1 egr inlet throttle diagnostics (L)"
fault_code_01_02="1-2 turbocharger wastegate diagnostics (L)"
fault_code_01_03="1-3 egr vacuum diagnostics (L)"
fault_code_01_04="1-4 temperature gauge diagnostics (L)"
fault_code_01_05="1-5 driver demand problem 1 (L)"
fault_code_01_06="1-6 driver demand problem 2 (L)"
fault_code_01_07="1-7 air flow circuit (L)"
fault_code_01_08="1-8 manifold pressure circuit (L)"
fault_code_02_01="2-1 inlet air temp. circuit (L)"
fault_code_02_02="2-2 fuel temp. circuit (L)"
fault_code_02_03="2-3 coolant temp. circuit (L)"
fault_code_02_04="2-4 battery volts (L)"
fault_code_02_05="2-5 reference voltage (L)"
fault_code_02_06="2-6 ambient air temp. circuit (L)"
fault_code_02_07="2-7 driver demand supply problem (L)"
fault_code_02_08="2-8 ambient pressure circuit (L)"
fault_code_03_01="3-1 egr inlet throttle diagnostics (L)"
fault_code_03_02="3-2 turbocharger wastegate diagnostics (L)"
fault_code_03_03="3-3 egr vacuum diagnostics (L)"
fault_code_03_04="3-4 temperature gauge diagnostics (L)"
fault_code_03_05="3-5 driver demand problem 1 (L)"
fault_code_03_06="3-6 driver demand problem 2 (L)"
fault_code_03_07="3-7 air flow circuit (L)"
fault_code_03_08="3-8 manifold pressure circuit (L)"
fault_code_04_01="4-1 inlet air temp. circuit (L)"
fault_code_04_02="4-2 fuel temperature circuit (L)"
fault_code_04_03="4-3 coolant temp. circuit (L)"
fault_code_04_04="4-4 battery volts (L)"
fault_code_04_05="4-5 reference voltage (L)"
fault_code_04_06="4-6 ambient air temperature circuit (L)"
fault_code_04_07="4-7 driver demand supply problem (L)"
fault_code_04_08="4-8 ambient pressure circuit (L)"
fault_code_05_01="5-1 egr inlet throttle diagnostics (C)"
fault_code_05_02="5-2 turbocharger wastegate diagnostics (C)"
fault_code_05_03="5-3 egr vacuum diagnostics (C)"
fault_code_05_04="5-4 temperature gauge diagnostics (C)"
fault_code_05_05="5-5 driver demand problem 1 (C)"
fault_code_05_06="5-6 driver demand problem 2 (C)"
fault_code_05_07="5-7 air flow circuit (C)"
fault_code_05_08="5-8 manifold pressure circuit (C)"
fault_code_06_01="6-1 inlet air temp. circuit (C)"
fault_code_06_02="6-2 fuel temperature circuit (C)"
fault_code_06_03="6-3 coolant temp. circuit (C)"
fault_code_06_04="6-4 battery voltage problem (C)"
fault_code_06_05="6-5 reference voltage (C)"
fault_code_06_07="6-7 driver demand supply problem (C)"
fault_code_06_08="6-8 ambient pressure circuit (C)"
fault_code_07_01="7-1 cruise lamp drive over temp. (L)"
fault_code_07_02="7-2 fuel used output drive over temp. (L)"
fault_code_07_03="7-3 radiator fan drive over temp. (L)"
fault_code_07_04="7-4 active engine mounting over temp. (L)"
fault_code_07_05="7-5 turbocharger wastegate short circuit (L)"
fault_code_07_06="7-6 egr inlet throttle short circuit (L)"
fault_code_07_07="7-7 egr vacuum modulator short circuit (L)"
fault_code_07_08="7-8 temperature gauge short circuit (L)"
fault_code_08_01="8-1 air conditioning fan drive over temp. (L)"
fault_code_08_02="8-2 fuel pump drive over temp. (L)"
fault_code_08_03="8-3 tacho drive over temp. (L)"
fault_code_08_04="8-4 gearbox/abs drive over temp. (L)"
fault_code_08_05="8-5 air conditioning clutch over temp. (L)"
fault_code_08_06="8-6 mil lamp drive over temp. (L)"
fault_code_08_07="8-7 glow plug relay drive over temp. (L)"
fault_code_08_08="8-8 glowplug lamp drive over temperature (L)"
fault_code_09_01="9-1 fuel used output drive open load (L)"
fault_code_09_02="9-2 cruise lamp drive open load (L)"
fault_code_09_03="9-3 radiator fan drive open load (L)"
fault_code_09_04="9-4 active engine mounting open load (L)"
fault_code_09_05="9-5 turbocharger wastegate open load (L)"
fault_code_09_06="9-6 egr inlett throttle open load (L)"
fault_code_09_07="9-7 egr vacuum modulator open load (L)"
fault_code_09_08="9-8 temperature gauge open load (L)"
fault_code_10_01="10-1 air conditioning fan drive open load (L)"
fault_code_10_02="10-2 fuel pump drive open load (L)"
fault_code_10_03="10-3 tachometer open load (L)"
fault_code_10_04="10-4 gearbox/abs drive open load (L)"
fault_code_10_05="10-5 air conditioning clutch open load (L)"
fault_code_10_06="10-6 mil lamp drive open load (L)"
fault_code_10_07="10-7 glow plug lamp drive open load (L)"
fault_code_10_08="10-8 glow plug relay drive open load (L)"
fault_code_11_01="11-1 cruise control lamp drive over temperature (C)"
fault_code_11_02="11-2 fuel used output drive over temperature (C)"
fault_code_11_03="11-3 radiator fan drive over temperature (C)"
fault_code_11_04="11-4 active engine mounting over temperature (C)"
fault_code_11_05="11-5 turbocharger wastegate short circuit (C)"
fault_code_11_06="11-6 egr inlet throttle short circuit (C)"
fault_code_11_07="11-7 egr vacuum modulator short circuit (C)"
fault_code_11_08="11-8 temperature gauge short circuit (C)"
fault_code_12_01="12-1 air conditioning fan drive open load (C)"
fault_code_12_02="12-2 fuel pump drive open load (C)"
fault_code_12_03="12-3 tachometer open load (C)"
fault_code_12_04="12-4 gearbox/abs drive open load (C)"
fault_code_12_05="12-5 air conditioning clutch open load (C)"
fault_code_12_06="12-6 mil lamp drive open load (C)"
fault_code_12_07="12-7 glow plug relay drive open load (C)"
fault_code_12_08="12-8 glowplug relay drive open load (C)"
fault_code_13_01="13-1 cruise control lamp drive over temp. (C)"
fault_code_13_02="13-2 fuel used output drive over temp. (C)"
fault_code_13_03="13-3 radiator fan drive over temp. (C)"
fault_code_13_04="13-4 active engine mounting over temp. (C)"
fault_code_13_05="13-5 turbocharger wastegate short circuit (C)"
fault_code_13_06="13-6 egr inlet throttle short circuit (C)"
fault_code_13_07="13-7 egr vacuum modulator short circuit (C)"
fault_code_13_08="13-8 temperature gauge short circuit (C)"
fault_code_14_01="14-1 air conditioning fan drive open load (C)"
fault_code_14_02="14-2 fuel pump drive open load (C)"
fault_code_14_03="14-3 tachometer open load (C)"
fault_code_14_04="14-4 gearbox/abs drive open load (C)"
fault_code_14_05="14-5 air conditioning clutch open load (C)"
fault_code_14_06="14-6 mil lamp drive open load (C)"
fault_code_14_07="14-7 glow plug relay drive open load (C)"
fault_code_14_08="14-8 glowplug relay drive open load (C)"
fault_code_15_02="15-2 high speed crank (L)"
fault_code_16_02="16-2 high speed crank (L)"
fault_code_17_02="17-2 high speed crank (C)"
fault_code_19_02="19-2 can rx/tx error (L)"
fault_code_19_03="19-3 can tx/rx error (L)"
fault_code_19_06="19-6 noisy crank signal has been detected (L)"
fault_code_19_08="19-8 can has had reset failure (L)"
fault_code_20_01="20-1 turbocharger under boosting (L)"
fault_code_20_02="20-2 turbocharger over boosting (L)"
fault_code_20_04="20-4 egr valve stuck open (L)"
fault_code_20_05="20-5 egr valve stuck closed (L)"
fault_code_21_04="21-4 driver demand 1 out of range (L)"
fault_code_21_05="21-5 driver demand 2 out of range (L)"
fault_code_21_06="21-6 problem detected with driver demand (L)"
fault_code_21_07="21-7 inconsistencies found with driver demand (L)"
fault_code_21_08="21-8 injector trim data corrupted (L)"
fault_code_22_01="22-1 road speed missing (L)"
fault_code_22_03="22-3 vehicle accel. outside bounds of cruise control (L)"
fault_code_22_07="22-7 cruise control resume stuck closed (L)"
fault_code_22_08="22-8 cruise control set stuck closed (L)"
fault_code_23_01="23-1 excessive can bus off (C)"
fault_code_23_02="23-2 can rx/tx error (C)"
fault_code_23_03="23-3 can tx/rx error (C)"
fault_code_23_04="23-4 unable to detect remote can mode (C)"
fault_code_23_05="23-5 under boost has occurred on this trip (C)"
fault_code_23_06="23-6 noisy crack signal has been detected (C)"
fault_code_24_01="24-1 turbocharger under boosting (C)"
fault_code_24_02="24-2 turbocharger over boosting (C)"
fault_code_24_03="24-3 over boost has occurred this trip (C)"
fault_code_24_04="24-4 egr valve stuck open (C)"
fault_code_24_05="24-5 egr valve stuck closed (C)"
fault_code_24_07="24-7 problem detected with auto gear box (C)"
fault_code_25_04="25-4 driver demand 1 out of range (L)"
fault_code_25_05="25-5 driver demand 2 out of range (L)"
fault_code_25_06="25-6 problem detected with drive demand (C)"
fault_code_25_07="25-7 inconsistencies found with driver demand (C)"
fault_code_25_08="25-8 injector trim data corrupted (C)"
fault_code_26_01="26-1 road speed missing (C)"
fault_code_26_02="26-2 cruise control system problem (C)"
fault_code_26_03="26-3 vehicle accel. outside bounds for cruise control (C)"
fault_code_26_07="26-7 cruise control resume stuck closed (C)"
fault_code_26_08="26-8 cruise control set stuck closed (C)"
fault_code_27_01="27-1 inj. 1 peak charge long (L)"
fault_code_27_02="27-2 inj. 2 peck charge long (L)"
fault_code_27_03="27-3 inj. 3 peak charge long (L)"
fault_code_27_04="27-4 inj. 4 peck charge long (L)"
fault_code_27_05="27-5 inj. 5 peak charge long (L)"
fault_code_27_06="27-6 inj. 6 peck charge long (L)"
fault_code_27_07="27-7 topside switch failed post injection (L)"
fault_code_28_01="28-1 inj. 1 peak charge short (L)"
fault_code_28_02="28-2 inj. 2 peck charge short (L)"
fault_code_28_03="28-3 inj. 3 peak charge short (L)"
fault_code_28_04="28-4 inj. 4 peck charge short (L)"
fault_code_28_05="28-5 inj. 5 peak charge short (L)"
fault_code_28_06="28-6 inj. 6 peck charge short (L)"
fault_code_28_07="28-7 topside switch failed pre injection (L)"
fault_code_29_01="29-1 inj. 1 peak charge long (C)"
fault_code_29_02="29-2 inj. 2 peck charge long (C)"
fault_code_29_03="29-3 inj. 3 peak charge long (C)"
fault_code_29_04="29-4 inj. 4 peck charge long (C)"
fault_code_29_05="29-5 inj. 5 peak charge long (C)"
fault_code_29_06="29-6 inj. 6 peck charge long (C)"
fault_code_29_07="29-7 topside switch failed post injection (C)"
fault_code_30_01="30-1 inj. 1 peak charge short (C)"
fault_code_30_02="30-2 inj. 2 peck charge short (C)"
fault_code_30_03="30-3 inj. 3 peak charge short (C)"
fault_code_30_04="30-4 inj. 4 peck charge short (C)"
fault_code_30_05="30-5 inj. 5 peak charge short (C)"
fault_code_30_06="30-6 inj. 6 peck charge short (C)"
fault_code_30_07="30-7 topside switch failed pre injection (C)"
fault_code_31_01="31-1 inj. 1 open circuit (L)"
fault_code_31_02="31-2 inj. 2 open circuit (L)"
fault_code_31_03="31-3 inj. 3 open circuit (L)"
fault_code_31_04="31-4 inj. 4 open circuit (L)"
fault_code_31_05="31-5 inj. 5 open circuit (L)"
fault_code_31_06="31-6 inj. 6 open circuit (L)"
fault_code_32_01="32-1 inj. 1 short circuit (L)"
fault_code_32_02="32-2 inj. 2 short circuit (L)"
fault_code_32_03=""   #fake due to unknown downloading error
_fault_code_32_03="32-3 inj. 3 short circuit (L)"  #duplicated and renamed due to unknown downloading error
fault_code_32_04="32-4 inj. 4 short circuit (L)"
fault_code_32_05="32-5 inj. 5 short circuit (L)"
fault_code_32_06="32-6 inj. 6 short circuit (L)"
fault_code_33_01="33-1 inj. 1 open circuit (C)"
fault_code_33_02="33-2 inj. 2 open circuit (C)"
fault_code_33_03="33-3 inj. 3 open circuit (C)"
fault_code_33_04="33-4 inj. 4 open circuit (C)"
fault_code_33_05="33-5 inj. 5 open circuit (C)"
fault_code_33_06="33-6 inj. 6 open circuit (C)"
fault_code_34_01="34-1 inj. 1 short circuit (C)"
fault_code_34_02="34-2 inj. 2 short circuit (C)"
fault_code_34_03="34-3 inj. 3 short circuit (C)"
fault_code_34_04="34-4 inj. 4 short circuit (C)"
fault_code_34_05="34-5 inj. 5 short circuit (C)"
fault_code_34_06="34-6 inj. 6 short circuit (C)"
fault_code_35_01="35-1 inj. 1 partial short circuit (L)"
fault_code_35_02="35-2 inj. 2 partial short circuit (L)"
fault_code_35_03="35-3 inj. 3 partial short circuit (L)"
fault_code_35_04="35-4 inj. 4 partial short circuit (L)"
fault_code_35_05="35-5 inj. 5 partial short circuit (L)"
fault_code_35_06="35-6 inj. 6 partial short circuit (L)"

fault_code_text = [
    fault_code_01_01, fault_code_01_02, fault_code_01_03, fault_code_01_04, fault_code_01_05, fault_code_01_06, fault_code_01_07, fault_code_01_08,
    fault_code_02_01, fault_code_02_02, fault_code_02_03, fault_code_02_04, fault_code_02_05, fault_code_02_06, fault_code_02_07, fault_code_02_08,
    fault_code_03_01, fault_code_03_02, fault_code_03_03, fault_code_03_04, fault_code_03_05, fault_code_03_06, fault_code_03_07, fault_code_03_08,
    fault_code_04_01, fault_code_04_02, fault_code_04_03, fault_code_04_04, fault_code_04_05, fault_code_04_06, fault_code_04_07, fault_code_04_08,
    fault_code_05_01, fault_code_05_02, fault_code_05_03, fault_code_05_04, fault_code_05_05, fault_code_05_06, fault_code_05_07, fault_code_05_08,
    fault_code_06_01, fault_code_06_02, fault_code_06_03, fault_code_06_04, fault_code_06_05, fault_code_void,  fault_code_06_07, fault_code_06_08,
    fault_code_07_01, fault_code_07_02, fault_code_07_03, fault_code_07_04, fault_code_07_05, fault_code_07_06, fault_code_07_07, fault_code_07_08,
    fault_code_08_01, fault_code_08_02, fault_code_08_03, fault_code_08_04, fault_code_08_05, fault_code_08_06, fault_code_08_07, fault_code_08_08,
    fault_code_09_01, fault_code_09_02, fault_code_09_03, fault_code_09_04, fault_code_09_05, fault_code_09_06, fault_code_09_07, fault_code_09_08,
    fault_code_10_01, fault_code_10_02, fault_code_10_03, fault_code_10_04, fault_code_10_05, fault_code_10_06, fault_code_10_07, fault_code_10_08,
    fault_code_11_01, fault_code_11_02, fault_code_11_03, fault_code_11_04, fault_code_11_05, fault_code_11_06, fault_code_11_07, fault_code_11_08,
    fault_code_12_01, fault_code_12_02, fault_code_12_03, fault_code_12_04, fault_code_12_05, fault_code_12_06, fault_code_12_07, fault_code_12_08,
    fault_code_13_01, fault_code_13_02, fault_code_13_03, fault_code_13_04, fault_code_13_05, fault_code_13_06, fault_code_13_07, fault_code_13_08,
    fault_code_14_01, fault_code_14_02, fault_code_14_03, fault_code_14_04, fault_code_14_05, fault_code_14_06, fault_code_14_07, fault_code_14_08,
    fault_code_void,  fault_code_15_02, fault_code_void,  fault_code_void,  fault_code_void,  fault_code_void,  fault_code_void,  fault_code_void,
    fault_code_void,  fault_code_16_02, fault_code_void,  fault_code_void,  fault_code_void,  fault_code_void,  fault_code_void,  fault_code_void,
    fault_code_void,  fault_code_17_02, fault_code_void,  fault_code_void,  fault_code_void,  fault_code_void,  fault_code_void,  fault_code_void,
    fault_code_void,  fault_code_void,  fault_code_void,  fault_code_void,  fault_code_void,  fault_code_void,  fault_code_void,  fault_code_void,
    fault_code_void,  fault_code_19_02, fault_code_19_03, fault_code_void,  fault_code_void,  fault_code_19_06, fault_code_void,  fault_code_19_08,
    fault_code_20_01, fault_code_20_02, fault_code_void,  fault_code_20_04, fault_code_20_05, fault_code_void,  fault_code_void,  fault_code_void,
    fault_code_void,  fault_code_void,  fault_code_void,  fault_code_21_04, fault_code_21_05, fault_code_21_06, fault_code_21_07, fault_code_void,
    fault_code_22_01, fault_code_void,  fault_code_22_03, fault_code_void,  fault_code_void,  fault_code_void,  fault_code_22_07, fault_code_22_08,
    fault_code_23_01, fault_code_23_02, fault_code_23_03, fault_code_23_04, fault_code_23_05, fault_code_23_06, fault_code_void,  fault_code_void,
    fault_code_24_01, fault_code_24_02, fault_code_24_03, fault_code_24_04, fault_code_24_05, fault_code_void,  fault_code_24_07, fault_code_void,
    fault_code_void,  fault_code_void,  fault_code_void,  fault_code_25_04, fault_code_25_05, fault_code_25_06, fault_code_25_07, fault_code_25_08,
    fault_code_26_01, fault_code_26_02, fault_code_26_03, fault_code_void,  fault_code_void,  fault_code_void,  fault_code_26_07, fault_code_26_08,
    fault_code_27_01, fault_code_27_02, fault_code_27_03, fault_code_27_04, fault_code_27_05, fault_code_27_06, fault_code_27_07, fault_code_void,
    fault_code_28_01, fault_code_28_02, fault_code_28_03, fault_code_28_04, fault_code_28_05, fault_code_28_06, fault_code_28_07, fault_code_void,
    fault_code_29_01, fault_code_29_02, fault_code_29_03, fault_code_29_04, fault_code_29_05, fault_code_29_06, fault_code_29_07, fault_code_void,
    fault_code_30_01, fault_code_30_02, fault_code_30_03, fault_code_30_04, fault_code_30_05, fault_code_30_06, fault_code_30_07, fault_code_void,
    fault_code_31_01, fault_code_31_02, fault_code_31_03, fault_code_31_04, fault_code_31_05, fault_code_31_06, fault_code_void,  fault_code_void,
    fault_code_32_01, fault_code_32_02, _fault_code_32_03, fault_code_32_04, fault_code_32_05, fault_code_32_06, fault_code_void,  fault_code_void,
    fault_code_33_01, fault_code_33_02, fault_code_33_03, fault_code_33_04, fault_code_33_05, fault_code_33_06, fault_code_void,  fault_code_void,
    fault_code_34_01, fault_code_34_02, fault_code_34_03, fault_code_34_04, fault_code_34_05, fault_code_34_06, fault_code_void,  fault_code_void,
    fault_code_35_01, fault_code_35_02, fault_code_35_03, fault_code_35_04, fault_code_35_05, fault_code_35_06, fault_code_void,  fault_code_void]








debug = 0
interframe_delay=0.002

logout_sleep=1

BATTERY_VOLTAGE     = Pid(bytearray([0x02, 0x21, 0x10, 0x00]),              8)
ENGINE_RPM          = Pid(bytearray([0x02, 0x21, 0x09, 0x00]),              6)
VEHICLE_SPEED       = Pid(bytearray([0x02, 0x21, 0x0D, 0x00]),              5)
get_bvolt=Pid(bytearray([0x02, 0x21, 0x10, 0x00]),              8)
get_rpm=Pid(bytearray([0x02, 0x21, 0x09, 0x00]),              6)
get_rpm_error=Pid(bytearray([0x02, 0x21, 0x21, 0x00]),              6)
get_speed=Pid(bytearray([0x02, 0x21, 0x0D, 0x00]),              5)
b_voltage=0
rpm=0
rpm_error=0
speed=0
TEMPS=Pid(bytearray([0x02, 0x21, 0x1A, 0x00]),              20)
t_coolant=0
t_air=0
t_ext=0
t_fuel =0
throttle=Pid(bytearray([0x02, 0x21, 0x1B, 0x00]),              14)
p1=0
p2=0
p3=0
p4=-1
supply = 0
aap_maf=Pid(bytearray([0x02, 0x21, 0x1C, 0x00]),              12)
aap=0
maf =0
pressures=Pid(bytearray([0x02, 0x21, 0x23, 0x00]),              8)
ap1=0
ap2=0
power_balance=Pid(bytearray([0x02, 0x21, 0x40, 0x00]),              14)
pb1=0
pb2=0
pb3=0
pb4=0
pb5=0
inputs=Pid(bytearray([0x02, 0x21, 0x1e, 0x00]),              6)
br1=0
br2=0
clutch=0
xfer=0
ccm=0
ccr=0
ccsa=0
accr=0
acfr=0
fu=Pid(bytearray([0x02, 0x21, 0x1D, 0x00]),              22)
fu1=0
fu2=0
fu3=0
fu4=0
fu5=0
fu6=0
fu7=0
fu8=0
setting=Pid(bytearray([0x02, 0x21, 0x32, 0x00]),              28)
ecu_type=""
map_variant=""
fuel_variant=""
homologation=""
VIN=""
faults=Pid(bytearray([0x02, 0x21, 0x3b, 0x00]),              39)
fault_list = []

# http://www.rangerovers.net/forum/12-diagnostic-equipment/39941-working-homemade-error-reader-scanner-need-help-ecu-output.html
ABS_INIT_FRAME      = Pid(bytearray([0x81, 0x29, 0xF7, 0x81, 0x0C]),        7)

INIT_FRAME          = Pid(bytearray([0x81, 0x13, 0xF7, 0x81, 0x0C]),        7)
START_DIAGNOSTICS   = Pid(bytearray([0x02, 0x10, 0xA0, 0xB2]),              3)
REQUEST_SEED        = Pid(bytearray([0x02, 0x27, 0x01, 0x2A]),              6)
KEY_RETURN          = Pid(bytearray([0x04, 0x27, 0x02, 0x00, 0x00, 0x00]),  4)
BATTERY_VOLTAGE     = Pid(bytearray([0x02, 0x21, 0x10, 0x00]),              8)
ENGINE_RPM          = Pid(bytearray([0x02, 0x21, 0x09, 0x00]),              6)
VEHICLE_SPEED       = Pid(bytearray([0x02, 0x21, 0x0D, 0x00]),              5)

#VIN=Pid(bytearray([0x02, 0x1a, 0x9a, 0x00]),              5).format(response[3:14].decode('latin1'),bcdtoint(response[14]),bcdtoint(response[15]),bcdtoint(response[16]))

HI = bytearray([0x01])
LO = bytearray([0x00])

response    = None
connected   = False
uart        = None

################################################################################
def pause(delay, step_size):
    ################################################################################
    end_time = time.monotonic() + delay
    while (time.monotonic() <= end_time):
        time.sleep(step_size)

################################################################################
def calculate_checksum(request):
    ################################################################################
    request_len = len(request)
    crc = 0
    for i in range(0, request_len - 1):
        crc = crc + request[i]

    return crc % 256 # crc & 0xF

################################################################################
def log_data(data, is_tx):
    ################################################################################
    print("{} {}".format(
        ">>" if is_tx else "<<",
        ''.join('{:02X} '.format(x) for x in data).rstrip()
    ))

################################################################################
def read_data(size, timeout):
    ################################################################################
    data = bytearray()
    start = time.monotonic()
    while True:
        buf = uart.read_data(size)
        data += buf
        size -= len(buf)
        if size <= 0:
            break
        if timeout is not None:
            ms = time.monotonic() - start
            if ms > timeout:
                break
            time.sleep(0.01)

    return data

################################################################################
def get_pid(pid):
    ################################################################################
    global response

    result = False

    # Punch the calculated checksum into the last byte and then send the request
    request_len = len(pid.request)
    pid.request[request_len - 1] = calculate_checksum(pid.request)
    if not connected:
        log_data(pid.request, True)

    if pid != INIT_FRAME:
        pause(SEND_REQUEST_DELAY, 0.001)

    uart.write_data(pid.request)

    # read the response
    response = None
    if CAUTIOUS_READ:
        response = read_data(READ_BUFFER_SIZE, 0.1)
    else:
        # The request is echoed in the response
        response = read_data(pid.response_len + request_len, 0.1)

    if not connected:
        log_data(response, False)

    # Remove the request from the response
    response = response[request_len:]

    # Check the response checksum
    response_len = len(response)
    if response_len > 1:
        cs1 = response[response_len - 1]
        cs2 = calculate_checksum(response)
        if cs1 == cs2:
            # Negative response ?
            if response[1] != 0x7F:
                result = True

    return result

################################################################################
def calculate_key(seed):
    ################################################################################
    count = ((seed >> 0xC & 0x8) + (seed >> 0x5 & 0x4) + (seed >> 0x3 & 0x2) + (seed & 0x1)) + 1

    for idx in range(0, count):
        tap = ((seed >> 1) + (seed >> 2 ) + (seed >> 8 ) + (seed >> 9)) & 1
        tmp = (seed >> 1) | ( tap << 0xF)

        if (seed >> 0x3 & 1) and (seed >> 0xD & 1):
            seed = tmp & ~1
        else:
            seed = tmp | 1

    return (seed >> 8, seed & 255)

################################################################################
def open_uart():
    ################################################################################
    global uart

    # set up the device
    uart = Ftdi()
    try:
        uart.open(0x403, 0x6001)
    except Exception as e:
        uart = None
        print("error={}".format(e))
        return

    uart.set_baudrate(10400)
    uart.set_line_property(8, 1, 'N')
    # print(uart.modem_status())

################################################################################
def slow_init(address):
    ################################################################################

    # Set K-line HI for 300ms
    # Transmit address byte at 5 baud (0x33)
    # Switch to 10400 baud
    # Wait 60-300ms for synchronisation pattern byte 0x55
    # Wait 5-20ms for KB1 (one of 0xE9 0x6B 0x6D 0xEF)
    # Wait 0-20ms for KB2 (always 0x8F)
    # Wait 25-50ms and send inverted KB2
    # Wait 25-50ms and send inverted address byte

    global uart
    global response
    global connected

    if uart is None:
        return

    uart.set_bitmode(0x01, 0x01)

    # K line HI for 300ms
    uart.write_data(HI)
    pause(0.300, 0.001)

    # Start bit LO
    uart.write_data(LO)
    pause(0.200, 0.001)

    # Send the target address LSB first at 5 Baud
    for i in range(0, 8):
        hilo = address >> i & 0x01
        uart.write_data(hilo)
        pause(0.200, 0.001)

    # Stop bit HI
    uart.write_data(HI)
    pause(0.200, 0.01)

    # Switch off bit bang
    uart.set_bitmode(0x00, 0x00)
    uart.purge_buffers()

    # Wait up 300ms + 20ms + 20ms to read Sync + KB1 + KB2 bytes
    response = uart.read_data(3, 0.340)

    response_len = len(response)
    log_data(response, False)
    if response[0] == 0x55 and response[2] == 0x8F:
        inverted_address    = bytearray([~address])
        inverted_kb2        = bytearray([~response[2]])

        # Send inverted KB2
        pause(0.025, 0.001)
        uart.write_data(inverted_kb2)
        log_data(inverted_kb2)

        # Send inverted address
        pause (0.025, 0.001)
        uart.write_data(inverted_address)
        log_data(inverted_address)

        connected = True
    else:
        uart.close()
        uart = None

################################################################################
def fast_init():
    ################################################################################
    global uart
    global KEY_RETURN
    global response
    global connected

    if uart is None:
        return

    HI = bytearray([0x01])
    LO = bytearray([0x00])

    attempt = 0
    while attempt < MAX_ATTEMPTS:
        # Toggle the TX line for the fast_init using the ftdi chip bit bang mode
        uart.set_bitmode(0x01, 0x01)

        uart.write_data(HI)
        pause(0.500, 0.01)

        uart.write_data(LO)
        pause(0.0245, 0.00025)

        uart.write_data(HI)
        pause(0.0245, 0.00025)

        # Switch off bit bang
        uart.set_bitmode(0x00, 0x00)
        uart.purge_buffers()

        # Start communications

        # >> 81 13 F7 81 0C
        # << 81 13 F7 81 0C 03 C1 57 8F AA
        # >> 02 10 A0 B2
        # << 02 10 A0 B2 01 50 51
        # >> 02 27 01 2A
        # << 02 27 01 2A 04 67 01 52 25 E3
        # >> 04 27 02 14 89 CA
        # << 04 27 02 14 89 CA 02 67 02 6B

        if (get_pid(INIT_FRAME) and get_pid(START_DIAGNOSTICS) and get_pid(REQUEST_SEED)):
            seed = response[3] << 8 | response[4]
            key_hi, key_lo = calculate_key(seed)
            KEY_RETURN.request[3] = key_hi
            KEY_RETURN.request[4] = key_lo
            connected = get_pid(KEY_RETURN)

        if connected:
            break
        pause(ATTEMPT_DELAY, 0.01)
        attempt += 1

    # fast_init failed
    if not connected:
        uart.close()
        uart = None


################################################################################
def start_logger():
    ################################################################################
    if not connected:
        return

    start = time.monotonic()
    while True:
        buf = "{:010.3f}".format(time.monotonic() - start)

        if get_pid(BATTERY_VOLTAGE):
            buf += " " "{:06.2f}".format((response[5] << 8 | response[6]) / 1000.0)

        if get_pid(ENGINE_RPM):
            buf += " " "{:06d}".format(response[3] << 8 | response[4])

        if get_pid(VEHICLE_SPEED):
            buf += " " "{:03d}".format(response[3])

        print(buf)

def initialize():
    fast_init()

def get_rpm():
    global rpm
    response=get_rpm
    if len(response)<6:
        #rpm=0
        i=0
    else:
        rpm=response[3]*256+response[4]

    return rpm

def get_rpm_error():
    global rpm_error
    response=get_rpm_error
    if len(response)<6:
        #rpm_error=0
        i=0
    else:
        rpm_error=response[3]*256+response[4]

    if rpm_error>32768:
        rpm_error=rpm_error-65537
    return rpm_error

def get_bvolt():
    global b_voltage
    response=get_bvolt
    b_voltage=response[3]*256+response[4]
    b_voltage=float(b_voltage)/1000

    return b_voltage

def get_speed():
    global speed
    response=get_speed
    speed=response[3]

    return speed

def get_temps():
    global t_coolant, t_air, t_ext, t_fuel
    response=TEMPS

    t_coolant=float(response[3]*256+response[4])/10-273.2
    t_air=float(response[7]*256+response[8])/10-273.2
    t_ext=float(response[11]*256+response[12])/10-273.2
    t_fuel=float(response[15]*256+response[16])/10-273.2

    return t_coolant, t_air, t_ext, t_fuel

def get_throttle():
    global p1, p2, p3, p4, supply
    response=throttle
    # if len(response)<12:
    #     p1=0
    #     p2=0
    #     p3=0
    #     p4=0
    #     supply=0
        # i=0
    # elif len(response)==12:
    #     p1=float(response[3]*256+response[4])/1000
    #     p2=float(response[5]*256+response[6])/1000
    #     p3=float(response[7]*256+response[8])/100
    #     p4=-1
    #     supply=float(response[9]*256+response[10])/1000
    # else:
    p1=float(response[3]*256+response[4])/1000
    p2=float(response[5]*256+response[6])/1000
    p3=float(response[7]*256+response[8])/1000
    p4=float(response[9]*256+response[10])/100
    supply=float(response[11]*256+response[12])/1000


    return p1, p2, p3, p4, supply

def get_aap_maf():
    global aap, maf
    debug=5
    response=aap_maf
    aap=float(response[3]*256+response[4])/10000
    maf=response[7]*256+response[8]

    return aap, maf

def get_pressures():
    global ap1, ap2
    debug=5
    response=pressures

    ap1=float(response[3]*256+response[4])/10000
    ap2=float(response[5]*256+response[6])/10000

    return ap1, ap2

def get_faults():

    global debug
    global fault_list
    fault_list=[]
    response=faults
    for i in range(0,36):
        for j in range(0,8):
            if ord(response[i+3]) & int(pow(2,int(j))) != 0:
                fault_list.append(int(i)*8+int(j))

    return fault_list


def get_power_balance():
    global pb1, pb2, pb3, pb4, pb5
    response=power_balance

    pb1=response[3]*256+response[4]
    pb2=response[5]*256+response[6]
    pb3=response[7]*256+response[8]
    pb4=response[9]*256+response[10]
    pb5=response[11]*256+response[12]

    if pb1>32768:
        pb1=pb1-65537
    if pb2>32768:
        pb2=pb2-65537
    if pb3>32768:
        pb3=pb3-65537
    if pb4>32768:
        pb4=pb4-65537
    if pb5>32768:
        pb5=pb5-65537

    return pb1,pb2,pb3,pb4,pb5

def get_fu():
    global fu1,fu2,fu3,fu4,fu5,fu6,fu7,fu8
    response=fu

    fu1=response[3]*256+response[4]
    fu2=response[5]*256+response[6]
    fu3=response[7]*256+response[8]
    fu4=response[9]*256+response[10]
    fu5=response[11]*256+response[12]
    fu6=response[13]*256+response[14]
    fu7=response[15]*256+response[16]
    fu8=response[17]*256+response[18]

    if fu1>32768:
        fu1=fu1-65537
    if fu2>32768:
        fu2=fu2-65537
    if fu3>32768:
        fu3=fu3-65537
    if fu4>32768:
        fu4=fu4-65537
    if fu5>32768:
        fu5=fu5-65537
    if fu6>32768:
        fu6=fu6-65537
    if fu7>32768:
        fu7=fu7-65537
    if fu8>32768:
        fu8=fu8-65537

    fu1=float(fu1)/100
    fu2=float(fu2)/100
    fu3=float(fu3)/10
    fu4=float(fu4)/100
    fu5=float(fu5)/100
    fu6=float(fu6)/100
    fu7=float(fu7)/100
    fu8=float(fu8)/100


    return fu1,fu2,fu3,fu4,fu5,fu6,fu7,fu8


def get_setting():
    #global ecu_type,map_variant,fuel_variant,homologation,VIN
    #response=send_packet(b"\x02\x1a\x87",50)        #Get VIN
    #if (len(response)>40): #is a NNN
     #   VIN='{}{:02d}{:02d}{:02d}'.format(response[3:14].decode('latin1'),bcdtoint(response[14]),bcdtoint(response[15]),bcdtoint(response[16]))
      #  response=send_packet(b"\x02\x1a\x9a",10)        #Get ECU Type
       # ecu_type='{}{:02d}{:02d}{:02d}'.format(response[3:6].decode('latin1'),bcdtoint(response[6]),bcdtoint(response[7]),bcdtoint(response[8]))
        #time.sleep(0.1)

    #response=send_packet(b"\x02\x1a\x9b",8)        #?
    #response=send_packet(b"\x02\x1a\x9c",8)        #?

    response=setting
    map_variant='{}'.format(response[3:11].decode('latin1'))
    fuel_variant='{}'.format(response[11:19].decode('latin1'))
    homologation='{}'.format(response[19:23].decode('latin1'))



def get_inputs():
    global br1,br2,clutch,xfer,ccm,ccr,ccsa,accr,acfr
    response=inputs
    byte1=response[3]
    byte2=response[4]
    if byte2 & 0b01000000 != 0:
        xfer=1
    else:
        xfer=0
    if byte1 & 0b1 != 0:
        br2=1
    else:
        br2=0
    if byte2 & 0b10000000 != 0:
        br1=1
    else:
        br1=0
    if byte1 & 0b00000010 != 0:
        clutch=1
    else:
        clutch=0
    if byte1 & 0b00000100 != 0:
        ccm=1
    else:
        ccm=0
    if byte1 & 0b00010000 != 0:
        ccr=1
    else:
        ccr=0
    if byte1 & 0b00001000 != 0:
        ccsa=1
    else:
        ccsa=0
    if byte2 & 0b00001000 != 0:
        accr=1
    else:
        accr=0
    if byte2 & 0b00000100 != 0:
        acfr=1
    else:
        acfr=0
    return br1,br2,clutch,xfer,ccm,ccr,ccsa,accr,acfr

################################################################################
if __name__ == "__main__":
    ################################################################################

    # TODO: Continuously wait to connect and handle ignition off and on
    # TODO: Start a new data file each time the ignition is switched on
    # TODO: See how fast we can reliably poll the ECU
    # TODO: Can you connect after the engine has started ?

    open_uart()
    fast_init()
    menu_code=0;
    current_mode=0;
    ser=0
    while (True):
        time.sleep(0.01)
        os.system("cls")
        print("-------------------------------------------------------------------------------")
        print("|                Land Rover Td5 Engine Analysis Program                   |")
        print("-------------------------------------------------------------------------------")
        print("|                                                                             |", end="\r")
        print("| Map: %s - Fuel: %s - Homol: %s"% (map_variant,fuel_variant,homologation))
        print("|                                                                             |", end="\r")
        print("| VIN: %s - ECU Model: %s"% (VIN,ecu_type))
        print("-------------------------------------------------------------------------------")
        print("| 1. Fuelling - 2. Inputs - 3. Outputs - 4. Settings - 5. Faults - 6. Map     |")
        print("-------------------------------------------------------------------------------")
        if (menu_code==0):
            print("\n Land Rover Td5 Engine Analysis Program")
            print("\t\t Welcome")
            print("")
            print(" BSD 2-Clause License")
            print(" Egilea: EA2EGA - Garmen - xabiergarmendia@gmail.com")
            print(" The code used:")
            print("\thttps://github.com/pajacobson/td5keygen")
            print("\t\tpaul@discotd5.com")
            print("\thttp://stackoverflow.com/questions/12090503")
            print("\t\thttp://stackoverflow.com/users/300783/thomas")
            print("\n")

            initialize()
            time.sleep(0.1)
            # response=send_packet(b"\x02\x3e\x01",3)             #Start outputs
            # current_mode=4
            # time.sleep(0.5)
            #
            # get_setting()
            #
            # response=send_packet(b"\x01\x20",3)
            # response=send_packet(b"\x01\x82",3)
            # ser.close()
            # current_mode=0
            # time.sleep(logout_sleep)
            #
            # time.sleep(0.5)

            menu_code=1
            continue

        if (menu_code==1):
            print("| Fuelling Parameters                                                         |")
            print("|-----------------------------------------------------------------------------|")
            print("\t Battery Voltage: ", str(b_voltage), " Volt")
            print("\t RPM: ", str(rpm))
            print("\t RPM Error: ", str(rpm_error))
            print("\t Speed: ", str(speed), " KMH")
            print("\t Coolant Temp: ", str(t_coolant), " C")
            print("\t Air Temp: ", str(t_air), " C")
            print("\t External Temp: ", str(t_ext), " C")
            print("\t Fuel Temp: ", str(t_fuel), " C")
            if p4==-1:
                print("\t Accelerator - P1 P2 Supply (Volt): ", str(p1), " ", str(p2)," ", str(supply))
            else:
                print("\t Accelerator - P1 P2 P3 Supply (Volt): ", str(p1), " ", str(p2), " ", str(p3)," ", str(supply))
            print("\t Manifold Pressure: ", str(aap), " Bar")
            print("\t Air Mass Mater: ", str(maf))
            print("\t External Pressure:", str(ap1), " Bar")
            print("\t Turbo Pressure (calculated):", str(aap-ap1), " Bar")
            print("\t Cylinders: ", str(pb1), " ", str(pb2), " ", str(pb3), " ", str(pb4), " ", str(pb5))
            print("\t EGR Modulation: N/A")
            print("\t EGR Inlet: N/A")
            print("\t Wastegate Modulation: N/A")
            print("\t -------------------------")
            print("\t Extras: ")
            if p4==-1:
                print("\t Driver pedal demand: ",p3," %")
            else:
                print("\t Driver pedal demand: ",p4," %")
            print("\t Driver fuel demand: ",fu1," mg/stroke")
            print("\t Idle fuel demand: ",fu8," mg/stroke")
            print("\t Air Intake: ",fu3," mg/stroke")
            print("\t Map Solution A/F: ",fu6," mg/stroke")
            print("\t Torque Limiter: ",fu7," mg/stroke")
            print("\t Injected fuel: ",fu4," mg/stroke")
            print("\t Consumption (Calculated): ",fu4*rpm*(5/2)*60/1000000," kg/hora")
            try:
                afratio=fu3/fu4
                print("\t A/F Ratio (Calculated): ",afratio)
            except:
                print("\t A/F Ratio (Calculated): inf")

            # response=send_packet(b"\x02\x21\x1e",6)
            # print "\n\n\tHex is: %s." % ":".join("{:02x}".format(ord(c)) for c in response)

            # response=send_packet(b"\x02\x21\x36",6)
            # print "\tHex is: %s." % ":".join("{:02x}".format(ord(c)) for c in response)

            if (current_mode!=1):
                if debug > 2:
                    print ("Logging in")
                initialize()
                time.sleep(0.1)
                # response=send_packet(b"\x02\x21\x20",15)             #Start Diagnostics
                current_mode=1


            b_voltage=get_bvolt()
            rpm=get_rpm()

            rpm_error=get_rpm_error()
            speed=get_speed()
            t_coolant, t_air, t_ext, t_fuel =get_temps()
            p1, p2, p3, p4, supply = get_throttle()
            aap, maf = get_aap_maf()
            ap1, ap2 = get_pressures()
            pb1,pb2,pb3,pb4,pb5=get_power_balance()
            fu1,fu2,fu3,fu4,fu5,fu6,fu7,fu8=get_fu()

            if msvcrt.kbhit():
                menu_code = int(msvcrt.getch())
                time.sleep(0.1)
                # if (menu_code != current_mode):                     #Logout
                #     if(ser.isOpen()):
                #         response=send_packet(b"\x01\x20",3)
                #         response=send_packet(b"\x01\x82",3)
                #         ser.close()
                #     current_mode=0
                #    if debug > 2:
                #         print ("Logging out")
                #     time.sleep(logout_sleep)
                #     os.system("cls")
                #     continue

        if (menu_code==2):
            print("| Inputs                                                                      |")
            print("|-----------------------------------------------------------------------------|")

            print("\t Brake 1, Brake 2: ", str(br1), " ", str(br2))
            print("\t Clutch: ", str(clutch))
            print("\t Transfer: ", str(xfer))
            print("\t Gear Box: N/A Yet")
            print("\t Cruise Control Main, Resume, Set/Accelerate: ", str(ccm), " ", str(ccr), " ", str(ccsa))
            print("\t A/C Clutch Req: ", str(accr))
            print("\t A/C Fan Req:  ", str(acfr))


            if (current_mode!=2):
                initialize()
                time.sleep(0.1)
            #    response=send_packet(b"\x02\x3e\x01",3)             #Start Inputs
                current_mode=2

            br1,br2,clutch,xfer,ccm,ccr,ccsa,accr,acfr=get_inputs()
            time.sleep(0.1)


            if msvcrt.kbhit():
                menu_code = int(msvcrt.getch())
                time.sleep(0.1)
                # if (menu_code != current_mode):                     #Logout
                #     if(ser.isOpen()):
                #         response=send_packet(b"\x01\x20",3)
                #         response=send_packet(b"\x01\x82",3)
                #         ser.close()
                #     current_mode=0
                #     if debug > 2:
                #         print ("Logging out")
                #     time.sleep(logout_sleep)
                #     os.system("cls")
                #     continue

        if (menu_code==3):
            print("| Outputs                                                                     |")
            print("|-----------------------------------------------------------------------------|")
            print("\t A: Test AC Clutch")
            print("\t B: Test AC Fan")
            print("\t C: Test MIL Lamp")
            print("\t D: Test Fuel Pump")
            print("\t E: Test Glow Plugs")
            print("\t F: Test Pulse Rev Counter")
            print("\t G: Test Turbo WG Modulator")
            print("\t H: Test Temperature Gauge")
            print("\t I: Test EGR Inlet Modulator")
            print("\t J: Test Injector 1")
            print("\t K: Test Injector 2")
            print("\t L: Test Injector 3")
            print("\t M: Test Injector 4")
            print("\t N: Test Injector 5")
            print("\n   Enter letter for test: ")

            if (current_mode!=3):
                initialize()
                time.sleep(0.1)
                # response=send_packet(b"\x02\x3e\x01",3)             #Start outputs
                current_mode=3

            # while(True):
            #     time.sleep(0.1)
            #     response=send_packet(b"\x02\x3e\x01",3)
            #     if msvcrt.kbhit():
            #         if (msvcrt.getch()=="a" or msvcrt.getch()=="A"):
            #             response=send_packet(b"\x03\x30\xa3\xff",4)
            #             print("\n   Testing AC Clutch")
            #             time.sleep(2)
            #             break
            #         elif (msvcrt.getch()=="b" or msvcrt.getch()=="B"):
            #             response=send_packet(b"\x03\x30\xa4\xff",4)
            #             print("\n   Testing AC FAN")
            #             time.sleep(2)
            #             break
            #         elif (msvcrt.getch()=="c" or msvcrt.getch()=="C"):
            #             response=send_packet(b"\x03\x30\xa2\xff",4)
            #             print("\n   Testing MIL Lamp")
            #             time.sleep(2)
            #             break
            #         elif (msvcrt.getch()=="d" or msvcrt.getch()=="D"):
            #             response=send_packet(b"\x03\x30\xa1\xff",4)
            #             print("\n   Testing Fuel Pump")
            #             time.sleep(2)
            #             break
            #         elif (msvcrt.getch()=="e" or msvcrt.getch()=="E"):
            #             response=send_packet(b"\x03\x30\xb3\xff",4)
            #             print("\n   Testing Glow Plugs")
            #             time.sleep(2)
            #             break
            #         elif (msvcrt.getch()=="f" or msvcrt.getch()=="F"):
            #             response=send_packet(b"\x03\x30\xb7\xff",4)
            #             print("\n   Testing Pulse Rev Counter")
            #             time.sleep(2)
            #             break
            #         elif (msvcrt.getch()=="g" or msvcrt.getch()=="G"):
            #             response=send_packet(b"\x07\x30\xbe\xff\x00\x0a\x13\x88",4)
            #             print("\n   Testing Turbo Wastegate Modulator")
            #             time.sleep(2)
            #             break
            #         elif (msvcrt.getch()=="h" or msvcrt.getch()=="H"):
            #             response=send_packet(b"\x03\x30\xba\xff",4)
            #             print("\n   Testing Temperature Gauge")
            #             time.sleep(2)
            #             break
            #         elif (msvcrt.getch()=="i" or msvcrt.getch()=="I"):
            #             response=send_packet(b"\x07\x30\xbd\xff\x00\xfa\x13\x88",4)
            #             print("\n   Testing EGR Inlet Modulator")
            #             time.sleep(2)
            #             break
            #         elif (msvcrt.getch()=="j" or msvcrt.getch()=="J"):
            #             response=send_packet(b"\x03\x31\xc2\x01",4)
            #             print("\n   Testing Injector 1")
            #             time.sleep(2)
            #             break
            #         elif (msvcrt.getch()=="k" or msvcrt.getch()=="K"):
            #             response=send_packet(b"\x03\x31\xc2\x02",4)
            #             print("\n   Testing Injector 2")
            #             time.sleep(2)
            #             break
            #         elif (msvcrt.getch()=="l" or msvcrt.getch()=="L"):
            #             response=send_packet(b"\x03\x31\xc2\x03",4)
            #             print("\n   Testing Injector 3")
            #             time.sleep(2)
            #             break
            #         elif (msvcrt.getch()=="m" or msvcrt.getch()=="M"):
            #             response=send_packet(b"\x03\x31\xc2\x04",4)
            #             print("\n   Testing Injector 4")
            #             time.sleep(2)
            #             break
            #         elif (msvcrt.getch()=="n" or msvcrt.getch()=="N"):
            #             response=send_packet(b"\x03\x31\xc2\x05",4)
            #             print("\n   Testing Injector 5")
            #             time.sleep(2)
            #             break
            #         entrada=msvcrt.getch()
            #         try:
            #             menu_code = int(entrada)
            #         except:
            #             donothing=0
            #         time.sleep(0.1)
            #         if (menu_code != current_mode):                     #Logout
            #             if(ser.isOpen()):
            #                 response=send_packet(b"\x01\x20",3)
            #                 response=send_packet(b"\x01\x82",3)
            #                 ser.close()
            #             current_mode=0
            #             if debug > 2:
            #                 print ("Logging out")
            #             time.sleep(logout_sleep)
            #             os.system("cls")
            #             break

        if (menu_code==4):
            print("| Settings                                                                    |")
            print("|-----------------------------------------------------------------------------|")

            if (current_mode!=4):
                initialize()
                time.sleep(0.1)
                # response=send_packet(b"\x02\x3e\x01",3)             #Start outputs
                current_mode=4
                time.sleep(0.5)

            get_setting()

            print("| VIN: "+VIN)
            print("| ECU Model: "+ecu_type)
            print("| Map Variant: "+map_variant)
            print("| Fuel variant: "+fuel_variant)
            print("| Homologation: "+homologation)


            time.sleep(0.5)
            if (menu_code != current_mode):                     #Logout
                # if(ser.isOpen()):
                #     response=send_packet(b"\x01\x20",3)
                #     response=send_packet(b"\x01\x82",3)
                #     ser.close()
                current_mode=0
                if debug > 2:
                    print ("Logging out")
                time.sleep(logout_sleep)
                os.system("cls")
                break

        if (menu_code==5):

            if (current_mode!=4):
                initialize()
                time.sleep(0.1)
                current_mode=4

            print("| Faults - Refresh: 5 - Clear Faults: C                                       |")
            print("|-----------------------------------------------------------------------------|")

            fault_list=get_faults()
            for error in fault_list:
                highb=(error/8)+1
                lowb=(error%8)+1
                try:
                    #print "\t",error, " ",highb,"-",lowb," ",fault_code_text[error]
                    print("\t",error, " ",fault_code_text[error])
                except:
                    exce1=1
            while(True):
                time.sleep(1)
                # response=send_packet(b"\x02\x3e\x01",3)
                if msvcrt.kbhit():
                    if (msvcrt.getch()=="5"): #Refresh
                        break
                    # if (msvcrt.getch()=="C" or msvcrt.getch()=="c"): #Clear Faults
                    #     response=send_packet(b"\x14\x31\xdd\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",4)
                    #     print("|Clearing Faults|")
                    #     break
                    entrada=msvcrt.getch()
                    try:
                        menu_code = int(entrada)
                    except:
                        donothing=0
                    time.sleep(0.1)
                    if (menu_code != current_mode):                     #Logout
                        # if(ser.isOpen()):
                        #     response=send_packet(b"\x01\x20",3)
                        #     response=send_packet(b"\x01\x82",3)
                        #     ser.close()
                        current_mode=0
                        if debug > 2:
                            print ("Logging out")
                        time.sleep(logout_sleep)
                        os.system("cls")
                        break

        if (menu_code==6):
            print("| Maps                                                                        |")
            print("|-----------------------------------------------------------------------------|")
            if (ecu_type!=""):
                print("|   FLASHABLE ECU                                                             |")
                print("|   R: Read Map    W: Write Map                                               |")
            else:
                print("|   NON FLASHABLE ECU                                                         |")
            print("|-----------------------------------------------------------------------------|")
            # while (1):
            #     if msvcrt.kbhit():
            #         entrada=msvcrt.getch()
            #         if (entrada.decode('latin1')=="R" or entrada.decode('latin1')=="r"): #Clear Faults
            #             print("|                                                                             |", end="\r")
            #             print("|     Reading Map - ", end="")
            #             name = input("Write filename to save: ")
            #             f=open(name, 'wb')
            #
            #             initialize()
            #             time.sleep(0.2)
            #             byte1=0x11
            #             byte2=0x00
            #             byte3=0x00
            #             while (1):
            #
            #                 percent=((byte1-0x11)*256*256+byte2*256+byte3)/(3*256*256)
            #                 address=bytes([byte1])+bytes([byte2])+bytes([byte3])
            #                 print("|                                                                             |", end="\r")
            #                 print("|\tReading Address: %s - %s Complete" % (binascii.b2a_hex(address),'{:.1%}'.format(percent)), end="\r")
            #
            #                 if (byte1==0x13 and byte2==0xff):
            #                     response=send_packet(b"\x05\x23"+bytes([byte1])+bytes([byte2])+bytes([byte3])+b"\x10",20)
            #                     while (len(response)<19):
            #                         response=send_packet(b"\x05\x23"+bytes([byte1])+bytes([byte2])+bytes([byte3])+b"\x10",20)
            #                     f.write(response[3:19])
            #                 else:
            #                     response=send_packet(b"\x05\x23"+bytes([byte1])+bytes([byte2])+bytes([byte3])+b"\x40",68)
            #                     while (len(response)<67):
            #                         response=send_packet(b"\x05\x23"+bytes([byte1])+bytes([byte2])+bytes([byte3])+b"\x40",68)
            #                     f.write(response[3:67])
            #
            #                 if (byte1==0x13 and byte2==0xff and byte3==0xe0):
            #                     break
            #
            #                 if (byte1==0x13 and byte2==0xff):
            #                     byte3=byte3+0x10
            #                 else:
            #                     byte3=byte3+0x40
            #
            #                 if byte3==256:
            #                     byte2=byte2+1
            #                     byte3=0
            #                     if byte2==256:
            #                         byte1=byte1+1
            #                         byte2=0
            #
            #             f.close()
            #             break
            #         try:
            #             menu_code = int(entrada)
            #         except:
            #             donothing=0
            #     time.sleep(0.1)

