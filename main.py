import re
import sys
import threading
import time
import typing

import serial

X_DIRECTION = 1
Y_DIRECTION = 1


def decode(l):
    if isinstance(l, list):
        return [x.decode('utf-8') for x in l]
    elif isinstance(l, str):
        return l.decode('utf-8')


class Success:
    def __init__(self, feature: str, value: typing.Union[int, float, None, typing.Tuple]= None,
                 axis: typing.Union[None, str, int] = None):
        self.feature = feature
        self.value = value

        self.axis = axis
        if axis is not None:
            if isinstance(axis, int):
                if axis == 0:
                    self.axis = "X"
                elif axis == 1:
                    self.axis = "Y"
                else:
                    self.axis = "Z"

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
        if len(self.response) > 0:
            if self.response[0] == "E":
                integer_code = int(re.search(r'\d+', self.response).group(0))
                print(integer_code)
                error_code = self.get_error_from_code(code=integer_code)
                print("[ERROR] : {feature} / {error_code}".format(feature=self.feature, error_code=error_code))
            else:
                print("[ERROR] : {feature} / {response}".format(feature=self.feature, response=self.response))
        else:
            print("[ERROR] : {feature} / {response}".format(feature=self.feature, response="Empty response message"))


class ZAxis:
    def __init__(self, parent):
        self.prior_controller = parent

        self._z_position = None
        self.speed = 100
        self.acceleration = 70

    @property
    def speed(self):
        self.prior_controller.write_cmd(cmd="SMZ")
        answer = self.prior_controller.cmd_answer()
        try:
            answer = int(answer)
        except:
            Error(feature=sys._getframe().f_code.co_name, response=answer)
        assert 4 <= answer <= 100, "Speed value is not in range [4 - 100]"
        return answer

    @speed.setter
    def speed(self, value: int):
        assert 4 <= value <= 100, "Speed value should to be in range [4 - 100]"
        cmd = "SMZ, {z}".format(z=value)
        self.prior_controller.write_cmd(cmd)

        answer = self.prior_controller.cmd_answer()
        if answer == "0":
            Success(feature=sys._getframe().f_code.co_name, axis=2, value=value)
        else:
            Error(feature=sys._getframe().f_code.co_name, response=answer)

    @property
    def acceleration(self):
        self.prior_controller.write_cmd(cmd="SAZ")
        answer = self.prior_controller.cmd_answer()
        try:
            answer = int(answer)
        except:
            Error(feature=sys._getframe().f_code.co_name, response=answer)
        assert 4 <= answer <= 100, "Acceleration value is not in range [4 - 100]"
        return answer

    @acceleration.setter
    def acceleration(self, value: int):
        assert 4 <= value <= 100, "Acceleration value should to be in range [4 - 100]"
        cmd = "SAZ, {z}".format(z=value)
        self.prior_controller.write_cmd(cmd)

        answer = self.prior_controller.cmd_answer()
        if answer == "0":
            Success(feature=sys._getframe().f_code.co_name, axis=2, value=value)
        else:
            Error(feature=sys._getframe().f_code.co_name, response=answer)


    @property
    def z_position(self) -> int:
        self.prior_controller.write_cmd("PZ")
        z_position = self.prior_controller.cmd_answer()
        try:
            return int(z_position.strip())
        except:
            if z_position == "0,0,0":
                return 0
            else:
                Error(feature=sys._getframe().f_code.co_name, response=z_position)

    @z_position.setter
    def z_position(self, value: int):
        cmd = "V, {z}\r".format(z=value).encode()
        self.prior_controller.write(cmd)

        self.prior_controller.looking_for_position(feature=sys._getframe().f_code.co_name, axis=2, value=value)

    def move_relative_down(self, value):
        cmd = "D, {z}".format(z=value)
        self.prior_controller.write_cmd(cmd)

        self.prior_controller.looking_for_position(feature=sys._getframe().f_code.co_name, axis="Z", value=value)

    def move_relative_up(self, value):
        cmd = "U, {z}".format(z=value)
        self.prior_controller.write_cmd(cmd)

        self.prior_controller.looking_for_position(feature=sys._getframe().f_code.co_name, axis="Z", value=value)



