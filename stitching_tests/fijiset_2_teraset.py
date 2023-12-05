import imutils.paths
import os
from PIL import Image

path_imageJ = r"C:\Users\tristan_cotte\Pictures\Stitching\test_new_device\ImageJ"
path_tera = r"C:\Users\tristan_cotte\Pictures\Stitching\test_new_device\zeta"

# os.mkdir(path_tera)

if __name__ == "__main__":
    grid_x = 4
    grid_y = 4

    img_size = [2448, 2048]
    overlap = 0.4

    current_x = 0
    current_y = 0

    order_y = True

    for index, img_path in enumerate(imutils.paths.list_images(path_imageJ)):
        if index == (grid_y * grid_x):
            break
        print(img_path)
        print(current_x, current_y)

        im = Image.open(img_path)
        dst = os.path.join(path_tera, str(current_x) + "_" + str(current_y) + ".tiff")
        im.save(dst, 'TIFF')

        if (index + 1) % 4 != 0:
            if order_y:
                current_y = round(0.4 * img_size[1] + current_y)
            else:
                current_y = round(current_y - 0.4 * img_size[1])


        else:
            # current_y = 0
            current_x = round(0.4 * img_size[0] + current_x)
            order_y = not order_y


