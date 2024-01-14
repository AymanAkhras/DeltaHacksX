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
        self.elapsedTime = 0
        self.distractedTime = 0
        self.blink = 0
        # Variables
        self.blink_thresh = 0.45
        self.succ_frame = 2
        self.count_frame = 0
        self.prevDistractedTs = 0

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

        while True:
            print(self.distractedTime)
            x = []
            _, frm = cam.read()
            frm = cv2.flip(frm, 1)
            res = holis.process(cv2.cvtColor(frm, cv2.COLOR_BGR2RGB))
            y.append(x)

            drawing.draw_landmarks(
                frm, res.face_landmarks, holistic.FACEMESH_CONTOURS
            )
            drawing.draw_landmarks(
                frm, res.left_hand_landmarks, hands.HAND_CONNECTIONS
            )
            drawing.draw_landmarks(
                frm, res.right_hand_landmarks, hands.HAND_CONNECTIONS
            )

            # if lookingAtScreen:
            end_time = time.perf_counter()
            self.elapsedTime = end_time - start_time
            elapsed_time_formatted = str(timedelta(seconds=self.elapsedTime))
            self.check_distracted(res, end_time)

            # Calculates Number of Blinks
            if cam.get(cv2.CAP_PROP_POS_FRAMES) == cam.get(
                cv2.CAP_PROP_FRAME_COUNT
            ):
                cam.set(cv2.CAP_PROP_POS_FRAMES, 0)
            else:
                _, frame = cam.read()
                frame = imutils.resize(frm, width=640)

                # converting frame to gray scale to
                # pass to detector
                img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

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
                    else:
                        if self.count_frame >= self.succ_frame:
                            cv2.putText(
                                frame,
                                "Blink Detected",
                                (30, 30),
                                cv2.FONT_HERSHEY_DUPLEX,
                                1,
                                (0, 200, 0),
                                1,
                            )
                        else:
                            self.count_frame = 0

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
