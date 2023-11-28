import cv2
import imagej
import os
import matplotlib.gridspec as gridspec
from matplotlib import pyplot as plt

os.environ["JAVA_HOME"] =r"C:\Program Files\Java\jdk-21"
os.environ["JDK_HOME"] =r"C:\Program Files\Java\jdk-21\bin\server"
os.environ["PATH"] =r"C:\Program Files\Java\jdk-21\bin\server"

from scyjava import jimport
# #os.environ["JAVA_HOME"] = r"C:\Environment\indexing\Library"
# # Initialize FIJI
ij = imagej.init(r"C:\Users\tristan_cotte\Downloads\fiji-win64\Fiji.app")

folder = r"C:\Users\tristan_cotte\Pictures\Stitching\test_new_device\ImageJ"
grid_size_x = 4
grid_size_y = 4
# Stitch
plugin = "Grid/Collection stitching"
args = {
  "type": "[Grid: snake by columns]",
  "order": "[Down & Right]",
  "grid_size_x": grid_size_x,
  "grid_size_y": grid_size_y,
  "tile_overlap": "40",
  "first_file_index_i": "1",
  "directory": folder,
  "file_names": "{ii}.jpg",
  "output_textfile_name": "TileConfiguration.txt",
  "fusion_method": "[Linear Blending]",
  "regression_threshold": "0.30",
  "max/avg_displacement_threshold": "2.50",
  "absolute_displacement_threshold": "3.50",
  "compute_overlap": True,
  "computation_parameters": "[Save computation time (but use more RAM)]",
  # "image_output": "[Write to disk]",
  "image_output": "[Fuse and display]",
}

if __name__ == "__main__":
  fig = plt.figure(layout="constrained")

  gs0 = gridspec.GridSpec(1, 2, figure=fig)

  gs1 = gridspec.GridSpecFromSubplotSpec(4, 4, subplot_spec=gs0[0])
  ax_array = plt.subplots(grid_size_x, grid_size_y, squeeze=False)

  for i in range(1, grid_size_y * grid_size_x + 1):
      filename = os.path.join(folder, str(i).zfill(2) + ".jpg")
      print(os.path.isfile(filename))

      col = (i - 1) // grid_size_x

      if col % 2 == 0:
          row = (i - 1) % grid_size_x
      else:
          row = (grid_size_x - 1) - ((i - 1) % grid_size_x)

      print(row, col)
      """      
      bgr_img = cv2.imread(filename)
      ax_array[row, col].imshow(cv2.cvtColor(bgr_img, cv2.COLOR_BGR2RGB))
      ax_array[row, col].axis("off")"""

      ax = plt.Subplot(fig, gs1[row, col])
      bgr_img = cv2.imread(filename)
      ax.imshow(cv2.cvtColor(bgr_img, cv2.COLOR_BGR2RGB))
      ax.axis("off")

      fig.add_subplot(ax)



  result = ij.py.run_plugin(plugin, args)
  window_manager = ij.WindowManager
  stitched_img = ij.py.from_java(window_manager.getCurrentImage())

  gs2 = gridspec.GridSpecFromSubplotSpec(1, 1, subplot_spec=gs0[1])
  ax = fig.add_subplot(gs2[0])
  ax.imshow(stitched_img)

  plt.show()




