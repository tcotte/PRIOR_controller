from typing import Tuple, Union

import numpy as np
import pygame
from threading import Thread
from main import PriorController

APP_SIZE = (700, 500)
GRID = (200, 200)  # width, height -> 1 pixel equals 10 µm
#IMAGE_SIZE = (5, 5)  # width, height -> camera image size
IMAGE_SIZE = (100, 100)  # width, height -> camera image size
RATIO = 10  # 1 pixel equals 10 µm


class Course:
    H_RIGHT = 1
    H_LEFT = 2
    V_LEFT = 3
    V_RIGHT = 4


class GridMovement:
    def __init__(self, x: int, y: int, velocity: int, ratio: int = 1, x_lim: Union[Tuple[int, int], None] = None,
                 y_lim: Union[Tuple[int, int], None] = None):
        self.ratio = ratio
        if y_lim is None:
            y_lim = [0, GRID[1] * self.ratio]
        if x_lim is None:
            x_lim = [0, GRID[0] * self.ratio]

        self.velocity = velocity
        self._x = x
        self._y = y
        self._x_lim = x_lim
        self._y_lim = y_lim
        self._recover_x = IMAGE_SIZE[0]
        self._recover_y = IMAGE_SIZE[1]

        self._direction = 1
        self.change_direction = False

        self._course = Course().H_LEFT

    @property
    def course(self):
        return self._course

    @course.setter
    def course(self, value):
        self._course = value
        if (value == Course().V_RIGHT) or (value == Course().V_LEFT):
            self.direction = 1
        elif value == Course().H_RIGHT:
            self.direction = 2
        elif value == Course().H_LEFT:
            self.direction = 4

    @property
    def recover_x(self) -> int:
        return self._recover_x

    @recover_x.setter
    def recover_x(self, value: int) -> None:
        self._recover_x = value

    @property
    def recover_y(self) -> int:
        return self._recover_y

    @recover_y.setter
    def recover_y(self, value: int) -> None:
        self._recover_y = value

    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, value):
        self._direction = value
        self.change_direction = True

    @property
    def x_lim(self) -> Tuple[int, int]:
        return self._x_lim

    @x_lim.setter
    def x_lim(self, value: Tuple[int, int]) -> None:
        self._x_lim = value

    @property
    def y_lim(self) -> Tuple[int, int]:
        return self._y_lim

    @y_lim.setter
    def y_lim(self, value: Tuple[int, int]) -> None:
        self._y_lim = value

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = value
        self.change_direction = False

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._y = value
        self.change_direction = False

    def move(self, to: Tuple[int, int]):
        if (self.x, self.y) == to:
            print("[SUCCESS] The position {} was reached".format(to))
            self.stop()

        if self._direction == 0:
            return self.x, self.y

        if self._course == Course().V_RIGHT:
            if self._direction == 1:  # DOWN
                if self.y + IMAGE_SIZE[1] >= self.y_lim[1]:

                    self.direction = 2
                else:
                    self.y += self.velocity

            if self._direction == 2:  # RIGHT
                if (self.x % self._recover_x == 0) and not self.change_direction:
                    if self.y == self.y_lim[0]:
                        self.direction = 1
                    else:
                        self.direction = 3
                else:
                    self.x += self.velocity

            if self._direction == 3:  # UP

                if self.y == self.y_lim[0]:
                    self.direction = 2
                else:
                    self.y -= self.velocity

        elif self._course == Course().V_LEFT:
            if self._direction == 1:  # DOWN
                if self.y + IMAGE_SIZE[1] == self._y_lim[1]:
                    self.direction = 4
                else:
                    self.y += self.velocity

            if self._direction == 4:  # LEFT
                if (self.x % self._recover_x == 0) and not self.change_direction:
                    if self.y == self.y_lim[0]:
                        self.direction = 1
                    else:
                        self.direction = 3
                else:
                    self.x -= self.velocity

            if self._direction == 3:  # UP
                if self.y == self.y_lim[0]:
                    self.direction = 4
                else:
                    self.y -= self.velocity

        elif self._course == Course().H_RIGHT:
            if self._direction == 1:  # DOWN
                if (self.y % self._recover_y == 0) and not self.change_direction:
                    # if self.x == self.x_lim:
                    #     self.direction = 4
                    if self.x == self.x_lim[0]:
                        self.direction = 2
                    else:
                        self.direction = 4

                else:
                    self.y += self.velocity

            if self._direction == 2:  # RIGHT
                if self.x == self.x_lim[1] - IMAGE_SIZE[0]:
                    self.direction = 1
                    # else:
                    #     self.direction = 3
                else:
                    self.x += self.velocity

            if self._direction == 4:  # LEFT
                if self.x == self.x_lim[0]:
                    self.direction = 1
                else:
                    self.x -= self.velocity

        elif self._course == Course().H_LEFT:
            if self._direction == 1:  # DOWN
                if (self.y % self._recover_y == 0) and not self.change_direction:
                    # if self.x == self.x_lim:
                    #     self.direction = 4
                    if self.x == self.x_lim[0]:
                        self.direction = 2
                    else:
                        self.direction = 4

                else:
                    self.y += self.velocity

            if self._direction == 2:  # RIGHT
                if self.x == self.x_lim[1] - IMAGE_SIZE[0]:
                    self.direction = 1
                    # else:
                    #     self.direction = 3
                else:
                    self.x += self.velocity

            if self._direction == 4:  # LEFT
                if self.x == self.x_lim[0]:
                    self.direction = 1
                else:
                    self.x -= self.velocity

        return self.x, self.y

    def stop(self):
        self._direction = 0

    def get_grid(self, start_pt: Tuple[int, int], final_pt: Tuple[int, int], step: int):
        self.velocity = step
        position_reached = False
        grid = []
        x, y = start_pt

        grid.append(start_pt)

        while not position_reached:
            if (x, y) == final_pt:
                position_reached = True
            else:
                x, y = self.move(to=final_pt)
                grid.append([x, y])
        return grid

    @staticmethod
    def get_x_limits(grid):
        np_grid = np.array(grid)
        return min(np_grid[:, 0]), max(np_grid[:, 0])

    @staticmethod
    def get_y_limits(grid):
        np_grid = np.array(grid)
        return min(np_grid[:, 1]), max(np_grid[:, 1])

    def get_bounding_rec_grid(self, grid):
        x_min, x_max = self.get_x_limits(grid)
        y_min, y_max = self.get_y_limits(grid)
        return x_min, y_min, x_max, y_max



