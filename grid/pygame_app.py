import threading
import time
import typing
from asyncio import Event

import numpy as np
import pygame
import serial
from pygame import QUIT
from pygame.locals import RESIZABLE, Rect

from grid.grid_movement import GridMovement, Course
from grid.prior_thread import RefreshPriorCoordsThread
from main import PriorController

APP_SIZE = (700, 500)
GRID = (1500, 1000)  # width, height -> 1 pixel equals 10 µm
IMAGE_SIZE = (100, 100)  # width, height -> camera image size
RATIO = 250  # 1 pixel equals 25 µm
X_LIMIT = 288000  # microscope's X limit (in µm)
Y_LIMIT = 80000  # microscope's Y limit (in µm)

REFRESH_PRIOR_POSITION = pygame.USEREVENT + 1


class Sprite:
    def __init__(self, prior_controller: serial.Serial, size=None):
        self.prior = prior_controller
        self.parent = None
        self.size = size

        # self.velocity = np.array([1.5, 0.5], dtype=float)

        self.angle = 0
        self.angular_velocity = 0

        self.color = 'red'

        # if file:
        #     self.image = pygame.image.load(file)
        #     if self.size:
        #         self.image = pygame.transform.scale(self.image, size)
        #         self.rect.size = self.image.get_size()
        # else:

        stop_flag = Event()
        # self.thread = RefreshPriorCoordsThread(prior_device=prior_controller, event=stop_flag, period=0.5)
        # self.thread.start()

        self.position = self.get_position()
        self.rect = Rect(self.position, IMAGE_SIZE)

        self.image = pygame.Surface(self.rect.size)
        self.image.fill(self.color)
        # self.image0 = self.image.copy()

    def set_pos(self, pos):
        if None not in pos:
            self.position = np.array(pos, dtype=float)
            self.rect.left = pos[0]
            self.rect.top = pos[1]

    #
    # def set_angle(self, angle):
    #     self.angle = angle
    #     self.image = pygame.transform.rotate(self.image0, self.angle)
    #     self.rect.size = self.image.get_size()

    def do(self, event):
        pass

    def update(self):
        self.position = self.get_position()
        self.set_pos(pos=self.position)

    def get_position(self):
        # time.sleep(1)


        # x_pos, y_pos, _ = self.thread.coords
        response_coords = self.prior.coords

        try:
            coords = [int(x) for x in response_coords.split(",")]

        except:
            # if we raise an error, we return the previous coordinates value
            print("error with report_xyz_values function / coords value = {}".format(response_coords))
            coords = 0, 0, 0
        x_pos, y_pos, _ = coords
        print("thread pos {} {}".format(x_pos, y_pos))

        if x_pos is not None:
            x_pos = round(float(x_pos) / RATIO)
        if y_pos is not None:
            y_pos = round(float(y_pos) / RATIO)

        return x_pos, y_pos

    # def move(self):
    #     self.position += self.velocity
    #
    #     if self.angular_velocity:
    #         self.angle += self.angular_velocity
    #         self.image = pygame.transform.rotate(self.image0, self.angle)
    #         self.rect.size = self.image.get_size()
    #
    #     self.rect.center = self.position

    def draw(self, surf):
        surf.blit(self.image, self.rect)

    def __del__(self):
        print("stop thread")
        # self.thread.stop()

    # def distance(self, other):
    #     distance = self.position - other.position
    #     distance *= distance
    #     d = np.sqrt(np.sum(distance))
    #     return d


