import sys
import typing

import serial
from email import message_from_bytes
from serial import Serial


def decode(l):
    if isinstance(l, list):
        return [x.decode('utf-8') for x in l]
    elif isinstance(l, str):
        return l.decode('utf-8')


class PriorController(serial.Serial):
    """
    X max = 123 289
            -122 895
    Y max = -80073

    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # self.std_mode = self.standard_mode()
        self.peripherals_info = self.initialization()
        self.set_index_stage()

        self.active_joystick = True

        self._x_position = None
        self._y_position = None

        self._scale = None

        self._speed = None

        self._step_size = None

        self._home_coords = None

    def set_position_as_home(self):
        self.write_cmd(cmd="Z")
        if int(self.read(100).decode().strip()) == 0:
            x = self.x_position
            y = self.y_position
            self.home_coords = (x, y)
        else:
            print("issue in " + sys._getframe().f_code.co_name)


    def set_index_stage(self):
        self.write_cmd(cmd="SIS")
        if self.read(100).decode().strip() == 'R':
            print("set Init")
            self.home_coords = (0, 0)
        else:
            print("error " + sys._getframe().f_code.co_name)

    @property
    def home_coords(self):
        return self._home_coords

    @home_coords.setter
    def home_coords(self, value):
        self._home_coords = (value[0], value[1])

    def write_cmd(self, cmd: str):
        self.write((cmd + "\r").encode())

    @property
    def step_size(self):
        self.write_cmd(cmd="X")
        return self.read(100).decode().strip()

    @step_size.setter
    def step_size(self, value: typing.Tuple):
        self.write_cmd(cmd="X , {u}, {v}".format(u=value[0], v=value[1]))
        if int(self.read(100).decode().strip()) == 0:
            print("Change step size success")
        else:
            print("Error")

    def standard_mode(self):
        self.write(('COMP {value}\r'.format(value=0)).encode())

        if int(self.read(100).decode().strip()) == 0:
            return True
        else:
            return False

    @property
    def speed(self):
        self.write(("SMS" + "\r").encode())
        speed = self.read(100).decode().strip()
        return int(speed.strip())

    @speed.setter
    def speed(self, value):
        cmd = "SMS, {speed}\r".format(speed=value).encode()
        self.write(cmd)
        if self.read(100).decode().strip() == 'R':
            pass

    @property
    def active_joystick(self) -> bool:
        return self.active_joystick

    def return2home(self):
        cmd = "M\r".encode()
        self.write(cmd)
        if self.read(100).decode().strip() == 'R':
            pass

    @property
    def coords(self) -> str:
        self.write(("P" + "\r").encode())
        pos_coords = self.read(100).decode().strip()
        return pos_coords

    @coords.setter
    def coords(self, value: typing.Tuple[int]):
        cmd = "G, {x}, {y}\r".format(x=value[0], y=value[1]).encode()
        print(cmd)
        self.write(cmd)
        if self.read(100).decode().strip() == 'R':
            print("ok")
        else:
            print("error")

    @property
    def x_position(self) -> int:
        self.write(("PX" + "\r").encode())
        x_position = self.read(100).decode().strip()
        print(x_position)
        return int(x_position.strip())

    @x_position.setter
    def x_position(self, value: int):
        cmd = "G, {x}, {y}\r".format(x=value, y=self.y_position).encode()
        print(cmd)
        self.write(cmd)
        if self.read(100).decode().strip() == 'R':
            print("Succes moving to {x}, {y}".format(x=value, y=self.y_position))
        else:
            print("Error")
        #     self._x_position = int(value)

    @property
    def y_position(self) -> int:
        self.write(("PY" + "\r").encode())
        y_position = self.read(100).decode()
        return int(y_position.strip())

    @y_position.setter
    def y_position(self, value: int):
        cmd = "G, {x}, {y}\r".format(x=self.x_position, y=value).encode()
        self.write(cmd)
        if self.read(100).decode().strip() == 'R':
            pass
        # if self.read(100).decode().strip() == 0:
        #     self._y_position = int(value)

    @active_joystick.setter
    def active_joystick(self, value: bool) -> None:
        if value:
            self.write(("J" + "\r").encode())
            if self.read(100).decode() == 0:
                self._active_joystick = True
        else:
            self.write(("H" + "\r").encode())
            if self.read(100).decode() == 0:
                self._active_joystick = False

    def initialization(self):
        """
        information about the peripherals connected currently to the controller
        :return:
        """
        self.write(("?" + "\r").encode())
        info = self.read(1000)
        print(info.decode('unicode-escape').encode('unicode-escape').decode())
        return info.decode('unicode-escape').encode('unicode-escape').decode()

    def emergency_stop(self):
        self.write(("K" + "\r").encode())
        response = self.read(100).decode().strip()
        if response == 'R':
            print("Emergency stop success")

        else:
            print("error")

    def stop_movement(self):
        self.write(("I" + "\r").encode())
        response = self.read(100).decode().strip()
        if response == 'R':
            print("Stop movement")
        else:
            print("error" + response)


if __name__ == "__main__":
    # prior = Serial(port="COM12", baudrate=9600, timeout=0.1)
    # prior.write(("G, 10000, 10000" + "\r").encode())
    # print(prior.read(100).decode().strip())
    #
    # prior.write(("P" + "\r").encode())
    # print(prior.read(100).decode().strip())
    #
    # prior.write(("X" + "\r").encode())
    # print(prior.read(100).decode().strip())

    prior = PriorController(port="COM12", baudrate=9600, timeout=0.1)
    # prior.stop_movement()
    prior.step_size = (1, 1)

    print(prior.coords)
    # print(prior.speed)
    prior.speed = 100

    # prior.coords = (1000000, -100000)

    # prior.set_position_as_home()
    print(prior.home_coords)
    print(prior.coords)


    prior.close()
