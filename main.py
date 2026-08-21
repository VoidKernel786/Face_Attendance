import sys
import cv2
import numpy as np
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QApplication, QWidget

from start_window import Ui_Form

class Window(QWidget):
	def __init__(self):
		super().__init__()

		# load the ui
		self.ui = Ui_Form()
		self.ui.setupUi(self)

		# open the webcam
		self.capture = cv2.VideoCapture(0)

		# set timer
		self.timer = QTimer()
		self.timer.timeout.connect(self.process_webcam)
		self.timer.start(30)

		# connect the buttons
		self.ui.login_button.clicked.connect(self.take_photo)
		self.ui.new_user_button.clicked.connect(self.new_user)

	def process_webcam(self):
		# try capture the image from the webcam
		ret, frame = self.capture.read()
		# check is the image even exists
		if not ret:
			return

		# jpeg compression
		success, buffer = cv2.imencode(".jpg", frame)
		if not success:
			return

		# jpeg decompression and converting to QImage
		image = QImage.fromData(buffer.tobytes())

		# here above we are using jpeg as a universal handoff format to bypass asking qt to directly understand numpy memory... Qt understand better how to use jpeg than using numpy memory
		# so basically the raw memory handoff was not being interpreted properly and we fixed it with this round about way...

		# convert to QPixmap
		pixmap = QPixmap.fromImage(image)

		# fitting the image inside QLabel
		# - scaling the image
		pixmap = pixmap.scaled(

			self.ui.webcam_label.size(),
			Qt.AspectRatioMode.KeepAspectRatio,
			Qt.TransformationMode.SmoothTransformation
		)
		# - setting the image
		self.ui.webcam_label.setPixmap(pixmap)

	def take_photo(self):
		ret, frame = self.capture.read()

		if ret:
			# in future we need to be able use this with face recognition to find the user and delete this pic so it does not take tooo much storage everytime anyone tries to login....
			cv2.imwrite("CapturedPic.jpg", frame)
			print("Photo Captured!")
	def new_user(self):
		print("Feature upcommming!!!")
	def closeEvent(self, event):
		# stop timer
		self.timer.stop()
		# release the webcam
		self.capture.release()
		event.accept()


app = QApplication(sys.argv)
window = Window()
window.show()
sys.exit(app.exec())

