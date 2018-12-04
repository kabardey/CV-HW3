import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QVBoxLayout, QWidget, QGroupBox, QAction, QFileDialog, qApp, QPushButton
from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPixmap, QImage, QIcon
from PyQt5.QtCore import Qt
import numpy as np
import cv2


class App(QMainWindow):
    def __init__(self):
        super(App, self).__init__()
        self.title = 'Image Morphing'
        self.left = 10
        self.top = 10
        self.width = 1000
        self.height = 600

        self.points1 = []
        self.points2 = []

        self.initUI()

    def placeImgToLabel1(self, image):

        pixmap_label = self.qlabel1
        height, width, channel = image.shape

        bytesPerLine = 3 * width
        qImg = QImage(image.data, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped()
        pixmap = QPixmap(qImg)
        pixmap_label.setPixmap(pixmap)


    def placeImgToLabel2(self, image):

        pixmap_label = self.qlabel2
        height, width, channel = image.shape

        bytesPerLine = 3 * width
        qImg = QImage(image.data, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped()
        pixmap = QPixmap(qImg)
        pixmap_label.setPixmap(pixmap)


    # Draw a point
    def draw_point1(self, p, color):

        cv2.circle(self.inputImg, p, 2, color, 2, 6, 0)
        self.placeImgToLabel1(self.inputImg)

    # Draw a point
    def draw_point2(self, p, color):

        cv2.circle(self.targetImg, p, 2, color, 2, 6, 0)
        self.placeImgToLabel2(self.targetImg)


    #get position of the pixel when the mouse clicked on a pixel
    def getPos1(self, event):

        x = event.pos().x()
        y = event.pos().y()

        self.points1.append((x, y))
        self.subdiv1.insert((x, y))

        self.draw_point1((x, y), (0, 0, 255))


    #get position of the pixel when the mouse clicked on a pixel
    def getPos2(self, event):

        x = event.pos().x()
        y = event.pos().y()

        self.points2.append((x, y))
        self.subdiv2.insert((x, y))

        self.draw_point2((x, y), (0, 0, 255))


    def openInputImage(self):

        # ******** place image into qlabel object *********************
        imagePath, _ = QFileDialog.getOpenFileName()
        self.inputImg = cv2.imread(imagePath)

        pixmap_label = self.qlabel1
        height, width, channel = self.inputImg.shape

        bytesPerLine = 3 * width
        qImg = QImage(self.inputImg.data, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped()
        pixmap = QPixmap(qImg)
        pixmap_label.setPixmap(pixmap)

        pixmap_label.mousePressEvent = self.getPos1

        ## TRIANGULATION PART ##
        self.rect1 = (0, 0, width, height)  # for triangular operation
        self.subdiv1 = cv2.Subdiv2D(self.rect1)
        # **************************************************************

    def openTargetImage(self):

        # ******** place image into qlabel object *********************
        imagePath, _ = QFileDialog.getOpenFileName()
        self.targetImg = cv2.imread(imagePath)

        pixmap_label = self.qlabel2
        height, width, channel = self.targetImg.shape

        bytesPerLine = 3 * width
        qImg = QImage(self.targetImg.data, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped()
        pixmap = QPixmap(qImg)
        pixmap_label.setPixmap(pixmap)

        pixmap_label.mousePressEvent = self.getPos2

        ## TRIANGULATION PART ##
        self.rect2 = (0, 0, width, height)  # for triangular operation
        self.subdiv2 = cv2.Subdiv2D(self.rect2)
        # **************************************************************

    # Check if a point is inside a rectangle
    def rect_contains(self, rect, point):
        if point[0] < rect[0]:
            return False
        elif point[1] < rect[1]:
            return False
        elif point[0] > rect[2]:
            return False
        elif point[1] > rect[3]:
            return False
        return True


    def createTriangulation1(self):

        triangleList = self.subdiv1.getTriangleList();

        height, width, channel = self.inputImg.shape
        r = (0, 0, width, height)

        for t in triangleList:

            pt1 = (t[0], t[1])
            pt2 = (t[2], t[3])
            pt3 = (t[4], t[5])

            if self.rect_contains(r, pt1) and self.rect_contains(r, pt2) and self.rect_contains(r, pt3):
                cv2.line(self.inputImg, pt1, pt2, (255,255,255), 1, 8, 0)
                cv2.line(self.inputImg, pt2, pt3, (255,255,255), 1, 8, 0)
                cv2.line(self.inputImg, pt3, pt1, (255,255,255), 1, 8, 0)


        triangleList = self.subdiv2.getTriangleList()

        for t in triangleList:

            pt1 = (t[0], t[1])
            pt2 = (t[2], t[3])
            pt3 = (t[4], t[5])

            if self.rect_contains(r, pt1) and self.rect_contains(r, pt2) and self.rect_contains(r, pt3):
                cv2.line(self.targetImg, pt1, pt2, (255, 255, 255), 1, 8, 0)
                cv2.line(self.targetImg, pt2, pt3, (255, 255, 255), 1, 8, 0)
                cv2.line(self.targetImg, pt3, pt1, (255, 255, 255), 1, 8, 0)

        self.placeImgToLabel1(self.inputImg)
        self.placeImgToLabel2(self.targetImg)


    def morphing(self):
        return None


    def initUI(self):
        # Write GUI initialization code

        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowTitle(self.title)

        #****************add the labels for images*********************
        wid = QWidget(self)
        self.setCentralWidget(wid)

        b1 = QPushButton("Create Triangulation")
        b1.clicked.connect(self.createTriangulation1)

        b2 = QPushButton("Morph")
        b2.clicked.connect(self.morphing)

        self.groupBox = QGroupBox()
        self.hBoxlayout = QHBoxLayout()

        self.qlabel1 = QLabel('Input', self)
        self.qlabel1.setStyleSheet("border: 1px inset grey; min-height: 200px; ")
        self.qlabel1.setAlignment(Qt.AlignCenter)
        self.hBoxlayout.addWidget(self.qlabel1)

        self.qlabel2 = QLabel('Target', self)
        self.qlabel2.setStyleSheet("border: 1px inset grey; min-height: 200px; ")
        self.qlabel2.setAlignment(Qt.AlignCenter)
        self.hBoxlayout.addWidget(self.qlabel2)

        self.qlabel3 = QLabel('Result', self)
        self.qlabel3.setStyleSheet("border: 1px inset grey; min-height: 200px; ")
        self.qlabel3.setAlignment(Qt.AlignCenter)
        self.hBoxlayout.addWidget(self.qlabel3)

        self.groupBox.setLayout(self.hBoxlayout)

        vBox = QVBoxLayout()
        vBox.addWidget(b1)
        vBox.addWidget(b2)
        vBox.addWidget(self.groupBox)

        wid.setLayout(vBox)

        #****************menu bar***********
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('File')

        openAction = QAction('Open Input', self)
        openAction.triggered.connect(self.openInputImage)
        fileMenu.addAction(openAction)

        openAction2 = QAction('Target Input', self)
        openAction2.triggered.connect(self.openTargetImage)
        fileMenu.addAction(openAction2)

        exitAct = QAction(QIcon('exit.png'), '&Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(qApp.quit)
        fileMenu.addAction(exitAct)

        #------------------------------------

        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())


