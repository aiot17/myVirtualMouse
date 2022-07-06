# import cv2
# import mediapipe
# import numpy
# import autopy

# cap = cv2.VideoCapture(0)
# initHand = mediapipe.solutions.hands  # Initializing mediapipe
# # Object of mediapipe with "arguments for the hands module"
# mainHand = initHand.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.8)
# draw = mediapipe.solutions.drawing_utils  # Object to draw the connections between each finger index
# wScr, hScr = autopy.screen.size()  # Outputs the high and width of the screen (1920 x 1080)
# pX, pY = 0, 0  # Previous x and y location
# cX, cY = 0, 0  # Current x and y location


# def handLandmarks(colorImg):
#     landmarkList = []  # Default values if no landmarks are tracked

#     landmarkPositions = mainHand.process(colorImg)  # Object for processing the video input
#     landmarkCheck = landmarkPositions.multi_hand_landmarks  # Stores the out of the processing object (returns False on empty)
#     if landmarkCheck:  # Checks if landmarks are tracked
#         for hand in landmarkCheck:  # Landmarks for each hand
#             for index, landmark in enumerate(hand.landmark):  # Loops through the 21 indexes and outputs their landmark coordinates (x, y, & z)
#                 draw.draw_landmarks(img, hand, initHand.HAND_CONNECTIONS)  # Draws each individual index on the hand with connections
#                 h, w, c = img.shape  # Height, width and channel on the image
#                 centerX, centerY = int(landmark.x * w), int(landmark.y * h)  # Converts the decimal coordinates relative to the image for each index
#                 landmarkList.append([index, centerX, centerY])  # Adding index and its coordinates to a list

#     return landmarkList


# def fingers(landmarks):
#     fingerTips = []  # To store 4 sets of 1s or 0s
#     tipIds = [4, 8, 12, 16, 20]  # Indexes for the tips of each finger
    
#     # Check if thumb is up
#     if landmarks[tipIds[0]][1] > lmList[tipIds[0] - 1][1]:
#         fingerTips.append(1)
#     else:
#         fingerTips.append(0)
    
#     # Check if fingers are up except the thumb
#     for id in range(1, 5):
#         if landmarks[tipIds[id]][2] < landmarks[tipIds[id] - 3][2]:  # Checks to see if the tip of the finger is higher than the joint
#             fingerTips.append(1)
#         else:
#             fingerTips.append(0)

#     return fingerTips


# while True:
#     check, img = cap.read()  # Reads frames from the camera
#     imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Changes the format of the frames from BGR to RGB
#     # imgRGB = cv2.flip(imgRGB,1)
#     lmList = handLandmarks(imgRGB)
#     print(lmList)
#     cv2.rectangle(img, (75, 75), (640 - 75, 480 - 75), (255, 0, 255), 2)

#     if len(lmList) != 0:
#         x1, y1 = lmList[8][1:]  # Gets index 8s x and y values (skips index value because it starts from 1)
#         x2, y2 = lmList[12][1:]  # Gets index 12s x and y values (skips index value because it starts from 1)
#         finger = fingers(lmList)  # Calling the fingers function to check which fingers are up
        
#         if finger[1] == 1 and finger[2] == 0:  # Checks to see if the pointing finger is up and thumb finger is down
#             x3 = numpy.interp(x1, (75, 640 - 75), (0, wScr))  # Converts the width of the window relative to the screen width
#             y3 = numpy.interp(y1, (75, 480 - 75), (0, hScr))  # Converts the height of the window relative to the screen height
            
#             cX = pX + (x3 - pX) / 7  # Stores previous x locations to update current x location
#             cY = pY + (y3 - pY) / 7  # Stores previous y locations to update current y location
            
#             # autopy.mouse.move(wScr-cX, cY)  # Function to move the mouse to the x3 and y3 values (wSrc inverts the direction)
#             autopy.mouse.move(wScr-cX, cY)
#             pX, pY = cX, cY  # Stores the current x and y location as previous x and y location for next loop

#         if finger[1] == 0 and finger[0] == 1:  # Checks to see if the pointer finger is down and thumb finger is up
#             autopy.mouse.click()  # Left click
            
#     cv2.imshow("Webcam", img)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

