import cv2, imutils
from PyQt5 import uic
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt5.QtGui import QPixmap, QImage
import time 
from PyQt5.QtCore import *
import datetime
import numpy as np
from PyQt5.QtGui import QPen, QColor, QPainter



from_class = uic.loadUiType("camera_app.ui")[0]

class WindowClass(QMainWindow, from_class): 
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("word best camera app")

        self.pixmap = QPixmap()
        self.camera = Camera(self) 
        self.record = Camera(self)  
        self.video_player =Camera(self) 
        self.groupBox_2.hide()
        self.groupBox_4.hide()
        self.groupBox_5.hide()
        

        self.camera.daemon = True   
        self.isCameraOn = False     
        self.isRecOn = False        
        self.current_time = 0
        self.image_toggle = ''
        self.btn_click = 0
        self.x, self.y = None, None
        self.video = 0


        self.pen = QPen(Qt.black, 3, Qt.SolidLine, Qt.SquareCap)
        self.colorCb.setCurrentText("Black")
        self.sizeCb.setCurrentText("3")
        self.penStyleCb.setCurrentText("SolidLine")
        self.capStyleCb.setCurrentText("SquareCap")


        # 이벤트
        self.btnOpen.clicked.connect(self.openFile)
        self.btnSave.clicked.connect(self.saveFile)
        self.btnCamera.clicked.connect(self.clickCamera)
        self.camera.update.connect(self.updateCamera)       
        self.btnRec.clicked.connect(self.clickRecord)
        self.record.update.connect(self.updateRecord)
        self.btnCapture.clicked.connect(self.capture)
        self.video_player.update.connect(self.updateVideo)

        self.btnColor.clicked.connect(lambda state, x = 'color' : self.inputToggle(x))
        self.btnCanny.clicked.connect(lambda state, x = 'canny' : self.inputToggle(x))
        self.btnGray.clicked.connect(lambda state, x = "gray" : self.inputToggle(x))
        self.btnBlur9.clicked.connect(lambda state, x = 'blur9' : self.inputToggle(x))
        self.btnBlur5.clicked.connect(lambda state, x = 'blur5' : self.inputToggle(x))
        self.redSlider.valueChanged.connect(lambda state, x = 'slider' : self.inputToggle(x))
        self.greenSlider.valueChanged.connect(lambda state, x = 'slider' : self.inputToggle(x))
        self.blueSlider.valueChanged.connect(lambda state, x = 'slider' : self.inputToggle(x))
        self.btnBinary.clicked.connect(lambda state, x = 'binary': self.inputToggle(x))
        self.btnApply.clicked.connect(self.applyPen)
        self.btnReset.clicked.connect(self.resetPen)

        



    def resetColor(self):
        self.image_toggle = ''
        self.redSlider.setValue(10)
        self.greenSlider.setValue(10)
        self.blueSlider.setValue(10)
        self.redLabel.setText(str(1.0))
        self.greenLabel.setText(str(1.0))
        self.blueLabel.setText(str(1.0))



    def changeSlider(self, x):
        if x == 'color':
            red_weight = self.redSlider.value() / 10
            green_weight = self.greenSlider.value() / 10
            blue_weight = self.blueSlider.value() / 10
            self.redLabel.setText(str(red_weight))
            self.greenLabel.setText(str(green_weight))
            self.blueLabel.setText(str(blue_weight))
            self.image[:, :, 0] = np.clip(self.original_image[:, :, 0] * red_weight, 0, 255).astype(np.uint8)
            self.image[:, :, 1] = np.clip(self.original_image[:, :, 1] * green_weight, 0, 255).astype(np.uint8)
            self.image[:, :, 2] = np.clip(self.original_image[:, :, 2] * blue_weight, 0, 255).astype(np.uint8)



    def inputToggle(self, x):
        self.image_toggle = x
        self.changeImage()
        self.setImage()
        
        


    def changeImage(self):
        if (self.image_toggle == 'slider'):
            self.changeSlider('color')
   

        elif (self.image_toggle == "gray"):
            self.resetColor()
            self.image_toggle = 'gray'
            self.image = cv2.cvtColor(self.original_image, cv2.COLOR_RGB2GRAY)
            self.image = cv2.cvtColor(self.image, cv2.COLOR_GRAY2RGB)
        
        elif (self.image_toggle == 'canny'):
            self.resetColor()
            self.image_toggle = 'canny'
            self.image = cv2.cvtColor(self.original_image, cv2.COLOR_RGB2GRAY)
            edges = cv2.Canny(self.image, 150, 100)
            self.image = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)

        elif (self.image_toggle == 'blur5'):
            self.resetColor()
            self.image_toggle = 'blur5'
            self.image = cv2.cvtColor(self.original_image, cv2.COLOR_RGB2GRAY)
            blurred = cv2.GaussianBlur(self.image, (5, 5), 0)
            self.image = cv2.cvtColor(blurred, cv2.COLOR_GRAY2RGB)


        elif (self.image_toggle == 'blur9'):
            self.resetColor()
            self.image_toggle = 'blur9'
            self.image = cv2.cvtColor(self.original_image, cv2.COLOR_RGB2GRAY)
            blurred = cv2.GaussianBlur(self.image, (9, 9), 0)
            self.image = cv2.cvtColor(blurred, cv2.COLOR_GRAY2RGB)
            

        
        elif (self.image_toggle == 'color'):
            self.resetColor()
            self.image = self.original_image



        elif self.image_toggle == 'binary':
            self.resetColor()
            self.image_toggle = 'binary'
            self.image = cv2.cvtColor(self.image, cv2.COLOR_RGB2GRAY)
            ret, binary = cv2.threshold(self.image, 100, 255, cv2.THRESH_BINARY)
            self.image = cv2.cvtColor(binary, cv2.COLOR_GRAY2RGB)


        else:
            pass


    def capture(self):
        now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        file_name = now + '.png'
        path = '/home/addinedu/dev_ws/PyQt/data/pyqt_camera_data/'
        image = self.image 
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        cv2.imwrite(path + file_name, image)



    def updateRecord(self):
        self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        self.writer.write(self.image)
        now = datetime.datetime.now()

        time_difference = now - self.current_time 
        seconds = time_difference.seconds
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        self.timeEdit.setText(f"{hours}:{minutes}:{seconds}")
        


    def clickRecord(self):
        if self.isRecOn == False:
            self.btnRec.setText("Rec Stop")
            self.isRecOn = True
            self.record.running = True
            self.record.start()

            # recording start 
            self.current_time = datetime.datetime.now()
            now = self.current_time.strftime('%Y%m%d_%H%M%S')
            filename = "/home/addinedu/dev_ws/PyQt/data/pyqt_camera_data/" + now + '.avi'
            fourcc = cv2.VideoWriter_fourcc(*'XVID')    
            w = int(self.video.get(cv2.CAP_PROP_FRAME_WIDTH))
            h = int(self.video.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = 20.0
            self.writer = cv2.VideoWriter(filename, fourcc, fps, (w,h))  
            


        else:
            self.btnRec.setText('Rec Start')
            self.record.running = False
            self.timeEdit.setText("0:0:0")

            # recording stop
            if self.isRecOn == True:
                self.writer.release()

            self.isRecOn = False



    def updateCamera(self):
        retval, image = self.video.read()

        if retval:
            self.image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            self.original_image = self.image.copy()
            self.inputToggle(self.image_toggle)


    def clickCamera(self):
        if self.isCameraOn == False:
            self.btnCamera.setText("Camera off")
            self.isCameraOn = True
            self.showGroup()


            self.camera.running = True      
            self.camera.start()                     
            self.video = cv2.VideoCapture(-1)      

        else:
            self.btnCamera.setText("Camera on")
            self.isCameraOn = False

            self.camera.running = False
            self.count = 0
            self.video.release()                   



    def saveFile(self):
        file, _ = QFileDialog.getSaveFileName(self, "Save Image", directory="/home/addinedu/dev_ws/PyQt/data/pyqt_camera_data", filter='Image (*.png *jpg)')
        if file:
            self.pixmap.save(file, format="PNG")


    def setImage(self):
        h, w, c = self.image.shape
        qimage = QImage(self.image.data, w, h, w*c, QImage.Format_RGB888)
        self.pixmap = self.pixmap.fromImage(qimage)
        self.pixmap = self.pixmap.scaled(self.label.width(), self.label.height())
        self.label.setPixmap(self.pixmap)


    def showGroup(self):
        self.groupBox_2.show()
        self.groupBox_4.show()
        self.groupBox_5.show()


    def openFile(self):
        file = QFileDialog.getOpenFileName(self, "Open Image", directory="/home/addinedu/dev_ws/PyQt/data/pyqt_camera_data", 
                                           filter='Image (*.png *.jpg *.avi *mp4)')
        
        if (file[0].split('.')[-1] == 'png' or file[0].split('.')[-1] == 'jpg'):
            
            if self.isCameraOn == True:
                self.isCameron = False
                self.btnCamera.setText("Camera on")
                self.camera.running = False
                self.video.release() 
            
            self.resetColor()
            self.showGroup()
            
            image = cv2.imread(file[0])
            self.image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            self.original_image = self.image.copy()
            self.setImage()

            

        elif (file[0].split('.')[-1] == 'avi' or file[0].split('.')[-1] == 'mp4'):
            if self.isCameraOn == True:
                self.isCameron = False
                self.btnCamera.setText("Camera on")
                self.camera.running = False
                self.video.release() 

            self.resetColor()
            self.showGroup()
            self.video_player.running = True      
            self.video_player.start()                      
            self.video = cv2.VideoCapture(file[0])
    

    def updateVideo(self):
        retval, image = self.video.read()
        if retval:
            self.image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            self.original_image = self.image.copy()
            self.inputToggle(self.image_toggle)
            # self.setImage()


        else:
            self.video_player.running = False
            self.video.release()

    
    def mouseMoveEvent(self, event):
        if self.x is None:
            self.x = event.x() 
            self.y = event.y() 
            return
        
        painter = QPainter(self.label.pixmap())
        painter.setPen(self.pen)
        painter.drawLine(self.x - 32 , self.y -30, event.x() - 32, event.y() - 30)
        painter.end()
        self.update()

        self.x = event.x()
        self.y = event.y()



    def mouseReleaseEvent(self, event):
        self.x = None
        self.y = None




    def strToQt(self, string):
        mapping = {'Red':Qt.red, "Black":Qt.black, "White":Qt.white,
                         "Green":Qt.green,"Blue":Qt.blue,"Cyan":Qt.cyan,
                         "Magenta":Qt.magenta,"Gray":Qt.gray,"Yellow":Qt.yellow,
                         "DarkGray":Qt.darkGray,"lightGray":Qt.lightGray,
                         "SolidLine":Qt.SolidLine, "DashLine":Qt.DashLine, "DotLine":Qt.DotLine,
                       "DashDotLine":Qt.DashDotLine, "DashDotDotLine":Qt.DashDotDotLine,
                       "SquareCap":Qt.SquareCap, "FlatCap":Qt.FlatCap, "RoundCap":Qt.RoundCap}

        return mapping.get(string)
    
    


    def resetPen(self):
        self.colorCb.setCurrentText("Black")
        self.sizeCb.setCurrentText("3")
        self.penStyleCb.setCurrentText("SolidLine")
        self.capStyleCb.setCurrentText("SquareCap")
        self.pen = QPen(Qt.black, 3, Qt.SolidLine, Qt.SquareCap)




    def applyPen(self):
        color = self.colorCb.currentText()
        size = int(self.sizeCb.currentText())
        penStyle = self.penStyleCb.currentText()
        capStyle = self.capStyleCb.currentText()
        self.pen = QPen(self.strToQt(color), size, self.strToQt(penStyle), self.strToQt(capStyle))





class Camera(QThread):
    update = pyqtSignal()

    def __init__(self, sec=0, parent=None):
        super().__init__()
        self.main = parent
        self.running =  True

    def run(self):
        count = 0
        while self.running == True:
            self.update.emit()         
            time.sleep(0.1)
    
    def stop(self):
        self.running = False



if __name__ == "__main__":
    app = QApplication(sys.argv)    
    myWindows = WindowClass()       
    myWindows.show()                
    sys.exit(app.exec_())          



