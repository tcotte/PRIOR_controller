import keyboard

from main import PriorController


def set_x_position():
    prior = PriorController(port="COM12", baudrate=9600, timeout=0.1)
    print(prior.x_position)
    prior.x_position = -10000
    print(prior.x_position)
    prior.close()


def set_y_position():
    prior = PriorController(port="COM12", baudrate=9600, timeout=0.1)
    # print(prior.y_position)
    prior.y_position = -20000
    print(prior.y_position)
    prior.close()


def return2home_demo():
    prior = PriorController(port="COM12", baudrate=9600, timeout=0.1)
    prior.set_index_stage()
    # prior.wait4available()
    print(prior.coords)
    prior.close()


def report_limit_switch():
    prior = PriorController(port="COM12", baudrate=9600, timeout=0.1)
    while True:
        prior.write_cmd("LMT")
        print(prior.cmd_answer())

        if keyboard.is_pressed("q"):
            print("q pressed, ending loop")
            prior.close()
            break


if __name__ == "__main__":
    prior = PriorController(port="COM12", baudrate=9600, timeout=0.1)
    prior.go2limit_switch()
    prior.set_position_as_home()
    prior.close()
    # report_limit_switch()

    # prior = PriorController(port="COM12", baudrate=9600, timeout=0.1)
    # prior.set_index_stage()
    # prior.close()

    # return2home_demo()

    # prior = PriorController(port="COM12", baudrate=9600, timeout=0.1)
    # prior.write_cmd("M")
    # prior.looking_for_position(feature="Restore index of stage", axis="ALL", value=None)
    # prior.close()
