import serial
import time
import serial.tools.list_ports

import thorlabs_apt_protocol as apt

ports = serial.tools.list_ports.comports()
n =1 
for port, desc, hwid in sorted(ports):
    print(f"{n}) {port}: {desc} [{hwid}]")
    n+=1

port = serial.Serial('COM6', 115200, rtscts=True, timeout=0.1)
port.rts = True
port.reset_input_buffer()
port.reset_output_buffer()
port.rts = False
port.write(apt.hw_no_flash_programming(source=1, dest=0x21))
print('serial should be connected')

msg = apt.mot_move_home(source=1, dest=0x21 ,chan_ident=1)

print(msg)
port.write(msg)


while True:
    print('looping')
    time.sleep(10)
#   msg = apt.mot_ack_dcstatusupdate(source=1, dest=0x21)
    msg = apt.mot_move_relative(source=1, dest=0x21, chan_ident=1, distance=1000)
    port.write(msg)

# port.write(apt.hw_no_flash_programming(source=1, dest=0x21))
# unpacker = apt.Unpacker(port)
# for msg in unpacker:
#     print(msg)
