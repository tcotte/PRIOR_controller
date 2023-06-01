from threading import Event

import pygame

from grid.prior_thread import RefreshPriorCoordsThread
from main import PriorController

APP_SIZE = (700, 500)
GRID = (1300, 800)  # width, height -> 1 pixel equals 10 µm
IMAGE_SIZE = (100, 100)  # width, height -> camera image size
RATIO = 100  # 1 pixel equals 10 µm


if __name__ == "__main__":
    pygame.init()
    win = pygame.display.set_mode(APP_SIZE)
    screen = pygame.Surface((GRID[0], GRID[1]))
    # screen.fill((0, 0, 255))
    pygame.display.set_caption("Grid simulation")

    # prior = PriorController(port="COM13", baudrate=9600, timeout=0.1)

    prior = PriorController(port="COM13", baudrate=9600, timeout=0.1)
    # create the thread
    stop_flag = Event()
    thread = RefreshPriorCoordsThread(prior_device=prior, event=stop_flag)
    # thread.prior = prior
    # start the thread
    thread.start()


    x, y = thread.coords
    x, y = round(float(x) / RATIO), round(float(y) / RATIO)

    REFRESH_PRIOR_POSITION = pygame.USEREVENT + 1
    pygame.time.set_timer(REFRESH_PRIOR_POSITION, 100)

    running = True
    while running:


        # Did the user click the window close button?

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            elif event.type == REFRESH_PRIOR_POSITION:
                print(thread.coords)
                x, y = thread.coords

                x, y = round(float(x)/RATIO), round(float(y)/RATIO)



        # Fill the background with white

        screen.fill((0, 0, 0))

        pygame.draw.rect(screen, (255, 0, 0), (x, y, *IMAGE_SIZE))  # This takes: window/surface, color, rect

        scaled_surface = pygame.transform.scale(screen, APP_SIZE)
        win.blit(scaled_surface, (0, 0))

        # print(position_done(last_position, current_position), (x, y))
        pygame.display.update()

    pygame.quit()