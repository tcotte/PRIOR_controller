from pycromanager import Core

save_dir = r'/Users/tristan_cotte/tmp'
save_name = r'Acquisition_test'

if __name__ == "__main__":

    # XY stage device is already connected into µmanager (into configs)


    core = Core()
    print(core)
    x_position = core.get_x_position()
    print(x_position)

    # core.snap_image()
