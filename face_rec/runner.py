import sys, cv2, pickle, face_recognition, cvzone
import numpy as np
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, Qt
from register import Ui_Form as Register_ui
import random,win32ui,win32con
from getlastfile import son_dosyanin_tam_yolu as getlastfile_f
from EncodingGenerator import main_encoder
from database_scripts import insert_data, fetch_data
from login import Ui_Form as Login_ui
import mediapipe as mp


class RegisterPage(QMainWindow):
    def __init__(self):
        super(RegisterPage, self).__init__()
        
        self.ui = Register_ui()
        self.ui.setupUi(self)
        self.mp_face_mesh = mp.solutions.face_mesh # type: ignore
        self.face_mesh = self.mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.mp_drawing = mp.solutions.drawing_utils # type: ignore
        self.drawing_spec = self.mp_drawing.DrawingSpec(thickness=1, circle_radius=1)
        self.capture_value = 0
        # 0 - Default OS camera 
        # 1 - Extended camera 
        
        self.img_left,self.img_left_b = None,False
        self.img_right,self.img_right_b = None, False
        self.img_up,self.img_up_b = None,False
        self.img_down,self.img_down_b = None,False
        self.temp_0,self.temp_1,self.temp_2,self.temp_3,self.temp_4 = None,None,None,None,None
        self.mesh_boolen = False
        
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
                            getlastfile_f(r"C:\Users\quliy\Desktop\face_rec\Images"),
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
                            t = 0
                            for i in self.full_imgs_list:
                                cv2.imwrite(rf"C:\Users\quliy\Desktop\face_rec\Images\{self.random_user_id}_{t}.png",i)
                                t+=1
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
                                self.close()
                                self.logine_kec.show()
                            
                    else:
                        QMessageBox.critical(window, "Register Error", "The user password cannot be less than 6 digits.")
                        
                else:
                    QMessageBox.critical(window, "Register Error", "The username cannot be less than 6 digits and must consist of 2 shares.")
            else:
                QMessageBox.critical(
                    window,
                    "Register Error",
                    "Email must be like : example123@gmail.com",
                )

    def update_frame(self):
        self.success, self.img = self.cap.read()
        self.clean_img = self.img
        
        self.img = cv2.flip(self.img, 1)
        height, width = self.img.shape[:2]
        center = (width // 2, height // 2)
        axes = (width // 4, height // 4)
        angle = 90
        color = (80,80,80)  # boz reng
        thickness = 2
        cv2.ellipse(self.img, center, axes,angle,0, 360, color, thickness)
        
        
        if self.capture_value == 1:
            self.img = cv2.rotate(self.img,cv2.ROTATE_90_CLOCKWISE)
        if self.success and not self.mesh_boolen:
            imgS = cv2.resize(self.img, (0, 0), None, 0.25, 0.25)
            imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
            faceCurFrame = face_recognition.face_locations(imgS)
            encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)
            if faceCurFrame:
                for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
                    matches = face_recognition.compare_faces(
                        self.encodeListKnown, encodeFace
                    )
                    #print("Uyğunlaşmalar: ", matches)
                    faceDis = face_recognition.face_distance(
                        self.encodeListKnown, encodeFace
                    )
                    #print("Üz dəyərləri: ", faceDis)
                    if True in matches and any(x < 0.3 for x in faceDis):
                        y1, x2, y2, x1 = faceLoc
                        y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                        bbox = x1, y1, x2 - x1, y2 - y1
                        cvzone.cornerRect(self.img, bbox=bbox, rt=0)
                        if len(self.studentIds) != 0:
                            print(fetch_data(str(self.studentIds[np.argmin(faceDis)])[:6]))
                            
                        self.frame_counter = 0
                        
                    else:
                        self.frame_counter += 1
                        
                        if self.frame_counter != 0:
                            self.ui.have_db_info_label.setText(
                                "Info: If you see a green frame next to your face, it means your face is recognized! "
                                + str(self.frame_counter)
                            )
                        if self.frame_counter == 5:
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
                                self.mesh_boolen = True
                                
        elif self.mesh_boolen:
            try:
                self.img.flags.writeable = False
            
                results = self.face_mesh.process(self.img)
                
                
                self.img.flags.writeable = True
                
                
                self.img = cv2.cvtColor(self.img, cv2.COLOR_RGB2BGR)

                img_h, img_w, img_c = self.img.shape
                face_3d = []
                face_2d = []

                if results.multi_face_landmarks:
                    for face_landmarks in results.multi_face_landmarks:
                        for idx, lm in enumerate(face_landmarks.landmark):
                            if idx == 33 or idx == 263 or idx == 1 or idx == 61 or idx == 291 or idx == 199:
                                if idx == 1:
                                    nose_2d = (lm.x * img_w, lm.y * img_h)
                                    nose_3d = (lm.x * img_w, lm.y * img_h, lm.z * 3000)

                                x, y = int(lm.x * img_w), int(lm.y * img_h)

                                # Get the 2D Coordinates
                                face_2d.append([x, y]) # type: ignore

                                # Get the 3D Coordinates
                                face_3d.append([x, y, lm.z])        # type: ignore
                        
                        # Convert it to the NumPy array
                        face_2d = np.array(face_2d, dtype=np.float64)

                        # Convert it to the NumPy array
                        face_3d = np.array(face_3d, dtype=np.float64)

                        # The camera matrix
                        focal_length = 1 * img_w

                        cam_matrix = np.array([ [focal_length, 0, img_h / 2],
                                                [0, focal_length, img_w / 2],
                                                [0, 0, 1]])

                        # The distortion parameters
                        dist_matrix = np.zeros((4, 1), dtype=np.float64)

                        # Solve PnP
                        success, rot_vec, trans_vec = cv2.solvePnP(face_3d, face_2d, cam_matrix, dist_matrix)

                        # Get rotational matrix
                        rmat, jac = cv2.Rodrigues(rot_vec)

                        # Get angles
                        angles, mtxR, mtxQ, Qx, Qy, Qz = cv2.RQDecomp3x3(rmat)

                        # Get the y rotation degree
                        x = angles[0] * 360
                        y = angles[1] * 360
                        z = angles[2] * 360

                        
                        #HER DEYER 10 VAHID ARTIRILIB !
                        
                        if self.temp_0 !=0:
                            QMessageBox.information(window,'Register step 1 (camera)','Please look at left for registration!')
                            self.temp_0=0
                        elif y < -20 and y > -25 and x > 20 and x < 25  and not self.img_left_b:
                            self.img_left_b = True
                            self.img_left = self.clean_img
                            if self.temp_1 !=1:
                                QMessageBox.information(window,'Register step 2 (camera)','Please look at right for registration!')
                                self.temp_1 = 1
                            
                        elif x > 10 and x<15 and y>10 and y<15  and not self.img_right_b and self.img_left_b:
                            self.img_right_b = True
                            self.img_right = self.clean_img
                            if self.temp_2 !=2    :
                                QMessageBox.information(window,'Register step 3 (camera)','Please look at down for registration!')
                                self.temp_2 = 2
                        elif x < -5 and x > -13 and y>0 and y<5 and not self.img_down_b and self.img_right_b and self.img_left_b:
                            self.img_down_b = True
                            self.img_down = self.clean_img
                            if self.temp_3 != 3:
                                QMessageBox.information(window,'Register step 4 (camera)','Please look at up for registration!')
                                self.temp_3 = 3
                                
                        elif x > 15  and x < 23 and y>0 and y<5 and not self.img_up_b and self.img_down_b and self.img_right_b and self.img_left_b:
                            
                            self.img_up_b = True
                            self.img_up = self.clean_img
                            
                            if self.temp_4 != 4:
                                QMessageBox.information(window,'Successfull','Registration has successfull!')
                                self.temp_4 = 4
                                self.full_imgs_list = [self.variable_img,self.img_left,self.img_right,self.img_up]
                                print('x: ',x,'y: ',y)            
                                self.cap.release()
                                cv2.destroyAllWindows()
                                self.success = not self.success
                                self.timer.timeout.disconnect(self.update_frame)
                                QMessageBox.information(window,'Fill form','Please fill out the form to complete the registration!!')   
                        
                        self.mp_drawing.draw_landmarks(
                        image=self.img,
                        landmark_list=face_landmarks,
                        connections=self.mp_face_mesh.FACEMESH_CONTOURS,
                        landmark_drawing_spec=self.drawing_spec,
                        connection_drawing_spec=self.drawing_spec)
                        
            except AttributeError:
                pass    
        
        height, width, channel = self.img.shape
        bytes_per_line = 3 * width
        q_image = QImage(
            self.img.data, width, height, bytes_per_line, QImage.Format_RGB888
        ).rgbSwapped()
        pixmap = QPixmap.fromImage(q_image)
        self.ui.camera_place_label.setPixmap(pixmap)
        self.ui.camera_place_label.setAlignment(Qt.AlignCenter)# type: ignore

class LoginPage(QMainWindow):
    def __init__(self):
        super(LoginPage,self).__init__()
        self.ui = Login_ui()
        self.ui.setupUi(self)
        self.cap = cv2.VideoCapture(r'C:\Users\quliy\Desktop\face_rec\Resources\TPIT5526.MOV')
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(int(1000 / 30))
        print("Loading Encode File ...")
        file = open("EncodeFile.p", "rb")
        self.encodeListKnownWithIds = pickle.load(file)
        file.close()
        self.encodeListKnown, self.studentIds = self.encodeListKnownWithIds
        print(self.studentIds)
        self.frame_counter = 0
        print("Encode File Loaded")
    
    def update_frame(self,b=0):
        self.success, self.img = self.cap.read()
        #self.img = cv2.rotate(self.img,cv2.ROTATE_90_CLOCKWISE)
        if self.success and b!=0:
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
                            self.cap.release()
                            cv2.destroyAllWindows()
                            self.success = not self.success
                            
                        self.frame_counter = 0
            
            height, width, channel = self.img.shape
            bytes_per_line = 3 * width
            q_image = QImage(
                self.img.data, width, height, bytes_per_line, QImage.Format_RGB888
            ).rgbSwapped()
            pixmap = QPixmap.fromImage(q_image)
            self.ui.camera_place_label.setPixmap(pixmap)
            self.ui.camera_place_label.setAlignment(Qt.AlignCenter) #type:ignore
        try:
            height, width, channel = self.img.shape
            target_size = (self.ui.camera_place_label.width(), self.ui.camera_place_label.height())
            scaled_frame = cv2.resize(self.img, target_size)
            bytes_per_line = 3 * target_size[0]
            q_img = QImage(scaled_frame.data, target_size[0], target_size[1], bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_img)
            self.ui.camera_place_label.setPixmap(pixmap)
            self.ui.camera_place_label.setAlignment(Qt.AlignCenter) #type:ignore
        
        except AttributeError:
            pass
    

if __name__ == "__main__":
    win32ui.MessageBox("Welcome to my app!", "test")
    app = QApplication(sys.argv)
    response = win32ui.MessageBox('Do you want go to [ Login Page ]','Query for next step!',win32con.MB_YESNO) #type:ignore
    
    if response == win32con.IDYES:
        window = LoginPage()
        window.show()
    else:
        window = RegisterPage()
        window.show()
    sys.exit(app.exec())