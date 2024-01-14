from datetime import timedelta
import time
import mediapipe as mp
import cv2
import dlib  # for face and landmark detection
import imutils
from imutils import face_utils

from app.config import (
    LEFT_FACE_PT,
    RIGHT_FACE_PT,
    NOSE_FACE_PT,
    FACE_TURNING_THRESHOLD,
)

from app import functionUtils

# Eye landmarks
(L_start, L_end) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(R_start, R_end) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

# Initializing the Models for Landmark and
# face Detection
dat_file = "./models/shape_predictor_68_face_landmarks.dat"
predictor = dlib.shape_predictor(dat_file)
detector2 = cv2.CascadeClassifier(
    "./models/haarcascade_frontalface_default.xml"
)

detector = dlib.get_frontal_face_detector()
landmark_predict = dlib.shape_predictor(dat_file)


class FaceReader:
    global COUNTER

    def __init__(self):
        self.yawn_thresh = 40
        self.blink_thresh = 0.25
        self.blink_count = 0
        self.yawn_count = 0
        self.elapsedTime = 0
        self.distractedTime = 0
        self.count_frame = 0
        self.prevDistractedTs = 0
        self.last_yawn_update_time = time.time()
        self.last_blink_update_time = time.time()

    # from imutils import

    cam = cv2.VideoCapture("assets/my_blink.mp4")

    def data_collection(self, name, duration):
        COUNTER = 0
        cam = cv2.VideoCapture(0)
        print("Starting Program To track your cute face", name, duration)
        holistic = mp.solutions.holistic  # type: ignore
        hands = mp.solutions.hands  # type: ignore
        holis = holistic.Holistic()
        drawing = mp.solutions.drawing_utils  # type: ignore
        y = []
        start_time = time.perf_counter()
        block_start_time = time.perf_counter()
        block_time_limit = duration // 5

        while True:
            x = []
            _, frame = cam.read()
            frame = cv2.flip(frame, 1)
            frame = imutils.resize(frame, width=640)
            res = holis.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            # y.append(x)

            img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # y.append(x)
            drawing.draw_landmarks(
                frame, res.face_landmarks, holistic.FACEMESH_CONTOURS
            )
            drawing.draw_landmarks(
                frame, res.left_hand_landmarks, hands.HAND_CONNECTIONS
            )
            drawing.draw_landmarks(
                frame, res.right_hand_landmarks, hands.HAND_CONNECTIONS
            )
            # if lookingAtScreen:
            end_time = time.perf_counter()
            self.elapsedTime = end_time - start_time
            elapsed_time_formatted = str(timedelta(seconds=self.elapsedTime))
            if self.elapsedTime >= duration:  # timer is done
                self.write_to_log(name)
                cam.release()
                cv2.destroyAllWindows()
                break
            if end_time >= block_start_time + block_time_limit:
                self.write_to_log(name)
                block_start_time = end_time

            self.check_distracted(res, end_time)
            rects = detector2.detectMultiScale(
                img_gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30),
                flags=cv2.CASCADE_SCALE_IMAGE,
            )

            # for rect in rects:
            for x, y, w, h in rects:
                rect = dlib.rectangle(int(x), int(y), int(x + w), int(y + h))

                shape = predictor(img_gray, rect)
                shape = face_utils.shape_to_np(shape)

                eye = functionUtils.final_ear(shape)
                ear = eye[0]
                leftEye = eye[1]
                rightEye = eye[2]

                distance = functionUtils.lip_distance(shape)

                leftEyeHull = cv2.convexHull(leftEye)
                rightEyeHull = cv2.convexHull(rightEye)
                cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
                cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)

                lip = shape[48:60]
                cv2.drawContours(frame, [lip], -1, (0, 255, 0), 1)

                if ear < self.blink_thresh:
                    time_since_last_blink = time.time()
                    COUNTER += 1
                    if (
                        time_since_last_blink - self.last_blink_update_time
                        >= 3
                    ):
                        cv2.putText(
                            frame,
                            "Blink Alert",
                            (10, 100),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7,
                            (0, 0, 255),
                            2,
                        )
                        self.blink_count += 1
                        print(f"blink count: {self.blink_count}")
                        self.time_since_last_blink = time_since_last_blink
                else:
                    COUNTER = 0
                if distance > self.yawn_thresh:
                    time_since_last_yawn = time.time()
                    print(time_since_last_yawn, self.last_yawn_update_time)
                    if time_since_last_yawn - self.last_yawn_update_time >= 2:
                        cv2.putText(
                            frame,
                            "Yawn Alert",
                            (10, 50),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7,
                            (0, 0, 255),
                            2,
                        )
                        self.yawn_count += 1
                        print(f"yawn count: {self.yawn_count}")
                        self.last_yawn_update_time = time_since_last_yawn

                else:
                    alarm_status2 = False

                cv2.putText(
                    frame,
                    "EAR: {:.2f}".format(ear),
                    (300, 25),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 0, 255),
                    2,
                )
                cv2.putText(
                    frame,
                    "YAWN: {:.2f}".format(distance),
                    (300, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 0, 255),
                    2,
                )
            cv2.imshow("window", frame)
            if cv2.waitKey(1) == 27:
                cam.release()
                cv2.destroyAllWindows()
                break

    def check_distracted(self, results, curr_time):
        # if face detected, then check if user is looking at the screen
        if results.face_landmarks:
            hl = results.face_landmarks.landmark
            left_pt_x = hl[LEFT_FACE_PT].x
            right_pt_x = hl[RIGHT_FACE_PT].x
            center_pt_x = (right_pt_x + left_pt_x) / 2
            nose_pt = hl[NOSE_FACE_PT].x

            # check if face turned by measuring the distance ratio between
            # midpoint of L and R side of face and nose
            dist_lr = (right_pt_x - left_pt_x) / 2
            if abs(nose_pt - center_pt_x) / dist_lr > FACE_TURNING_THRESHOLD:
                self.distractedTime += curr_time - self.prevDistractedTs
        # if no face detected, user is prob doing something else
        else:
            self.distractedTime += curr_time - self.prevDistractedTs
        self.prevDistractedTs = curr_time

    def write_to_log(self, name):
        with open(f"./logs/{name}.csv", "a+") as f:
            f.write(
                f"{self.elapsedTime},{self.distractedTime},{self.blink_count},{self.yawn_count}\n"
            )

    def close(self):
        print("Session complete; closing the camera and saving logs...")
