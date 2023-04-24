import re
import string
import sys
import time
import typing

import serial
from email import message_from_bytes
from serial import Serial


def decode(l):
    if isinstance(l, list):
        return [x.decode('utf-8') for x in l]
    elif isinstance(l, str):
        return l.decode('utf-8')


class Success:
    def __init__(self, feature: str, value: typing.Union[int, float, None, typing.Tuple],
                 axis: typing.Union[None, str, int] = None):
        self.feature = feature
        self.value = value

        self.axis = axis
        if axis is not None:
            if isinstance(axis, int):
                self.axis = "x" if axis == 0 else "y"
            else:
                self.axis = axis

        self.__call__()

    def __call__(self, *args, **kwargs):
        if self.axis is None:
            if self.value is not None:
                print("[SUCCESS] : set {feature} to {val}".format(feature=self.feature, val=self.value))
            else:
                print("[SUCCESS] : {feature}".format(feature=self.feature))
        else:
            print("[SUCCESS] : set {feature} {axis} to {val}".format(feature=self.feature, axis=self.axis,
                                                                     val=self.value))


class Error:
    def __init__(self, feature, response):
        self.feature = feature
        self.response = response
        self.__call__()

    @staticmethod
    def get_error_from_code(code):
        if code == 1:
            return "NO STAGE"
        elif code == 2:
            return "NOT IDLE"
        elif code == 3:
            return "NO DRIVE"
        elif code == 4:
            return "STRING PARSE"
        elif code == 5:
            return "COMMAND NOT FOUND"
        elif code == 6:
            return "INVALID SHUTTER"
        elif code == 7:
            return "NO FOCUS"
        elif code == 8:
            return "VALUE OUT OF RANGE"
        elif code == 9:
            return "INVALID WHEEL"
        elif code == 10:
            return "ARG1 OUT OF RANGE"
        elif code == 11:
            return "ARG2 OUT OF RANGE"
        elif code == 12:
            return "ARG3 OUT OF RANGE"
        elif code == 13:
            return "ARG4 OUT OF RANGE"
        elif code == 14:
            return "ARG5 OUT OF RANGE"
        elif code == 15:
            return "ARG6 OUT OF RANGE"
        elif code == 16:
            return "INCORRECT STATE"
        elif code == 17:
            return "WHEEL NOT FITTED"
        elif code == 18:
            return "QUEUE FULL"
        elif code == 19:
            return "COMPATIBILITY MODE SET"
        elif code == 20:
            return "SHUTTER NOT FITTED"
        elif code == 21:
            return "INVALID CHECKSUM"
        elif code == 60:
            return "ENCODER ERROR"
        elif code == 61:
            return "ENCODER RUN OFF"
        else:
            return "ERROR NOT RECOGNIZED"

    def __call__(self, *args, **kwargs):
        print("[ERROR]", str(self.response))

        if self.response[0] == "E":
            integer_code = int(re.search(r'\d+', self.response).group(0))
            print(integer_code)
            error_code = self.get_error_from_code(code=integer_code)
            print("[ERROR] : {feature} / {error_code}".format(feature=self.feature, error_code=error_code))
        else:
            print("[ERROR] : {feature} / {response}".format(feature=self.feature, response=self.response))


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

        self.acceleration = 99


        self.speed = 100
        self.resolution = 0.1

        self.active_joystick = True

        self._x_position = None
        self._y_position = None

        self._scale = None

        self._speed = None
        self._acceleration = None
        self._s_curve = None

        self._busy_controller = False

        self._step_size = None

        self._home_coords = None

        self._resolution = None

        # print(self.s_curve)

    @property
    def busy_controller(self):
        self.reset_input_buffer()
        self.reset_output_buffer()

        self.write_cmd("$")
        answer = self.cmd_answer()
        if len(answer) >= 1:
            if int(answer) == 3:
                return True
            elif int(answer) == 0:
                return False
            else:
                raise ("New value for busy function : {value}".format(value=answer))
        else:
            return False

    @busy_controller.setter
    def busy_controller(self, value):
        pass

    def cmd_answer(self):
        full_answer = self.read(100).decode().strip()
        return full_answer.split("\r", 1)[0]

    @property
    def s_curve(self):
        self.write_cmd(cmd="SCS")
        self._s_curve = self.cmd_answer()
        return self._s_curve

    @s_curve.setter
    def s_curve(self, value: int):

        self.write_cmd(cmd="SCS,{value}".format(value=value))
        # limit 0 - 100
        response = self.cmd_answer()
        if response == '0':
            Success(feature=sys._getframe().f_code.co_name, value=value)
        else:
            Error(feature=sys._getframe().f_code.co_name, response=response)

    @property
    def acceleration(self):
        self.write_cmd(cmd="SAS")
        self._acceleration = self.cmd_answer()
        return self._acceleration

    @acceleration.setter
    def acceleration(self, value: int) -> None:
        self.write_cmd(cmd="SAS, {acceleration}".format(acceleration=value))
        # limit 0 - 100
        response = self.cmd_answer()
        if int(response) == 0:
            # self._acceleration = value
            Success(feature=sys._getframe().f_code.co_name, value=value)

        else:
            print("error " + sys._getframe().f_code.co_name)

    @property
    def resolution(self):
        self.write_cmd(cmd="RES,s")
        return self.read(100).decode().strip()

    @resolution.setter
    def resolution(self, value: float):
        self.write_cmd(cmd="RES,s,{resolution}".format(resolution=value))
        response = self.cmd_answer()
        if int(response) == 0:
            Success(feature=sys._getframe().f_code.co_name, value=value)
        else:
            print(response)
            print("error " + sys._getframe().f_code.co_name)

    def set_position_as_home(self, previous_coords=None):
        self.write_cmd(cmd="Z")
        if int(self.read(100).decode().strip()) == 0:
            x = self.x_position
            y = self.y_position
            self.home_coords = (x, y)

            if previous_coords is not None:
                Success(feature="home coordinates {coords}".format(coords=previous_coords), value=(x, y))
            else:

                Success(feature="home coordinates", value=(x, y))
        else:
            print("issue in " + sys._getframe().f_code.co_name)

    def set_index_stage(self) -> None:
        """
        This command would normally only be used on first installation of the system.
        The stage moves to limits and sets absolute position to 0,0. The controller will always remember this internally
        as zero even with subsequent uses of Z and P, x , y command.

        """
        self.write_cmd(cmd="SIS")
        if self.read(100).decode().strip() == 'R':
            self.home_coords = (0, 0)
            Success(feature="return to home", value=None)
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
        speed = int(self.read(100).decode().strip())
        if (speed > 0) and (speed <= 100):
            self._speed = speed
            return speed

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
            Success(feature="return to home", value=None)

    @property
    def coords(self) -> str:
        self.write(("P" + "\r").encode())
        pos_coords = self.read(100).decode().strip()
        return pos_coords

    @coords.setter
    def coords(self, value: typing.Tuple[int]):
        cmd = "G, {x}, {y}\r".format(x=value[0], y=value[1])
        self.write_cmd(cmd)
        response = self.cmd_answer()
        if response == 'R':
            Success(feature="position", value=value[0], axis=0)
            Success(feature="position", value=value[1], axis=1)
        else:
            Error(feature="Set coords", response=response)

    @property
    def x_position(self) -> int:
        self.write(("PX" + "\r").encode())
        x_position = self.read(100).decode().strip()
        return int(x_position.strip())

    @x_position.setter
    def x_position(self, value: int):
        cmd = "G, {x}, {y}\r".format(x=value, y=self.y_position).encode()
        self.write(cmd)
        if self.read(100).decode().strip() == 'R':
            Success(feature="position", axis=0, value=value)
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

        return info.decode('unicode-escape').encode('unicode-escape').decode()

    def emergency_stop(self):
        self.write(("K" + "\r").encode())
        response = self.read(100).decode().strip()
        if response == 'R':
            Success(feature="Emergency stop", value=None)

        else:
            print("error")

    def stop_movement(self):
        self.write(("I" + "\r").encode())
        response = self.read(100).decode().strip()
        if response == 'R':
            print("Stop movement")
        else:
            print("error" + response)

    def set_relative_position_steps(self, x: int = 0, y: int = 0) -> None:
        self.write_cmd(cmd="GR, {x_value}, {y_value}".format(x_value=x, y_value=y))
        response = self.cmd_answer()
        if response == 'R':
            Success(feature="x position, y_position", value=("+" + str(x), "+" + str(y)))
            print("Succes moving ({x}, {y}) steps".format(x=x, y=y))
        else:
            print("error" + response)

    def wait4available(self):
        while self.busy_controller:
            time.sleep(0.01)


