import serial
import time
import serial.tools.list_ports
import thorlabs_apt_protocol as apt


ports = serial.tools.list_ports.comports()
ENCODER_POS_COUNTS = 20000 #per mm
ENCODER_VEL_COUNTS = 204.8 #per mm/s




# msg = apt.mot_move_absolute(source=1, dest=0x50, chan_ident=1, position=2048)
# port.write(msg)
# print(f'{msg=}')
# print(f'ch1 to pos 2048 == {2048/ENCODER_POS_COUNTS}mm')

# host = 0x01
# ch1 = 0x21
# ch2 = 0x22
# ch3 = 0x23


class Thor_stage():
    def __init__(self):
        self.pos_x = 0
        self.pos_y = 0
        self.ref_x = 0
        self.ref_y = 0
        self.step_x = 0
        self.step_y = 0

        # self.unpacker = apt.Unpacker(self.port)

    def list_ports(self):
        ports = serial.tools.list_ports.comports()
        n =1 
        for port, desc, hwid in sorted(ports):
            print(f"{n}) {port}: {desc} [{hwid}]")
            n+=1

    def connect_serial(self, port):
        self.port = serial.Serial(port, 115200, rtscts=True, timeout=0.1)
        self.port.rts = True
        self.port.reset_input_buffer()
        self.port.reset_output_buffer()
        self.port.rts = False
        self.port.write(apt.hw_no_flash_programming(source=1, dest=0x21))
        print('serial should be connected')
        self.unpacker = apt.Unpacker(self.port)

    def update(self):
        msg = apt.mot_ack_dcstatusupdate(source=1, dest=0x21)
        self.port.write(msg)
        for msg in self.unpacker:
            print(msg)

            # if msgid == status update
            #     self.pos_x =
            #     self.pos_y = 

    def home(self):
        msg = apt.mot_move_home(source=1, dest=0x21 ,chan_ident=1)
        self.port.write(msg)
        print('ch1 moved home')
        msg = apt.mot_move_home(source=1, dest=0x21 ,chan_ident=2)
        self.port.write(msg)
        print('ch2 moved home')

    def set_reference_pos(self, x=None, y=None):
        if x:
            self.ref_x = x
        else:
            self.ref_x = self.pos_x

        if y:
            self.ref_y = y
        else:
            self.ref_y = self.pos_y

    def move_relative(self, dx, dy):

        print(f'moving relative position dx={dx}mm dy={dy}mm')
        dx_counts = dx * ENCODER_POS_COUNTS
        msg = apt.mot_move_relative(source=1, dest=0x50, chan_ident=1, distance=dx_counts)
        self.port.write(msg)

        dy_counts = dy * ENCODER_POS_COUNTS
        msg = apt.mot_move_relative(source=1, dest=0x50, chan_ident=2, distance=dy_counts)
        self.port.write(msg)

    def move_absolute(self, x, y):
        print(f'moving to position x={x}mm y={y}mm')
        x_counts = x * ENCODER_POS_COUNTS
        msg = apt.mot_move_absolute(source=1, dest=0x50, chan_ident=1, position=x_counts)
        self.port.write(msg)
        y_counts = y * ENCODER_POS_COUNTS
        msg = apt.mot_move_absolute(source=1, dest=0x50, chan_ident=2, position=y_counts)
        self.port.write(msg)


if __name__ == "__main__":

    stage = Thor_stage()
    stage.list_ports()
    stage.connect_serial(port='COM6')

    # stage.move_absolute(5, 5)


    while True:
        print('updating')
        print(stage.port.read())
        time.sleep(0.1)
        stage.update()





# def parse_line():
#     response = bytes('900401002101', 'utf-8')
#     response = bytes.fromhex('91040E008121010040420F000000000000000000')
#     response = bytes.fromhex('91040E008121010054D500000000000000000080')


#     print(f'{response.hex()=}')

#     msg_id = response[0:2]
#     print(f'{msg_id=}')


#     # packed = pack('lll', 1, 2, 3)
#     # print(f'{packed=}')
#     # unpacked = unpack('hhl', packed)
#     # print(f'{unpacked=}')

#     # response = [response[i:i+2] for i in range(0, len(response), 2)]

#     if msg_id == b'\x44\x04':
#         chan = response[2:3]
#         print('ch{chan} has been homed')

#     if msg_id == b'\x91\x04':
#         chan = response[6:8] #Is this always 0x0100?
#         position = int(unpack('<l', response[8:12])[0])/ENCODER_POS_COUNTS
#         velocity = int(unpack('<H', response[12:14])[0])/ENCODER_VEL_COUNTS
#         status = int(unpack('>I', response[16:20])[0])
#         print(f'{response[16:20]=}')
#         print(f'{status=}')

#         status_decode = {
#         0x00000001 : 'forward hardware limit switch is active',
#         0x00000002 : 'reverse hardware limit switch is active',
#         0x00000010 : 'in motion, moving forward',
#         0x00000020 : 'in motion, moving reverse',
#         0x00000040 : 'in motion, jogging forward',
#         0x00000080 : 'in motion, jogging reverse',
#         0x00000200 : 'in motion, homing',
#         }

#         print(f'{status=}')
#         if status in status_decode:
#             print('success')
#             print(status_decode[status])

#         print(f'ch{chan} position={position}, velocity={velocity}, status={status}')
#         print()


# def send_status_update_ack(ch):
#     message_id_1 = 0x92
#     message_id_2 = 0x04
#     param1 = 0x01
#     param2 = 0x00
#     dest = ch
#     source = 0x01
#     output_bytes = bytes([message_id_1, message_id_2, param1, param2, dest, source])
#     print(f'{output_bytes.hex()=}')
#     print(f'{(type(output_bytes))=}')

# send_status_update_ack(ch1)
# parse_line()