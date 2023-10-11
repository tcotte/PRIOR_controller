# \file    mainwindow.py
# \author  IDS Imaging Development Systems GmbH
# \date    2022-06-01
# \since   1.2.0
#
# \version 1.3.0
#
# Copyright (C) 2021 - 2023, IDS Imaging Development Systems GmbH.
#
# The information in this document is subject to change without notice
# and should not be construed as a commitment by IDS Imaging Development Systems GmbH.
# IDS Imaging Development Systems GmbH does not assume any responsibility for any errors
# that may appear in this document.
#
# This document, or source code, is provided solely as an example of how to utilize
# IDS Imaging Development Systems GmbH software libraries in a sample application.
# IDS Imaging Development Systems GmbH does not assume any responsibility
# for the use or reliability of any portion of this document.
#
# General permission to copy or modify is hereby granted.

import sys
from importlib.metadata import version

import cv2
import numpy as np
from PyQt5.QtCore import QTimer, QRectF
from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import QVBoxLayout, QMessageBox, QWidget, QPushButton
from ids_peak import ids_peak
from ids_peak_ipl import ids_peak_ipl
from packaging.version import parse as parse_version

from camera.display import CustomGraphicsScene
from grid.display import Display

if parse_version(version('ids_peak')) > parse_version('1.6'):
    from ids_peak import ids_peak_ipl_extension

VERSION = "1.2.0"
FPS_LIMIT = 30


def convertQImageToMat(incoming_image: QImage):
    """
    Converts a QImage into an opencv MAT format
    :param incoming_image:
    :return: OpenCV RGB picture
    """
    incoming_image = incoming_image.convertToFormat(4)

    width = incoming_image.width()
    height = incoming_image.height()

    ptr = incoming_image.bits()
    ptr.setsize(incoming_image.byteCount())
    arr = np.array(ptr).reshape(height, width, 4)  # Copies the data
    return arr


