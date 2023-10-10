from main import PriorController

X_LIMIT = 288000  # microscope's X limit (in µm)
Y_LIMIT = 80000  # microscope's Y limit (in µm)

class SerialSingleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SerialSingleton, cls).__new__(cls)
            # Initialize your Serial instance here
            cls._instance.serial = PriorController(port="COM15", baudrate=9600, timeout=0.1)  # Replace Serial() with your actual Serial class instantiation
        return cls._instance