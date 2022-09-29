# 深度學習辨識全台道路晴雨APP
An app to identify the weather of roads in Taiwan.

## Language and Environment
* Python 3.7.4
* Windows 10
* Google Colab

## Feature
    
* Crawler
<ol>
<li> Visit the websites by getting the URL from .csv file.</li>
<li> Get the screenshot from the website.</li>
<li> Crop and store the image.</li>
</ol>

* Training Model

    Use google colab to train the model.

  | parameter | value |
  | ---- | ---- |
  | image size | 224 x 224 |
  | batch size | 32 |
  | epoch | 50 |
  | data augmentation | RandomFlip<br>RandomRotation<br>Rescaling<br>RandomTranslation<br> |
  
* User Interface
<ol>
<li> Choose the city, district and road sequentially.</li>
<li> App will get the real-time image of the road.</li>
<li> Show the result.</li>
</ol>

## Operating Method
* Install correct version of chromedriver.exe, which is corresponding to the version of google chrome.
* Run APP.py.