class App:
    def __init__(self, caption: str, prior: serial, grid: typing.List):

        pygame.init()
        pygame.display.set_caption(caption)

        self.prior = prior
        self.grid = grid

        self.flags = RESIZABLE
        # self.flags = []
        self.size = GRID
        self.screen = pygame.display.set_mode(APP_SIZE)
        self.running = True
        self.updating = True
        self.objects = []
        self.bg_color = 'black'
        self.load_bg_game()
        # self.image = pygame.Surface(self.size)
        # self.image.fill(self.bg_color)
        self.rect = self.image.get_rect()
        self.key_cmd = {}

        # stop_flag = Event()
        # self.thread = RefreshPriorCoordsThread(prior_device=prior_controller, event=stop_flag)
        # self.thread.start()

        # pygame.time.set_timer(REFRESH_PRIOR_POSITION, 100)

        self.prior_visualisation = Sprite(prior_controller=self.prior, size=IMAGE_SIZE)
        self.add(self.prior_visualisation)

    def load_bg_game(self):
        self.image = pygame.Surface(self.size)
        self.image.fill(self.bg_color)
        self.rect = self.image.get_rect()

    # def load_image(self, file):
    #     self.image = pygame.image.load(file).convert()
    #     self.rect = self.image.get_rect()
    #     self.screen = pygame.display.set_mode(self.rect.size, self.flags)

    def run(self):
        self.update()
        self.draw()
        while self.running:
            pygame.time.delay(1000)
            for event in pygame.event.get():
                self.do(event)



            self.grid.pop(0)
            print(self.grid)
            pos = self.grid[0]
            print("############### start ############")
            self.prior.coords = (pos[0] * RATIO, pos[1] * RATIO)


            self.update()
            self.draw()

    # def add_cmd(self, key, cmd):
    #     self.key_cmd[key] = cmd
    #     print(self.key_cmd)
    #
    def add(self, object):
        self.objects.append(object)
        object.parent = self

    def do(self, event):
        if event.type == QUIT:

            self.running = False
            for obj in self.objects:
                self.objects.remove(obj)
                del obj

            # self.prior_visualisation.thread.stop()
            pygame.quit()

        # elif event.type == REFRESH_PRIOR_POSITION:
        # print("refresh")
        #     x_pos, y_pos, _ = self.thread.coords
        #     if x_pos is not None:
        #         x_pos = round(float(x_pos) / RATIO)
        #     if y_pos is not None:
        #         y_pos = round(float(y_pos) / RATIO)
        #
        #     if x_pos is not None and y_pos is not None:
        #         self.image.fill(self.bg_color)
        #         pygame.draw.rect(self.image, (255, 0, 0), (x_pos, y_pos, *IMAGE_SIZE))

        for obj in self.objects:
            obj.do(event)

    def update(self):
        if self.updating:
            for obj in self.objects:
                obj.update()

    def draw(self):
        scaled_surface = pygame.transform.scale(self.image, APP_SIZE)
        self.screen.blit(scaled_surface, self.rect)
        for obj in self.objects:
            obj.draw(self.screen)
        pygame.display.update()


if __name__ == '__main__':
    lock = threading.Lock()

    prior = PriorController(port="COM12", baudrate=9600, timeout=0.1)
    prior.go2limit_switch()
    prior.set_position_as_home()
    prior.speed = 50
    prior.return2home()


    # lock.acquire(blocking=True)
    # prior.set_index_stage()
    # lock.release()

    x, y = 0, 0
    vel = 5
    step= 50
    movement = GridMovement(x, y, vel, x_lim=(0, round(280000/RATIO)), y_lim=(0, round(80000 / RATIO)), ratio=RATIO)
    movement.course = Course().V_RIGHT
    movement.recover_x = 50

    grid = movement.get_grid(start_pt=(x, y), final_pt=(600, 600), step=step)

    app = App('Motorized microscope', prior, grid)

    # lock.acquire(blocking=True)
    # for i in grid[1:]:
    #     lock.acquire(blocking=True)
    #     prior.coords = i
    #     lock.release()
    #     time.sleep(1000)
    # # lock.release()
    # #
    # lock.acquire(blocking=True)
    # prior.set_index_stage()
    # lock.release()
    # lock.acquire(blocking=True)
    # prior.wait4available()
    # lock.release()
    # print("Is available")
    #
    # x, y = 0, 0
    # vel = 5
    # movement = GridMovement(x, y, vel, x_lim=(0, GRID[0]), y_lim=(0, round(50000/RATIO)), ratio=RATIO)
    # movement.course = Course().V_RIGHT
    #
    # grid = movement.get_grid(start_pt=(x, y), final_pt=(600, 0), step=5)
    # print(grid)
    # # #



        # time.sleep(1)

    app.run()

    # time.sleep(2)
    # for pos in grid[1:10]:
    #     print("############### start ############")
    #     prior.coords = (pos[0] * RATIO, pos[1] * RATIO)
    #     app.update()
    #     print("############### end ############")
