import sys, cv2, pickle, face_recognition, cvzone
import numpy as np
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, Qt
from register import Ui_Form as Register_ui
import random
from getlastfile import son_dosyanin_tam_yolu as getlastfile_f
from EncodingGenerator import main_encoder
from database_scripts import insert_data, fetch_data


class RegisterPage(QMainWindow):
    def __init__(self):
        super(RegisterPage, self).__init__()
        self.ui = Register_ui()
        
        
        self.capture_value = 0 
        # 0 - Default OS camera 
        # 1 - Extended camera 
        
        
        
        self.ui.setupUi(self)
        self.cap = cv2.VideoCapture(self.capture_value)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(int(1000 / 30))
        print("Loading Encode File ...")
        file = open("EncodeFile.p", "rb")
        self.encodeListKnownWithIds = pickle.load(file)
        file.close()
        self.encodeListKnown, self.studentIds = self.encodeListKnownWithIds
        print(self.studentIds)
        print("Encode File Loaded")
        self.frame_counter = 0
        self.ui.register_button.clicked.connect(self.register_now)
        self.ui.recapture_button.clicked.connect(self.recapture_now)
        self.random_user_id = str(random.randint(100000, 999999))
        self.ui.user_id_lineedit.setText(self.random_user_id)

    def recapture_now(self):
        if not self.success:
            print("Video Capture starting...")
            print("Loading New encode File ...")
            file = open("EncodeFile.p", "rb")
            self.encodeListKnownWithIds = pickle.load(file)
            file.close()
            self.encodeListKnown, self.studentIds = self.encodeListKnownWithIds
            print(self.studentIds)
            self.random_user_id = str(random.randint(100000, 999999))
            self.ui.user_id_lineedit.setText(self.random_user_id)
            print("New encode File Loaded")
            self.cap = cv2.VideoCapture(self.capture_value)

    def register_now(self):
        if not self.success:
            self.user_email = self.ui.email_lineedit.text()
            self.user_fullname = self.ui.fullname_lineedit.text()
            self.user_password = self.ui.pass_lineedit.text()

            if (
                self.user_email
                and self.user_email.endswith(".com")
                and "@" in self.user_email
            ):
                if (
                    self.user_fullname
                    and len(self.user_fullname.split(" ")) >= 2
                    and len(self.user_fullname) >= 6
                ):
                    if self.user_password and len(self.user_password) > 6:
                        print(
                            self.user_email,
                            self.user_password,
                            self.user_fullname,
                            getlastfile_f(r"Images"),
                        )
                        response = QMessageBox.question(
                            window,
                            "Dialog window",
                            "Do you agree to save the face inside the frame??",
                            QMessageBox.Yes | QMessageBox.No,
                            QMessageBox.No,
                        )
                        if response == QMessageBox.Yes:
                            insert_data(
                                self.random_user_id,
                                self.ui.email_lineedit.text(),
                                self.ui.fullname_lineedit.text(),
                                self.ui.pass_lineedit.text(),
                            )
                            print("Data insertion has successfully")
                            cv2.imwrite(
                                rf"Images\{self.random_user_id}.png",
                                self.variable_img,
                            )
                            print("File saved to IMAGES folder!")
                            main_encoder()
                            QMessageBox.information(
                                window,
                                "Information window",
                                "Face and user personal datas saved to database!",
                            )
                            response = QMessageBox.question(
                            window,
                            "Dialog window",
                            "Do you agree to go to the login page???",
                            QMessageBox.Yes | QMessageBox.No,
                            QMessageBox.No,
                        )
                            if response== QMessageBox.Yes:
                                pass
                else:
                    QMessageBox.critical(window, "Register Error", "")
            else:
                QMessageBox.critical(
                    window,
                    "Register Error",
                    "Email must be like : example123@gmail.com",
                )

    def update_frame(self):
        self.success, self.img = self.cap.read()
        if self.capture_value == 1:
            self.img = cv2.rotate(self.img,cv2.ROTATE_90_CLOCKWISE)
        if self.success:
            imgS = cv2.resize(self.img, (0, 0), None, 0.25, 0.25)
            imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
            faceCurFrame = face_recognition.face_locations(imgS)
            encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)
            if faceCurFrame:
                for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
                    matches = face_recognition.compare_faces(
                        self.encodeListKnown, encodeFace
                    )
                    print("Uyğunlaşmalar: ", matches)
                    faceDis = face_recognition.face_distance(
                        self.encodeListKnown, encodeFace
                    )
                    print("Üz dəyərləri: ", faceDis)
                    if True in matches and any(x < 0.3 for x in faceDis):
                        y1, x2, y2, x1 = faceLoc
                        y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                        bbox = x1, y1, x2 - x1, y2 - y1
                        cvzone.cornerRect(self.img, bbox=bbox, rt=0)
                        if len(self.studentIds) != 0:
                            print(fetch_data(str(self.studentIds[np.argmin(faceDis)])))
                            
                        self.frame_counter = 0
                    else:
                        self.frame_counter += 1
                        if self.frame_counter != 0:
                            self.ui.have_db_info_label.setText(
                                "Info: If you see a green frame next to your face, it means your face is recognized! "
                                + str(self.frame_counter)
                            )
                        if self.frame_counter == 20:
                            self.frame_counter = 0

                            reponse = QMessageBox.question(
                                window,
                                "Frame Query",
                                "New face query dedected! Do you agree with save this frame?",
                                QMessageBox.Yes | QMessageBox.No,
                                QMessageBox.No,
                            )
                            if reponse == QMessageBox.Yes:
                                self.variable_img = self.img
                                # cv2.imwrite(fr"C:\Users\quliy\Desktop\face_rec\Images\{random_user_id}.png", self.img)
                                print("Frame saved in variable!")
                                self.cap.release()
                                cv2.destroyAllWindows()
                                self.success = not self.success

            height, width, channel = self.img.shape
            bytes_per_line = 3 * width
            q_image = QImage(
                self.img.data, width, height, bytes_per_line, QImage.Format_RGB888
            ).rgbSwapped()
            pixmap = QPixmap.fromImage(q_image)
            self.ui.camera_place_label.setPixmap(pixmap)
            self.ui.camera_place_label.setAlignment(Qt.AlignCenter)  # type: ignore


    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RegisterPage()
    window.show()
    sys.exit(app.exec())