'''以下7.4早上修改'''
# from cmath import pi
# from cv2 import mean
# import mediapipe as mp
# import cv2
# import numpy as np
# from mediapipe.framework.formats import landmark_pb2
# import time
# from math import sqrt
# import win32api
# import pyautogui

# '''以下是影像畫圖,手勢相關,與串流的初始化'''
# mp_drawing = mp.solutions.drawing_utils
# mp_hands = mp.solutions.hands 
# video = cv2.VideoCapture(0)
# '''以上是影像畫圖,手勢相關,與串流的初始化'''
# # currentX, currentY = 0,0 # 用除法縮小前後座標的方式,指標會抖動,效果不好
# # previousX, previousY = 0,0 # 用除法縮小前後座標的方式,指標會抖動,效果不好
# '''以下兩個串列,侍衛移動平均值設置,讓xy座標可以各存入七個座標後再取平均值'''
# movingX = []
# movingY = []
# '''以上兩個串列,侍衛移動平均值設置,讓xy座標可以各存入七個座標後再取平均值'''

# '''以下設置t/f閘門,讓滑鼠點擊手勢向下時只執行一次點擊動作,並且點擊完後恢復指尖座標(向上時)不會二度執行點擊'''
# switch = True
# '''以上設置t/f閘門,讓滑鼠點擊手勢向下時只執行一次點擊動作,並且點擊完後恢復指尖座標(向上時)不會二度執行點擊'''

# '''以下先將串流包進手勢使用的模組,如此flip的時候,手勢與座標圖式的位置才回一致'''
# with mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.8,max_num_hands=1) as hands: 
#     '''以下開啟串流'''
#     while video.isOpened():
#         _, frame = video.read()
#         image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         '''image是一個numpy多維陣列'''
#         '''image.shape是(x,y,3),x=高,y=寬'''
#         # print(image.shape)
#         # print(image)
#         # print(frame)
#         # print(hands) # 純粹物件
#         image = cv2.flip(image, 1) # 圖像左右翻轉
#         image = cv2.resize(image,(1280,840)) # 1280是寬,840是高
#         imageHeight, imageWidth, _ = image.shape # 取出串流畫面的長與寬值
#         # print(image)
#         # print(image.shape)
#         # print(imageHeight," : ",imageWidth)
#         results = hands.process(image) # 將串流畫面包進手勢標示物件去
#         # print(f"results: {results}")
#         image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR) # 轉回openCV可撥放的BGR格式
#         # print(image)
#         # print(results.multi_hand_landmarks)
#         # results = hands.process(image) # 寫在這邊時常偵測不到
#         '''下面是在螢幕上畫手得座標示意圖;可移除,滑鼠依然可以偵測'''
#         if results.multi_hand_landmarks:
#             for _, hand in enumerate(results.multi_hand_landmarks):
#                 mp_drawing.draw_landmarks(image, hand, mp_hands.HAND_CONNECTIONS, 
#                                         mp_drawing.DrawingSpec(color=(250, 44, 250), thickness=2, circle_radius=5),
#                                          )
#                 # print(hand)
#         '''上面是在螢幕上畫手得座標示意圖'''
#         # results.multi_hand_landmarks是將座標寫入字典,再將字典包入串列
#         fingerMap = [] # 裝入每一次while回圈內每節手部座標的xy值
#         # 當results.multi_hand_landmarks != None, 手部移開畫面後不會造成錯誤訊息
#         if results.multi_hand_landmarks != None:
#           for handLandmarks in results.multi_hand_landmarks:
#             '''handLandmarks將字典手部座標從串列中拿出來'''
#             '''mp_hands.HandLandmark是具enum的物件'''
#             # print(results.multi_hand_landmarks)
#             # print(handLandmarks.landmark) # 取出所有的座標
#             for point in mp_hands.HandLandmark:
#                 '''point顯示手掌上每一個座標的標示名稱,列如食指拇指,用0~20表示'''
#                 '''handLandmarks.landmark是每一個while迴圈中,每一個手部節點的xyz座標'''
#                 # print(f"indexTip{handLandmarks.landmark[8]}") # 只取了indexTip的x座標
#                 # print(len(handLandmarks.landmark)) # 有21項串列
#                 # print(f"point: {point}")
#                 temp = int(f"{point}") # 用這種方式取出point的值才會是0~20,不然會顯示成物件本身
#                 onePosition = [] # 取出每一個節點的名稱,0~20,作為後續儲存的索引值(index)
#                 onePosition.append(temp)
#                 # print(onePosition[0])
#                 '''normalizedLandmark用索引值將座標xyz一個個單獨取出來(x,y)型態'''
#                 normalizedLandmark = handLandmarks.landmark[point]
#                 # print(normalizedLandmark) # 顯示xyz座標
#                 # print(f"x: {normalizedLandmark.x}")
#                 # print(f"y: {normalizedLandmark.y}")
#                 '''顯示normalizedLandmark的xyz座標值(0~1之間)並轉換成螢幕座標(整數畫素質) => (x,y)'''
#                 pixelCoordinatesLandmark = mp_drawing._normalized_to_pixel_coordinates(normalizedLandmark.x, normalizedLandmark.y, imageWidth, imageHeight)
#                 # print("-----上分隔線----")
#                 # print(pixelCoordinatesLandmark) # 顯示normalizedLandmark的xyz座標並轉換成螢幕座標(畫素質) => (x,y)
#                 # print("-----下分隔線----")
#                 # print(type(pixelCoordinatesLandmark))