def real_time_positions_demo():
    prior = PriorController(port="COM12", baudrate=9600, timeout=0.1)
    prior.x_position = 10000
    while prior.busy_controller:
        print(prior.x_position, prior.y_position)
        time.sleep(0.1)
    prior.close()


def return2home_demo():
    prior = PriorController(port="COM12", baudrate=9600, timeout=0.1)
    prior.set_index_stage()
    prior.wait4available()
    print(prior.coords)
    prior.close()

def set_new_home_demo():
    prior = PriorController(port="COM12", baudrate=9600, timeout=0.1)
    prior.set_index_stage()
    prior.wait4available()
    prior.coords = (10000, -10000)
    prior.wait4available()
    print("X, Y, Z POSITIONS : {coords}".format(coords=prior.coords))
    prior.set_position_as_home(previous_coords=(prior.x_position, prior.y_position))
    prior.x_position = 20000
    prior.wait4available()
    print("X POSITION : {X}".format(X=prior.x_position))
    prior.wait4available()
    prior.return2home()
    prior.wait4available()
    print("X, Y, Z POSITIONS : {coords}".format(coords=prior.coords))
    prior.close()


if __name__ == "__main__":
    # return2home_demo()
    # set_new_home_demo()

    prior = PriorController(port="COM12", baudrate=9600, timeout=0.1)
    prior.emergency_stop()
    prior.speed = 10
    prior.set_relative_position_steps(x=10000)
    prior.wait4available()
    prior.speed = 100
    prior.set_relative_position_steps(x=-10000)
    prior.close()
