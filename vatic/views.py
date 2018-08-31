from django.shortcuts import render
from django.http import HttpResponse
from django.views import View
from . import read
from PIL import Image
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from tempfile import mkstemp
from shutil import move
from os import fdopen, remove
import subprocess

import json
import cv2
import os
from importlib import reload
import sys
reload(sys)


class viaView(View):

    def get(self, request):
        testView = viaView()
        return render(request, 'via.html', {'testView': testView})

    def post(self, request):

        print(request.FILES.getlist('files[]'))

        if(request.FILES.getlist('files[]')) != []:
            print("Saving images")
            imgdirname = './media/images/'
            subprocess.call(['mkdir', '-p', imgdirname])
            data = request.FILES.getlist('files[]')
            numFiles = len(data)
            for x in range(numFiles):
                imagePathName = 'images/' + str(data[x])
                path = default_storage.save(
                    imagePathName, ContentFile(data[x].read()))
                tmp_file = os.path.join(settings.MEDIA_ROOT, path)
        else:
            print(request.POST)
            print("Saving Specifications")
            premodel = request.POST.get('premodel')
            batches = request.POST.get('batches')
            subdiv = request.POST.get('subdiv')
            height = request.POST.get('height')
            width = request.POST.get('width')
            rate = request.POST.get('rate')
            max_batches = request.POST.get('max_batches')
            steps = request.POST.get('steps')
            scales = request.POST.get('scales')

            if premodel == 'true':
                subprocess.call(
                    ['cp', 'master_predockerscript.py', 'copy_dockerScript.py'])
                docker_script = 'copy_dockerScript.py'
            else:
                subprocess.call(['cp', 'master_dockerScript.py', 'copy_dockerScript.py'])
                docker_script = 'copy_dockerScript.py'

            # copy master then change copy
            replace_(docker_script, "replace_(settings,'# batch=64','batch=8')",
                     "replace_(settings,'# batch=64','batch=" + batches + "')")
            replace_(docker_script, "replace_(settings,'# subdivisions=8','subdivisions=1')",
                     "replace_(settings,'# subdivisions=8','subdivisions=" + subdiv + "')")
            replace_(docker_script, "replace_(settings,'max_batches = 500200','max_batches = 10000')",
                     "replace_(settings,'max_batches = 500200','max_batches = " + max_batches + "')")
            replace_(docker_script, "replace_(settings,'steps=400000,450000','steps=3000,6000')",
                     "replace_(settings,'steps=400000,450000','steps=" + steps + "')")
            replace_(docker_script, "replace_(settings,'width=416','width=416')",
                     "replace_(settings,'width=416','width=" + width + "')")
            replace_(docker_script, "replace_(settings,'height=416','height=416')",
                     "replace_(settings,'height=416','height=" + height + "')")
            replace_(docker_script, "replace_(settings,'scales=.1,.1','scales=.1,.1')",
                     "replace_(settings,'scales=.1,.1','scales=" + scales + "')")
            replace_(docker_script, "replace_(settings,'learning_rate=0.001','learning_rate=0.001')",
                     "replace_(settings,'learning_rate=0.001','learning_rate=" + rate + "')")

        return HttpResponse("Settings Configured")


def replace_(file_path, pattern, subst):
    # Create temp file
    fh, abs_path = mkstemp()
    with fdopen(fh, 'w') as new_file:
        with open(file_path) as old_file:
            for line in old_file:
                new_file.write(line.replace(pattern, subst))
    remove(file_path)
    move(abs_path, file_path)
    return 1


def train(request):
    return render(request, 'training.html')


def done_training(request):
    return render(request, 'done_train.html')
