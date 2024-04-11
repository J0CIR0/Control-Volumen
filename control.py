#@JOCIROPY
import cv2
import math
import numpy as np
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import mediapipe as mp
mode, modelComplexity, maxHands = False, 1, 1
detectionCon, trackCon = 0.5, 0.5
mpHands = mp.solutions.hands
hands = mpHands.Hands(mode, maxHands, modelComplexity, detectionCon, trackCon)
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volRange = volume.GetVolumeRange()
minVol, maxVol = volRange[0], volRange[1]
vol, volBar, volPerc = -20.0, 360, 20
while True:
    success, img = cap.read()
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)
    if results.multi_hand_landmarks:
        myHand = results.multi_hand_landmarks[0]
        puntos = [[id, int(lm.x * img.shape[1]), int(lm.y * img.shape[0])] for id, lm in enumerate(myHand.landmark)]
        x1, y1, x2, y2 = puntos[4][1:3] + puntos[8][1:3]
        cv2.circle(img, (x1, y1), 15, (0, 0, 0), cv2.FILLED)
        cv2.circle(img, (x2, y2), 15, (0, 0, 0), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 255, 255), 3)
        lengh = math.hypot(x2 - x1, y2 - y1)
        vol, volBar, volPerc = np.interp(lengh, [50, 300], [minVol, maxVol]), np.interp(lengh, [50, 300], [360, 150]), np.interp(lengh, [50, 300], [0, 100])
        volume.SetMasterVolumeLevelScalar(volPerc / 100, None)
    else:
        volume.SetMasterVolumeLevelScalar(volPerc / 100, None)
    cv2.rectangle(img, (560, int(volBar)), (600, 360), (0, 0, 0), cv2.FILLED)
    cVol = round(volume.GetMasterVolumeLevelScalar() * 100)
    cv2.putText(img, f'{cVol}', (560, 400), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 1, (0, 0, 0), 3)
    cv2.imshow("@jociropy", img)
    k = cv2.waitKey(1) & 0xFF
    if k == (27):
        break