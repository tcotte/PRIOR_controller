import os

import cv2
import matplotlib.pyplot as plt
import numpy as np
from stitching import Stitcher
from imutils.paths import list_images


def filter_img_by_coords(list_img, x):
    filtered_pictures = []
    for img_path in list_img:
        head, tail = os.path.split(img_path)
        img_name = tail[:-4]
        x_coord, y_coord = [int(i) for i in img_name.split("_")]
        if x_coord == x:
            filtered_pictures.append(img_path)

    return filtered_pictures


def get_ordered_pictures(list_img):
    y_coords = []
    for img_path in list_img:
        head, tail = os.path.split(img_path)
        img_name = tail[:-4]
        _, y_coord = [int(i) for i in img_name.split("_")]
        y_coords.append(y_coord)

    y_coord_array = np.array(y_coords)
    sort_index = np.argsort(y_coord_array)


if __name__ == "__main__":
    settings = {"detector": "sift", "confidence_threshold": 0.01}
    stitcher = Stitcher(**settings)

    list_img = list(list_images(r"output_pictures\sharpest_in_grid"))

    # filtered_pictures = filter_img_by_coords(list_img=list_img, x=304)
    # print(filtered_pictures)
    panorama_bgr = stitcher.stitch(list_images)

    panorama_rgb = cv2.cvtColor(panorama_bgr, cv2.COLOR_BGR2RGB)
    plt.imshow(panorama_rgb)

    plt.show()
