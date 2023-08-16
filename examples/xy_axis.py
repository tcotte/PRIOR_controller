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

if __name__ == "__main__":
    set_y_position()
    # return2home_demo()

    # prior = PriorController(port="COM12", baudrate=9600, timeout=0.1)
    # prior.write_cmd("M")
    # prior.looking_for_position(feature="Restore index of stage", axis="ALL", value=None)
    # prior.close()
