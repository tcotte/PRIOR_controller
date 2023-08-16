import time

from main import PriorController


def z_axis():
    prior = PriorController(port="COM12", baudrate=9600, timeout=0.1)
    print(prior.z_controller.z_position)
    prior.z_controller.z_position = 10000

    prior.close()


def move_down():
    prior = PriorController(port="COM12", baudrate=9600, timeout=0.1)
    print(prior.z_controller.z_position)
    prior.z_controller.move_relative_down(3000)
    print(prior.z_controller.z_position)

    prior.close()


def move_up():
    prior = PriorController(port="COM12", baudrate=9600, timeout=0.1)
    print(prior.z_controller.z_position)
    prior.z_controller.move_relative_up(3000)
    # time.sleep(0.1)
    print(prior.z_controller.z_position)

    prior.close()


def get_z_axis_speed():
    prior = PriorController(port="COM12", baudrate=9600, timeout=0.1)
    print("####################################################################")
    print(prior.z_controller.speed)
    prior.z_controller.speed = 29
    print(prior.z_controller.speed)
    prior.close()


if __name__ == "__main__":
    # z_axis()
    # move_down()
    get_z_axis_speed()
