import cv2
import matplotlib.pyplot as plt
import numpy as np

from grid.grid_movement import GridMovement, Course


def draw_square(img_size, pt, m, rgb_color = (0, 0, 0)):
    x0 = pt[0]
    y0 = pt[1]
    x1 = pt[0] + img_size[0]
    y1 = pt[1] + img_size[1]


    m[y0, x0: x1] = rgb_color
    m[y1, x0: x1] = rgb_color
    m[y0: y1, x0] = rgb_color
    m[y0: y1, x1] = rgb_color

    # m[pt[1] , pt[0]: pt[0] + img_size[0]] = 255
    # m[pt[0], pt[1]: pt[1] + img_size[1]] = 255
    # m[pt[0]:pt[0] + img_size[0], pt[1]:pt[1] + img_size[1]] = 255
    return m

def draw_bouding_rect(bounding_rect, m):
    x0 = bounding_rect[0]
    y0 = bounding_rect[1]
    x1 = bounding_rect[2]
    y1 = bounding_rect[3]
    rgb_color = (0, 255, 0)

    m[y0, x0: x1] = rgb_color
    m[y1, x0: x1] = rgb_color
    m[y0: y1, x0] = rgb_color
    m[y0: y1, x1] = rgb_color
    return m


img_size = (4*85, 4*68)
gm = GridMovement(x=0, y=0, img_size=img_size, x_lim=(0, 5000), y_lim=(0, 5000))
gm.course = Course().V_RIGHT
grid = gm.get_grid(start_pt=(0, 0), final_pt=(1000, 1000), percentage_overlap=(0.4, 0.4))

bounding_rect = list(gm.get_bounding_rec_grid(grid))

bounding_rect[2] += img_size[0]
bounding_rect[3] += img_size[1]
print(bounding_rect)

m=np.ones((bounding_rect[3] +1 , bounding_rect[2] +1, 3), dtype=np.uint8)*255
m = draw_bouding_rect((0, 0, 1000, 1000), m)



for point in grid:
    # m = draw_square(img_size=(4*85, 4*68), pt=point, m=m)

    # cv2.rectangle(m, point, (point[0] + img_size[0], point[1] + img_size[1]), (200, 200, 200), -1)
    #
    # alpha = 0.4  # Transparency factor.
    #
    # # Following line overlays transparent rectangle over the image
    # image_new = cv2.addWeighted(m, alpha, image, 1 - alpha, 0)


    sub_img = m[point[1]:point[1] + img_size[1], point[0]:point[0] + img_size[0]]
    white_rect = np.ones(sub_img.shape, dtype=np.uint8) * 10

    alpha = 0.9
    res = cv2.addWeighted(sub_img, alpha, white_rect, 1-alpha, 0)

    # Putting the image back to its position
    m[point[1]:point[1] + img_size[1], point[0]:point[0] + img_size[0]] = res
    m = draw_square(img_size, point, m)

m = m.astype(int)

if __name__ == "__main__":
    plt.imshow(m, cmap="gray")

    plt.xticks(list(set(np.array(grid)[:, 0])))
    plt.yticks(list(set(np.array(grid)[:, 1])))
    plt.tick_params(top=True, labeltop=True, bottom=False, labelbottom=False)

    plt.show()