#                 # point=str(point)
#                 # print(point)
#                 '''以下將座標放入串列中,用if判斷有否xy座標(手移除鏡頭外會變成None,造成下面append出錯,故,需要加一個判斷是否為空值,再進行添加)'''
#                 # onePosition.append(point)
#                 if pixelCoordinatesLandmark != None:
#                     onePosition.append(pixelCoordinatesLandmark[0])
#                     onePosition.append(pixelCoordinatesLandmark[1])
#                     fingerMap.append(onePosition)
#                     # try:
#                     #     print(fingerMap)
#                     #     # print(f"x: {fingerMap[0][1]}, y: {fingerMap[0][2]}")
#                     #     print(f"x: {fingerMap[8][1]}, y: {fingerMap[8][2]}")
#                     #     # win32api.SetCursorPos((fingerMap[8][1],fingerMap[8][2]))
#                     # except:
#                     #     pass
#                 '''以上將座標放入串列中,用if判斷有否xy座標(手移除鏡頭外會變成None,造成下面append出錯,故,需要加一個判斷是否為空值,再進行添加)'''
#             # if fingerMap[8][1] and fingerMap[8][2]:
#             # if fingerMap[8][1]!= None and fingerMap[8][2]!=None:
#                 # print(f"x: {fingerMap[8][1]}, y: {fingerMap[8][2]}")
#             try:
#                 # print(fingerMap)
#                 # print(fingerMap[0][1],fingerMap[0][2])
#                 '''以下測試current&previous location方式;可行但效果不如移動平均值,會輕微抖動'''
#                 # currentX = int(previousX + (fingerMap[0][1] - previousX) / 7)
#                 # currentY = int(previousY + (fingerMap[0][2] - previousX) / 7)
#                 # print(f"x:{currentX},y: {currentY}")
#                 # win32api.SetCursorPos((currentX*5,currentY*2))
#                 # win32api.SetCursorPos((currentX,currentY))
#                 # win32api.SetCursorPos((currentX*3-600,currentY*2-500)) # 指標會顫抖第一次的參數,可用
#                 '''以上測試current&previous location方式'''
                
#                 '''以下是虛擬滑鼠移動功能區塊'''
#                 '''以下移動平均值方式,幾乎消除了滑鼠抖動'''
#                 movingX.append(fingerMap[0][1])
#                 if len(movingX) > 7 : # 取七個座標的平均值表較滑鼠指標表現較平穩,超過七個就移除第一順位索引值
#                     movingX.pop(0)
#                 movingY.append(fingerMap[0][2])
#                 if len(movingY) > 7:
#                     movingY.pop(0)
#                 xMean = sum(movingX) // len(movingX) # 取xy分別的平均值放入win32api執行滑鼠移動
#                 yMean = sum(movingY) // len(movingY)
#                 # print(xMean,yMean,'mX=',movingX,'mY=',movingY)
#                 # win32api.SetCursorPos((xMean,yMean))
#                 # win32api.SetCursorPos((fingerMap[0][1]*3-600,fingerMap[0][2]*2-500))
#                 win32api.SetCursorPos((xMean*7-2500,yMean*6-3000)) # 教室電腦,浮標移動比例已調整好,可用了
#                 '''以上是虛擬滑鼠移動功能區塊'''
#             except:
#                 pass

