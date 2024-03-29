import time
import serial
import serial.tools.list_ports
import thorlabs_apt_protocol as apt
import logging
import math
import random

logging.basicConfig(level=logging.INFO)

class Thorlabs_Stage():
    def __init__(self):
        self.encoder_pos_counts = 20000 #per mm
        self.encoder_vel_counts = 204.8 #per mm/s
        self.home_pos_x = 55 #mm
        self.home_pos_y = 37.5 #mm

        self.pos_x = 0
        self.pos_y = 0
        self.ref_ax = 0
        self.ref_ay = 0
        self.ref_bx = 0
        self.ref_by = 0

        self.slide_rotation = 0 #degrees

        self.status_msg_x = None
        self.status_msg_y = None

        self.serial_port = None
        self.port = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.disconnect_serial()

    def scan_serial_ports(self):
        ports = serial.tools.list_ports.comports()
        n =1 
        for port, desc, hwid in sorted(ports):
            logging.debug(f"{n}) {port}: {desc} [{hwid}]")
            n+=1
        return ports

    def connect_serial(self, serial_port=None):
        self.serial_port = serial_port

        if self.serial_port:
            if self.port:
                self.port.close()
            self.port = serial.Serial(self.serial_port, 115200, rtscts=True, timeout=0.1)
            self.port.rts = True
            self.port.reset_input_buffer()
            self.port.reset_output_buffer()
            self.port.rts = False
            self.port.write(apt.hw_no_flash_programming(source=1, dest=0x21))
            logging.info(f'thorlabs serial connection on {self.serial_port}')

            self.unpacker = apt.Unpacker(self.port)
        else:
            self.port=None
            logging.warning('thorlabs serial port not specified')

    def disconnect_serial(self):
        if self.port:
            logging.info(f'Closing serial port')
            self.port.close()
            self.port = None
        else:
            logging.info(f'SIMULATING Closing serial port')
            self.port = None

    def enable(self):
        logging.info('Enabling stage channels')
        self._apt_cmd(apt.mod_set_chanenablestate(source=1, dest=0x21 ,chan_ident=1, enable_state=1))
        self._apt_cmd(apt.mod_set_chanenablestate(source=1, dest=0x22 ,chan_ident=1, enable_state=1))
        self.enabled = True

    def _apt_cmd(self, cmd_string):
        if self.port:
            self.port.write(cmd_string)
            # logging.debug(f'{cmd_string.hex()=}')
        else:
            logging.debug(f'SIMULATING {cmd_string.hex()=}')

    def set_position_reference_a(self, x=None, y=None):
        if x and y:
            self.ref_ax = x
            self.ref_ay = y
        else:
            self.get_position()
            self.ref_ax = self.pos_x
            self.ref_ay = self.pos_y
        self._calculate_rotation()

    def set_position_reference_b(self, x=None, y=None):
        if x and y:
            self.ref_bx = x
            self.ref_by = y
        else:
            self.get_position()
            self.ref_bx = self.pos_x
            self.ref_by = self.pos_y
        self._calculate_rotation()

    def _calculate_rotation(self):
        if (self.ref_bx != 0) and (self.ref_by != 0):                
            slope = (self.ref_by-self.ref_ay)/(self.ref_bx-self.ref_ax)
            logging.debug(f'{slope=}')
            self.slide_rotation = round(math.degrees(math.atan(slope)),2)
            # negative angle indicates anticlockwise rotation
            logging.info(f'Slide rotation = {self.slide_rotation}deg')

    def _wait_for_position(self):
        logging.info('getting position')
        self._apt_cmd(apt.hw_start_updatemsgs(source=1, dest=0x21))
        self._apt_cmd(apt.hw_start_updatemsgs(source=1, dest=0x22))

        self.pos_x = None
        self.pos_y = None
        while self.pos_x == None or self.pos_y == None:
            for msg in self.unpacker:
                if msg.msg == 'mot_get_dcstatusupdate':
                    if msg.source == 0x21:
                        self.status_msg_x = msg
                        self.pos_x = msg.position/self.encoder_pos_counts
                    if msg.source == 0x22:
                        self.status_msg_y = msg
                        self.pos_y = msg.position/self.encoder_pos_counts

        logging.info(f'{self.pos_x=} {self.pos_y=}')

        self._apt_cmd(apt.hw_stop_updatemsgs(source=1, dest=0x21))
        self._apt_cmd(apt.hw_stop_updatemsgs(source=1, dest=0x22))

        # clear unpacker buffer
        # self.port.reset_input_buffer() #is this better? TODO
        for msg in self.unpacker: pass

    def _wait_for_home(self):
        logging.info('waiting for home')
        self._apt_cmd(apt.hw_start_updatemsgs(source=1, dest=0x21))
        self._apt_cmd(apt.hw_start_updatemsgs(source=1, dest=0x22))

        home_complete_x = False
        home_complete_y = False
        while home_complete_x == False or home_complete_y == False:
            for msg in self.unpacker:
                if msg.msg == 'mot_get_dcstatusupdate':
                    if msg.source == 0x21 and msg.homed:
                        home_complete_x = True
                    if msg.source == 0x22 and msg.homed:
                        home_complete_y = True

        self._apt_cmd(apt.hw_stop_updatemsgs(source=1, dest=0x21))
        self._apt_cmd(apt.hw_stop_updatemsgs(source=1, dest=0x22))
        
        # clear unpacker buffer
        # self.port.reset_input_buffer() #is this better? TODO
        for msg in self.unpacker: pass

    def _wait_for_move(self):
        logging.info('waiting for move')
        self._apt_cmd(apt.hw_start_updatemsgs(source=1, dest=0x21))
        self._apt_cmd(apt.hw_start_updatemsgs(source=1, dest=0x22))

        move_complete_x = False
        move_complete_y = False
        while move_complete_x == False or move_complete_y == False:
            for msg in self.unpacker:
                # if msg.msg == 'mot_get_dcstatusupdate':
                    # logging.info(f"{msg.source=} {msg.position=} {msg.homed=} {msg.velocity=} {msg.channel_enabled=}")
                if msg.msg == 'mot_move_completed':
                    if msg.source == 0x21:
                        move_complete_x = True
                        # logging.info('x move complete')
                    if msg.source == 0x22:
                        move_complete_y = True
                        # logging.info('y move complete')

        self._apt_cmd(apt.hw_stop_updatemsgs(source=1, dest=0x21))
        self._apt_cmd(apt.hw_stop_updatemsgs(source=1, dest=0x22))

        # clear unpacker buffer
        # self.port.reset_input_buffer() #is this better? TODO
        for msg in self.unpacker: pass

    def disable(self):
        logging.info('Disabling stage')
        self._apt_cmd(apt.hw_stop_updatemsgs(source=1, dest=0x21))
        self._apt_cmd(apt.hw_stop_updatemsgs(source=1, dest=0x22))
        self._apt_cmd(apt.mod_set_chanenablestate(source=1, dest=0x21 ,chan_ident=1, enable_state=0))
        self._apt_cmd(apt.mod_set_chanenablestate(source=1, dest=0x22 ,chan_ident=1, enable_state=0))

    def home(self):
        if not self.enabled:
            self.enable()
        self._apt_cmd(apt.mot_move_home(source=1, dest=0x21 ,chan_ident=1))
        self._apt_cmd(apt.mot_move_home(source=1, dest=0x22 ,chan_ident=1))
        if self.port:
            logging.info('Homing stage')
            self._wait_for_home()
        else:
            logging.info('SIMULATING Homing stage')
            time.sleep(6)
        self.pos_x = self.home_pos_x
        self.pos_y = self.home_pos_y
        self.homed = True

    def move_abs(self, x, y):

        # Clamp values between 0 and home x2
        x_lim = min(max(0,x),self.home_pos_x*2)
        y_lim = min(max(0,y),self.home_pos_y*2)

        if (x > self.home_pos_x*2) or x < 0:
            logging.warning(f'X position {x} out of bounds for stage, limiting to {x_lim}mm')
        if (y > self.home_pos_y*2) or y < 0:
            logging.warning(f'X position {y} out of bounds for stage, limiting to {y_lim}mm')

        x_counts = int(x_lim * self.encoder_pos_counts)
        y_counts = int(y_lim * self.encoder_pos_counts)
        self._apt_cmd(apt.mot_move_absolute(source=1, dest=0x21, chan_ident=1, position=x_counts))
        self._apt_cmd(apt.mot_move_absolute(source=1, dest=0x22, chan_ident=1, position=y_counts))
        if self.port:
            logging.info(f'moving to position {x_lim},{y_lim}')
            self._wait_for_move()
        else:
            logging.info(f'SIMULATING moving to position {x_lim},{y_lim}')
            time.sleep(0.5)
        self.pos_x = x
        self.pos_y = y

    def move_vs_ref(self, x, y):

        rads = math.radians(self.slide_rotation)

        if self.ref_bx != 0:
            # correct for rotation
            x = round(x*math.cos(rads) - y*math.sin(rads), 2)
            y = round(y*math.cos(rads) + x*math.sin(rads), 2)

        if x == (self.pos_x-self.ref_ax) and y == (self.pos_y - self.ref_ay):
            logging.debug('already in position, not moving')
            return

        x_abs = self.ref_ax + x
        y_abs = self.ref_ay + y

        # Clamp values between 0 and home x2
        x_lim = min(max(0,x_abs),self.home_pos_x*2)
        y_lim = min(max(0,y_abs),self.home_pos_y*2)

        if (x_abs > self.home_pos_x*2) or x_abs < 0:
            logging.warning(f'X position {x_abs} out of bounds for stage, limiting to {x_lim}mm')
        if (y_abs > self.home_pos_y*2) or y_abs < 0:
            logging.warning(f'Y position {y_abs} out of bounds for stage, limiting to {y_lim}mm')

        x_counts = int(x_lim * self.encoder_pos_counts)
        y_counts = int(y_lim * self.encoder_pos_counts)
        self._apt_cmd(apt.mot_move_absolute(source=1, dest=0x21, chan_ident=1, position=x_counts))
        self._apt_cmd(apt.mot_move_absolute(source=1, dest=0x22, chan_ident=1, position=y_counts))
        if self.port:
            logging.debug(f'moving to position {x},{y} vs reference {self.ref_ax},{self.ref_ay}')
            self._wait_for_move()
        else:
            logging.debug(f'SIMULATING moving to position {x},{y} vs reference {self.ref_ax},{self.ref_ay}')
            time.sleep(2)

        logging.debug(f'position = {x}, {y} after correcting for {self.slide_rotation}deg rotation')
        self.pos_x = self.ref_ax + x
        self.pos_y = self.ref_ay + y

    def get_position(self):
        if self.port:
            self._wait_for_position()
            if self.status_msg_x and self.status_msg_y:
                logging.info(self.status_msg_x)
                logging.info(self.status_msg_y)
        else:
            logging.info(f'SIMULATING random position')
            self.pos_x = random.randint(0,25)
            self.pos_y = random.randint(-10,10)


if __name__ == "__main__":

    # Can use with a context manager (with statement) to ensure serial port gets closed.
    with Thorlabs_Stage() as stage:
        stage.scan_serial_ports()
        stage.connect_serial(serial_port='COM4')
        stage.enable()
        stage.home()
        stage.move_vs_ref(10,20)
        stage.move_vs_ref(10,20)
        stage.move_vs_ref(10,20)

