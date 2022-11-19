import math
import time

import cv2
import mediapipe as mp

mpPose = mp.solutions.pose
mpLamdmark = mpPose.PoseLandmark

right_hand_id = [
    mpLamdmark.RIGHT_PINKY,
    mpLamdmark.RIGHT_INDEX,
    mpLamdmark.RIGHT_THUMB,
    mpLamdmark.RIGHT_WRIST,
]

head_id = [
    mpLamdmark.NOSE,
    mpLamdmark.LEFT_EYE_INNER,
    mpLamdmark.LEFT_EYE,
    mpLamdmark.LEFT_EYE_OUTER,
    mpLamdmark.RIGHT_EYE_INNER,
    mpLamdmark.RIGHT_EYE,
    mpLamdmark.RIGHT_EYE_OUTER,
    mpLamdmark.LEFT_EAR,
    mpLamdmark.RIGHT_EAR,
    mpLamdmark.MOUTH_LEFT,
    mpLamdmark.MOUTH_RIGHT,
]

# src joint, dst joint, angle,
T_position = [
    (mpLamdmark.LEFT_SHOULDER, mpLamdmark.RIGHT_SHOULDER, 0),
    (mpLamdmark.LEFT_ELBOW, mpLamdmark.RIGHT_ELBOW, 0),
    (mpLamdmark.LEFT_WRIST, mpLamdmark.RIGHT_WRIST, 0),
    (mpLamdmark.LEFT_SHOULDER, mpLamdmark.LEFT_WRIST, 0),
]

L_position = [
    (mpLamdmark.LEFT_SHOULDER, mpLamdmark.RIGHT_SHOULDER, 0),
    (mpLamdmark.LEFT_ELBOW, mpLamdmark.LEFT_SHOULDER, 0),
    (mpLamdmark.LEFT_WRIST, mpLamdmark.LEFT_ELBOW, 0),
    (mpLamdmark.RIGHT_HIP, mpLamdmark.RIGHT_ELBOW, math.pi/2),
    (mpLamdmark.RIGHT_ELBOW, mpLamdmark.RIGHT_WRIST, math.pi/2),
]

L_position_inv = [
    (mpLamdmark.RIGHT_SHOULDER, mpLamdmark.LEFT_SHOULDER, 0),
    (mpLamdmark.RIGHT_ELBOW, mpLamdmark.RIGHT_SHOULDER, 0),
    (mpLamdmark.RIGHT_WRIST, mpLamdmark.RIGHT_ELBOW, 0),
    (mpLamdmark.LEFT_HIP, mpLamdmark.LEFT_ELBOW, math.pi/2),
    (mpLamdmark.LEFT_ELBOW, mpLamdmark.LEFT_WRIST, math.pi/2),
]


def right_hand_center(pose_landmarks):
    x = 0
    y = 0
    count = 0
    for id, lm in enumerate(pose_landmarks.landmark):
        if id in right_hand_id:
            x += lm.x
            y += lm.y
            count += 1

    x /= count
    y /= count
    return x, y


def head_heading(pose_landmarks):
    """
    calculate the heading of the head from the center of the image using the nose and both eyes.
    """
    nose = pose_landmarks.landmark[mpLamdmark.NOSE]
    inner_left_eye = pose_landmarks.landmark[mpLamdmark.LEFT_EYE_INNER]
    inner_right_eye = pose_landmarks.landmark[mpLamdmark.RIGHT_EYE_INNER]
    outer_left_eye = pose_landmarks.landmark[mpLamdmark.LEFT_EYE_OUTER]
    outer_right_eye = pose_landmarks.landmark[mpLamdmark.RIGHT_EYE_OUTER]

    # calculate the distance between the outer right eye and the inner right eye
    x = outer_right_eye.x - inner_right_eye.x
    y = outer_right_eye.y - inner_right_eye.y
    right_eye_width = math.sqrt(x * x + y * y)

    # calculate the distance between the outer left eye and the inner left eye
    x = outer_left_eye.x - inner_left_eye.x
    y = outer_left_eye.y - inner_left_eye.y
    left_eye_width = math.sqrt(x * x + y * y)

    # estimate the y heading of the head
    heading = -math.atan(
        (right_eye_width - left_eye_width) / (nose.y - inner_left_eye.y))

    return heading, (nose.x, nose.y)


def head_bounds(pose_landmarks):
    x_min = 1
    x_max = 0
    y_min = 1
    y_max = 0
    for id, lm in enumerate(pose_landmarks.landmark):
        if id in head_id:
            if lm.x < x_min:
                x_min = lm.x
            if lm.x > x_max:
                x_max = lm.x
            if lm.y < y_min:
                y_min = lm.y
            if lm.y > y_max:
                y_max = lm.y

    # addjust the paddings
    y_min = y_min - (y_max - y_min) * 0.6
    y_max = y_max + (y_max - y_min) * 0.3

    return x_min, x_max, y_min, y_max


def is_in_position(pose_landmarks, position):
    """
    check if the pose is in the given position
    """
    in_position = [False for _ in position]
    ids = [p[0] for p in position]

    landmarks = list(enumerate(pose_landmarks.landmark))
    landmarks_ids = [i[0] for i in landmarks]

    for i, (src_id, dst_id, target_angle) in enumerate(position):

        # find the landmark for the source joint
        src_idx = landmarks_ids.index(src_id)
        dst_idx = landmarks_ids.index(dst_id)

        src_joint = landmarks[src_idx][1]
        dst_joint = landmarks[dst_idx][1]

        # calculate the angle between the two joints
        x = src_joint.x - dst_joint.x
        y = src_joint.y - dst_joint.y
        angle = math.atan2(y, x) % math.pi

        # check if the angle is in the target angle
        if abs(angle - target_angle) < 0.1 or abs(angle - target_angle) > math.pi - 0.1:
            in_position[i] = True
        else:
            return False

    return all(in_position)


