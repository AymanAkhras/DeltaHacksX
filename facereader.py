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


class FaceReader:
    def __init__(self):
        self.focusedTime = 0
        self.elapsedTime = 0
        self.distractedTime = 0

    def data_collection(self):
        cap = cv2.VideoCapture(0)
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
            _, frm = cap.read()
            frm = cv2.flip(frm, 1)
            res = holis.process(cv2.cvtColor(frm, cv2.COLOR_BGR2RGB))
            y.append(x)

            self.check_distracted(res)

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

            if focused:
                self.focusedTime += end_time - start_time
            else:
                self.distractedTime += self.focusedTime - end_time

            cv2.putText(
                frm,
                str("Elapsed Time: " + elapsed_time_formatted),
                (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2,
            )
            cv2.imshow("window", frm)
            # tracker = liveTimeTracking.LiveTimeTracker()
            # tracker.start_timer(liveTimeTracking.process_elapsed_time)
            if cv2.waitKey(1) == 27:  # esc
                cap.release()
                cv2.destroyAllWindows()
                break

    def check_distracted(self, results):
        if results.face_landmarks:
            hl = results.face_landmarks.landmark
            left_pt_x = hl[LEFT_FACE_PT].x
            right_pt_x = hl[RIGHT_FACE_PT].x
            center_pt_x = (right_pt_x + left_pt_x) / 2
            nose_pt = hl[NOSE_FACE_PT].x

            dist = (right_pt_x - left_pt_x) / 2

            if abs(nose_pt - center_pt_x) / dist > FACE_TURNING_THRESHOLD:
                print("turned")
                # add to distracted time
