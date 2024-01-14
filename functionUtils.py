# for calculating dist b/w the eye landmarks
from scipy.spatial import distance as dist
# to get the landmark ids of the left and right eyes
# you can do this manually too

# defining a function to calculate the Eye Aspect Ratio
def calculate_EAR(eye):
    # calculate the vertical distances
    y1 = dist.euclidean(eye[1], eye[5])
    y2 = dist.euclidean(eye[2], eye[4])

    # calculate the horizontal distance
    x1 = dist.euclidean(eye[0], eye[3])

    # calculate the EAR
    ear = (y1 + y2) / x1
    return ear