def is_arm_aligned(pose_landmarks):
    """
    check if the wrist, elbows, and shoulders are aligned
    """

    landmarks = list(enumerate(pose_landmarks.landmark))
    landmarks_ids = [i[0] for i in landmarks]

    src_joints = [mpLamdmark.LEFT_WRIST, mpLamdmark.LEFT_ELBOW,
                  mpLamdmark.LEFT_SHOULDER, mpLamdmark.LEFT_SHOULDER]
    dst_joints = [mpLamdmark.RIGHT_WRIST, mpLamdmark.RIGHT_ELBOW,
                  mpLamdmark.RIGHT_SHOULDER, mpLamdmark.LEFT_WRIST]

    prev_angle = None
    for src_joint, dst_joint in zip(src_joints, dst_joints):
        src_idx = landmarks_ids.index(src_joint)
        dst_idx = landmarks_ids.index(dst_joint)

        src_joint = landmarks[src_idx][1]
        dst_joint = landmarks[dst_idx][1]

        # calculate the angle between the two joints
        x = src_joint.x - dst_joint.x
        y = src_joint.y - dst_joint.y
        angle = math.atan2(y, x) % math.pi

        if angle > math.pi / 2:
            angle = math.pi - angle

        if prev_angle is not None:
            if abs(angle - prev_angle) > 0.1:
                return False
        else:
            prev_angle = angle

    return True


class Screen:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.buttons = [
            Button(width-200, 0, 100, 125, "Etirements",
                   icon_path="icons/hand.png"),
            # Button(width-100, 125, 100, 125, "Cervicales",
            #        icon_path="icons/hand.png"),
        ]

        self.hand_color = (255, 0, 255)
        self.head_color = (0, 255, 0)
        self.joint_color = (0, 0, 255)

    def draw(self, img, pose_landmarks, debug=True):

        if not pose_landmarks:
            return
        # don't forget to flip the x coordinate

        # in_pos = is_in_position(pose_landmarks, T_position)
        # in_pos = is_in_position(pose_landmarks, L_position) or in_pos
        # in_pos = is_in_position(pose_landmarks, L_position_inv) or in_pos
        in_pos = is_arm_aligned(pose_landmarks)
        if in_pos:
            self.joint_color = (0, 255, 0)
        else:
            self.joint_color = (0, 0, 255)

        if self.buttons[0].state:
            for id, lm in enumerate(pose_landmarks.landmark):
                cv2.circle(img, (int((1 - lm.x) * self.width), int(lm.y * self.height)),
                           5, self.joint_color, cv2.FILLED)

        hx_min, hx_max, hy_min, hy_max = head_bounds(pose_landmarks)
        hx_min = int((1 - hx_min) * self.width)
        hx_max = int((1 - hx_max) * self.width)
        hy_min = int(hy_min * self.height)
        hy_max = int(hy_max * self.height)

        # draw head bounds
        if not self.buttons[0].state:
            cv2.rectangle(img, (hx_min, hy_min),
                          (hx_max, hy_max), self.head_color, 2)

        rx, ry = right_hand_center(pose_landmarks)
        rx = int((1 - rx) * self.width)
        ry = int(ry * self.height)

        heading, center = head_heading(pose_landmarks)

        # draw right hand
        cv2.circle(img, (rx, ry), 10, self.hand_color, cv2.FILLED)

        for b in self.buttons:
            b.click(rx, ry)
            b.draw(img)


class Button:
    def __init__(self, x, y, w, h, text, icon_path=None):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.text = text
        self.color = (0, 0, 255)

        if icon_path:
            # transparent image
            self.icon = cv2.imread(icon_path, cv2.IMREAD_UNCHANGED)
        else:
            self.icon = None

        self.timecount = 0
        self.lastclick = time.time()

        self.state = False

    def draw(self, img):

        if self.icon is not None:
            # resize the icon
            icon = cv2.resize(self.icon, (self.w, self.h))

            # add the transparent icon to the image
            alpha_s = icon[:, :, 3] / 255.0
            alpha_l = 1.0 - alpha_s

            for c in range(0, 3):
                img[self.y:self.y + self.h, self.x:self.x + self.w, c] = (
                    alpha_s * icon[:, :, c] + alpha_l *
                    img[self.y:self.y + self.h, self.x:self.x + self.w, c]
                )

        # draw the selection circle growing with time
        cv2.circle(img, (self.x + self.w//2, self.y + self.h//2),
                   int(self.timecount * 50), self.color, cv2.FILLED)

        cv2.putText(img, self.text, (self.x + 10, self.y + 50),
                    cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)

    def click(self, x, y):
        if self.x < x < self.x + self.w and self.y < y < self.y + self.h:

            if time.time() - self.lastclick > 2.0:
                self.color = (0, 255, 0)
                self.timecount += 1/20
            else:
                self.color = (255, 0, 0)

            if self.timecount > 1:
                self.timecount = 0
                self.lastclick = time.time()
                self.color = (0, 0, 255)
                self.state = not self.state
                return True
        else:
            self.color = (0, 0, 255)
            self.timecount = max(self.timecount - 1/20, 0)
        return False


class Pose():
    def __init__(self):
        self.pose = mpPose.Pose()
        self.mpDraw = mp.solutions.drawing_utils

    def findPose(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w, c = img.shape
        self.results = self.pose.process(imgRGB)
        if self.results.pose_landmarks:

            if draw:
                self.mpDraw.draw_landmarks(
                    img,
                    self.results.pose_landmarks,
                    mpPose.POSE_CONNECTIONS,
                )
        img = cv2.flip(img, 1)
        return self.results.pose_landmarks, img
