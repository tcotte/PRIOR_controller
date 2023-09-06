import os.path

import numpy as np
import pandas as pd
import skimage
from imutils import paths
import cv2
from matplotlib import pyplot as plt

from sharpness.local_extremas import plot_sharpness_depending_on_z

path_folder = r"C:\Users\tristan_cotte\PycharmProjects\prior_controller\output_picture\test_z_x40\-323_0"


def variance_of_laplacian(rgb_img):
    """
    https://www.researchgate.net/publication/315919131_Blur_image_detection_using_Laplacian_operator_and_Open-CV
    :return:
    """
    gray_img = cv2.cvtColor(rgb_img, cv2.COLOR_BGR2GRAY)
    return cv2.Laplacian(gray_img, cv2.CV_64F).var()


def variance_of_sobel(rgb_img, ddepth=cv2.CV_16S):
    """
    https://www.researchgate.net/publication/315919131_Blur_image_detection_using_Laplacian_operator_and_Open-CV
    :return:
    """
    scale=1
    delta=0
    gray_img = cv2.cvtColor(rgb_img, cv2.COLOR_BGR2GRAY)

    grad_x = cv2.Sobel(gray_img, ddepth, 1, 0, ksize=3, scale=scale, delta=delta, borderType=cv2.BORDER_DEFAULT)
    # Gradient-Y
    # grad_y = cv.Scharr(gray,ddepth,0,1)
    grad_y = cv2.Sobel(gray_img, ddepth, 0, 1, ksize=3, scale=scale, delta=delta, borderType=cv2.BORDER_DEFAULT)

    abs_grad_x = cv2.convertScaleAbs(grad_x)
    abs_grad_y = cv2.convertScaleAbs(grad_y)

    grad = cv2.addWeighted(abs_grad_x, 0.5, abs_grad_y, 0.5, 0)
    return grad.var()


if __name__ == "__main__":
    x = []
    y = []

    steps = list(range(0, 500, 5))

    # for img_path in list(paths.list_images(path_folder)):
    for step in steps:
        img_path = os.path.join(path_folder, str(step) + ".png")
        img = cv2.imread(img_path)
        sp = variance_of_sobel(rgb_img=img)

        # sharpness = 1-blurness

        head, tail = os.path.split(img_path)

        print(tail, " - {:.2f}".format(sp))

        x.append(int(tail[:-4]))
        y.append(sp)

    # with open(os.path.join(path_folder, 'sobel_values.txt'), 'w+') as f:
    #     for line in y:
    #         f.write(str(line))
    #         f.write('\n')
    # f.close()

    # df = pd.DataFrame(data={"z": x, "sobel": y})
    # df.to_csv(os.path.join(r"C:\Users\tristan_cotte\PycharmProjects\prior_controller\sharpness", "test_z_x40.csv"))
    plot_sharpness_depending_on_z(sharpness_array=np.array(y), z_positions=x)
