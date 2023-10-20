import time
import typing

from serial import Serial
from serial.tools import list_ports


class PriorSearcher:
    def __init__(self, baudrate_list: typing.Union[None, typing.List[int]] = None):
        """
        The aim of this class is to detect right COM PORT and baud rate to communicate with PRIOR ProScan II.
        :param baudrate_list: list of communication speeds tested to communicate with PRIOR.
                              if this parameter is None -> try all standard baud rates.
        """
        # detect available com ports
        self.ports = list_ports.comports()

        self.baudrate_list = baudrate_list
        if self.baudrate_list is None:
            self.baudrate_list = [110, 300, 600, 1200, 2400, 4800, 9600, 14400, 19200, 38400, 57600, 115200]

        self.port, self.baudrate = self.find_prior()

    def find_prior(self) -> [typing.Union[str, None], typing.Union[int, None]]:
        """
        This function iterates over all COM ports and all baud rates. During these iterations, it tries to communicate
        with the Prior thanks to Serial communication. When the communication is established, the script
        launches an initialization writing by UART. The script writes "SERIAL", if the communicating device is the
        Prior, it has to return the serial number of the device (otherwise it returns empty encoded string). One thing
        remains mysterious: if the com port was tested with one "wrong" baud rate before 9600 (right baud rate to ensure
        communication with Prior), the device return encoded "R" when the script ask for the serial number on 9600
        bauds.
        :return: port com, baud rate
        - port com : like "COM3" if a right communication was found else None.
        - baud rate : baud rate if a right communication was found else None.
        """
        for port, _, _ in self.ports:
            for baudrate in self.baudrate_list:
                try:
                    serial = Serial(port=port, baudrate=baudrate)
                    serial.timeout = 0.1
                    cmd = "SERIAL"

                    serial.write((cmd + "\r").encode())
                    serial_response = serial.readline()
                    serial_number = serial_response.decode().strip()

                    if serial_number.isdigit() or serial_number == "R":
                        serial.close()
                        return port, baudrate

                    serial.close()
                    del serial

                except Exception as e:
                    print(str(e))

        print("We didn't find any COM PORT which is managing lights.")
        return None, None


if __name__ == '__main__':
    start = time.time()
    lc = PriorSearcher(baudrate_list=[9600])
    print(time.time() - start)
    print(lc.port)

    # try:
    #     lm = LightManager(port=lc.port, baudrate=lc.baudrate, list_channels=[1, 2, 3])
    #     print(lc.port)
    #     lm.switch_on([0, 255, 0])
    #     lm.switch_off()
    #
    # except Exception as e:
    #     print(str(e))
