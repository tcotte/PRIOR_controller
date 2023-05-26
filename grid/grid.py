from typing import Tuple

import numpy as np
import pygame

GRID = (200, 200)  # width, height
WINDOW_SIZE = (50, 50)  # width, height


class GridMovement:
    def __init__(self, x, y, velocity):
        self.velocity = velocity
        self._x = x
        self._y = y
        self.recover = WINDOW_SIZE[0]

        self._direction = 1
        self.change_direction = False

    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, value):
        self._direction = value
        self.change_direction = True

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

        if self._direction == 1:  # DOWN
            if self.y + WINDOW_SIZE[1] == GRID[1]:
                print("reach limit y")
                self.direction = 2
            else:
                self.y += self.velocity

        if self._direction == 2:  # RIGHT
            if (self.x % self.recover == 0) and not self.change_direction:
                if self.y == 0:
                    self.direction = 1
                else:
                    self.direction = 3
            else:
                self.x += self.velocity

        if self._direction == 3:  # UP

            if self.y == 0:
                self.direction = 2
            else:
                self.y -= self.velocity

        # self.change_direction = False

        return self.x, self.y

    def stop(self):
        self._direction = 0


def position_done(last_bbox, current_bbox):
    # position down
    if last_bbox[0] == current_bbox[0]:
        height = current_bbox[1] - last_bbox[1]
        if height > 0:
            return last_bbox[0], last_bbox[1], WINDOW_SIZE[0], height
        else:
            return last_bbox[0], last_bbox[1] + WINDOW_SIZE[1] - np.abs(height), WINDOW_SIZE[0], np.abs(height)

    # position right
    elif last_bbox[1] == current_bbox[1]:
        width = current_bbox[0]-last_bbox[0]
        if width > 0:
            return last_bbox[0], last_bbox[1], width, WINDOW_SIZE[1]
        else:
            return last_bbox[0] + WINDOW_SIZE[0], last_bbox[1], width, WINDOW_SIZE[1]
    else:
        raise "The diagonal movement is forbidden in this application"


# def xyxy2xywh():


if __name__ == "__main__":
    pygame.init()
    win = pygame.display.set_mode(GRID)
    pygame.display.set_caption("Grid simulation")

    x = 0
    y = 0
    vel = 5

    current_position = (x, y, x + WINDOW_SIZE[0], y + WINDOW_SIZE[1])
    last_position = current_position
    precedent_positions = []
    positions_made = []

    movement = GridMovement(x, y, vel)

    run = True
    while run:
        pygame.time.delay(
            100)  # This will delay the game the given amount of milliseconds. In our casee 0.1 seconds will be the delay

        for event in pygame.event.get():  # This will loop through a list of any keyboard or mouse events.
            if event.type == pygame.QUIT:  # Checks if the red button in the corner of the window is clicked
                run = False  # Ends the game loop

        current_position = (x, y, x + WINDOW_SIZE[0], y + WINDOW_SIZE[1])

        # positions_made.append([x,y])
        rec = [position_done(last_position, current_position)]
        # rec[2] = rec[2] - WINDOW_SIZE[0]
        # rec[3] = rec[3] - WINDOW_SIZE[1]
        pygame.draw.rect(win, (0, 255, 0), position_done(last_position, current_position))
        pygame.draw.rect(win, (255, 0, 0), (x, y, *WINDOW_SIZE))  # This takes: window/surface, color, rect

        print(position_done(last_position, current_position), (x, y))
        pygame.display.update()

        x, y = movement.move(to=(0, 1000))
        # print(positions_made)
        last_position = current_position

    pygame.quit()
