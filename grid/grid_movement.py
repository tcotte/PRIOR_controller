from typing import Tuple, Union, List

import numpy as np

from app.utils.position import Position

APP_SIZE = (700, 500)
GRID = (200, 200)  # width, height -> 1 pixel equals 10 µm
# IMAGE_SIZE = (5, 5)  # width, height -> camera image size
IMAGE_SIZE = (11, 9)  # width, height -> camera image size
RATIO = 76 * 2 * 4  # 1 pixel equals 10 µm

""""
Objectif Olympus x40:
Scale: 11.6372 px/µm

img: 2448*2048
img_size = 210.35988*175.98735

"""


class Course:
    H_RIGHT = 1
    H_LEFT = 2
    V_LEFT = 3
    V_RIGHT = 4


class GridMovement:
    def __init__(self, x: int, y: int, img_size, ratio: int = 1, x_lim: Union[Tuple[float, float], None] = None,
                 y_lim: Union[Tuple[float, float], None] = None):
        self.start_pt = None
        self.final_pt = None
        self.ratio = ratio
        if y_lim is None:
            y_lim = [0, GRID[1] * self.ratio]
        if x_lim is None:
            x_lim = [0, GRID[0] * self.ratio]

        self.img_size = img_size
        self._velocity = (1, 1)
        self._x = x
        self._y = y
        self._x_lim = x_lim
        self._y_lim = y_lim
        self._recover_x = IMAGE_SIZE[0]
        self._recover_y = IMAGE_SIZE[1]

        self.outward_nb = 0

        self._direction = 1
        self.change_direction = False

        self._course = Course().H_LEFT

    @property
    def velocity(self):
        return self._velocity

    @velocity.setter
    def velocity(self, value):
        if isinstance(value, float):
            self._velocity = (value * self.img_size[0], value * self.img_size[1])
        elif isinstance(value, Tuple):
            self._velocity = (value[0] * self.img_size[0], value[1] * self.img_size[1])

        self._velocity = tuple([round(x) for x in self._velocity])

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

        """
                if (self._x, self._y) == to:
            print("[SUCCESS] The position {} was reached".format(to))
            self.stop()
        """

        if self._direction == 0:
            return self.x, self.y

        if self._course == Course().V_RIGHT or self._course == Course().V_LEFT:
            if self._direction == 1:  # DOWN
                if self._y + self.img_size[1] >= self._y_lim[1]:
                    self.direction = 2 if self._course == Course().V_RIGHT else 4
                    self.outward_nb += 1
                    return None, None
                else:
                    self.y += self._velocity[1]

            elif self._direction == 2:  # RIGHT
                if (self._x % self._velocity[0] == 0) and not self.change_direction:
                    # self.x == self.x_lim[0]
                    if self._y == self._y_lim[0]:
                        self.direction = 1
                        return None, None
                    else:
                        self.direction = 3
                        return None, None
                else:
                    self.x += self._velocity[0]

            elif self._direction == 3:  # UP

                if self._y <= self._y_lim[0]:
                    self.direction = 2 if self._course == Course().V_RIGHT else 4
                    self.outward_nb += 1
                    return None, None
                else:
                    self.y -= self._velocity[1]

        elif self._course == Course().H_RIGHT:
            if self._direction == 1:  # DOWN
                if (self.y % self._recover_y == 0) and not self.change_direction:
                    # if self.x == self.x_lim:
                    #     self.direction = 4
                    if self.x == self.x_lim[0]:
                        self.direction = 2
                        return None, None
                    else:
                        self.direction = 4
                        return None, None

                else:
                    self.y += self._velocity

            if self._direction == 2:  # RIGHT
                if self.x == self.x_lim[1] - self.img_size[0]:
                    self.direction = 1
                    # else:
                    #     self.direction = 3
                else:
                    self.x += self._velocity

            if self._direction == 4:  # LEFT
                if self.x == self.x_lim[0]:
                    self.direction = 1
                else:
                    self.x -= self._velocity

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
                    self.y += self._velocity

            if self._direction == 2:  # RIGHT
                if self.x == self.x_lim[1] - self.img_size[0]:
                    self.direction = 1
                    # else:
                    #     self.direction = 3
                else:
                    self.x += self._velocity

            if self._direction == 4:  # LEFT
                if self.x == self.x_lim[0]:
                    self.direction = 1
                else:
                    self.x -= self._velocity

        return self.x, self.y

    def stop(self):
        self._direction = 0

    def get_grid_from_matrix(self, start_pt: Tuple[int, int], matrix: Tuple[int, int],
                             percentage_non_overlap: Union[Tuple, float]):
        self.velocity = percentage_non_overlap
        position_reached = False

        grid = []
        self.direction = 0
        self.start_pt = start_pt
        self.x, self.y = self.start_pt
        x, y = self.start_pt

        grid.append(list(self.start_pt))
        matrix = (matrix[0] - 1, matrix[1] - 1)
        matrix_counter = [0, 0]

        while not position_reached:

            if self._course == Course().V_RIGHT or self._course == Course().V_LEFT:
                if self._direction == 0:  # DOWN
                    print("down")
                    if matrix_counter[1] == matrix[1]:
                        self.direction = 2

                    # if matrix_counter[1] == 0 and matrix_counter[0] != 0:
                    #     self.direction = 2

                    else:
                        self.y += self._velocity[1]
                        matrix_counter[1] += 1
                        grid.append([self._x, self._y])

                elif self._direction == 2:  # RIGHT
                    self.x += self._velocity[0]
                    matrix_counter[0] += 1
                    grid.append([self._x, self._y])

                    if matrix_counter[0] % 2 == 0:

                        self.direction = 0
                    else:
                        self.direction = 3

                elif self._direction == 3:  # UP
                    if matrix_counter[1] != 0:
                        self.y -= self._velocity[1]
                        matrix_counter[1] -= 1
                        grid.append([self._x, self._y])

                    else:
                        self.direction = 2

            if matrix_counter == list(matrix):
                position_reached = True

        if matrix[0] % 2 != 0:
            while matrix_counter[1] != 0:
                self.y -= self._velocity[1]
                matrix_counter[1] -= 1
                grid.append([self._x, self._y])

        return grid

    def get_grid(self, start_pt: Tuple[int, int], final_pt: Tuple[int, int],
                 percentage_non_overlap: Union[Tuple, float]):
        self.final_pt = final_pt
        self.start_pt = start_pt

        self.y_lim = [start_pt[1], final_pt[1]]
        self.x_lim = [start_pt[0], final_pt[0]]

        # if isinstance(percentage_overlap, Tuple):
        #     percentage_overlap = list(percentage_overlap)
        #     percentage_overlap[0] = 1 - percentage_overlap[0]
        #     percentage_overlap[1] = 1 - percentage_overlap[1]
        # else:
        #     percentage_overlap = 1 - percentage_overlap

        self.velocity = percentage_non_overlap

        position_reached = False
        grid = []
        self.x, self.y = self.start_pt
        x, y = self.start_pt

        grid.append(self.start_pt)

        while not position_reached:
            if x + self.img_size[0] >= final_pt[0] and y + self.img_size[1] >= final_pt[1]:
                if self.outward_nb % 2 == 0:
                    position_reached = True
                else:
                    # last outward
                    while not position_reached:
                        if x - self.img_size[0] * percentage_non_overlap[0] <= final_pt[0] and \
                                y - self.img_size[1] * percentage_non_overlap[1] <= start_pt[1]:
                            position_reached = True
                        if self._course == Course().V_RIGHT:
                            self.direction = 3

                        x, y = self.move(to=(final_pt[0], start_pt[1]))
                        if x is not None:
                            grid.append([x, y])
                        else:
                            x, y = grid[-1]
            else:
                x, y = self.move(to=final_pt)
                print(x, y)
                if x is not None:
                    grid.append([x, y])
                else:
                    x, y = grid[-1]

        return grid

    @staticmethod
    def grid_translation(new_start_pt: Position, grid):
        new_grid = []

        current_start_point = Position(*grid[0])
        offset_x = current_start_point.x - new_start_pt.x
        offset_y = current_start_point.y - new_start_pt.y

        for pt in grid:
            pt[0] -= offset_x
            pt[1] -= offset_y
            new_grid.append(pt)

        return new_grid

    @staticmethod
    def remove_duplicate_positions(grid: List) -> List:
        output_grid = []
        for idx in range(len(grid) - 1):
            if grid[idx] != grid[idx + 1]:
                output_grid.append(grid[idx])
        return output_grid

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

    def get_bounding_rec_visu(self):
        if self.start_pt is None and self.final_pt is None:
            return 0, 0, 0, 0
        else:
            return self.start_pt[0], self.start_pt[1], self.final_pt[0], self.final_pt[1]


def get_bounding_rec_grid(grid, img_size):
    x_min, x_max = get_x_limits(grid)
    y_min, y_max = get_y_limits(grid)
    return x_min, y_min, x_max + img_size[0], y_max + img_size[1]


def get_x_limits(grid):
    np_grid = np.array(grid)
    return min(np_grid[:, 0]), max(np_grid[:, 0])


def get_y_limits(grid):
    np_grid = np.array(grid)
    return min(np_grid[:, 1]), max(np_grid[:, 1])


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


def get_prior_coords(prior):
    print(prior.coords)


if __name__ == "__main__":
    gm = GridMovement(x=0, y=0, img_size=(4 * 85, 4 * 68), x_lim=(0, 1000), y_lim=(0, 1000))
    gm.course = Course().V_RIGHT
    # gm.recover_x = 1
    # gm.recover_y = 1
    # print(gm.get_grid(start_pt=(0, 0), final_pt=(1000, 1000), percentage_non_overlap=(0.5, 0.5)))
    grid = gm.get_grid_from_matrix(start_pt=(800, 800), matrix=(10, 10),
                                  percentage_non_overlap=0.5)
    print("ok")
