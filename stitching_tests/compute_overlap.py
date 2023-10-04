import os.path

import cv2
import natsort
from imutils.paths import list_images

folder_img = r"C:\Users\tristan_cotte\Desktop\ds0_focused-20230922T113146Z-001\ds0_focused"
hx100, wx100 = (68, 85)
hx40 = hx100*4
wx40 = wx100*4

if __name__ == "__main__":
    init_img = list(list_images(folder_img))[0]
    res_y, res_x, _ = cv2.imread(init_img).shape
    print(res_x, res_y)

    _, tail = os.path.split(list(list_images(folder_img))[0])
    x, y, z = tail.replace(".jpg", "").split("_")
    x_init, y_init = int(x), int(y)

    for img_path in list(list_images(folder_img))[1:2]:
        _, tail = os.path.split(img_path)
        x, y, z = tail.replace(".jpg", "").split("_")
        x, y = int(x) - x_init, int(y) - y_init
        print(x, y)

    part_y_of_pix_non_overlapped = y/hx40
    part_y_of_pix_overlapped = 1 - part_y_of_pix_non_overlapped
    print(part_y_of_pix_overlapped)
    pixel_y_overlapped = part_y_of_pix_overlapped*res_y
    print(pixel_y_overlapped)

    part_x_of_pix_non_overlapped = y / wx40
    part_x_of_pix_overlapped = 1 - part_x_of_pix_non_overlapped
    pixel_x_overlapped = part_x_of_pix_overlapped * res_x
    print(pixel_x_overlapped)

