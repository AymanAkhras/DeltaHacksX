from datetime import timedelta
import time
import mediapipe as mp
import cv2

from config import (
    LEFT_FACE_PT,
    RIGHT_FACE_PT,
    NOSE_FACE_PT,
    FACE_TURNING_THRESHOLD,
)
import dlib  # for face and landmark detection
import imutils
from scipy.spatial import distance as dist

from imutils import face_utils
import functionUtils

# Eye landmarks
(L_start, L_end) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(R_start, R_end) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

# Initializing the Models for Landmark and
# face Detection
datFile = "./models/shape_predictor_68_face_landmarks.dat"

detector = dlib.get_frontal_face_detector()
landmark_predict = dlib.shape_predictor(datFile)


class FaceReader:
    def __init__(self):
        self.focusedTime = 0
        self.elapsedTime = 0
        self.distractedTime = 0
        self.blink = 0
        # Variables
        self.blink_thresh = 0.35
        self.succesful_frames = 15
        self.count_frame = 0

    # from imutils import

    cam = cv2.VideoCapture("assets/my_blink.mp4")

    def data_collection(self):
        cam = cv2.VideoCapture(0)
        print("Starting Program To track your cute face")
        holistic = mp.solutions.holistic  # type: ignore
        hands = mp.solutions.hands  # type: ignore
        holis = holistic.Holistic()
        drawing = mp.solutions.drawing_utils  # type: ignore
        y = []
        start_time = time.perf_counter()
        focused = True

        while True:
            x = []
            _, frame = cam.read()
            frame = cv2.flip(frame, 1)
            frame = imutils.resize(frame, width=640)
            res = holis.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            y.append(x)

            self.check_distracted(res)

            img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            y.append(x)
            drawing.draw_landmarks(frame, res.face_landmarks, holistic.FACEMESH_CONTOURS)
            drawing.draw_landmarks(frame, res.left_hand_landmarks, hands.HAND_CONNECTIONS)
            drawing.draw_landmarks(frame, res.right_hand_landmarks, hands.HAND_CONNECTIONS)
            # if lookingAtScreen:
            end_time = time.perf_counter()
            self.elapsedTime = end_time - start_time
            elapsed_time_formatted = str(timedelta(seconds=self.elapsedTime))
            if focused:
                self.focusedTime += end_time - start_time
            else:
                self.distractedTime += self.focusedTime - end_time
            # Calculates Number of Blinks
            # if cam.get(cv2.CAP_PROP_POS_FRAMES) == cam.get(
            #     cv2.CAP_PROP_FRAME_COUNT
            # ):
            #     cam.set(cv2.CAP_PROP_POS_FRAMES, 0)
            # else:


            # img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # y.append(x)
            # drawing.draw_landmarks(frame, res.face_landmarks, holistic.FACEMESH_CONTOURS)
            # drawing.draw_landmarks(frame, res.left_hand_landmarks, hands.HAND_CONNECTIONS)
            # drawing.draw_landmarks(frame, res.right_hand_landmarks, hands.HAND_CONNECTIONS)
            # converting frame to gray scale to
            # pass to detector

            # detecting the faces
            faces = detector(img_gray)
            for face in faces:

                # landmark detection
                shape = landmark_predict(img_gray, face)

                # converting the shape class directly
                # to a list of (x,y) coordinates
                shape = face_utils.shape_to_np(shape)

                # parsing the landmarks list to extract
                # lefteye and righteye landmarks--#
                lefteye = shape[L_start:L_end]
                righteye = shape[R_start:R_end]

                # Calculate the EAR
                left_EAR = functionUtils.calculate_EAR(lefteye)
                right_EAR = functionUtils.calculate_EAR(righteye)

                # Avg of left and right eye EAR
                avg = (left_EAR + right_EAR) / 2

                if avg < self.blink_thresh:
                    self.count_frame += 1  # incrementing the frame count
                    cv2.putText(frame, "1", (30, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    self.blink += 1
                else:
                    if self.count_frame >= self.succesful_frames:

                        cv2.putText(frame, "2", (30, 30),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    else:
                        self.count_frame = 0
                        cv2.putText(frame, "3", (30, 30),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(
                frame,
                str("Elapsed Time: " + elapsed_time_formatted),
                (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2,
            )
            cv2.imshow("window", frame)
            # tracker = liveTimeTracking.LiveTimeTracker()
            # tracker.start_timer(liveTimeTracking.process_elapsed_time)
            if cv2.waitKey(1) == 27:
                cam.release()
                cv2.destroyAllWindows()
                break

    def check_distracted(self, results):
        if results.face_landmarks:
            hl = results.face_landmarks.landmark
            left_pt_x = hl[LEFT_FACE_PT].x
            right_pt_x = hl[RIGHT_FACE_PT].x
            center_pt_x = (right_pt_x + left_pt_x) / 2
            nose_pt = hl[NOSE_FACE_PT].x

            dist_lr = (right_pt_x - left_pt_x) / 2

            if abs(nose_pt - center_pt_x) / dist_lr > FACE_TURNING_THRESHOLD:
                print("turned")
                # add to distracted time
