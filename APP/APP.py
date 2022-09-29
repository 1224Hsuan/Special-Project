import kivy
import kivy.resources
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.utils import get_color_from_hex
from kivy.graphics import Rectangle, Color
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from PIL import Image
import tensorflow as tf
from tensorflow import keras
from keras.models import load_model
from keras.preprocessing import image
from keras.preprocessing.image import load_img
import os
import pandas as pd
import numpy as np
import time
import threading
import cv2

kivy.resources.resource_add_path('D:/insert/')
p = kivy.resources.resource_find('Droid-Sans-Fallback.ttf')

# set the text of labels
cityName = ["台北市", "新北市", "桃園市", "高雄市", "基隆市",
            "宜蘭縣", "新竹市", "新竹縣", " 台中市", "彰化縣",
            "南投縣", "嘉義市", "嘉義縣", "台南市", "屏東縣",
            "苗栗縣", "花蓮縣", "台東縣", "雲林縣"
            ]
distName1 = ["松山區", "信義區", "大安區", "中山區", "中正區",
             "大同區", "萬華區", "文山區", "南港區", "內湖區",
             "士林區", "北投區"
             ]
distName2 = ["八里區", "板橋區", "淡水區", "貢寮區", "金山區",
             "林口區", "蘆洲區", "坪林區", "瑞芳區", "三重區",
             "三峽區", "三芝區", "深坑區", "石碇區", "樹林區",
             "泰山區", "土城區", "萬里區", "五股區", "烏來區",
             "新店區", "新莊區", "汐止區", "鶯歌區", "永和區",
             "中和區"
            ]
distName3 = ["八德區", "大溪區", "大園區", "復興區", "龜山區",
             "龍潭區", "蘆竹區", "平鎮區", "桃園區", "新屋區",
             "楊梅區", "中壢區"
            ]
distName4 = ["大寮區", "大社區", "大樹區", "鳳山區", "岡山區",
             "鼓山區", "苓雅區", "林園區", "路竹區", "美濃區",
             "彌陀區", "楠梓區", "鳥松區", "前金區", "前鎮區",
             "橋頭區", "湖內區", "旗津區", "旗山區", "仁武區",
             "三民區", "小港區", "新興區", "燕巢區", "鹽埕區",
             "永安區", "梓官區", "左營區"
             ]

urls = pd.read_csv("TNroad.csv", header = None, names = ['url'])
tainanRoad = urls.url
roadName = []

roadLength = 0


# record the invalid input has happened or not
invalid1, invalid2, invalid3 = 0, 0, 0
tainan_invalid = 0
pageNum = 1
photoPrepared = 0
justRoad = -1

# set the global TextInput and Button
cityInput = TextInput(text = "",
                    multiline = False,
                    size_hint = (.1, .05),
                    pos = (300, 355),
                    font_name = p,
                    )

distInput = TextInput(text = "",
                    multiline = False,
                    size_hint = (.1, .05),
                    pos = (300, 395),
                    font_name = p,
                    )

roadInput = TextInput(text = "",
                    multiline = False,
                    size_hint = (.1, .05),
                    pos = (300, 505),
                    font_name = p,
                    )

tainanInput = TextInput(text = "",
                    multiline = False,
                    size_hint = (.1, .05),
                    pos = (300, 450),
                    font_name = p,
                    )

lastPageBtn = Button(text = "\n\n\n回上頁",
                size_hint = (.18, .25),
                pos = (20, 180),
                font_name = p,
                font_size = "17sp",
                background_normal = "btn.gif",
                background_down = "btn.gif",
                color = "green",
                )

nextPageBtn = Button(text = "\n\n\n下一頁",
                size_hint = (.18, .25),
                pos = (650, 180),
                font_name = p,
                font_size = "17sp",
                background_normal = "btn.gif",
                background_down = "btn.gif",
                color = "green",
                )

