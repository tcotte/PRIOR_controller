import os

import cv2
import matplotlib.pyplot as plt
from natsort import natsort
from stitching import Stitcher
from imutils.paths import list_images

path_images = r"C:\Users\tristan_cotte\Downloads\ds0_focused-20230922T113146Z-001\ds0_focused"


def get_filename_from_path(list_images):
    filenames = []
    for image_path in list_images:
        _, tail = os.path.split(image_path)
        filenames.append(tail)
    return filenames


def find_indices(lst, condition):
    return [i for i, elem in enumerate(lst) if condition(elem)]


def get_pictures_on_x(x_value, list_images, preset: str = "Z_autofocus_ds2_"):
    filtered_images = []
    list_filenames = get_filename_from_path(list_images)
    list_filenames = [image.replace(preset, "") for image in list_filenames]
    x_values = [image.split("_")[0] for image in list_filenames]
    indexes = find_indices(x_values, lambda x: int(x) == x_value)

    filtered_images = [list_images[i] for i in indexes]
    return natsort.natsorted(filtered_images)

def get_pictures_on_y(y_value, list_images, preset: str = "Z_autofocus_ds2_"):
    filtered_images = []
    list_filenames = get_filename_from_path(list_images)
    list_filenames = [image.replace(preset, "") for image in list_filenames]
    y_values = [image.split("_")[1] for image in list_filenames]
    indexes = find_indices(y_values, lambda y: int(y) == y_value)

    filtered_images = [list_images[i] for i in indexes]
    return natsort.natsorted(filtered_images)


if __name__ == "__main__":
    stitcher = Stitcher(detector="sift", confidence_threshold=0.01, matches_graph_dot_file="matches_graph.dot")

    list_images = list(list_images(path_images))

    # print(list_images)
    # filtered_images = get_pictures_on_y(2280, list_images)
    # print(filtered_images)

    panorama_bgr = stitcher.stitch(list_images)
    panorama_rgb = cv2.cvtColor(panorama_bgr, cv2.COLOR_BGR2RGB)
    plt.imshow(panorama_rgb)
    plt.show()
