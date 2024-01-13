import cv2
import mediapipe as mp
from config import (
    LEFT_FACE_PT,
    RIGHT_FACE_PT,
    NOSE_FACE_PT,
    FACE_TURNING_THRESHOLD,
)


mp_holistic = mp.solutions.holistic
holistic_model = mp_holistic.Holistic(
    min_detection_confidence=0.5, min_tracking_confidence=0.5
)

mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
capture = cv2.VideoCapture(0)

previousTime = 0
currentTime = 0

while capture.isOpened():
    ret, frame = capture.read()
    frame = cv2.resize(frame, (800, 600))

    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    image.flags.writeable = False
    results = holistic_model.process(image)
    image.flags.writeable = True

    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    if results.face_landmarks:
        hl = results.face_landmarks.landmark
        left_pt_x = hl[LEFT_FACE_PT].x
        right_pt_x = hl[RIGHT_FACE_PT].x
        center_pt_x = (right_pt_x + left_pt_x) / 2
        nose_pt = hl[NOSE_FACE_PT].x

        dist = (right_pt_x - left_pt_x) / 2

        if abs(nose_pt - center_pt_x) / dist > FACE_TURNING_THRESHOLD:
            print("turned")

    mp_drawing.draw_landmarks(
        image,
        results.face_landmarks,
        mp_holistic.FACEMESH_CONTOURS,
        mp_drawing.DrawingSpec(
            color=(255, 0, 255), thickness=1, circle_radius=1
        ),
        mp_drawing.DrawingSpec(
            color=(0, 255, 255), thickness=1, circle_radius=1
        ),
    )

    cv2.imshow("Facial and Hand Landmarks", image)

    if cv2.waitKey(5) & 0xFF == ord("q"):
        break

capture.release()
cv2.destroyAllWindows()
