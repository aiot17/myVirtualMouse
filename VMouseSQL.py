import mediapipe as mp
import cv2
import numpy as np
import pyautogui
import autopy
import connect

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands 
video = cv2.VideoCapture(0)

previousX = 0
previousY = 0
currentX = 0
currentY = 0
r = 3.5

wScr,hScr = autopy.screen.size()
frameRx = 400
frameRy = 100
wCam,hCam = 1280,840

movingX = []
movingY = []

switch = True

with mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.8,max_num_hands=1) as hands: 
    
    while video.isOpened():
        _, frame = video.read()
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        image = cv2.flip(image, 1) 
        image = cv2.resize(image,(wCam,hCam)) 
        imageHeight, imageWidth, _ = image.shape 
        results = hands.process(image) 
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR) 
        
        cv2.rectangle(image,(frameRx,frameRy),(wCam-frameRx,hCam-frameRy),(255,0,255),2)
        
        if results.multi_hand_landmarks:
            for _, hand in enumerate(results.multi_hand_landmarks):
                mp_drawing.draw_landmarks(image, hand, mp_hands.HAND_CONNECTIONS, 
                                        mp_drawing.DrawingSpec(color=(250, 44, 250), thickness=2, circle_radius=5),
                                         )
        fingerMap = [] 

        if results.multi_hand_landmarks != None:
          for handLandmarks in results.multi_hand_landmarks:
            for point in mp_hands.HandLandmark:
                temp = int(f"{point}") 
                onePosition = []
                onePosition.append(temp)
                normalizedLandmark = handLandmarks.landmark[point]
                pixelCoordinatesLandmark = mp_drawing._normalized_to_pixel_coordinates(normalizedLandmark.x, normalizedLandmark.y, imageWidth, imageHeight)

                if pixelCoordinatesLandmark != None:
                    onePosition.append(pixelCoordinatesLandmark[0])
                    onePosition.append(pixelCoordinatesLandmark[1])
                    fingerMap.append(onePosition)
            try:
                x = fingerMap[0][1]
                y = fingerMap[0][2]
                
                movingX.append(x)
                if len(movingX) > 4:
                    movingX.pop(0)
                movingY.append(y)
                if len(movingY) > 4:
                    movingY.pop(0)

                currentX = sum(movingX)/len(movingX)
                currentY = sum(movingY)/len(movingY)

                if ((int(currentX-previousX))**2+(int(currentY-previousY))**2) <= (int(previousX-(previousX+r))**2+int(previousY-(previousY+r))**2):
                    tempX, tempY = int(previousX),int(previousY) 
                    newX = np.interp(tempX,(frameRx,wCam-frameRx),(0,wScr)) 
                    newY = np.interp(tempY*2-650,(frameRy,hCam-frameRy),(0,hScr))    
                    autopy.mouse.move(newX,newY)
                
                else:
                    previousX = currentX
                    previousY = currentY
                    newX = np.interp(previousX,(frameRx,wCam-frameRx),(0,wScr))
                    newY = np.interp(previousY*2-650,(frameRy,hCam-frameRy),(0,hScr))
                    autopy.mouse.move(newX,newY)
            except:
                pass

            try:
                if fingerMap[8][2] >= fingerMap[7][2]:
                    if switch == True:
                        pyautogui.click()
                        switch = False
                if fingerMap[8][2] <= fingerMap[7][2]:
                     if switch == False:
                        switch = True
            except:
                pass
 
        cv2.imshow('Hand Tracking', image)
        
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
video.release()