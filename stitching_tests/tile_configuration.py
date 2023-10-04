import os.path
import natsort
from imutils.paths import list_images

folder_img = r"C:\Users\tristan_cotte\Desktop\ds0_focused-20230922T113146Z-001\ds0_focused"

dim = 2

if __name__ == "__main__":
    init_img = list(list_images(folder_img))[0]
    head, tail = os.path.split(init_img)
    x_init, y_init, z = tail.replace(".jpg", "").split("_")
    x_init, y_init = int(x_init), int(y_init)

    with open('tile_configuration.txt', 'w+') as f:
        f.write("dim = {} \n \n".format(str(dim)))

        for img_nb, img_path in enumerate(natsort.natsorted(list(list_images(folder_img)))):
            head, tail = os.path.split(img_path)

            x, y, z = tail.replace(".jpg", "").split("_")
            x, y = int(x), int(y)
            x -= x_init
            y -= y_init
            print(x, y)

            # img_73.tif; ; (0.0, 0.0, 0.0)
            f.write("tile_{img_nb:02d}.tif; ; ({x}, {y})\n".format(img_nb=img_nb + 1, x=str(x*8.9), y=str(y*5.921)))

    f.close()