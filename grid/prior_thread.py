from time import sleep
from threading import Thread

# custom thread class
from main import PriorController


class CustomThread(Thread):
    def __init__(self, prior_device):
        super().__init__()
        self.prior = prior_device

    # override the run function
    def run(self):
        while True:
            # block for a moment
            sleep(0.1)
            # display a message
            print(self.prior.coords)


if __name__ == "__main__":
    prior = PriorController(port="COM13", baudrate=9600, timeout=0.1)
    # prior.coords = (10000, 5000)
    prior.set_index_stage()
    # create the thread
    thread = CustomThread(prior_device=prior)
    # thread.prior = prior
    # start the thread
    thread.start()
    # wait for the thread to finish
    print('Waiting for the thread to finish')
    thread.join()
