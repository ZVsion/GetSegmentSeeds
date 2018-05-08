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
        self.temp_overlay = np.zeros_like(self.image)

        self.seed_type = 1
        self.seedStartX = 0
        self.seedStartY = 0
        self.seedReleaseX = 0
        self.seedReleaseY = 0
        self.IsEraser = False

        self.initUI()


    def initUI(self):

        clearButton = QPushButton("Clear All Seeds")
        clearButton.setStyleSheet("background-color:white")
        clearButton.clicked.connect(self.on_clear)

        segmentButton = QPushButton("Finish")
        segmentButton.setStyleSheet("background-color:white")
        segmentButton.clicked.connect(self.on_segment)

        nextButton = QPushButton("next")
        nextButton.setStyleSheet("background-color:white")
        nextButton.clicked.connect(self.on_skip)

        lastButton = QPushButton("last")
        lastButton.setStyleSheet("background-color:white")
        lastButton.clicked.connect(self.on_last)

        self.thinkness = QLineEdit("3")
        self.thinkness.setStyleSheet("background-color:white")
        self.thinkness.setMaximumWidth(30)

        self.eraserButton = QPushButton("eraser")
        self.eraserButton.setStyleSheet("background-color:white")
        self.eraserButton.clicked.connect(self.on_eraser)


        hbox = QHBoxLayout()
        # hbox.addWidget(foregroundButton)
        # hbox.addWidget(backgroundButton)
        hbox.addWidget(clearButton)
        hbox.addWidget(self.eraserButton)
        hbox.addWidget(segmentButton)
        hbox.addWidget(lastButton)
        hbox.addWidget(nextButton)
        hbox.addWidget(self.thinkness)


        hbox.addStretch(1)

        self.seedLabel = QLabel()

        # self.seedLabel.setAlignment(Qt.AlignCenter)

        self.seedLabel.mousePressEvent = self.mouse_down
        self.seedLabel.mouseReleaseEvent = self.mouse_release
        self.seedLabel.mouseMoveEvent = self.mouse_drag

        self.seedLabel.setPixmap(QPixmap.fromImage(
            self.get_qimage(self.get_image_with_overlay())))

        # scroll1 = QScrollArea()
        # scroll1.setWidgetResizable(False)
        # scroll1.setWidget(self.seedLabel)
        # scroll1.setAlignment(Qt.AlignCenter)

        imagebox = QHBoxLayout()
        # imagebox.addWidget(scroll1)
        imagebox.addWidget(self.seedLabel)

        vbox = QVBoxLayout()

        vbox.addLayout(hbox)
        vbox.addLayout(imagebox)
        vbox.addStretch()

        self.setLayout(vbox)

        self.setWindowTitle('GetSeeds')
        self.show()
    @staticmethod
    def get_qimage(cvimage):
        height, width, bytes_per_pix = cvimage.shape
        bytes_per_line = width * bytes_per_pix

        cv2.cvtColor(cvimage, cv2.COLOR_BGR2RGB, cvimage)
        return QImage(cvimage.data, width, height, bytes_per_line, QImage.Format_RGB888)

    def mouse_down(self, event):
        thinkness = int(self.thinkness.text())

        if event.button() == Qt.LeftButton:
            self.seed_type = 1
        elif event.button() == Qt.RightButton:
            self.seed_type = 0

        temp_overlay = self.get_image_with_overlay()
        self.seedStartX = event.x()
        self.seedStartY = event.y()
        self.seedReleaseX = event.x()
        self.seedReleaseY = event.y()
        if not self.IsEraser:
            if self.seed_type == 1:
                cv2.circle(temp_overlay, (self.seedStartX, self.seedStartY), int(thinkness / 2), (255, 255, 255), int(thinkness / 2))
                # self.temp_overlay[event.y(), event.x()] = [255, 255, 255]
            else:
                cv2.circle(temp_overlay, (self.seedStartX, self.seedStartY), int(thinkness / 2), (0, 0, 255), int(thinkness / 2))
                # self.temp_overlay[event.y(), event.x()] = [0, 0, 255]
        else:
            cv2.circle(self.overlay, (self.seedStartX, self.seedStartY), int(thinkness / 2) + 1, (0, 0, 0),
                       int(thinkness / 2) + 1)

        self.seedLabel.setPixmap(QPixmap.fromImage(
                self.get_qimage(temp_overlay)))

    def mouse_drag(self, event):
        thinkness = int(self.thinkness.text())

        self.seedReleaseX = event.x()
        self.seedReleaseY = event.y()
        temp_overlay = self.get_image_with_overlay()

        if not self.IsEraser:
            if self.seed_type == 1:
                cv2.line(temp_overlay, (self.seedStartX, self.seedStartY), (self.seedReleaseX, self.seedReleaseY), (255, 255, 255), thinkness)
                # self.overlay[event.y(), event.x()] = [255, 255, 255]
            else:
                cv2.line(temp_overlay, (self.seedStartX, self.seedStartY), (self.seedReleaseX, self.seedReleaseY), (0, 0, 255), thinkness)
        else:
            cv2.circle(self.overlay, (self.seedReleaseX, self.seedReleaseY), int(thinkness / 2) + 1, (0, 0, 0),
                       int(thinkness / 2) + 1)

        self.seedLabel.setPixmap(QPixmap.fromImage(
                self.get_qimage(temp_overlay)))


    def mouse_release(self, event):
        thinkness = int(self.thinkness.text())

        if not self.IsEraser:
            if self.seed_type == 1:
                cv2.line(self.overlay, (self.seedStartX, self.seedStartY), (self.seedReleaseX, self.seedReleaseY), (255, 255, 255), thinkness)
            else:
                cv2.line(self.overlay, (self.seedStartX, self.seedStartY), (self.seedReleaseX, self.seedReleaseY), (0, 0, 255), thinkness)
        # else:
        #     cv2.line(self.overlay, (self.seedStartX, self.seedStartY), (self.seedReleaseX, self.seedReleaseY), (0, 0, 0), thinkness)

        self.seedLabel.setPixmap(QPixmap.fromImage(
                self.get_qimage(self.get_image_with_overlay())))

    @pyqtSlot()
    def on_eraser(self):
        if not self.IsEraser:
            self.IsEraser = True
            self.eraserButton.setStyleSheet("background-color:gray")
        else:
            self.IsEraser = False
            self.eraserButton.setStyleSheet("background-color:white")

    @pyqtSlot()
    def on_segment(self):
        cv2.imwrite("./seeds/" + self.images[self.id].split(".")[0] + ".png", self.overlay)

        self.id += 1
        self.image = cv2.imread("./dataset/images/" + self.images[self.id])
        self.overlay = np.zeros_like(self.image)

        self.seedLabel.setPixmap(QPixmap.fromImage(
            self.get_qimage(self.get_image_with_overlay())))
    @pyqtSlot()
    def on_skip(self):
        self.id += 1
        self.image = cv2.imread("./dataset/images/" + self.images[self.id])
        self.overlay = np.zeros_like(self.image)

        self.seedLabel.setPixmap(QPixmap.fromImage(
            self.get_qimage(self.get_image_with_overlay())))

    @pyqtSlot()
    def on_last(self):
        self.id -= 1
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
        return cv2.addWeighted(self.image, 0.7, self.overlay, 1, 0.1)

    # def get_image_with_temp_overlay(self):
    #     image = self.get_image_with_overlay()
    #     image[self.temp_overlay != (0, 0, 0)] = self.temp_overlay[self.temp_overlay != (0, 0, 0)]
    #     return image



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())