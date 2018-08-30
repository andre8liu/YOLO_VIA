# coding=utf-8
import json
import cv2
import os
from importlib import reload
import sys
reload(sys)


# 1. need to turn this into a python function then import it into views.py and call it on the json file
# need to switch json file  g

def check_contain_chinese(check_str):
    for ch in check_str.decode('utf-8'):
        if u'\u4e00' <= ch <= u'\u9fff':
            return True
    return False


def test():
    print("hi from read.test")
    labelNames = open('labels.names', 'w+')
    labelNames.write("hey")
    return(32)


def convertToYolo():
    sys.setdefaultencoding('utf-8')
    imgdirname = './images/'
    jsonname = str(sys.argv[1])
    namefile = 'labels.names'

    lbldirname = imgdirname.rstrip('images/')+'/labels/'
    os.system('mkdir -p '+lbldirname)
    listname = jsonname.strip('.json')
    listdata = open(listname, 'wb')
    labelNames = open(namefile, 'w+')

    objDict = {}
    objcount = 0
    count = 0
    with open(jsonname, 'r') as f:
        data = json.loads(f.readline())
        # print data
        print(len(data))
        for key1 in data.keys():  # goes through each file

            filename = imgdirname+data[key1]['filename']  # gets file name
            print(filename, count)
            listdata.write(filename.encode('gbk')+'\n')

            if os.path.isfile(filename):
                if check_contain_chinese(filename):
                    print(filename + ' is chinese')
                else:
                    # reading in picture
                    image = cv2.imread(
                        filename, cv2.IMREAD_IGNORE_ORIENTATION | cv2.IMREAD_COLOR)
                    # getting second set of keys
                    rectangles = data[key1]['regions']
                    # returns number of rows columns and channels
                    height_image, width_image, _ = image.shape
                    print(len(rectangles.keys()), image.shape,
                          height_image, width_image)
                    with open(lbldirname+'/'+os.path.splitext(os.path.basename(filename))[0]+'.txt', 'w') as ff:
                        for key2 in rectangles.keys():
                            objType = rectangles[key2]["region_attributes"]
                            obj = str(objType["Animal"])
                            if not objDict.has_key(obj):
                                objDict[obj] = objcount
                                labelNames.write(obj)
                                labelNames.write(' ')
                                objcount += 1
                            xywh = rectangles[key2]["shape_attributes"]
                            x = int(xywh["x"])
                            y = int(xywh["y"])
                            w = int(xywh["width"])
                            h = int(xywh["height"])
                            xn = float(xywh["x"])/width_image
                            yn = float(xywh["y"])/height_image
                            wn = float(xywh["width"])/width_image
                            hn = float(xywh["height"])/height_image
                            ff.write('%d %1.5f %1.5f %1.5f %1.5f\n' %
                                     (objDict[obj], xn+wn/2, yn+hn/2, wn, hn))
                            print('%d %1.5f %1.5f %1.5f %1.5f' %
                                  (objDict[obj], xn+wn/2, yn+hn/2, wn, hn))
                            image = cv2.rectangle(
                                image, (x, y), (x+w, y+h), (255, 0, 0), 1)
                    cv2.imshow('test', image)
                    cv2.waitKey(0)
                    count += 1
