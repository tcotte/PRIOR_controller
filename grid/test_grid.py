import pygame

from grid import GridMovement, Course, IMAGE_SIZE, APP_SIZE, GRID

if __name__ == "__main__":
    x, y = (0, 0)
    vel = 5
    movement = GridMovement(x, y, vel, x_lim=(0, 200), y_lim=(0, 200))
    # movement.recover_x = 40
    # movement.recover_y = 30
    movement.course = Course().V_RIGHT

    grid = movement.get_grid(start_pt=(x,y), final_pt=(50, 50), step=vel)
    print(grid)

    pygame.init()
    win = pygame.display.set_mode(APP_SIZE)
    screen = pygame.Surface((GRID[0], GRID[1]))
    # screen.fill((0, 0, 255))
    pygame.display.set_caption("Grid simulation")

    run = True
    for coord in grid:
        pygame.time.delay(
            100)  # This will delay the game the given amount of milliseconds. In our casee 0.1 seconds will be the delay

        for event in pygame.event.get():  # This will loop through a list of any keyboard or mouse events.
            if event.type == pygame.QUIT:  # Checks if the red button in the corner of the window is clicked
                run = False  # Ends the game loop

        # current_position = (x, y, x + IMAGE_SIZE[0], y + IMAGE_SIZE[1])
        x,y = coord
        current_position = (x, y, x + IMAGE_SIZE[0], y + IMAGE_SIZE[1])

        # positions_made.append([x,y])

        #pygame.draw.rect(screen, (0, 255, 0), position_done(last_position, current_position))
        pygame.draw.rect(screen, (255, 0, 0), (x, y, *IMAGE_SIZE))  # This takes: window/surface, color, rect

        scaled_surface = pygame.transform.scale(screen, APP_SIZE)
        win.blit(scaled_surface, (0, 0))

        # print(position_done(last_position, current_position), (x, y))
        pygame.display.update()

        #x, y = movement.move(to=(100000, 100000))
        # print(prior.coords)
        # print(positions_made)
        last_position = current_position

    pygame.quit()