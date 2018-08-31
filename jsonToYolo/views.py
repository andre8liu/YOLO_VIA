from django.shortcuts import render
from django.http import HttpResponse
from django.views import View
from PIL import Image
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from tempfile import mkstemp
from shutil import move
from os import fdopen, remove
import subprocess
from subprocess import Popen, PIPE

import json
import cv2
import os
from importlib import reload
import sys
import time
reload(sys)

import mimetypes
from django.http import StreamingHttpResponse
from wsgiref.util import FileWrapper



class jsonToYolo(View):
    def get(self, request):
        with open('pre_annot.json') as json_file:
            data = json.load(json_file)
            print(data)
        return HttpResponse(json.dumps({'data':data}),content_type = 'application/json')


    def post(self, request):
        if(request.POST.get('premodel') == 'false'):  # for main model
            print("Saving JSON and converting to YOLO")
            subprocess.call(['rm','media/yolov2_final.weights'])
            jsondata = json.loads(request.POST.get("data[]"))
            with open('data.json', 'w') as outfile:
                json.dump(jsondata, outfile)
            convertToYolo(False)
            print("Starting Docker")
            startDocker(False)
            print("Stopping Docker")
            subprocess.call(['rm', '-rf', './media/images/'])
            subprocess.call(['rm', '-rf', './media/labels/'])
            subprocess.call(['rm','-rf', './premodel_images'])
            subprocess.call(['docker','cp','darknetv2:usr/local/src/darknet/yolov2_final.weights','./media'])
            return HttpResponse("Model Done Training")
        elif request.POST.get('premodel') == 'true':  # for premodel
            print("Saving JSON and converting to YOLO")
            jsondata = json.loads(request.POST.get("data[]"))
            with open('data.json', 'w') as outfile:
                json.dump(jsondata, outfile)

            convertToYolo(True)

            print("Starting Docker")
            startDocker(True)
            print("Stopping Docker")

            subprocess.call(['docker','cp','darknetv2:usr/local/src/darknet/pre_annot.json','.'])
            subprocess.call(['cp','-a','premodel_images/.','media/images'])
            subprocess.call(['rm', '-r','premodel_images'])

            #might have to move pictures back to images folder
            return(HttpResponse("Premodel Done Training"))
        else:
            return(download(request,'yolov2_final.weights'))

def download(request, path):
    response = HttpResponse()
    the_file = os.path.join(settings.MEDIA_ROOT, path)
    filename = path
    if os.path.exists(the_file):
        chunk_size = 8192
        response = StreamingHttpResponse(FileWrapper(open(the_file, 'rb'), chunk_size),
                                         content_type=mimetypes.guess_type(the_file)[0])
        response['Content-Length'] = os.path.getsize(the_file)
        response['Content-Disposition'] = "attachment; filename=%s" % filename
        return response
    #raise Http404


def check_contain_chinese(check_str):
    # for ch in check_str.decode('utf-8'):
     #   if u'\u4e00' <= ch <= u'\u9fff':
     #       return True
    return False


def convertToYolo(is_premodel):
    imgdirname = './media/images/'
    dockimgdir = './trainData/images/'
    predockimgdir = './trainData/pre_images/'
    jsonname = 'data.json'
    namefile = 'labels.names'

    # creating files and getting filenames
    #lbldirname = imgdirname.rstrip('images/')+'/labels/'
    lbldirname = './media/labels/'

    # subprocess.call(['rm','-rf',imgdirname])
    # subprocess.call(['mkdir','-p',imgdirname])
    subprocess.call(['mkdir', '-p', lbldirname])
    if is_premodel:
        subprocess.call(['mkdir', '-p', 'premodel_images'])
        # paths for inference images
        pre_imagepaths = open('pre_imagepaths', 'wb')

    #os.system('mkdir -p '+lbldirname)
    # listname = jsonname.strip('.json')
    listname = 'imagePaths'
    listdata = open(listname, 'wb')    # imagepaths
    labelNames = open(namefile, 'w+')  # creates names file

    # for names file
    objDict = {}
    objcount = 0
    count = 0

    with open(jsonname, 'r') as f:
        data = json.loads(f.readline())
        print(len(data))
        for key1 in data.keys():  # goes through each picture

            filename = imgdirname+data[key1]['filename']  # gets file name
            filepath = dockimgdir + data[key1]['filename']
            print(filename, count, type(filename))

            if os.path.isfile(filename):
                print("Found Picture")
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
                    if is_premodel:  # if for premodel, we wont include non annotated images
                        if rectangles == {}:
                            subprocess.call(
                                ['mv', filename, 'premodel_images'])
                            filepath = predockimgdir + data[key1]['filename']
                            pre_imagepaths.write(filepath.encode('gbk'))
                            pre_imagepaths.write('\n'.encode('gbk'))
                            # moving premodel inference images to new folder
                            print("There are no annotations for this picture")
                            continue
                    listdata.write(filepath.encode('gbk'))
                    listdata.write('\n'.encode('gbk'))

                    with open(lbldirname+'/'+os.path.splitext(os.path.basename(filename))[0]+'.txt', 'w') as ff:
                        for key2 in rectangles.keys():
                            objType = rectangles[key2]["region_attributes"]
                            for key3 in objType.keys():
                                obj = str(objType[key3])
                                if not obj in objDict:
                                    objDict[obj] = objcount
                                    labelNames.write(obj)
                                    labelNames.write(' \n')
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
                    # cv2.imshow('test', image) 
                    # cv2.waitKey(0)
                    count += 1


def startDocker(premodel):
    # starting docker
    
    subprocess.call(['docker', 'kill', 'darknetv2'])
    subprocess.call(['docker', 'rm', 'darknetv2'])
    subprocess.call(['nvidia-docker', 'run', '-it', '-d',
                     '--name', 'darknetv2', 'andre8liu/darknet:v2.0'])
    
    
    #subprocess.call(['docker', 'start', 'darknetv2'])
    # tranfering images
    if premodel:
        subprocess.call(['docker', 'cp', 'premodel_images',
                         'darknetv2:usr/local/src/darknet'])

    subprocess.call(['docker', 'cp', 'media/images',
                     'darknetv2:usr/local/src/darknet'])
    # transfering labels
    subprocess.call(['docker', 'cp', 'media/labels',
                     'darknetv2:usr/local/src/darknet'])
    # transfering names file
    subprocess.call(['docker', 'cp', 'labels.names',
                     'darknetv2:usr/local/src/darknet'])
    # transfering image paths
    subprocess.call(['docker', 'cp', 'imagePaths',
                     'darknetv2:usr/local/src/darknet'])
    # transfering pre_imagepaths
    if premodel:
        subprocess.call(['docker', 'cp', 'pre_imagepaths',
                         'darknetv2:usr/local/src/darknet'])
    # transfer script to docker
    subprocess.call(['docker', 'cp', 'copy_dockerScript.py',
                     'darknetv2:/usr/local/src/darknet'])
   
    print("Starting Training")
    subprocess.call(['nvidia-docker', 'exec', '-it',
                     'darknetv2', 'python', 'copy_dockerScript.py'])
    print("Ending Training")


