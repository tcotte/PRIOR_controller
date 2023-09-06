import os

import numpy as np
from matplotlib import pyplot as plt
from scipy.signal import argrelextrema
from sklearn.linear_model import LinearRegression

path_folder = r"C:\Users\tristan_cotte\PycharmProjects\prior_controller\output_picture\test_z_x40"

if __name__ == "__main__":
    fr_values = []
    fp12_values = []

    for folder in os.listdir(path_folder):
        if folder != "x-y":
            with open(os.path.join(path_folder, folder, 'sobel_values.txt')) as f:
                lines = f.readlines()
            f.close()

            sharpness_values = np.array([float(x.replace('\n', '')) for x in lines])
            z_positions = list(range(0, 500, 5))

            # find local maximas
            local_maxima_idx = argrelextrema(sharpness_values, np.greater, order=3)[0]

            if len(local_maxima_idx) == 2:
                try:
                    local_maxima_positions = [z_positions[x] for x in local_maxima_idx]
                except IndexError:
                    print("index error", folder)

                fp12 = sum(local_maxima_positions)

                with open(os.path.join(path_folder, folder, 'best.txt')) as f:
                    line = f.readline()
                f.close()
                sharpest_value = float(line.replace('\n', ''))

                fr_values.append(sharpest_value)
                fp12_values.append(fp12)

    reg = LinearRegression().fit(np.array(fp12_values).reshape(-1, 1), np.array(fr_values).reshape(-1, 1))
    print(reg.coef_)
    print(reg.intercept_)
    print(reg.score(np.array(fp12_values).reshape(-1, 1), np.array(fr_values).reshape(-1, 1)))

    plt.scatter(x=fp12_values, y=fr_values)
    plt.ylabel('True focus position fr(µm)')
    plt.xlabel('Sum of two pseudo focus positions fp12(µm)')
    plt.axline((400, 400*reg.coef_[0][0] + reg.intercept_[0]), slope=reg.coef_[0][0], color="red", linestyle=(0, (5, 5)))
    plt.title('Distribution of the sum of two pseudo focus positions and real focus position')
    plt.show()

