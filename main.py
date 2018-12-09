import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QVBoxLayout, QWidget, QGroupBox, QAction, QFileDialog, qApp, QPushButton, QMessageBox
from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPixmap, QImage, QIcon
from PyQt5.QtCore import Qt
import numpy as np
import cv2


class App(QMainWindow):
    def __init__(self):
        super(App, self).__init__()
        self.title = 'Image Warping'
        self.left = 10
        self.top = 10
        self.width = 1000
        self.height = 600

        self.input_opened = False
        self.target_opened = False
        self.triangulation_done = False

        self.selected_coord1 = []
        self.selected_coord2 = []
        self.average = []

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

    def placeImgToLabel3(self, image):

        pixmap_label = self.qlabel3
        height, width, channel = image.shape

        bytesPerLine = 3 * width
        qImg = QImage(image.data, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped()
        pixmap = QPixmap(qImg)
        pixmap_label.setPixmap(pixmap)

    #  Draw a point
    def draw_point1(self, p, color):

        tmp_image = self.inputImg
        cv2.circle(tmp_image, p, 2, color, 2, 6, 0)
        self.placeImgToLabel1(tmp_image)

    #  Draw a point
    def draw_point2(self, p, color):

        tmp_image = self.targetImg
        cv2.circle(tmp_image, p, 2, color, 2, 6, 0)
        self.placeImgToLabel2(tmp_image)

    #  get position of the pixel when the mouse clicked on a pixel
    def getPos1(self, event):

        x = event.pos().x()
        y = event.pos().y()

        self.selected_coord1.append((x, y))
        self.draw_point1((x, y), (0, 0, 255))

    #get position of the pixel when the mouse clicked on a pixel
    def getPos2(self, event):

        x = event.pos().x()
        y = event.pos().y()

        self.selected_coord2.append((x, y))
        self.draw_point2((x, y), (0, 0, 255))

    def openInputImage(self):
        # ******** place image into qlabel object *********************
        self.input_opened = True

        imagePath, _ = QFileDialog.getOpenFileName()
        self.inputImg = cv2.imread(imagePath)
        self.inputImg2 = cv2.imread(imagePath)
        self.inputImg3 = cv2.imread(imagePath)

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
        self.target_opened = True

        imagePath, _ = QFileDialog.getOpenFileName()
        self.targetImg = cv2.imread(imagePath)

        pixmap_label = self.qlabel2
        height, width, channel = self.targetImg.shape

        bytesPerLine = 3 * width
        qImg = QImage(self.targetImg.data, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped()
        pixmap = QPixmap(qImg)
        pixmap_label.setPixmap(pixmap)
        pixmap_label.mousePressEvent = self.getPos2

        QMessageBox.question(self, 'How to select points?', "Please, select equal number of points at input and target image, also you should select the points in the same order at two images!", QMessageBox.Ok, QMessageBox.Ok)
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
        if (self.input_opened == False and self.target_opened == False):
            return QMessageBox.question(self, 'Error Message', "Please, load input and target image", QMessageBox.Ok, QMessageBox.Ok)
        elif(self.input_opened == True and self.target_opened == False):
            return QMessageBox.question(self, 'Error Message', "Please, load target image", QMessageBox.Ok, QMessageBox.Ok)
        elif(self.input_opened == False and self.target_opened == True):
            return QMessageBox.question(self, 'Error Message', "Please, load input image", QMessageBox.Ok, QMessageBox.Ok)

        if len(self.selected_coord1) != len(self.selected_coord2):
            return QMessageBox.question(self, 'Error Message', "Please, select equal number of points!", QMessageBox.Ok, QMessageBox.Ok)

        self.triangulation_done = True

        for i in range(len(self.selected_coord1)):
            avg_x = int((self.selected_coord1[i][0] + self.selected_coord2[i][0]) / 2)
            avg_y = int((self.selected_coord1[i][1] + self.selected_coord2[i][1]) / 2)

            for j in range(len(self.average)):  # check if there is an average value as same with just calculated
                if avg_x == self.average[j][0]:  # if there is same average x coordinate, increment by one
                    avg_x += 1
                if avg_y == self.average[j][1]:  # if there is same average y coordinate, increment by one
                    avg_y += 1

            self.average.append((avg_x, avg_y))
            self.subdiv1.insert((avg_x, avg_y))

        triangleList = self.subdiv1.getTriangleList()

        height, width, channel = self.inputImg.shape
        r = (0, 0, width, height)

        tmp_input = self.inputImg
        tmp_input2 = self.inputImg2
        tmp_target = self.targetImg

        for t in triangleList:

            pt1 = (t[0], t[1])
            pt2 = (t[2], t[3])
            pt3 = (t[4], t[5])

            if self.rect_contains(r, pt1) and self.rect_contains(r, pt2) and self.rect_contains(r, pt3):

                for i in range(len(self.average)):
                    if pt1 == self.average[i]:
                        index1 = i

                    if pt2 == self.average[i]:
                        index2 = i

                    if pt3 == self.average[i]:
                        index3 = i

                input_pt1 = self.selected_coord1[index1]
                target_pt1 = self.selected_coord2[index1]

                input_pt2 = self.selected_coord1[index2]
                target_pt2 = self.selected_coord2[index2]

                input_pt3 = self.selected_coord1[index3]
                target_pt3 = self.selected_coord2[index3]

                self.points1.append((input_pt1[0], input_pt1[1], input_pt2[0], input_pt2[1], input_pt3[0], input_pt3[1]))
                self.points2.append((target_pt1[0], target_pt1[1], target_pt2[0], target_pt2[1], target_pt3[0], target_pt3[1]))

                cv2.line(tmp_input, input_pt1, input_pt2, (255, 255, 255), 1, 8, 0)
                cv2.line(tmp_input, input_pt2, input_pt3, (255, 255, 255), 1, 8, 0)
                cv2.line(tmp_input, input_pt3, input_pt1, (255, 255, 255), 1, 8, 0)

                cv2.line(tmp_target, target_pt1, target_pt2, (255, 255, 255), 1, 8, 0)
                cv2.line(tmp_target, target_pt2, target_pt3, (255, 255, 255), 1, 8, 0)
                cv2.line(tmp_target, target_pt3, target_pt1, (255, 255, 255), 1, 8, 0)

                cv2.line(tmp_input2, target_pt1, target_pt2, (255, 255, 255), 1, 8, 0)
                cv2.line(tmp_input2, target_pt2, target_pt3, (255, 255, 255), 1, 8, 0)
                cv2.line(tmp_input2, target_pt3, target_pt1, (255, 255, 255), 1, 8, 0)

        self.placeImgToLabel1(tmp_input)
        self.placeImgToLabel2(tmp_target)
        self.placeImgToLabel3(tmp_input2)

    def affineTransformMatrix(self, tri1, tri2):

        a = np.zeros((6, 6), dtype=np.float32)

        pt1_x = tri1[0][0]
        pt1_y = tri1[0][1]

        pt2_x = tri1[1][0]
        pt2_y = tri1[1][1]

        pt3_x = tri1[2][0]
        pt3_y = tri1[2][1]

        a[0, 0] = pt1_x
        a[0, 1] = pt1_y
        a[0, 4] = 1
        a[1, 2] = pt1_x
        a[1, 3] = pt1_y
        a[1, 5] = 1
        a[2, 0] = pt2_x
        a[2, 1] = pt2_y
        a[2, 4] = 1
        a[3, 2] = pt2_x
        a[3, 3] = pt2_y
        a[3, 5] = 1
        a[4, 0] = pt3_x
        a[4, 1] = pt3_y
        a[4, 4] = 1
        a[5, 2] = pt3_x
        a[5, 3] = pt3_y
        a[5, 5] = 1

        a = np.linalg.inv(a)

        b = np.zeros((6, 1), dtype=np.float32)

        qt1_x = tri2[0][0]
        qt1_y = tri2[0][1]

        qt2_x = tri2[1][0]
        qt2_y = tri2[1][1]

        qt3_x = tri2[2][0]
        qt3_y = tri2[2][1]

        b[0] = qt1_x
        b[1] = qt1_y
        b[2] = qt2_x
        b[3] = qt2_y
        b[4] = qt3_x
        b[5] = qt3_y

        m = np.zeros((6, 1), dtype=np.float32)

        m[0] = a[0, 0] * b[0] + a[0, 1] * b[1] + a[0, 2] * b[2] + a[0, 3] * b[3] + a[0, 4] * b[4] + a[0, 5] * b[5]
        m[1] = a[1, 0] * b[0] + a[1, 1] * b[1] + a[1, 2] * b[2] + a[1, 3] * b[3] + a[1, 4] * b[4] + a[1, 5] * b[5]
        m[2] = a[2, 0] * b[0] + a[2, 1] * b[1] + a[2, 2] * b[2] + a[2, 3] * b[3] + a[2, 4] * b[4] + a[2, 5] * b[5]
        m[3] = a[3, 0] * b[0] + a[3, 1] * b[1] + a[3, 2] * b[2] + a[3, 3] * b[3] + a[3, 4] * b[4] + a[3, 5] * b[5]
        m[4] = a[4, 0] * b[0] + a[4, 1] * b[1] + a[4, 2] * b[2] + a[4, 3] * b[3] + a[4, 4] * b[4] + a[4, 5] * b[5]
        m[5] = a[5, 0] * b[0] + a[5, 1] * b[1] + a[5, 2] * b[2] + a[5, 3] * b[3] + a[5, 4] * b[4] + a[5, 5] * b[5]

        affMat = np.zeros((3, 3), dtype=np.float32)

        affMat[0, 0] = m[0]
        affMat[0, 1] = m[1]
        affMat[0, 2] = m[4]
        affMat[1, 0] = m[2]
        affMat[1, 1] = m[3]
        affMat[1, 2] = m[5]
        affMat[2, 0] = 0
        affMat[2, 1] = 0
        affMat[2, 2] = 1

        return affMat

    def applyAffine(self, img1Cropped, affMat, r2):

        height, width, channel = img1Cropped.shape
        result_image = np.zeros((r2[3]+20, r2[2]+20, 3), dtype=np.float32)

        for j in range(0, height):
            for k in range(0, width):
                try:
                    coord = [k, j, 1]
                    inv_aff_mat = np.linalg.inv(affMat)
                    new_coord = np.matmul(inv_aff_mat, coord)

                    pixel_value = img1Cropped[int(new_coord[1]), int(new_coord[0]), :]
                    result_image[j, k, :] = pixel_value

                except Exception:
                    pass

        return result_image

    def warphing(self):
        if (self.input_opened == False and self.target_opened == False):
            return QMessageBox.question(self, 'Error Message', "Please, load input and target image", QMessageBox.Ok, QMessageBox.Ok)
        elif(self.input_opened == True and self.target_opened == False):
            return QMessageBox.question(self, 'Error Message', "Please, load target image", QMessageBox.Ok, QMessageBox.Ok)
        elif(self.input_opened == False and self.target_opened == True):
            return QMessageBox.question(self, 'Error Message', "Please, load input image", QMessageBox.Ok, QMessageBox.Ok)

        if(self.triangulation_done == False):
            return QMessageBox.question(self, 'Error Message', "Please, do triangulation part", QMessageBox.Ok, QMessageBox.Ok)


        # create a white space for result image after morphing
        resultImg = 255 * np.ones(self.inputImg.shape, dtype=self.inputImg.dtype)

        # take the triangular points from input(points1) and target(points2) list
        for i in range(len(self.points1)):
            triangular1 = np.float32([[[self.points1[i][0], self.points1[i][1]], [self.points1[i][2], self.points1[i][3]], [self.points1[i][4], self.points1[i][5]]]])
            triangular2 = np.float32([[[self.points2[i][0], self.points2[i][1]], [self.points2[i][2], self.points2[i][3]], [self.points2[i][4], self.points2[i][5]]]])

            # take the top-left points(x, y) and width, height property of box that covers the triangulars
            r1 = cv2.boundingRect(triangular1)
            r2 = cv2.boundingRect(triangular2)

            triangular1_cropped = []
            triangular2_cropped = []

            for j in range(0, 3):
                triangular1_cropped.append(((triangular1[0][j][0] - r1[0]), (triangular1[0][j][1] - r1[1])))
                triangular2_cropped.append(((triangular2[0][j][0] - r2[0]), (triangular2[0][j][1] - r2[1])))

            # Crop input image
            img1Cropped = self.inputImg3[r1[1]:r1[1] + r1[3] + 20, r1[0]:r1[0] + r1[2] + 20]

            affMat = self.affineTransformMatrix(np.float32(triangular1_cropped), np.float32(triangular2_cropped))
            outImage = self.applyAffine(img1Cropped, affMat, r2)

            # Get mask by filling triangle
            mask = np.zeros((r2[3], r2[2], 3), dtype=np.float32)
            cv2.fillConvexPoly(mask, np.int32(triangular2_cropped), (1.0, 1.0, 1.0), 16, 0)

            outImage = outImage[:(r2[3]), :(r2[2])] * mask

            # Copy triangular region of the rectangular patch to the output image
            resultImg[r2[1]:r2[1] + r2[3], r2[0]:r2[0] + r2[2]] = resultImg[r2[1]:r2[1] + r2[3], r2[0]:r2[0] + r2[2]] * ((1.0, 1.0, 1.0) - mask)
            resultImg[r2[1]:r2[1] + r2[3], r2[0]:r2[0] + r2[2]] = resultImg[r2[1]:r2[1] + r2[3], r2[0]:r2[0] + r2[2]] + outImage


        self.placeImgToLabel3(resultImg)


    def initUI(self):
        # Write GUI initialization code

        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowTitle(self.title)

        #****************add the labels for images*********************
        wid = QWidget(self)
        self.setCentralWidget(wid)

        b1 = QPushButton("Create Triangulation")
        b1.clicked.connect(self.createTriangulation1)

        b2 = QPushButton("Warp")
        b2.clicked.connect(self.warphing)

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


