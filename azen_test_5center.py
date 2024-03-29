'''以下是7.13取五點平均值後再while5次的平均, 也可以'''
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
import autopy
import connect

connect.set_interval(connect.conn, 5)

'''Virtual Mouse complete version/虛擬滑鼠完整版'''

'''以下是影像畫圖,手勢相關,與串流的初始化'''
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands 
video = cv2.VideoCapture(0)
'''以上是影像畫圖,手勢相關,與串流的初始化'''

'''一下半徑用參數'''
previousX = 0
previousY = 0
currentX = 0
currentY = 0
r = 1
'''一上半徑用參數'''

'''以下取螢幕尺寸'''
wScr,hScr = autopy.screen.size()
frameRx = 400
frameRy = 250
wCam,hCam = 1280,840
'''以上取螢幕尺寸'''

'''以下兩個串列,侍衛移動平均值設置,讓xy座標可以各存入七個座標後再取平均值'''
movingX = []
movingY = []
accArr = [] # 臨時用來記錄 acc 觀測值
velArr = [] # 臨時用來記錄 vel(速度)觀測值
xArr = [] # 臨時用來記錄 x 觀測值
yArr = [] # 臨時用來記錄 y 觀測值
numIdx = 0
'''以上兩個串列,侍衛移動平均值設置,讓xy座標可以各存入七個座標後再取平均值'''

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
        image = cv2.flip(image, 1) # 圖像左右翻轉
        # image = cv2.resize(image,(1280,840)) # 1280是寬,840是高
        image = cv2.resize(image,(wCam,hCam)) # 1280是寬,840是高
        imageHeight, imageWidth, _ = image.shape # 取出串流畫面的長與寬值
        results = hands.process(image) # 將串流畫面包進手勢標示物件去
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR) # 轉回openCV可撥放的BGR格式
        
        '''以下畫長方形'''
        cv2.rectangle(image,(frameRx,frameRy),(wCam-frameRx,hCam-frameRy),(255,0,255),2)
        '''以上畫長方形'''
        
        '''下面是在螢幕上畫手得座標示意圖;可移除,滑鼠依然可以偵測'''
        if results.multi_hand_landmarks:
            for _, hand in enumerate(results.multi_hand_landmarks):
                mp_drawing.draw_landmarks(image, hand, mp_hands.HAND_CONNECTIONS, 
                                        mp_drawing.DrawingSpec(color=(250, 44, 250), thickness=2, circle_radius=5),
                                         )
        '''上面是在螢幕上畫手得座標示意圖'''
        # results.multi_hand_landmarks是將座標寫入字典,再將字典包入串列
        fingerMap = [] # 裝入每一次while回圈內每節手部座標的xy值
        # 當results.multi_hand_landmarks != None, 手部移開畫面後不會造成錯誤訊息
        if results.multi_hand_landmarks != None:
          for handLandmarks in results.multi_hand_landmarks:
            '''handLandmarks將字典手部座標從串列中拿出來'''
            '''mp_hands.HandLandmark是具enum的物件'''
            for point in mp_hands.HandLandmark:
                '''point顯示手掌上每一個座標的標示名稱,列如食指拇指,用0~20表示'''
                '''handLandmarks.landmark是每一個while迴圈中,每一個手部節點的xyz座標'''
                # print(f"indexTip{handLandmarks.landmark[8]}") # 只取了indexTip的x座標
                # print(len(handLandmarks.landmark)) # 有21項串列
                temp = int(f"{point}") # 用這種方式取出point的值才會是0~20,不然會顯示成物件本身
                onePosition = [] # 取出每一個節點的名稱,0~20,作為後續儲存的索引值(index)
                onePosition.append(temp)

                '''normalizedLandmark用索引值將座標xyz一個個單獨取出來(x,y)型態'''
                normalizedLandmark = handLandmarks.landmark[point]
                # print(normalizedLandmark) # 顯示xyz座標

                '''顯示normalizedLandmark的xyz座標值(0~1之間)並轉換成螢幕座標(整數畫素質) => (x,y)'''
                pixelCoordinatesLandmark = mp_drawing._normalized_to_pixel_coordinates(normalizedLandmark.x, normalizedLandmark.y, imageWidth, imageHeight)
                # print(pixelCoordinatesLandmark) # 顯示normalizedLandmark的xyz座標並轉換成螢幕座標(畫素質) => (x,y)

                '''以下將座標放入串列中,用if判斷有否xy座標(手移除鏡頭外會變成None,造成下面append出錯,故,需要加一個判斷是否為空值,再進行添加)'''
                if pixelCoordinatesLandmark != None:
                    onePosition.append(pixelCoordinatesLandmark[0])
                    onePosition.append(pixelCoordinatesLandmark[1])
                    fingerMap.append(onePosition)
                '''以上將座標放入串列中,用if判斷有否xy座標(手移除鏡頭外會變成None,造成下面append出錯,故,需要加一個判斷是否為空值,再進行添加)'''
            try:
                '''以下是虛擬滑鼠移動功能區塊'''
                '''一下是滑鼠移動取五點座標平均值的測試'''
                xList = [fingerMap[0][1],fingerMap[5][1],fingerMap[9][1],fingerMap[13][1],fingerMap[17][1]]
                yList = [fingerMap[0][2],fingerMap[5][2],fingerMap[9][2],fingerMap[13][2],fingerMap[17][2]]
                xMean = sum(xList)/len(xList)
                yMean = sum(yList)/len(yList)
                movingX.append(xMean)
                if len(movingX) > 10:
                    movingX.pop(0)
                movingY.append(yMean)
                if len(movingY) > 10:
                    movingY.pop(0)
                # 計算移動平均座標
                if len(movingX) >= 10:
                    # 最後一點與倒數第3點的速度差(加速度)
                    acc = (movingX[-1] - 2*movingX[-2] + movingX[-3])**2 + (movingY[-1] - 2*movingY[-2] + movingY[-3])**2
                    # 最後一點與倒數第2點的速度(距離,只是沒有開根號)
                    vel = (movingX[-1] - movingX[-2])**2 + (movingY[-1] - movingY[-2])**2
                    accArr.append(acc) # 觀察記錄 acc 用
                    velArr.append(vel) # 觀察記錄 vel(速度) 用
                    xArr.append(xMean) # 觀察記錄 x 用
                    yArr.append(yMean) # 觀察記錄 y 用
                    # print(int(acc),end="          \r") # 觀察顯示用
                    # 使用不同速度, 動態改變平均點數(動態移動平均法)
                    if (vel <= 20):
                        # numIdx = 9
                        movingX[-1] = movingX[-2]
                        movingY[-1] = movingY[-2]
                        xMean = movingX[-2]
                        yMean = movingY[-2]
                    else:
                        if (vel > 20 and vel <= 50):
                            numIdx = 1
                        elif (vel > 50 and vel <= 100):
                            numIdx = 2
                        elif (vel > 100 and vel <= 400):
                            numIdx = 3
                        elif (vel > 400 and vel <= 4000):
                            numIdx = 4
                        elif (vel > 4000 and vel <= 10000):
                            numIdx = 7
                        else:
                            numIdx = 10
                        xMean = sum(movingX[-numIdx:])/numIdx
                        yMean = sum(movingY[-numIdx:])/numIdx
                else:
                    xMean = sum(movingX)/len(movingX)
                    yMean = sum(movingY)/len(movingY)
                # ------原方法------
                # xMean = sum(movingX)/len(movingX)
                # yMean = sum(movingY)/len(movingY)
                newX = np.interp(xMean,(frameRx,wCam-frameRx),(0,wScr))
                newY = np.interp(yMean,(frameRy,hCam-frameRy),(0,hScr))
                autopy.mouse.move(newX,newY)
                '''一上是滑鼠移動取五點座標平均值的測試'''

                '''以下移動平均值方式,幾乎消除了滑鼠抖動'''
                # movingX.append(fingerMap[0][1])
                # if len(movingX) > 5 : # 取七個座標的平均值表較滑鼠指標表現較平穩,超過七個就移除第一順位索引值
                #     movingX.pop(0)
                # movingY.append(fingerMap[0][2])
                # if len(movingY) > 5:
                #     movingY.pop(0)
                # xMean = sum(movingX) / len(movingX) # 取xy分別的平均值放入win32api執行滑鼠移動
                # yMean = sum(movingY) / len(movingY)
                
                # '''以下設定滑鼠範圍自動照螢幕比例變更(可用)'''
                # newX = np.interp(xMean,(frameRx,wCam-frameRx),(0,wScr))
                # newY = np.interp(yMean,(frameRy,hCam-frameRy),(0,hScr))
                # autopy.mouse.move(newX,newY)
                '''以上設定滑鼠範圍自動照螢幕比例變更(可用)'''

                # win32api.SetCursorPos((xMean*7-2500,yMean*6-3000)) # 教室電腦,浮標移動比例已調整好,可用了
                '''以上是虛擬滑鼠移動功能區塊'''

                '''***以下是根據半徑大小,看能否完全移除指標抖動'''
                # currentX = fingerMap[0][1]
                # currentY = fingerMap[0][2]

                # if ((currentX-previousX)**2+(currentY-previousY)**2) <= ((previousX-(previousX+r))**2+(previousY-(previousY+r))**2):
                #     X,Y = previousX,previousY
                #     print(f"previous: {X},{Y}")
                #     # win32api.SetCursorPos((X*6-2500,Y*6-2500)) # 家用
                #     win32api.SetCursorPos((X*7-2500,Y*6-3000)) # 教室電腦,浮標移動比例已調整好,可用了
                # else:
                #     previousX, previousY = currentX,currentY
                #     X,Y = previousX,previousY
                #     print(f"current: {X},{Y}")
                #     # win32api.SetCursorPos((X*6-2500,Y*6-2500)) # 家用
                #     win32api.SetCursorPos((X*7-2500,Y*6-3000)) # 教室電腦,浮標移動比例已調整好,可用了
                '''***以上是根據半徑比大小,看能否完全移除指標抖動'''
            except:
                pass

            try:
                '''以下是滑鼠點擊功能區塊'''
                '''以下滑鼠點擊手勢向下時只執行一次點擊動作,並且點擊完後恢復指尖座標(向上時)不會二度執行點擊'''  
                if fingerMap[8][2] >= fingerMap[7][2]:
                    if switch == True:
                        # print("downward => click")
                        pyautogui.click()
                        switch = False
                if fingerMap[8][2] <= fingerMap[7][2]:
                     if switch == False:
                        # print("upward => no click")
                        switch = True
                '''以上是滑鼠點擊功能區塊'''
            except:
                pass
 
        cv2.imshow('Hand Tracking', image) # 有這條程式才能開啟串流
        
        '''點擊串流畫面,按下q結束程式'''
        if cv2.waitKey(10) & 0xFF == ord('q'):
            # ---紀錄 acc 數據做觀察---
            a = np.asarray(accArr)
            a.tofile('sampleA.csv',sep=',')
            # ---紀錄 x 數據做觀察---
            b = np.asarray(xArr)
            b.tofile('sampleX.csv',sep=',')
            # ---紀錄 y 數據做觀察---
            c = np.asarray(yArr)
            c.tofile('sampleY.csv',sep=',')
            # ---紀錄 v(速度) 數據做觀察---
            d = np.asarray(velArr)
            d.tofile('sampleV.csv',sep=',')
            break
video.release() # 結束程式執行,釋放串流物件資源
'''以上完整版'''
'''以上是7.13取五點平均值後再while5次的平均, 也可以'''
connect.t.cancel()