def position_done(last_bbox, current_bbox):
    # position down
    if last_bbox[0] == current_bbox[0]:
        height = current_bbox[1] - last_bbox[1]
        if height > 0:
            return last_bbox[0], last_bbox[1], IMAGE_SIZE[0], height
        else:
            return last_bbox[0], last_bbox[1] + IMAGE_SIZE[1] - np.abs(height), IMAGE_SIZE[0], np.abs(height)

    # position right
    elif last_bbox[1] == current_bbox[1]:
        width = current_bbox[0] - last_bbox[0]
        if width > 0:
            return last_bbox[0], last_bbox[1], width, IMAGE_SIZE[1]
        else:
            return last_bbox[2] - np.abs(width), last_bbox[1], np.abs(width), IMAGE_SIZE[1]
    else:
        raise "The diagonal movement is forbidden in this application"


class Game():
    engine_running = True
    gui_running = True
    clock = pygame.time.Clock()

    gui_framerate = 60.0
    engine_framerate = 120.0

    def __init__(self):

        pygame.init()
        win = pygame.display.set_mode(APP_SIZE)
        screen = pygame.Surface((GRID[0], GRID[1]))
        # screen.fill((0, 0, 255))
        pygame.display.set_caption("Grid simulation")

        self.gui_loop()

    def start_polling(self):
        """Starts the main loop"""
        self.engine_running = True

    def stop_polling(self):
        """Stops the main loop"""
        self.engine_running = False

    def gui_loop(self):
        run = True
        while run:
            pygame.time.delay(
                100)  # This will delay the game the given amount of milliseconds. In our casee 0.1 seconds will be the delay

            for event in pygame.event.get():  # This will loop through a list of any keyboard or mouse events.
                if event.type == pygame.QUIT:  # Checks if the red button in the corner of the window is clicked
                    run = False  # Ends the game loop

            current_position = (x, y, x + IMAGE_SIZE[0], y + IMAGE_SIZE[1])

            # positions_made.append([x,y])

            pygame.draw.rect(screen, (0, 255, 0), position_done(last_position, current_position))
            pygame.draw.rect(screen, (255, 0, 0), (x, y, *IMAGE_SIZE))  # This takes: window/surface, color, rect

            scaled_surface = pygame.transform.scale(screen, APP_SIZE)
            win.blit(scaled_surface, (0, 0))

            # print(position_done(last_position, current_position), (x, y))
            pygame.display.update()

            x, y = movement.move(to=(10000, 10000))
            prior.coords = (x * RATIO, y * RATIO)
            print(prior.coords)
            # print(positions_made)
            last_position = current_position

        pygame.quit()

    ### Define GUI events here

    def quit_button_event(self):
        """Shut down the GUI"""
        print("Quit-button pressed!")
        self.gui_running = False
        self.engine_running = False


