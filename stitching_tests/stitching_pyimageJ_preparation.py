import os
import shutil
import time

import natsort
import imutils.paths
from PIL import Image

path_input_images = r"C:\Users\tristan_cotte\Pictures\Stitching\test_new_device"
path_output_images = r"C:\Users\tristan_cotte\Pictures\Stitching\test_new_device\ImageJ"

if __name__ == "__main__":
    try:
        os.mkdir(path_output_images)
    except FileExistsError:
        print("This folder already exists. Take caution there is not any file in it.")
    d = {}

    for index, img_path in enumerate(natsort.natsorted(list(imutils.paths.list_images(path_input_images)))):

        exif = Image.open(img_path)._getexif()
        head, tail = os.path.split(img_path)
        src = img_path

        d[tail] = float(os.path.getmtime(img_path))

    sorted_dict = dict(sorted(d.items(), key=lambda x: x[1]))
    for index, value in enumerate(sorted_dict.items()):
        filename = str(index+1).zfill(2)
        src = os.path.join(path_input_images, value[0])
        dst = os.path.join(path_output_images, filename +".jpg")
        shutil.copy(src, dst)