class PriorController(serial.Serial):
    """
    X max = 123 289
            -122 895
    Y max = -80073

    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # self.std_mode = self.standard_mode()
        self._write_lock = threading.Lock()
        self._read_lock = threading.Lock()

        self.peripherals_info = self.initialization()

        self.acceleration = 10
        self.speed = 70
        self.resolution = 0.1

        self._active_joystick = True

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

        self.set_x_direction(direction=X_DIRECTION)
        self.set_y_direction(direction=Y_DIRECTION)

        self.z_controller = ZAxis(parent=self)

        self.busy = False

        # print(self.s_curve)

    def move_relative_down(self, value):
        cmd = "D, {z}".format(z=value)
        self.write_cmd(cmd)

        self.looking_for_position(feature=sys._getframe().f_code.co_name, axis="Z", value=value)

    def move_relative_up(self, value):
        cmd = "U, {z}".format(z=value)
        self.write_cmd(cmd)
        self.looking_for_position(feature=sys._getframe().f_code.co_name, axis="Z", value=value)

    @property
    def busy_controller(self):
        self.reset_input_buffer()
        self.reset_output_buffer()

        self.write_cmd("$")
        answer = self.cmd_answer()
        if len(answer) >= 1:
            if answer == '3':
                return True
            elif answer == '0':
                return False
            elif answer == 'R':
                return False
            elif answer == '3\rR':
                return False
            else:
                raise ("New value for busy function : {value}".format(value=answer))
        else:
            return False

    @busy_controller.setter
    def busy_controller(self, value):
        pass

    def cmd_answer(self):
        # full_answer = self.readline().decode().strip()
        full_answer = self.read_until(b'\r').decode().strip()
        print("ANSWER     ", full_answer)
        return full_answer
        # self.readline().decode().strip()
        # return full_answer.split("\r", 1)[0]

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
        self._acceleration = int(self.cmd_answer())
        return self._acceleration

    @acceleration.setter
    def acceleration(self, value: int) -> None:
        self.write_cmd(cmd="SAS, {acceleration}".format(acceleration=value))
        # limit 0 - 100
        response = self.cmd_answer()
        if response == '0':
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
            Success(feature = sys._getframe().f_code.co_name, value=value)
        else:
            print("error " + sys._getframe().f_code.co_name)

    def set_position_as_home(self):
        self.write_cmd(cmd="Z")
        answer = self.cmd_answer()
        if answer == '0':
            Success(feature="New home coordinates", value=(self._x_position, self._y_position, self.z_controller._z_position))
        else:
            Error(feature=sys._getframe().f_code.co_name, response=answer)

    def set_index_stage(self) -> None:
        """
        This command would normally only be used on first installation of the system.
        The stage moves to limits and sets absolute position to 0,0. The controller will always remember this internally
        as zero even with subsequent uses of Z and P, x , y command.

        """
        ##### a chercher
        self.write_cmd(cmd="SIS")

        self.looking_for_position(feature=sys._getframe().f_code.co_name, axis="ALL", value=None)

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
        response = self.cmd_answer()
        speed = int(response)

        if (speed >= 0) and (speed <= 100):
            self._speed = speed
            return speed

    @speed.setter
    def speed(self, value):
        # https://stackoverflow.com/questions/74182624/two-threads-reading-writing-on-the-same-serial-port-at-the-same-time
        cmd = "SMS, {speed}".format(speed=value)
        self.write_cmd(cmd)

        response = self.cmd_answer()
        if response == '0':
            Success(feature="speed", value=value)
        else:
            Error(feature=sys._getframe().f_code.co_name, response=response)

    @property
    def active_joystick(self) -> bool:
        return self._active_joystick

    def return2home(self):
        cmd = "M"
        self.write_cmd(cmd)

        self.looking_for_position(feature=sys._getframe().f_code.co_name, axis="ALL", value=None)

    @property
    def coords(self) -> str:
        self.write_cmd("P")
        pos_coords = self.cmd_answer()
        return pos_coords

    @coords.setter
    def coords(self, value: typing.Tuple[int]):
        cmd = "G, {x}, {y}".format(x=value[0], y=value[1])
        self.write_cmd(cmd)

        self.looking_for_position(feature=sys._getframe().f_code.co_name, axis="XY", value=value)

        # response = self.cmd_answer()
        # if response == 'R':
        #     Success(feature="position", value=value[0], axis=0)
        #     Success(feature="position", value=value[1], axis=1)
        # else:
        #     Error(feature="Set coords", response=response)

    @property
    def x_position(self) -> int:
        self.write(("PX" + "\r").encode())
        x_position = self.cmd_answer()
        try:
            return int(x_position.strip())
        except:
            if x_position == "0,0,0":
                return 0
            else:
                Error(feature=sys._getframe().f_code.co_name, response=x_position)

    @x_position.setter
    def x_position(self, value: int):
        cmd = "G, {x}, {y}".format(x=value, y=self._y_position)
        self.write_cmd(cmd=cmd)

        self.looking_for_position(feature=sys._getframe().f_code.co_name, axis=0, value=value)

    def looking_for_position(self, feature, axis, value):
        self.busy = True
        time.sleep(5 * self.timeout)
        answer = self.cmd_answer()
        while 'R' not in answer:
            self.busy = True
            answer = self.cmd_answer()

        if answer == 'R':
            Success(feature=feature, axis=axis, value=value)
        else:
            Error(feature=feature, response=answer)

        self.busy = False

    @property
    def y_position(self) -> int:
        self.write(("PY" + "\r").encode())
        y_position = self.cmd_answer()
        try:
            return int(y_position.strip())
        except:
            if y_position == "0,0,0":
                return 0
            else:
                Error(feature=sys._getframe().f_code.co_name, response=y_position)

    @y_position.setter
    def y_position(self, value: int):
        cmd = "G, {x}, {y}".format(x=self._x_position, y=value)
        self.write_cmd(cmd)

        self.looking_for_position(feature=sys._getframe().f_code.co_name, axis=1, value=value)
        # if self.cmd_answer() == 'R':
        #     Success(feature="position", axis=1, value=value)
        # else:
        #     print("Error")

    @active_joystick.setter
    def active_joystick(self, value: bool) -> None:
        if value:
            self.write_cmd("J")
            if self.cmd_answer() == 0:
                self._active_joystick = True
        else:
            self.write_cmd("H")
            if self.cmd_answer() == 0:
                self._active_joystick = False

    def initialization(self):
        """
        information about the peripherals connected currently to the controller
        :return:
        """
        self.write(("?" + "\r").encode())
        info = self.read(1000)
        print(info)

        return info.decode('unicode-escape').encode('unicode-escape').decode()

    def emergency_stop(self):
        self.flushOutput()
        self.write_cmd("K")
        response = self.cmd_answer()

        if response == 'R' or response == '':
            Success(feature="Emergency stop", value=None)

        else:
            Error(feature=sys._getframe().f_code.co_name, response=response)

    def stop_movement(self):
        self.write(("I" + "\r").encode())
        response = self.read(100).decode().strip()
        if response == 'R':
            print("Stop movement")
        else:
            print("error" + response)

    def set_relative_position_steps(self, x: int = 0, y: int = 0) -> None:
        if x < 0 or y < 0:
            print("inverse")

        if x != 0:
            axis = "X"
            value = x
        else:
            axis = "Y"
            value = y

        self.write_cmd(cmd="GR, {x_value}, {y_value}".format(x_value=x, y_value=y))
        # response = self.cmd_answer()
        # if response == 'R':
        #     Success(feature="x position, y_position", value=("+" + str(x), "+" + str(y)))
        # else:
        #     Error(feature=sys._getframe().f_code.co_name, response=response)

        self.looking_for_position(feature=sys._getframe().f_code.co_name, axis=axis, value=value)

    def wait4available(self):
        while self.busy_controller:
            time.sleep(0.01)

    def set_x_direction(self, direction):
        self.write_cmd(cmd="XD, {}".format(direction))
        response = self.cmd_answer()
        if response == '0':
            Success(feature="Direction", value=direction, axis="X")
        else:
            Error(feature=sys._getframe().f_code.co_name, response=response)

    def set_y_direction(self, direction):
        self.write_cmd(cmd="YD, {}".format(direction))
        response = self.cmd_answer()
        if response == '0':
            Success(feature="Direction", value=direction, axis="Y")
        else:
            Error(feature=sys._getframe().f_code.co_name, response=response)


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
    prior = PriorController(port="COM13", baudrate=9600, timeout=0.1)
    prior.set_index_stage()
    prior.wait4available()
    prior.coords = (10000, 10000)
    prior.wait4available()
    print("X, Y, Z POSITIONS : {coords}".format(coords=prior.coords))
    prior.set_position_as_home()
    prior.x_position = 20000
    prior.wait4available()
    print("X POSITION : {X}".format(X=prior.x_position))
    prior.wait4available()
    prior.return2home()
    prior.wait4available()
    print("X, Y, Z POSITIONS : {coords}".format(coords=prior.coords))
    prior.close()


def set_new_speed_demo():
    prior = PriorController(port="COM12", baudrate=9600, timeout=0.1)
    prior.emergency_stop()
    prior.set_index_stage()

    prior.acceleration = 1
    prior.speed = 70
    prior.set_relative_position_steps(x=10000)
    # print(prior.speed)
    while prior.busy_controller:
        print(prior.speed)
        time.sleep(0.01)
    # prior.set_relative_position_steps(x=10000)
    # prior.wait4available()
    # prior.acceleration = 100
    #
    # prior.speed = 100
    # prior.set_index_stage()
    prior.close()


if __name__ == "__main__":
    # return2home_demo()
    set_new_home_demo()
    # set_new_speed_demo()
