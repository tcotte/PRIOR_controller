from time import sleep
from threading import Thread, Event
from app.ui import locked_thread, lock
from main import PriorController


class RefreshPriorCoordsThread(Thread):
    def __init__(self, prior_device, event, period: float = 0.3):
        super().__init__()
        self.prior = prior_device
        self.coords = self.get_coords()
        self.stopped = event
        self.period = period
        self.running = True

    # override the run function
    def run(self):
        while self.running:
            if not self.prior.busy:
                # display a message
                # self.coords = self.get_coords()
                # self.coords = [self.prior.x_position, self.prior.y_position]
                sleep(self.period)
                self.coords = self.get_coords()
            # print("run")
            # print([self.prior.x_position, self.prior.y_position])

    def stop(self):
        self.running = False

    # @locked_thread
    def get_coords(self):
        lock.acquire(blocking=True)
        response_coords = self.prior.coords
        # print("get coords")
        # print(response_coords)
        lock.release()
        try:
            return [int(x) for x in response_coords.split(",")]

        except:
            # if we raise an error, we return the previous coordinates value
            print("error with report_xyz_values function / coords value = {}".format(response_coords))
            return self.coords



        # return [self.prior.x_position, self.prior.y_position]


if __name__ == "__main__":
    prior = PriorController(port="COM13", baudrate=9600, timeout=0.05)
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
