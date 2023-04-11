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
    Y max = -80073

    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.std_mode = self.standard_mode()
        self.peripherals_info = self.initialization()

        self.active_joystick = True

        self._x_position = None
        self._y_position = None


    def standard_mode(self):
        self.write(('COMP {value}\r'.format(value=0)).encode())

        if int(self.read(100).decode().strip()) == 0:
            return True
        else:
            return False


    @property
    def active_joystick(self) -> bool:
        return self.active_joystick

    @property
    def x_position(self) -> int:
        self.write(("P" + "\r").encode())
        x_position = self.read(100).decode().strip().split(',')[0]
        return int(x_position.strip())


    @x_position.setter
    def x_position(self, value: int):
        cmd = "G, {x}, {y}\r".format(x=value, y=self.y_position).encode()
        self.write(cmd)
        if self.read(100).decode().strip() == 'R':
            self._x_position = int(value)

    @property
    def y_position(self) -> int:
        self.write(("P" + "\r").encode())
        y_position = self.read(100).decode().strip().split(',')[1]
        return int(y_position.strip())

    @y_position.setter
    def y_position(self, value: int):
        cmd = "G, {x}, {y}\r".format(x=self.x_position, y=value).encode()
        self.write(cmd)
        if self.read(100).decode().strip() == 0:
            self._y_position = int(value)



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
        info = self.read(100)
        return info.decode('unicode-escape').encode('unicode-escape').decode()


if __name__ == "__main__":
    prior = Serial(port="COM12", baudrate=9600, timeout=0.1)
    prior.write(("G, 0, 10000 " + "\r").encode())
    print(prior.read(100).decode().strip())

    prior.write(("P" + "\r").encode())
    print(prior.read(100).decode().strip())

    # prior = PriorController(port="COM12", baudrate=9600, timeout=0.1)
    # print(prior.std_mode)
    # print(prior.x_position)
    # prior.x_position = 0
    # print(prior.x_position)


    # print(prior.x_position)
    # prior.x_position = 1

    # print(prior.x_position)
    # prior.x_position = 10000
    # print(prior.x_position)

    # prior.write(("J" + "\r").encode())
    #
    # print(int(prior.read(100).decode().strip()) == 0)
    #     # print("joy")
    #
    # prior.write(("PX, 1000" + "\r").encode())
    # print(int(prior.read(100).decode().strip()) == 0)
    #
    # prior.write(("G, 10000, 10000" + "\r").encode())
    # print(prior.read(100).decode())
    # print(prior.x_position)

    # print(prior.y_position)
    # prior.x_position = 10000
    # print(prior.x_position)

    # # prior.write(("G 100 200 "+ "\r").encode())
    # prior.write(("I"+ "\r").encode())
    # print(prior.read(100).decode())
    #
    # prior.write(("PS 1 1"+ "\r").encode())
    # print(prior.read(100).decode())
    #
    # prior.write(("PS" + "\r").encode())
    # print(prior.read(100).decode())
    #
    # prior.write(("PX 10" + "\r").encode())
    # print(prior.read(100).decode())

    # prior.write(("J" + "\r").encode())
    #
    # #
    # prior.write(("PY" + "\r").encode())
    # # prior.write(("G, 10000, 10000" + "\r").encode())
    # # print(prior.read(100).decode())
    #
    # print(prior.read(100).decode())
    #
    # prior.write(("?" + "\r").encode())
    # # print(decode(prior.readlines(100)))
    # a = prior.read(100)
    # # print(a.replace('\r', '\n'))
    # x = a.decode('unicode-escape').encode('unicode-escape').decode()
    # print(x)

    prior.close()
