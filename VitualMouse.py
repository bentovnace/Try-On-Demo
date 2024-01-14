import cv2 as cv
import mediapipe
import numpy as np
import pyautogui
import os


cv_cuda_available = cv.cuda.getCudaEnabledDeviceCount() > 0

mphands = mediapipe.solutions.hands
if cv_cuda_available:
    detector = mphands.Hands(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5, model_complexity=1)
else:
    detector = mphands.Hands()

draw = mediapipe.solutions.drawing_utils

wscreen,  hscreen = pyautogui.size()
px, py = 0, 0
cx, cy = 0, 0

def handLandmarks(img, frame):
    landmarkList = []
    landmarkPositions = detector.process(img)

    landmarkCheck = landmarkPositions.multi_hand_landmarks

    if landmarkCheck:
        for hand in landmarkCheck:
            for i, landmark in enumerate(hand.landmark):
                draw.draw_landmarks(frame, hand, mphands.HAND_CONNECTIONS)
                h, w, c = img.shape
                centerX, centerY = int(landmark.x*w), int(landmark.y*h)
                landmarkList.append([i, centerX, centerY])
    return landmarkList, frame

def fingers(landmarks):
    fingerTips = []
    tipIds = [4, 8, 12, 16, 20]

    if landmarks[4][1] > landmarks[3][1]:
        fingerTips.append(1)
    else:
        fingerTips.append(0)

    for i in range(1, 5):
        if landmarks[tipIds[i]][2] < landmarks[tipIds[i] - 3][2]:
            fingerTips.append(1)
        else:
            fingerTips.append(0)
    return fingerTips



cap = cv.VideoCapture(0, cv.CAP_DSHOW)
if cv_cuda_available:
    cap.set(cv.CAP_PROP_CUDA_DEVICE, 0)  # Set the CUDA device
while cap.isOpened():
    ret, frame = cap.read()
    if ret:
        rgbFrame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        lmList, frame = handLandmarks(rgbFrame, frame)

        if len(lmList) !=0:
            x1, y1 = lmList[8][1:]
            x2, y2 = lmList[12][1:]
            finger = fingers(lmList)

            if finger[1] == 1 and finger[2] == 0:
                x3 = np.interp(x1, (0, int(cap.get(cv.CAP_PROP_FRAME_WIDTH))), (0, wscreen))
                y3 = np.interp(y1, (0, int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))), (0, hscreen))

                cx = px + (x3 - px)/7
                cy = py + (y3 - py)/7

                if (abs(cx-px)+abs(cy-py))>3:
                    pyautogui.moveTo(wscreen-cx, cy)
                px, py = cx, cy

            if finger[1] == 0 and finger[0]==1:
                pyautogui.click()

            if finger [0] == finger[1] == finger[2] == finger[3] == 0 and finger[4] == 1:
                pyautogui.scroll(10)

            if finger [0] == finger[1] == finger[2] == finger[3] == 1 and finger[4] == 0:
                pyautogui.scroll(-10)
        cv.imshow('frame', frame)
        if cv.waitKey(1) == 25:
            break
cap.release()
cv.destroyAllWindows()