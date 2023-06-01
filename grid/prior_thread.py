from time import sleep
from threading import Thread, Event

# custom thread class
from app.ui import locked_thread
from main import PriorController


class RefreshPriorCoordsThread(Thread):
    def __init__(self, prior_device, event, period: float = 0.2):
        super().__init__()
        self.prior = prior_device
        self.coords = [self.prior.x_position, self.prior.y_position]
        self.stopped = event
        self.period = period

    # override the run function
    def run(self):
        while not self.stopped.wait(self.period):
            # display a message
            # self.coords = self.get_coords()
            self.coords = [self.prior.x_position, self.prior.y_position]

    @locked_thread
    def get_coords(self):
        return [self.prior.x_position, self.prior.y_position]


if __name__ == "__main__":
    prior = PriorController(port="COM13", baudrate=9600, timeout=0.1)
    # prior.coords = (10000, 5000)
    prior.set_index_stage()
    # create the thread
    stop_flag = Event()
    thread = RefreshPriorCoordsThread(prior_device=prior, event=stop_flag)
    # thread.prior = prior
    # start the thread
    thread.start()

    # wait for the thread to finish
    print('Waiting for the thread to finish')
    thread.join()

    # stop_flag.set()