class IDSCamWindow(QWidget):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self.__layout = QVBoxLayout()
        self.setLayout(self.__layout)
        # self.setCentralWidget(self.widget)

        self.__device = None
        self.__nodemap_remote_device = None
        self.__datastream = None

        self.display = None
        self.__acquisition_timer = QTimer()
        self.frame_counter = 0
        self.__error_counter = 0
        self.__acquisition_running = False

        self.__label_infos = None
        self.__label_version = None
        self.__label_aboutqt = None

        # initialize peak library
        ids_peak.Library.Initialize()

        if self.__open_device():
            try:
                # Create a display for the camera image
                self.display = Display()

                self.scene = CustomGraphicsScene(self.display)
                self.scene_rec = self.scene.sceneRect()
                self.display.setScene(self.scene)

                if not self.__start_acquisition():
                    QMessageBox.critical(self, "Unable to start acquisition!", QMessageBox.Ok)
                else:
                    self.__layout.addWidget(self.display)

            except Exception as e:
                QMessageBox.critical(self, "Exception", str(e), QMessageBox.Ok)

        else:
            self.__destroy_all()
            sys.exit(0)

        self.photo_btn = QPushButton("Photo")
        self.photo_btn.clicked.connect(self.capture_png)

        self.setMinimumSize(350, 250)

    def __del__(self):
        self.__destroy_all()

    def __destroy_all(self):
        # Stop acquisition
        self.__stop_acquisition()

        # Close device and peak library
        self.__close_device()
        ids_peak.Library.Close()

    def capture_png(self, picture_path: str) -> None:
        np_img = self.display.get_image()
        # np_img = convertQImageToMat(incoming_image=q_img)

        cv2.imwrite(picture_path, np_img)

    def capture_jpg(self, picture_path: str, percentage_compression: int = 95) -> None:
        q_img = self.display.get_image()
        np_img = convertQImageToMat(incoming_image=q_img)

        cv2.imwrite(picture_path, np_img, [cv2.IMWRITE_JPEG_QUALITY, percentage_compression])

    def change_exp_time(self, value: int) -> None:
        """
        Change exposure time of the camera when QSpinBox exposure time is changed on Camera Manager
        :param value:
        """
        self.__nodemap_remote_device.FindNode("ExposureTime").SetValue(value * 1000)

    def change_white_balance(self, value: int) -> None:
        """
        Execute a white balance.
        :param value: int value which specifies if we make the white balance or we cancel it.
                      - 2 => do the whitebalance
                      - 0 => cancel it
        """
        # Automatic white balance
        if value == 2:
            self.__nodemap_remote_device.FindNode("BalanceWhiteAuto").SetCurrentEntry("Once")
        elif value == 1:
            self.__nodemap_remote_device.FindNode("BalanceWhiteAuto").SetCurrentEntry("Continuous")
        else:
            self.__nodemap_remote_device.FindNode("BalanceWhiteAuto").SetCurrentEntry("Off")

    # def capture_photo(self):
    #     frame = self.__display.__scene.image()
    #     frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    #     image = QImage(frame, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
    #     filename, _ = QFileDialog.getSaveFileName(self, "Save Photo", "", "JPEG Image (*.jpg)")
    #     if filename:
    #         image.save(filename, "jpg")

    def __open_device(self):
        try:
            # Create instance of the device manager
            device_manager = ids_peak.DeviceManager.Instance()

            # Update the device manager
            device_manager.Update()

            # Return if no device was found
            if device_manager.Devices().empty():
                QMessageBox.critical(self, "Error", "No device found!", QMessageBox.Ok)
                return False

            # Open the first openable device in the managers device list
            for device in device_manager.Devices():
                if device.IsOpenable():
                    self.__device = device.OpenDevice(ids_peak.DeviceAccessType_Control)
                    break

            # Return if no device could be opened
            if self.__device is None:
                QMessageBox.critical(self, "Error", "Device could not be opened!", QMessageBox.Ok)
                return False

            # Open standard data stream
            datastreams = self.__device.DataStreams()
            if datastreams.empty():
                QMessageBox.critical(self, "Error", "Device has no DataStream!", QMessageBox.Ok)
                self.__device = None
                return False

            self.__datastream = datastreams[0].OpenDataStream()

            # Get nodemap of the remote device for all accesses to the genicam nodemap tree
            self.__nodemap_remote_device = self.__device.RemoteDevice().NodeMaps()[0]

            # To prepare for untriggered continuous image acquisition, load the default user set if available and
            # wait until execution is finished
            try:
                self.__nodemap_remote_device.FindNode("UserSetSelector").SetCurrentEntry("Default")
                self.__nodemap_remote_device.FindNode("UserSetLoad").Execute()
                self.__nodemap_remote_device.FindNode("UserSetLoad").WaitUntilDone()
            except ids_peak.Exception:
                # Userset is not available
                pass

            # Get the payload size for correct buffer allocation
            payload_size = self.__nodemap_remote_device.FindNode("PayloadSize").Value()

            # Get minimum number of buffers that must be announced
            buffer_count_max = self.__datastream.NumBuffersAnnouncedMinRequired()

            # Allocate and announce image buffers and queue them
            for i in range(buffer_count_max):
                buffer = self.__datastream.AllocAndAnnounceBuffer(payload_size)
                self.__datastream.QueueBuffer(buffer)

            return True
        except ids_peak.Exception as e:
            QMessageBox.critical(self, "Exception", str(e), QMessageBox.Ok)

        return False

    def __close_device(self):
        """
        Stop acquisition if still running and close datastream and nodemap of the device
        """
        # Stop Acquisition in case it is still running
        self.__stop_acquisition()

        # If a datastream has been opened, try to revoke its image buffers
        if self.__datastream is not None:
            try:
                for buffer in self.__datastream.AnnouncedBuffers():
                    self.__datastream.RevokeBuffer(buffer)
            except Exception as e:
                QMessageBox.information(self, "Exception", str(e), QMessageBox.Ok)

    def __start_acquisition(self):
        """
        Start Acquisition on camera and start the acquisition timer to receive and display images

        :return: True/False if acquisition start was successful
        """
        # Check that a device is opened and that the acquisition is NOT running. If not, return.
        if self.__device is None:
            return False
        if self.__acquisition_running is True:
            return True

        # Get the maximum framerate possible, limit it to the configured FPS_LIMIT. If the limit can't be reached, set
        # acquisition interval to the maximum possible framerate
        try:
            max_fps = self.__nodemap_remote_device.FindNode("AcquisitionFrameRate").Maximum()
            target_fps = min(max_fps, FPS_LIMIT)
            self.__nodemap_remote_device.FindNode("AcquisitionFrameRate").SetValue(target_fps)
        except ids_peak.Exception:
            # AcquisitionFrameRate is not available. Unable to limit fps. Print warning and continue on.
            QMessageBox.warning(self, "Warning",
                                "Unable to limit fps, since the AcquisitionFrameRate Node is"
                                " not supported by the connected camera. Program will continue without limit.")

        # Setup acquisition timer accordingly
        self.__acquisition_timer.setInterval((1 / target_fps) * 1000)
        self.__acquisition_timer.setSingleShot(False)
        self.__acquisition_timer.timeout.connect(self.on_acquisition_timer)

        try:
            # Lock critical features to prevent them from changing during acquisition
            self.__nodemap_remote_device.FindNode("TLParamsLocked").SetValue(1)

            # Start acquisition on camera
            self.__datastream.StartAcquisition()
            self.__nodemap_remote_device.FindNode("AcquisitionStart").Execute()
            self.__nodemap_remote_device.FindNode("AcquisitionStart").WaitUntilDone()
        except Exception as e:
            print("Exception: " + str(e))
            return False

        # Start acquisition timer
        self.__acquisition_timer.start()
        self.__acquisition_running = True

        return True

    def __stop_acquisition(self):
        """
        Stop acquisition timer and stop acquisition on camera
        :return:
        """
        # Check that a device is opened and that the acquisition is running. If not, return.
        if self.__device is None or self.__acquisition_running is False:
            return

        # Otherwise try to stop acquisition
        try:
            remote_nodemap = self.__device.RemoteDevice().NodeMaps()[0]
            remote_nodemap.FindNode("AcquisitionStop").Execute()

            # Stop and flush datastream
            self.__datastream.KillWait()
            self.__datastream.StopAcquisition(ids_peak.AcquisitionStopMode_Default)
            self.__datastream.Flush(ids_peak.DataStreamFlushMode_DiscardAll)

            self.__acquisition_running = False

            # Unlock parameters after acquisition stop
            if self.__nodemap_remote_device is not None:
                try:
                    self.__nodemap_remote_device.FindNode("TLParamsLocked").SetValue(0)
                except Exception as e:
                    QMessageBox.information(self, "Exception", str(e), QMessageBox.Ok)

        except Exception as e:
            QMessageBox.information(self, "Exception", str(e), QMessageBox.Ok)

    # def update_counters(self):
    #     """
    #     This function gets called when the frame and error counters have changed
    #     :return:
    #     """
    #     self.__label_infos.setText("Acquired: " + str(self.frame_counter) + ", Errors: " + str(self.__error_counter))

    def on_acquisition_timer(self):
        """
        This function gets called on every timeout of the acquisition timer
        """
        try:
            # Get buffer from device's datastream
            buffer = self.__datastream.WaitForFinishedBuffer(5000)

            # Create IDS peak IPL image for debayering and convert it to RGBa8 format
            if parse_version(version('ids_peak')) < parse_version('1.6'):
                # Create IDS peak IPL image for debayering and convert it to RGB8 format
                ipl_image = ids_peak_ipl.Image_CreateFromSizeAndBuffer(
                    buffer.PixelFormat(),
                    buffer.BasePtr(),
                    buffer.Size(),
                    buffer.Width(),
                    buffer.Height()
                )
            else:
                ipl_image = ids_peak_ipl_extension.BufferToImage(buffer)
            converted_ipl_image = ipl_image.ConvertTo(ids_peak_ipl.PixelFormatName_BGRa8)

            # Queue buffer so that it can be used again
            self.__datastream.QueueBuffer(buffer)

            # Get raw image data from converted image and construct a QImage from it
            image_np_array = converted_ipl_image.get_numpy_1D()
            image = QImage(image_np_array,
                           converted_ipl_image.Width(), converted_ipl_image.Height(),
                           QImage.Format_RGB32)

            # Make an extra copy of the QImage to make sure that memory is copied and can't get overwritten later on
            image_cpy = image.copy()

            # Emit signal that the image is ready to be displayed
            self.display.on_image_received(image_cpy)
            self.display.update()

            # Increase frame counter
            self.frame_counter += 1

            if self.scene.sceneRect() != self.scene_rec:
                self.scene_rec = self.scene.sceneRect()
                self.display.on_new_image_flux()


        except ids_peak.Exception as e:
            self.__error_counter += 1
            print("Exception: " + str(e))

        # Update counters
        # self.update_counters()