def get_prior_coords(prior):
    print(prior.coords)


if __name__ == "__main__":
    pygame.init()
    win = pygame.display.set_mode(APP_SIZE)
    screen = pygame.Surface((GRID[0], GRID[1]))
    # screen.fill((0, 0, 255))
    pygame.display.set_caption("Grid simulation")

    x = 0
    y = 0
    vel = 500

    current_position = (x, y, x + IMAGE_SIZE[0], y + IMAGE_SIZE[1])
    last_position = current_position
    precedent_positions = []
    positions_made = []

    movement = GridMovement(x, y, vel)
    # movement.recover_x = 40
    # movement.recover_y = 30
    movement.course = Course().H_RIGHT

    prior = PriorController(port="COM12", baudrate=9600, timeout=0.1)
    prior.return2home()


    print("Init coords {}".format(prior.coords))

    run = True
    while run:
        pygame.time.delay(
            100)  # This will delay the game the given amount of milliseconds. In our casee 0.1 seconds will be the delay

        for event in pygame.event.get():  # This will loop through a list of any keyboard or mouse events.
            if event.type == pygame.QUIT:  # Checks if the red button in the corner of the window is clicked
                run = False  # Ends the game loop

        # current_position = (x, y, x + IMAGE_SIZE[0], y + IMAGE_SIZE[1])
        answer = prior.coords
        try:
            x, y, _ = [int(x) for x in answer.split(",")]
            x, y = round(x / 10), round(y / 10)
        except:
            print("ERROR {}".format(answer))
        current_position = (x, y, x + IMAGE_SIZE[0], y + IMAGE_SIZE[1])

        # positions_made.append([x,y])

        pygame.draw.rect(screen, (0, 255, 0), position_done(last_position, current_position))
        pygame.draw.rect(screen, (255, 0, 0), (x, y, *IMAGE_SIZE))  # This takes: window/surface, color, rect

        scaled_surface = pygame.transform.scale(screen, APP_SIZE)
        win.blit(scaled_surface, (0, 0))

        # print(position_done(last_position, current_position), (x, y))
        pygame.display.update()

        x, y = movement.move(to=(100000, 100000))
        prior.coords = (x, y)
        # print(prior.coords)
        # print(positions_made)
        last_position = current_position

    pygame.quit()