class Widget(FloatLayout):

    def __init__(self, **kwargs):
        super(Widget, self).__init__(**kwargs)

        def update_rect(layout,*args):
            layout.rect.pos=layout.pos
            layout.rect.size=layout.size

        with self.canvas:
            self.rect = Rectangle(pos = self.pos, size = self.size,
                                  source = "background.jpeg")
            self.bind(pos = update_rect, size = update_rect)

        # set the parameter to record the users choice
        global city, district, road, dist_show
        city, district, road = -1, -1, -1
        dist_show = 0

        # call the function to create interface of city
        self.cityWidget()
        
        

    def cityWidget(self):
        # set the label
        self.createLabel("請輸入查詢縣市:", 180, 350, "black", "19sp")

        # set the textinput of city
        self.add_widget(cityInput)

        # set the options of city
        option = ""
        for i in range(len(cityName)):
            option += str(i+1) + "." + cityName[i] + " "
            if i != 0 and (i+1) % 5 == 0:
                option += "\n"
        self.createLabel(option, 330, 280, "blue", "18sp")

        # set the "ok" button of city
        button = Button(text = "OK",
                        size_hint = (.06, .05),
                        pos = (390, 355),
                        font_name = p,
                        font_size = "17sp",
                        )
        button.bind(on_press = self.pressCity)
        self.add_widget(button)

    def distWidget(self):
        self.clear_widgets()
        self.createLabel("請輸入查詢區域:", 180, 390, "black", "19sp")
        self.add_widget(distInput)
        self.createDistButton()
        self.createDistLabel()
        lastPageBtn.bind(on_press = self.pressLast)
        self.add_widget(lastPageBtn)

    def roadWidget(self):
        self.clear_widgets()
        self.createLabel("請輸入查詢道路:", 180, 500, "black", "19sp")
        self.add_widget(roadInput)
        self.createRoadButton()
        self.createRoadLabel()
        self.add_widget(lastPageBtn)

    def roadWidget_2(self):
        self.clear_widgets()
        self.createLabel("請輸入查詢道路:", 180, 500, "black", "19sp")
        self.add_widget(roadInput)
        self.createRoadButton()
        self.createRoadLabel_2()
        lastPageBtn.bind(on_press = self.pressLast)
        self.add_widget(lastPageBtn)

    def waitWidget(self):
        self.clear_widgets()
        global waitMsg, picture, restartBtn, restartCityBtn
        waitMsg = Label(text = "請稍候...",
                      size_hint = (.1, .07),
                      pos = (350, 400),
                      font_name = p,
                      font_size = "18sp",
                      color = "blue",
                    )
        self.add_widget(waitMsg)
        picture = Button(
                        size = self.size,
                        size_hint = (.40, .38),
                        pos = (240, 100),
                        background_normal = "wait.gif",
                        background_down = "wait.gif",
                        )
        self.add_widget(picture)
        restartBtn = Button(text = "",
                            size_hint = (.09, .06),
                            pos = (600, 100),
                            font_name = p,
                            font_size = "17sp",
                            background_color = (0, 0, 0, 0),
                            )
        restartBtn.bind(on_press = self.pressRestart)
        self.add_widget(restartBtn)
        restartCityBtn = Button(text = "",
                            size_hint = (.09, .06),
                            pos = (600, 50),
                            font_name = p,
                            font_size = "17sp",
                            background_color = (0, 0, 0, 0),
                            )
        restartCityBtn.bind(on_press = self.pressRestartCity)
        self.add_widget(restartCityBtn)
        
    def getCity(self):
        global city
        for i in range(1, len(cityName)+1):
            if cityInput.text != '':
                if float(cityInput.text) == i:
                    city = i-1
                    break
                else:
                    city = -1
            else:
                city = -1

    def pressCity(self, instance):
        global invalid1, city, pageNum, district
        global justRoad
        self.getCity()
        # check the input is valid or not
        if city != -1:
            if city <= 3:
                self.distWidget()
                pageNum += 1
                justRoad = 0
            else:
                self.roadWidget_2()
                pageNum += 3
                district = -1
                justRoad = 1
        
        elif invalid1 == 0:
            # invalid input, ask users to input again
            label_invalid1 = Label(text = "無效輸入，請重新輸入",
                            size_hint = (.1, .07),
                            pos = (510, 353),
                            font_name = p,
                            font_size = "18sp",
                            color = 'red',
                            )
            self.add_widget(label_invalid1)
            cityInput.text = ""
            invalid1 = 1
        else:
            cityInput.text = ""

    # create the labels and button of district
    def createDistButton(self):
        button = Button(text = "OK",
                        size_hint = (.06, .05),
                        pos = (390, 395),
                        font_name = p,
                        font_size = "17sp",
                        )
        button.bind(on_press = self.pressDist)
        self.add_widget(button)

    def createDistLabel(self):
        option = ""
        global city
        temp = []
        if city == 0:
            temp = distName1
        elif city == 1:
            temp = distName2
        elif city == 2:
            temp = distName3
        elif city == 3:
            temp = distName4
        
        for i in range(len(temp)):
                option += str(i+1) + "." + temp[i] + " "
                if i != 0 and (i+1) % 5 == 0:
                    option += "\n"
        self.createLabel(option, 320, 300, "blue", "18sp")

    # create the event of district button
    def pressDist(self, instance):
        global district, invalid2, pageNum
        length = 0
        if city == 0:
            length = len(distName1)
        elif city == 1:
            length = len(distName2)
        elif city == 2:
            length = len(distName3)
        elif city == 3:
            length = len(distName4)
                
        # check the district input is valid or not
        if distInput.text != '':
            for i in range(1, length+1):
                if float(distInput.text) == i:
                    district = i - 1
                    break
        else:
            district = -1
        if district == -1:
            if invalid2 == 0:
                label_invalid2 = Label(text = "無效輸入，請重新輸入",
                                size_hint = (.1, .07),
                                pos = (510, 393),
                                font_name = p,
                                font_size = "18sp",
                                color = 'red',
                                )
                self.add_widget(label_invalid2)
                invalid2 = 1
            distInput.text = ""
        else:
            self.roadWidget()
            pageNum += 1
            
    # create buttons and labels of roads in the chosen district
    def createRoadButton(self):
        button = Button(text = "OK",
                        size_hint = (.06, .05),
                        pos = (390, 505),
                        font_name = p,
                        font_size = "17sp",
                        )
        button.bind(on_press = self.pressRoad)
        self.add_widget(button)
        
    def createRoadLabel(self):
        global city, district, road, roadLength
        global roadName
        if city == 0:
            roadName = pd.read_csv("TProad.csv", header = None)
        elif city == 1:
            roadName = pd.read_csv("NTProad.csv", header = None)
        elif city == 2:
            roadName = pd.read_csv("TYroad.csv", header = None)
        elif city == 3:
            roadName = pd.read_csv("KHroad.csv", header = None)
        option = ""
        for i in range(len(roadName[district * 2 + 1])):
            tmp = str(roadName[district * 2 + 1][i])
            if tmp == "nan" or i == len(roadName[district * 2 + 1])-1:
                roadLength = i
                break
            option += str(i+1) + "." + tmp + " "
            if i != 0 and (i+1) % 2 == 0:
                option += '\n'
        self.createLabelR(option, 520, 180, "blue", "18sp")

    # create the event of road button
    def pressRoad(self, instance):
        global road, district, invalid3, roadLength
        if roadInput.text != '':
            for i in range(1, roadLength+1):
                if float(roadInput.text) == i:
                    road = i-1
                    break
        else:
            road = -1
        if road == -1:
            if invalid3 == 0:
                label_invalid3 = Label(text = "無效輸入，請重新輸入",
                                size_hint = (.1, .07),
                                pos = (500, 498),
                                font_name = p,
                                font_size = "18sp",
                                color = 'red',
                                )
                self.add_widget(label_invalid3)
                invalid3 = 1
            roadInput.text = ""
        else:
            self.waitWidget()
            t = threading.Thread(target = self.threadProcess)
            t.start()

    def createRoadLabel_2(self):
        global city, road, roadLength
        global roadName
        if city == 4:
            roadName = pd.read_csv("KLroad.csv", header = None)
        elif city == 5:
            roadName = pd.read_csv("YLroad.csv", header = None)
        elif city == 6:
            roadName = pd.read_csv("SJroad.csv", header = None)
        elif city == 7:
            roadName = pd.read_csv("HCroad.csv", header = None)
        elif city == 8:
            roadName = pd.read_csv("TCroad.csv", header = None)
        elif city == 9:
            roadName = pd.read_csv("CHroad.csv", header = None)
        elif city == 10:
            roadName = pd.read_csv("NTroad.csv", header = None)
        elif city == 11:
            roadName = pd.read_csv("CYroad.csv", header = None)
        elif city == 12:
            roadName = pd.read_csv("CCroad.csv", header = None)
        elif city == 13:
            roadName = pd.read_csv("TNroad.csv", header = None)
        elif city == 14:
            roadName = pd.read_csv("PTroad.csv", header = None)
        elif city == 15:
            roadName = pd.read_csv("MLroad.csv", header = None)
        elif city == 16:
            roadName = pd.read_csv("HLroad.csv", header = None)
        elif city == 17:
            roadName = pd.read_csv("TTroad.csv", header = None)
        elif city == 18:
            roadName = pd.read_csv("ULroad.csv", header = None)
        option = ""
        for i in range(len(roadName[1])):
            tmp = str(roadName[1][i])
            if tmp == "nan":
                roadLength = i
                break
            option += str(i+1) + "." + tmp + " "
            if i != 0 and (i+1) % 2 == 0:
                option += '\n'
            if i == len(roadName[1])-1:
                roadLength = i+1
                break
        self.createLabelR(option, 520, 180, "blue", "18sp")

    def pressRestart(self, instance):
        global city, district, road, pageNum, justRoad
        if district == -1:
            road, pageNum = -1, 4
            roadInput.text = ""
            self.clear_widgets()
            self.roadWidget_2()
        elif district != -1:
            district, road, pageNum, justRoad = -1, -1, 2, -1
            distInput.text = ""
            roadInput.text = ""
            self.clear_widgets()
            self.distWidget()

    def pressRestartCity(self, instance):
        global city, district, road, pageNum, justRoad
        city, district, road, pageNum, justRoad = -1, -1, -1, 1, -1
        cityInput.text = ""
        distInput.text = ""
        roadInput.text = ""
        self.clear_widgets()
        self.cityWidget()
    
    def threadProcess(self):
        global photoPrepared, result
        if justRoad == 1:
            tmpURL = str(roadName[0][road])
        else:
            tmpURL = str(roadName[district*2][road])
        self.getScreenshot(tmpURL)
        self.pngTojpg()
        photoPrepared = 1
        self.getResult()

    # the function to create label
    def createLabel(self, s, posX, posY, col, size):
        label = Label(text = s,
                      size_hint = (.1, .07),
                      pos = (posX, posY),
                      font_name = p,
                      font_size = size,
                      color = col,
                      halign = "left",
                      valign = "top",
                      )
        self.add_widget(label)

    def createLabelR(self, s, posX, posY, col, size):
        label = Label(text = s,
                      size_hint = (.1, .07),
                      pos = (posX, posY),
                      font_name = p,
                      font_size = size,
                      color = col,
                      text_size = self.size,
                      halign = "left",
                      valign = "top",
                      )
        self.add_widget(label)

    # the function to set the event when press the last page button
    def pressLast(self, instance):
        global pageNum
        self.clear_widgets()
        if pageNum == 2:
            self.cityWidget()
            cityInput.text = ""
        elif pageNum == 3:
            self.distWidget()
            distInput.text = ""
        elif pageNum == 4:
            self.cityWidget()
            cityInput.text = ""
            pageNum -= 2
        nextPageBtn.bind(on_press = self.pressNext)
        self.add_widget(nextPageBtn)
        pageNum -= 1

    def pressNext(self, instance):
        global pageNum, city, district, road, justRoad
        self.clear_widgets()
        if justRoad == 1:
            self.roadWidget_2()
            roadInput.text = ""
            pageNum += 2
        elif pageNum == 1 and city != -1:
            self.distWidget()
            distInput.text = ""
            if district != -1:
                nextPageBtn.bind(on_press = self.pressNext)
                self.add_widget(nextPageBtn)
        else:
            self.roadWidget()
            roadInput.text = ""
        pageNum += 1

    # get the screenshot from the website
    def getScreenshot(self, url):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--incognito")
        chrome_options.add_argument("--disable-popup-blocking ")
        s = Service(r"D:\insert\chromedriver.exe")
        browser = webdriver.Chrome(options = chrome_options,
                                   service = s)
        # set the window size
        browser.maximize_window()
        browser.get(url)

        # get the screenshot of the element
        photo = browser.find_element(By.CLASS_NAME, 'image-container')
        action = ActionChains(browser)
        action.move_to_element(photo).perform()

        # save the screenshot
        file_name = 'screenshot.png'
        browser.get_screenshot_as_file(file_name)

        # crop the image
        photo = browser.find_element(By.CLASS_NAME, 'image-container')
        left = 148
        top = 180
        right = left + 470
        bottom = top + 270
        photo = Image.open(file_name)
        photo = photo.crop((left, top, right, bottom))
        photo.save(file_name)
        browser.close()

    # convert the picture from png to jpg
    def pngTojpg(self):
        img = Image.open('screenshot.png')
        data = "screenshot"
        image = img.convert('RGB')
        imgName = data + '.jpg'
        image.save(imgName, quality = 95)

    # get the result by using the training model
    def getResult(self):
        model = load_model('model.h5')
        img = keras.preprocessing.image.load_img(
            "screenshot.jpg", target_size = (224, 224)
        )
        img_array = keras.preprocessing.image.img_to_array(img)
        img_array = tf.expand_dims(img_array, 0)

        predictions = model.predict(img_array)
        score = predictions[0]
        # get and show the result
        global city, district, road
        global waitMsg
        global picture, restartBtn, restartCityBtn
        result = cityName[city]
        if city == 0:
            result += distName1[district]
        elif city == 1:
            result += distName2[district]
        elif city == 2:
            result += distName3[district]
        elif city == 3:
            result += distName4[district]
        if city >= 4:
            result += roadName[1][road]
        else:
            result += roadName[district*2+1][road]
        if score >= 1-score:
            result += "\n天氣不錯，沒有下雨"
            picture.background_normal = "sunny.gif"
            picture.background_down = "sunny.gif"
        else:
            result += "\n天氣為雨，出門請記得帶傘"
            picture.background_normal = "rainy.gif"
            picture.background_down = "rainy.gif"
        waitMsg.text = result
        restartBtn.text = "重新查詢"
        restartBtn.background_color = (1, 1, 1, 1)
        restartCityBtn.text = "重設縣市"
        restartCityBtn.background_color = (1, 1, 1, 1)


class APP(App):
    def build(self):
        return Widget()

if __name__ == '__main__':
    APP().run()