#             try:
#                 '''以下是滑鼠點擊功能區塊'''
#                 '''以下滑鼠點擊手勢向下時只執行一次點擊動作,並且點擊完後恢復指尖座標(向上時)不會二度執行點擊'''  
#                 if fingerMap[8][2] >= fingerMap[7][2]:
#                     if switch == True:
#                         print("downward => click")
#                         pyautogui.click()
#                         switch = False
#                 if fingerMap[8][2] <= fingerMap[7][2]:
#                      if switch == False:
#                         print("upward => no click")
#                         switch = True
#                 '''以上是滑鼠點擊功能區塊'''

#                 '''以下寫法,可以執行滑鼠左鍵,但餘數為零的方式讓點擊效果依隨機執行,並不理想,而且當條件滿足時,點擊動作會連續執行,不理想'''
#                 # if fingerMap[8][2] >= fingerMap[7][2]:   
#                 #     click=click+1
#                 #     print("single click")
#                 #     if click%3==0:
#                 #         print("點擊成功")
#                 #         pyautogui.click()
#                 '''以上寫法,可以執行滑鼠左鍵,但餘數為零的方式讓點擊效果依隨機執行,並不理想,而且當條件滿足時,點擊動作會連續執行,不理想'''
#             except:
#                 pass
 
#         cv2.imshow('Hand Tracking', image) # 有這條程式才能開啟串流
        
#         '''點擊串流畫面,按下q結束程式'''
#         if cv2.waitKey(10) & 0xFF == ord('q'):
#             break
# video.release() # 結束程式執行,釋放串流物件資源
'''以上7.4早上修改'''

'''------------下面是虛擬滑鼠7/5晚上修改後的檔案------------'''
from cmath import pi
from cv2 import mean
import mediapipe as mp
import cv2
import numpy as np
from mediapipe.framework.formats import landmark_pb2
import time
from math import sqrt
import win32api
import pyautogui
import math

'''以下是影像畫圖,手勢相關,與串流的初始化'''
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands 
video = cv2.VideoCapture(0)
'''以上是影像畫圖,手勢相關,與串流的初始化'''
# currentX, currentY = 0,0 # 用除法縮小前後座標的方式,指標會抖動,效果不好
# previousX, previousY = 0,0 # 用除法縮小前後座標的方式,指標會抖動,效果不好
'''以下兩個串列,侍衛移動平均值設置,讓xy座標可以各存入七個座標後再取平均值'''
movingX = []
movingY = []
'''以上兩個串列,侍衛移動平均值設置,讓xy座標可以各存入七個座標後再取平均值'''

'''一下半徑用參數'''
previousX = 0
previousY = 0
currentX = 0
currentY = 0
r = 4
'''一上半徑用參數'''


'''以下設置t/f閘門,讓滑鼠點擊手勢向下時只執行一次點擊動作,並且點擊完後恢復指尖座標(向上時)不會二度執行點擊'''
switch = True
'''以上設置t/f閘門,讓滑鼠點擊手勢向下時只執行一次點擊動作,並且點擊完後恢復指尖座標(向上時)不會二度執行點擊'''

