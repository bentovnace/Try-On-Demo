from kivymd.uix.screen import MDScreen
from kivy.clock import Clock
import cv2
from kivy.graphics.texture import Texture
from kivy.properties import ObjectProperty
import mediapipe
import numpy as np
import pyautogui
import time
import random
import urllib
import base64
import json
import requests
from urllib.request import urlopen

cv2_cuda_available = cv2.cuda.getCudaEnabledDeviceCount() > 0

mphands = mediapipe.solutions.hands
if cv2_cuda_available:
    detector = mphands.Hands(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5, model_complexity=1)
else:
    detector = mphands.Hands()

draw = mediapipe.solutions.drawing_utils

wscreen,  hscreen = pyautogui.size()
global px , py, cx , cy, state_Vitual_Mouse

px, py = 0, 0
cx, cy = 0, 0

class CameraScreen(MDScreen):

    name=ObjectProperty(None) 
    global api, response, local, save_image_obj
    
    file_obj = open('API_SERVER.txt')
    data = file_obj.read()
    file_obj.close()
    local = data
    





    def build_camera(self):
        global state_Vitual_Mouse
        
        self.ids.main.current = 'scr_2'

        state_Vitual_Mouse = "On"

        self.videocapture = cv2.VideoCapture(0,cv2.CAP_DSHOW)
        if cv2_cuda_available:
            self.videocapture.set(cv2.CAP_PROP_CUDA_DEVICE, 0)
        
        self.scheduled_event = Clock.schedule_interval(self.update_camera, 1.0/33.0)
    
            

    def update_camera(self,*args):
        global px , py, cx , cy, state_Vitual_Mouse
        ret, frame = self.videocapture.read()
        self.image = frame
        #----------------------------------------------------------------
        if state_Vitual_Mouse =="On":
            if ret:
                rgbFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                lmList, frame = self.handLandmarks(rgbFrame, frame)

                if len(lmList) !=0:
                    x1, y1 = lmList[8][1:]
                    x2, y2 = lmList[12][1:]
                    finger = self.fingers(lmList)

                    if finger[1] == 1 and finger[2] == 0:
                        x3 = np.interp(x1, (0, int(self.videocapture.get(cv2.CAP_PROP_FRAME_WIDTH))), (0, wscreen))
                        y3 = np.interp(y1, (0, int(self.videocapture.get(cv2.CAP_PROP_FRAME_HEIGHT))), (0, hscreen))

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

        #----------------------------------------------------------------
        
        buf1 = cv2.flip(frame, 0)

        
        buf = buf1.tostring()
        texture1 = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr') 

        texture1.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
       
        self.ids.img_camera.texture = texture1

        


    def handLandmarks(self, img, frame):
        landmarkList = []
        landmarkPositions = detector.process(img)

        landmarkCheck = landmarkPositions.multi_hand_landmarks

        if landmarkCheck:
            for hand in landmarkCheck:
                for i, landmark in enumerate(hand.landmark):
                    #draw.draw_landmarks(frame, hand, mphands.HAND_CONNECTIONS)
                    h, w, c = img.shape
                    centerX, centerY = int(landmark.x*w), int(landmark.y*h)
                    landmarkList.append([i, centerX, centerY])
        return landmarkList, frame
    
    def fingers(self,landmarks):
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
    



    def Capture_image(self):
        global state_Vitual_Mouse
        print("Capture")
        #Clock.schedule_once(lambda dt: Clock.unschedule(self.scheduled_event))
        
        #self.scheduled_event_2 = Clock.schedule_interval(self.update_camera_2, 1.0/33.0)
        state_Vitual_Mouse = "Off"  
        
        Clock.schedule_once(self.start_countdown, 1)

        
        
        
        #Clock.schedule_once(lambda dt: Clock.unschedule(self.scheduled_event_2))

        

    def start_countdown(self, dt):
        # Đặt giá trị khởi đầu cho biến đếm
        self.counter = 5
        # Đặt hàm cập nhật đồng hồ đếm ngược
        Clock.schedule_interval(self.update_countdown, 1)

    def update_countdown(self, dt):
        # Cập nhật giá trị đồng hồ đếm ngược trên Label
        self.ids.counter.text = str(self.counter)

        # Giảm giá trị đồng hồ đếm ngược
        self.counter -= 1
        print(self.counter)

        # Kiểm tra nếu đồng hồ đếm ngược đã đạt đến 1, dừng cập nhật
        if self.counter < 0:
            self.ids.counter.text = ""
            Clock.unschedule(self.update_countdown)
            Clock.schedule_once(self.write_img,1)



    def number_counter(self,i):
        self.ids.counter.text = str(i)
    

    def write_img(self,*args):
        global   save_image_obj
        print("Capture")
        timestr = time.strftime("%Y%m%d_%H%M%S")
        print(timestr)
        save_image_obj = "Capture_pic\\" + str(random.randint(1,10000))+ str(random.randint(1,1000))+"Day"+timestr+".png"
        cv2.imwrite(save_image_obj, self.image)
        Clock.schedule_once(self.Send_Img_2Server)
        #self.ids.main.current = 'scr_1'

    def update_camera_2(self,*args):
        global px , py, cx , cy
        ret, frame = self.videocapture.read()
        self.image = frame
        
        buf1 = cv2.flip(frame, 0)
        
        buf = buf1.tostring()
        texture1 = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr') 

        texture1.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
       
        self.ids.img_camera.texture = texture1

    def Send_Img_2Server(self,*args):
        
        global api, response, local, save_image_obj
        
        try:
            urlopen(local, timeout=1)
            print("Internet is active")
            api = local + "/image_capture_remove_bg"
            image_file = save_image_obj

            with open(image_file, "rb") as f:
                im_bytes = f.read()        
            im_b64 = base64.b64encode(im_bytes).decode("utf8")

            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            
            payload = json.dumps({"image": im_b64, "other_key": "value"})
            response = requests.post(api, data=payload, headers=headers)


            self.Dowload_Remove_Bg_From_Server(response)
        except urllib.error.URLError as Error:
            print(Error)
            print("Internet disconnected") 
            self.ids.main.current = 'disconnect_network'
        
        self.ids.main.current = 'Clothes_change'
    
    def check_internet(self,*args):
        global local
        print(local)
        try:
            urlopen(local, timeout=1)
            print("Internet is active")
            self.ids.main.current = 'scr_1'
        except urllib.error.URLError as Error:
            print(Error)
            print("Internet disconnected") 
            self.ids.main.current = 'disconnect_network'


    def reload_check(self,*args):
        Clock.schedule_once(self.check_internet)



    def count_down(self):
        print('count_down')


    def back(self):
        global state_Vitual_Mouse
        self.ids.main.current= 'scr_2'
        state_Vitual_Mouse = 'On'

    def show_img_capture(self):
        global save_image_obj
        self.ids.capture_img.source = save_image_obj


    def Dowload_Remove_Bg_From_Server(self,response):
        global local
        
    
        im_b64 = response.text
        img_bytes = base64.b64decode(im_b64.encode('utf-8'))
        np_data = np.fromstring(img_bytes,np.uint8)
        img = cv2.imdecode(np_data,cv2.IMREAD_UNCHANGED)
        timestr = time.strftime("%Y%m%d_%H%M%S")
        print(timestr)
        name_img = str(random.randint(1, 10000)) + str(random.randint(1, 1000)) + "Day" + timestr + ".png"
        name_img_save = "Remove_Background\\"+name_img
        cv2.imwrite(name_img_save,img)
        self.ids.capture_img.source = name_img_save
