import sys
import os
import numpy as np
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import cv2

class Example(QWidget):

    def __init__(self):
        super().__init__()

        self.images = os.listdir("./dataset/images")
        self.id = 0

        self.image = cv2.imread("./dataset/images/" + self.images[self.id])
        self.overlay = np.zeros_like(self.image)

        self.seed_type = 1

        self.initUI()


    def initUI(self):
        self.resize(1000, 600)

        clearButton = QPushButton("Clear All Seeds")
        clearButton.setStyleSheet("background-color:white")
        clearButton.clicked.connect(self.on_clear)

        segmentButton = QPushButton("Segment Image")
        segmentButton.setStyleSheet("background-color:white")
        segmentButton.clicked.connect(self.on_segment)

        hbox = QHBoxLayout()
        # hbox.addWidget(foregroundButton)
        # hbox.addWidget(backgroundButton)
        hbox.addWidget(clearButton)
        hbox.addWidget(segmentButton)
        hbox.addStretch(1)

        self.seedLabel = QLabel()

        self.seedLabel.setAlignment(Qt.AlignCenter)
        self.seedLabel.mousePressEvent = self.mouse_down
        self.seedLabel.mouseMoveEvent = self.mouse_drag
        self.seedLabel.setPixmap(QPixmap.fromImage(
            self.get_qimage(self.get_image_with_overlay())))

        scroll1 = QScrollArea()
        scroll1.setWidgetResizable(False)
        scroll1.setWidget(self.seedLabel)
        scroll1.setAlignment(Qt.AlignCenter)

        imagebox = QHBoxLayout()
        imagebox.addWidget(scroll1)

        vbox = QVBoxLayout()


        vbox.addLayout(hbox)
        vbox.addLayout(imagebox)

        self.setLayout(vbox)

        self.setWindowTitle('GetSeeds')
        self.show()
    @staticmethod
    def get_qimage(cvimage):
        height, width, bytes_per_pix = cvimage.shape
        bytes_per_line = width * bytes_per_pix;

        cv2.cvtColor(cvimage, cv2.COLOR_BGR2RGB, cvimage)
        return QImage(cvimage.data, width, height, bytes_per_line, QImage.Format_RGB888)

    def mouse_down(self, event):
        if event.button() == Qt.LeftButton:
            self.seed_type = 1
        elif event.button() == Qt.RightButton:
            self.seed_type = 0

        if self.seed_type == 1:
            self.overlay[event.y(), event.x()] = [255, 255, 255]
        else:
            self.overlay[event.y(), event.x()] = [0, 0, 255]

        self.seedLabel.setPixmap(QPixmap.fromImage(
                self.get_qimage(self.get_image_with_overlay())))

    def mouse_drag(self, event):
        if self.seed_type == 1:
            self.overlay[event.y(), event.x()] = [255, 255, 255]
        else:
            self.overlay[event.y(), event.x()] = [0, 0, 255]

        self.seedLabel.setPixmap(QPixmap.fromImage(
            self.get_qimage(self.get_image_with_overlay())))

    @pyqtSlot()
    def on_segment(self):
        cv2.imwrite("./seeds/" + self.images[self.id].split(".")[0] + ".png", self.overlay)

        self.id += 1
        self.image = cv2.imread("./dataset/images/" + self.images[self.id])
        self.overlay = np.zeros_like(self.image)

        self.seedLabel.setPixmap(QPixmap.fromImage(
            self.get_qimage(self.get_image_with_overlay())))

    @pyqtSlot()
    def on_clear(self):
        self.overlay = np.zeros_like(self.image)
        self.seedLabel.setPixmap(QPixmap.fromImage(
                self.get_qimage(self.get_image_with_overlay())))

    def get_image_with_overlay(self):
        return cv2.addWeighted(self.image, 0.7, self.overlay, 0.3, 0.1)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())