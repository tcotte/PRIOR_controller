import typing

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.signal import argrelextrema
from scipy.signal import find_peaks

"""
Bibliography:
https://www.mdpi.com/1424-8220/21/7/2487#FD5-sensors-21-02487

An Auto-Focus Method of Microscope for the Surface Structure of Transparent Materials under Transmission Illumination
"""

csv_file = r"C:\Users\tristan_cotte\PycharmProjects\prior_controller\sharpness\test_z_x40.csv"

director_coef = 0.46641
beta = -10.8728
step = 5


def get_nearest_multiple(number: float, multiple: int) -> int:
    return round(number / multiple) * multiple


def plot_sharpness_depending_on_z(sharpness_array: np.array, z_positions: typing.List, plot_fr: bool = True,
                                  order: int = 3):
    # find local maximas
    local_maxima_idx = argrelextrema(sharpness_array, np.greater, order=order)[0]

    if len(local_maxima_idx) == 2:
        local_maxima_positions = [z_positions[x] for x in local_maxima_idx]

        # plot z positions and related sharpness values + local maximas
        for idx, val in enumerate(local_maxima_positions):
            plt.vlines(x=val, ymin=-15, ymax=sharpness_array[local_maxima_idx[idx]], linestyles='dotted',
                       colors='#7d828a')
            plt.text(x=val - 5, y=sharpness_array[local_maxima_idx[idx]] + 3, s="fp" + str(idx + 1), color='#7d828a')

        if plot_fr:
            fr_z = sum(local_maxima_positions) * director_coef + beta
            nearest_fr_z = get_nearest_multiple(fr_z, step)

            sharpness_fr_value = sharpness_array[round(nearest_fr_z / step)]
            plt.vlines(x=nearest_fr_z, ymin=-15, ymax=sharpness_fr_value, linestyles='dotted',
                       colors='#cf7806')
            plt.text(x=nearest_fr_z - 5, y=sharpness_fr_value + 3, s="fr", color='#cf7806')

    elif len(local_maxima_idx) == 1:
        fr = z_positions[local_maxima_idx]
        if plot_fr:
            plt.vlines(x=fr, ymin=-15, ymax=sharpness_array[round(fr/step)], linestyles='dotted',
                       colors='#cf7806')
            plt.text(x=fr - 5, y=sharpness_array[round(fr/step)] + 3, s="fr", color='#cf7806')


    else:
        print("There was not two local maximas !")

    plt.scatter(z_positions, sharpness_array)

    plt.ylim(0, max(sharpness_array) + 10)
    plt.ylabel('Image sharpness (UA)')
    plt.xlabel('Lens position in z axis (µm)')
    plt.title('Sharpness in function of lens position')
    plt.show()





if __name__ == "__main__":
    df = pd.read_csv(csv_file, index_col=0)

    list_z_positions = df.z.values
    sharpness_array = np.array(df.sobel.values)

    plot_sharpness_depending_on_z(sharpness_array, z_positions=df.z.values)
