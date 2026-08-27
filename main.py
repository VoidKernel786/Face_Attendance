import datetime
import subprocess
import sys
import cv2
import os
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QApplication, QWidget, QMessageBox
from New_User_Window import Ui_Form as new_User_Window
from start_window import Ui_Form as StartWindowUi

class Window(QWidget):
	def __init__(self):
		super().__init__()

		# load the ui
		self.ui = StartWindowUi()
		self.ui.setupUi(self)
		self.setWindowTitle("Login")

		# open the webcam
		self.capture = cv2.VideoCapture(0)

		# set timer
		self.timer = QTimer()
		self.timer.timeout.connect(self.process_webcam)
		self.timer.start(30)

		# connect the buttons
		self.ui.login_button.clicked.connect(self.login)
		self.ui.new_user_button.clicked.connect(self.new_user)

		# Creating a variable to hold the path to the log file to store attendance
		self.log_path = './.log.txt'

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

	def login(self):
		ret, frame = self.capture.read()
		if not ret:
			return
		unknown_img_path = './.temp.jpg'
		cv2.imwrite(unknown_img_path, frame)

		output = str(subprocess.check_output(['face_recognition', './db', unknown_img_path], creationflags=subprocess.CREATE_NO_WINDOW))
		os.remove(unknown_img_path)
		name = output.split(',')[1][:-5]
		if name == 'no_persons_found':
			QMessageBox.warning(self, "Error", "No Face Found.\n\nTry a clearer photo maby?")
		elif name == 'unknown_person':
			QMessageBox.warning(self, "Error", "Unknown User\n\nPls register if you are a new user and try again :)")
		else:
			QMessageBox.information(self, "Welcome Buddy!!", "Welcome {}. \nWhat a pleasant day it is?".format(name))
			with open(self.log_path, "a") as f:
				f.write("{},{}\n" .format(name, datetime.datetime.now()))
				f.close()

	def new_user(self):
		ret, frame = self.capture.read()
		if not ret:
			return
		self.new_user_window = NewUserWindow(frame)
		self.new_user_window.show()

	def closeEvent(self, event):
		# stop timer
		self.timer.stop()
		# release the webcam
		self.capture.release()
		event.accept()

class NewUserWindow(QWidget):
	def __init__(self, frame):
		super().__init__()

		self.ui = new_User_Window()
		self.ui.setupUi(self)
		self.setWindowTitle("Register New User")

		self.pic = frame

		success, buffer = cv2.imencode(".jpg", frame)
		if not success:
			self.ui.pic_label.setText("Could Not Load Image...")
		else:
			image = QImage.fromData(buffer.tobytes())
			pixmap = QPixmap.fromImage(image)
			pixmap = pixmap.scaled(
				self.ui.pic_label.size(),
				Qt.AspectRatioMode.KeepAspectRatio,
				Qt.TransformationMode.SmoothTransformation
			)
			self.ui.pic_label.setPixmap(pixmap)

		self.dir_db = './db'
		if not os.path.exists(self.dir_db):
			os.mkdir(self.dir_db)

		self.ui.accept_button.clicked.connect(self.accept_reg_new_user)
		self.ui.pushButton_2.clicked.connect(self.close)

	def accept_reg_new_user(self):
		username = self.ui.username_textEdit.toPlainText()
		cv2.imwrite(os.path.join(self.dir_db, "{}.jpg" .format(username)), self.pic)
		QMessageBox.information(self, "Success", "New User has been Registered!!!!")
		self.close()


app = QApplication(sys.argv)
window = Window()
window.show()
sys.exit(app.exec())

