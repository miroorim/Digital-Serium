import cv2
import utils
import time
import numpy as np

cap = cv2.VideoCapture(0)
h, w, c = cap.read()[1].shape

pose = utils.Pose()
screen = utils.Screen(w, h)


while True:
    success, img = cap.read()
    
    pose_landmarks, img = pose.findPose(img, draw=screen.buttons[0].state)
    screen.draw(img, pose_landmarks)

    cv2.imshow("Image", img)
    cv2.waitKey(1)
