import mediapipe as mp
import cv2
import numpy as np
import pyautogui
import autopy
# import win32api

'''7.14.2022: Virtual Mouse complete version 1.4 / 虛擬滑鼠完整版 1.4v'''

'''以下是影像畫圖,手勢相關,與串流的初始化; image and hand-position objects initialization'''
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands 
video = cv2.VideoCapture(0)
''''''

'''畢氏定理半徑用參數/Pythagorean theorem radius parameters & xy-axis coordinates'''
previousX = 0
previousY = 0
currentX = 0
currentY = 0
r1 = 3
r2 = 10
''''''

'''以下取螢幕尺寸 / screen and frame resizing parameters'''
wScr,hScr = autopy.screen.size()
frameRx = 400
frameRy = 100
wCam,hCam = 1280,840
''''''

'''以下兩個串列,侍衛移動平均值設置,讓xy座標可以各存入七個座標後再取平均值/ storing 7 while loops coordinates for average calculation'''
movingX = []
movingY = []
''''''

'''以下設置t/f閘門,讓滑鼠點擊手勢向下時只執行一次點擊動作,並且點擊完後恢復指尖座標(向上時)不會二度執行點擊 / mouse right click switch lock, prevent 
unwanted click'''
switch = True
''''''

'''以下先將串流包進手勢使用的模組,如此flip的時候,手勢與座標圖式的位置才回一致 / wrap while loop in with, for image fliping purpose,keep 
hand and image movements coherent '''
with mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.8,max_num_hands=1) as hands: 
    '''以下開啟串流 / below: image streaming starts'''
    while video.isOpened():
        _, frame = video.read()
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        '''image是一個numpy多維陣列'''
        '''image.shape => (x,y,3), x = 高height, y = 寬width'''
        image = cv2.flip(image, 1) # 圖像左右翻轉,flip => right -> left
        image = cv2.resize(image,(wCam,hCam)) # (w,h) => (1280,840)
        imageHeight, imageWidth, _ = image.shape # 取出串流畫面的長與寬值; extract height and width
        results = hands.process(image) # 將串流畫面包進手勢標示物件去; wrap image into mp object
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR) # 轉回openCV可撥放的BGR格式; convert back to CV playable format
        
        '''以下畫長方形 / drawing rectangle in cv frame'''
        cv2.rectangle(image,(frameRx,frameRy),(wCam-frameRx,hCam-frameRy),(255,0,255),2)
        ''''''
        
        '''下面是在螢幕上畫手得座標示意圖;可移除,滑鼠依然可以偵測 / drawing hand-positions map'''
        if results.multi_hand_landmarks:
            for _, hand in enumerate(results.multi_hand_landmarks):
                mp_drawing.draw_landmarks(image, hand, mp_hands.HAND_CONNECTIONS, 
                                        mp_drawing.DrawingSpec(color=(250, 44, 250), thickness=2, circle_radius=5),
                                         )
        ''''''
        # results.multi_hand_landmarks是將座標寫入字典,再將字典包入串列 / put hand coordinate in dictionary and in list
        fingerMap = [] # 裝入每一次while回圈內每節手部座標的xy值 / add hand coordinates from each loop into list

        '''以下處裡座標/below block is to process coordinates'''
        if results.multi_hand_landmarks != None: # != None =>手部移開畫面後不會造成錯誤訊息;prevent error when hand move out the screen
          for handLandmarks in results.multi_hand_landmarks:
            '''handLandmarks將字典手部座標從串列中拿出來/extract coordinates out form list'''
            '''mp_hands.HandLandmark是具(is)enum的物件(object)'''
            for point in mp_hands.HandLandmark:
                '''point顯示手掌上每一個座標的標示名稱,列如食指拇指,用0~20表示/point is the label for each coordinate name'''
                '''handLandmarks.landmark是每一個(is every)while(loop)迴圈中,每一個手部節點的xyz座標(hand coordinates)'''
                # print(f"indexTip{handLandmarks.landmark[8]}") => 只取了indexTip的x座標 / get indexTip's x coordiante
                # print(len(handLandmarks.landmark)) # 有21項串列 / 21 items in the list
                temp = int(f"{point}") # 用這種方式取出point的值才會是0~20,不然會顯示成物件本身 / to get just number value out;otherwise, the object
                onePosition = [] # 取出每一個節點的名稱,0~20,作為後續儲存的索引值(index) / to store 0~20 as index
                onePosition.append(temp)

                '''normalizedLandmark用索引值將座標xyz一個個單獨取出來(x,y)型態 / use index to get xy coordinates'''
                normalizedLandmark = handLandmarks.landmark[point]
                # print(normalizedLandmark) # 顯示xyz座標 

                '''顯示normalizedLandmark的xyz座標值(0~1之間)並轉換成螢幕座標(整數畫素質) => (x,y); convert xyz coordinates to screen pixels'''
                pixelCoordinatesLandmark = mp_drawing._normalized_to_pixel_coordinates(normalizedLandmark.x, normalizedLandmark.y, imageWidth, imageHeight)

                '''以下將座標放入串列中,用if判斷有否xy座標(手移除鏡頭外會變成None,造成下面append出錯,故,需要加一個判斷是否為空值,再進行添加)
                if no hand then no coordinate, but loop would not be interrupted'''
                if pixelCoordinatesLandmark != None:
                    onePosition.append(pixelCoordinatesLandmark[0])
                    onePosition.append(pixelCoordinatesLandmark[1])
                    fingerMap.append(onePosition)
                ''''''
            try:
                '''以下是虛擬滑鼠移動功能區塊 / below block is for mouse movement'''

                '''以下是平均值與畢氏定理綜合版 / Combination of Pythagorean,Circle area, and Average method for smooth mouse cursor movements'''
                '''滑鼠移動座標 / cursor moving xy coordinates '''
                x = fingerMap[0][1]
                y = fingerMap[0][2]
                
                '''取平均數(四次座標數),讓滑鼠移動軌跡平滑;getting 4 while loops of coordinates for smoother cursor movement'''
                movingX.append(x)
                if len(movingX) > 4:
                    movingX.pop(0)
                movingY.append(y)
                if len(movingY) > 4:
                    movingY.pop(0)

                if ((movingX[-1]-movingX[-3])**2+(movingY[-1]-movingY[-3])**2) <= ((movingX[-3]-(movingX[-3]+r1))**2+(movingY[-3]-(movingY[-3]+r1))**2):
                    '''設定指標半徑,新座標在前座標面積內,則指標不變動,反之採用新座標,用畢氏定理半段距離大小,主要處裡靜態指標防止抖動
                    using Pythagorean & Circle area,if new coordinate falls within previous area, no movement change, otherwise, use new coordinate
                    main purpose is to prevent cursor shaking when still'''
                    tempX, tempY = previousX,previousY 
                    newX = np.interp(tempX,(frameRx,wCam-frameRx),(0,wScr)) # keep hand movement & cursor coherent within range of rectangle
                    newY = np.interp(tempY*2-650,(frameRy,hCam-frameRy),(0,hScr))    
                    autopy.mouse.move(newX,newY)
                else:
                    '''使用移動平均值,讓指標移動順暢/using average of 4 coordinates to allow cursor move smoothly'''
                    currentX = sum(movingX)//len(movingX)
                    currentY = sum(movingY)//len(movingY)
                    previousX = currentX
                    previousY = currentY
                    newX = np.interp(previousX,(frameRx,wCam-frameRx),(0,wScr))
                    newY = np.interp(previousY*2-650,(frameRy,hCam-frameRy),(0,hScr)) # to prevent left click auto triggler when index tip reaching out the screen 
                    autopy.mouse.move(newX,newY)
                '''以上是平均值與畢氏定理綜合版'''

                '''一下是滑鼠移動取五點座標平均值的測試 / below: development notes'''
                # xList = [fingerMap[0][1],fingerMap[5][1],fingerMap[9][1],fingerMap[13][1],fingerMap[17][1]]
                # yList = [fingerMap[0][2],fingerMap[5][2],fingerMap[9][2],fingerMap[13][2],fingerMap[17][2]]
                # xMean = sum(xList)/len(xList)
                # yMean = sum(yList)/len(yList)
                # movingX.append(xMean)
                # if len(movingX) > 7:
                #     movingX.pop(0)
                # movingY.append(yMean)
                # if len(movingY) > 7:
                #     movingY.pop(0)
                # xMean = sum(movingX)/len(movingX)
                # yMean = sum(movingY)/len(movingY)
                # newX = np.interp(xMean,(frameRx,wCam-frameRx),(0,wScr))
                # newY = np.interp(yMean,(frameRy,hCam-frameRy),(0,hScr))
                # autopy.mouse.move(newX,newY)
                ''''''

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
                ''''''

                # win32api.SetCursorPos((xMean*7-2500,yMean*6-3000)) # 教室電腦,浮標移動比例已調整好,可用了

                '''以下是根據半徑大小,看能否完全移除指標抖動'''
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
                '''above: note'''
            except:
                pass

            try:
                '''以下是滑鼠點擊功能區塊/below: mouse left click function block'''
                '''以下滑鼠點擊手勢向下時只執行一次點擊動作,並且點擊完後恢復指尖座標(向上時)不會二度執行點擊
                to turn on left click when switch is True, prevent unwanted click actions'''  
                if fingerMap[8][2] >= fingerMap[7][2]:
                    if switch == True:
                        # print("downward => click")
                        pyautogui.click()
                        switch = False
                if fingerMap[8][2] <= fingerMap[7][2]:
                     if switch == False:
                        # print("upward => no click")
                        switch = True
                ''''''
            except:
                pass
 
        cv2.imshow('Hand Tracking', image) # 有這條程式才能開啟串流 / this is to turn on video streaming
        
        '''點擊串流畫面,按下q結束程式 / press q to quit the program'''
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
video.release() # 結束程式執行,釋放串流物件資源 / program over, release object from ram
'''以上完整版'''