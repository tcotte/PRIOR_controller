import typing
from asyncio import Event

import pygame

from app.ui import locked_thread
from grid.grid_movement import GridMovement, Course
from grid.prior_thread import RefreshPriorCoordsThread
from main import PriorController

APP_SIZE = (700, 500)
GRID = (1300, 800)  # width, height -> 1 pixel equals 10 µm
IMAGE_SIZE = (100, 100)  # width, height -> camera image size
RATIO = 100  # 1 pixel equals 10 µm


@locked_thread
def set_absolute_coords(device, position: typing.Tuple) -> None:
    setattr(device, 'coords', position)

if __name__ == "__main__":
    x, y = (0, 0)
    vel = 5
    movement = GridMovement(x, y, vel, x_lim=(0, GRID[0]), y_lim=(0, GRID[1]))
    # movement.recover_x = 40
    # movement.recover_y = 30
    movement.course = Course().V_RIGHT

    grid = movement.get_grid(start_pt=(x, y), final_pt=(600, 0), step=vel)
    pos_grid = 0
    print(grid)

    prior = PriorController(port="COM13", baudrate=9600, timeout=0.1)
    prior.coords = grid[0]
    prior.wait4available()



    pygame.init()
    win = pygame.display.set_mode(APP_SIZE)
    screen = pygame.Surface((GRID[0], GRID[1]))
    # screen.fill((0, 0, 255))
    pygame.display.set_caption("Grid simulation")

    # create the thread
    stop_flag = Event()
    thread = RefreshPriorCoordsThread(prior_device=prior, event=stop_flag)
    # thread.prior = prior
    # start the thread
    thread.start()

    response_coords = thread.coords
    print(response_coords)

    try:
        x, y, _ = response_coords
        x, y = round(float(x) / RATIO), round(float(y) / RATIO)
    except:
        x, y = 0, 0

    REFRESH_PRIOR_POSITION = pygame.USEREVENT + 1
    pygame.time.set_timer(REFRESH_PRIOR_POSITION, 100)

    x_pos, y_pos = x, y


    run = True
    while run:
        pygame.time.delay(100)

        for event in pygame.event.get():  # This will loop through a list of any keyboard or mouse events.
            if event.type == pygame.QUIT:  # Checks if the red button in the corner of the window is clicked
                run = False  # Ends the game loop
                thread.stop()
                thread.join()

            elif event.type == REFRESH_PRIOR_POSITION:
                print("event refresh coords")
                response_coords = thread.coords
                print("RESONSE COORDS {}".format(response_coords))

                # str_xyz = prior.coords
                # try:
                #     x, y, z = str_xyz.split(",")
                #     x_pos, y_pos = int(x), int(y)
                # except:
                #     print("[ERROR] The value {} does not take part into x, y, z coordinate system".format(str_xyz))
                #     x_pos, y_pos = None, None
                # if x_pos is not None:
                #     x_pos = round(float(x_pos) / RATIO)
                # if y_pos is not None:
                #     y_pos = round(float(y_pos) / RATIO)
                x_pos, y_pos, _ = response_coords
                if x_pos is not None:
                    x_pos = round(float(x_pos) / RATIO)
                if y_pos is not None:
                    y_pos = round(float(y_pos) / RATIO)


        # current_position = (x, y, x + IMAGE_SIZE[0], y + IMAGE_SIZE[1])
        if pos_grid != len(grid):
            y, x = grid[pos_grid]
            pos_grid += 1

        # prior.coords = x*RATIO, y*RATIO
        set_absolute_coords(prior, position=(x*RATIO, y*RATIO))

        current_position = (x, y, x + IMAGE_SIZE[0], y + IMAGE_SIZE[1])

        # positions_made.append([x,y])

        # pygame.draw.rect(screen, (0, 255, 0), position_done(last_position, current_position))
        if x_pos is not None and y_pos is not None:
            pygame.draw.rect(screen, (255, 0, 0), (x_pos, y_pos, *IMAGE_SIZE))  # This takes: window/surface, color, rect

        scaled_surface = pygame.transform.scale(screen, APP_SIZE)
        win.blit(scaled_surface, (0, 0))

        # print(position_done(last_position, current_position), (x, y))
        pygame.display.update()

        # x, y = movement.move(to=(100000, 100000))
        # print(prior.coords)
        # print(positions_made)
        last_position = current_position

    thread.join()

    pygame.quit()