'''以下先將串流包進手勢使用的模組,如此flip的時候,手勢與座標圖式的位置才回一致'''
with mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.8,max_num_hands=1) as hands: 
    '''以下開啟串流'''
    while video.isOpened():
        _, frame = video.read()
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        '''image是一個numpy多維陣列'''
        '''image.shape是(x,y,3),x=高,y=寬'''
        # print(image.shape)
        # print(image)
        # print(frame)
        # print(hands) # 純粹物件
        image = cv2.flip(image, 1) # 圖像左右翻轉
        image = cv2.resize(image,(1280,840)) # 1280是寬,840是高
        imageHeight, imageWidth, _ = image.shape # 取出串流畫面的長與寬值
        # print(image)
        # print(image.shape)
        # print(imageHeight," : ",imageWidth)
        results = hands.process(image) # 將串流畫面包進手勢標示物件去
        # print(f"results: {results}")
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR) # 轉回openCV可撥放的BGR格式
        # print(image)
        # print(results.multi_hand_landmarks)
        # results = hands.process(image) # 寫在這邊時常偵測不到
        '''下面是在螢幕上畫手得座標示意圖;可移除,滑鼠依然可以偵測'''
        if results.multi_hand_landmarks:
            for _, hand in enumerate(results.multi_hand_landmarks):
                mp_drawing.draw_landmarks(image, hand, mp_hands.HAND_CONNECTIONS, 
                                        mp_drawing.DrawingSpec(color=(250, 44, 250), thickness=2, circle_radius=5),
                                         )
                # print(hand)
        '''上面是在螢幕上畫手得座標示意圖'''
        # results.multi_hand_landmarks是將座標寫入字典,再將字典包入串列
        fingerMap = [] # 裝入每一次while回圈內每節手部座標的xy值
        # 當results.multi_hand_landmarks != None, 手部移開畫面後不會造成錯誤訊息
        if results.multi_hand_landmarks != None:
          for handLandmarks in results.multi_hand_landmarks:
            '''handLandmarks將字典手部座標從串列中拿出來'''
            '''mp_hands.HandLandmark是具enum的物件'''
            # print(results.multi_hand_landmarks)
            # print(handLandmarks.landmark) # 取出所有的座標
            for point in mp_hands.HandLandmark:
                '''point顯示手掌上每一個座標的標示名稱,列如食指拇指,用0~20表示'''
                '''handLandmarks.landmark是每一個while迴圈中,每一個手部節點的xyz座標'''
                # print(f"indexTip{handLandmarks.landmark[8]}") # 只取了indexTip的x座標
                # print(len(handLandmarks.landmark)) # 有21項串列
                # print(f"point: {point}")
                temp = int(f"{point}") # 用這種方式取出point的值才會是0~20,不然會顯示成物件本身
                onePosition = [] # 取出每一個節點的名稱,0~20,作為後續儲存的索引值(index)
                onePosition.append(temp)
                # print(onePosition[0])
                '''normalizedLandmark用索引值將座標xyz一個個單獨取出來(x,y)型態'''
                normalizedLandmark = handLandmarks.landmark[point]
                # print(normalizedLandmark) # 顯示xyz座標
                # print(f"x: {normalizedLandmark.x}")
                # print(f"y: {normalizedLandmark.y}")
                '''顯示normalizedLandmark的xyz座標值(0~1之間)並轉換成螢幕座標(整數畫素質) => (x,y)'''
                pixelCoordinatesLandmark = mp_drawing._normalized_to_pixel_coordinates(normalizedLandmark.x, normalizedLandmark.y, imageWidth, imageHeight)
                # print("-----上分隔線----")
                # print(pixelCoordinatesLandmark) # 顯示normalizedLandmark的xyz座標並轉換成螢幕座標(畫素質) => (x,y)
                # print("-----下分隔線----")
                # print(type(pixelCoordinatesLandmark))

                # point=str(point)
                # print(point)
                '''以下將座標放入串列中,用if判斷有否xy座標(手移除鏡頭外會變成None,造成下面append出錯,故,需要加一個判斷是否為空值,再進行添加)'''
                # onePosition.append(point)
                if pixelCoordinatesLandmark != None:
                    onePosition.append(pixelCoordinatesLandmark[0])
                    onePosition.append(pixelCoordinatesLandmark[1])
                    fingerMap.append(onePosition)
                    # try:
                    #     print(fingerMap)
                    #     # print(f"x: {fingerMap[0][1]}, y: {fingerMap[0][2]}")
                    #     print(f"x: {fingerMap[8][1]}, y: {fingerMap[8][2]}")
                    #     # win32api.SetCursorPos((fingerMap[8][1],fingerMap[8][2]))
                    # except:
                    #     pass
                '''以上將座標放入串列中,用if判斷有否xy座標(手移除鏡頭外會變成None,造成下面append出錯,故,需要加一個判斷是否為空值,再進行添加)'''
            # if fingerMap[8][1] and fingerMap[8][2]:
            # if fingerMap[8][1]!= None and fingerMap[8][2]!=None:
                # print(f"x: {fingerMap[8][1]}, y: {fingerMap[8][2]}")
            try:
                # print(fingerMap)
                # print(fingerMap[0][1],fingerMap[0][2])
                '''以下測試current&previous location方式;可行但效果不如移動平均值,會輕微抖動'''
                # currentX = int(previousX + (fingerMap[0][1] - previousX) / 7)
                # currentY = int(previousY + (fingerMap[0][2] - previousX) / 7)
                # print(f"x:{currentX},y: {currentY}")
                # win32api.SetCursorPos((currentX*5,currentY*2))
                # win32api.SetCursorPos((currentX,currentY))
                # win32api.SetCursorPos((currentX*3-600,currentY*2-500)) # 指標會顫抖第一次的參數,可用
                '''以上測試current&previous location方式'''
                
                '''***以下測試半徑比大小,看能否完全移除指標抖動'''
                currentX = fingerMap[0][1]
                currentY = fingerMap[0][2]

                if ((currentX-previousX)**2+(currentY-previousY)**2) <= ((previousX-(previousX+r))**2+(previousY-(previousY+r))**2):
                    X,Y = previousX,previousY
                    print(f"previous: {X},{Y}")
                    # win32api.SetCursorPos((X*6-2500,Y*6-2500)) # 家用
                    win32api.SetCursorPos((X*7-2500,Y*6-3000)) # 教室電腦,浮標移動比例已調整好,可用了
                else:
                    previousX, previousY = currentX,currentY
                    X,Y = previousX,previousY
                    print(f"current: {X},{Y}")
                    # win32api.SetCursorPos((X*6-2500,Y*6-2500)) # 家用
                    win32api.SetCursorPos((X*7-2500,Y*6-3000)) # 教室電腦,浮標移動比例已調整好,可用了
                '''***以上測試半徑比大小,看能否完全移除指標抖動'''

                '''以下是虛擬滑鼠移動功能區塊'''
                '''以下移動平均值方式,幾乎消除了滑鼠抖動'''
                # movingX.append(fingerMap[0][1])
                # if len(movingX) > 7 : # 取七個座標的平均值表較滑鼠指標表現較平穩,超過七個就移除第一順位索引值
                #     movingX.pop(0)
                # movingY.append(fingerMap[0][2])
                # if len(movingY) > 7:
                #     movingY.pop(0)
                # xMean = sum(movingX) // len(movingX) # 取xy分別的平均值放入win32api執行滑鼠移動
                # yMean = sum(movingY) // len(movingY)
                # # print(xMean,yMean,'mX=',movingX,'mY=',movingY)
                # # win32api.SetCursorPos((xMean,yMean))
                # # win32api.SetCursorPos((fingerMap[0][1]*3-600,fingerMap[0][2]*2-500))
                # win32api.SetCursorPos((xMean*7-2500,yMean*6-3000)) # 教室電腦,浮標移動比例已調整好,可用了
                '''以上是虛擬滑鼠移動功能區塊'''
            except:
                pass

            try:
                '''以下是滑鼠點擊功能區塊'''
                '''以下滑鼠點擊手勢向下時只執行一次點擊動作,並且點擊完後恢復指尖座標(向上時)不會二度執行點擊'''  
                if fingerMap[8][2] >= fingerMap[7][2]:
                    if switch == True:
                        print("downward => click")
                        pyautogui.click()
                        switch = False
                if fingerMap[8][2] <= fingerMap[7][2]:
                     if switch == False:
                        print("upward => no click")
                        switch = True
                '''以上是滑鼠點擊功能區塊'''

                '''以下寫法,可以執行滑鼠左鍵,但餘數為零的方式讓點擊效果依隨機執行,並不理想,而且當條件滿足時,點擊動作會連續執行,不理想'''
                # if fingerMap[8][2] >= fingerMap[7][2]:   
                #     click=click+1
                #     print("single click")
                #     if click%3==0:
                #         print("點擊成功")
                #         pyautogui.click()
                '''以上寫法,可以執行滑鼠左鍵,但餘數為零的方式讓點擊效果依隨機執行,並不理想,而且當條件滿足時,點擊動作會連續執行,不理想'''
            except:
                pass
 
        cv2.imshow('Hand Tracking', image) # 有這條程式才能開啟串流
        
        '''點擊串流畫面,按下q結束程式'''
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
video.release() # 結束程式執行,釋放串流物件資源
'''上面是虛擬滑鼠7/5晚上修改後的檔案'''


