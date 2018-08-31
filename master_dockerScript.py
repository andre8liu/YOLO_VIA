import subprocess
from tempfile import mkstemp
from shutil import move
from os import fdopen, remove
from subprocess import Popen, PIPE
import time



def replace_(file_path, pattern, subst):
    # Create temp file
    fh, abs_path = mkstemp()
    with fdopen(fh, 'w') as new_file:
        with open(file_path) as old_file:
            for line in old_file:
                new_file.write(line.replace(pattern, subst))
    # Remove original file
    remove(file_path)
    # Move new file
    move(abs_path, file_path)

#create datafolder and move images/labels
subprocess.call(['mkdir','trainData'])
subprocess.call(['mv','labels','trainData/labels'])
subprocess.call(['mv','images','trainData/images'])
subprocess.call(['mv','premodel_images','trainData/pre_images'])


settings = 'cfg/yolov2.cfg'
paths = 'cfg/coco.data'
p = subprocess.Popen(['wc','-l','labels.names'], stdout = PIPE)
numClasses = p.stdout.read()
#classes = numClasses.rstrip('labels.names')
classes = numClasses[0]
print("Number of Classes")
print(classes)
filters = str((int(classes)+5)*5)
filterstr = '237s/filters=425/filters=' + filters + '/'


#for yolov2.cfg
replace_(settings,'batch=1','#batch=1') #commenting out testing config
replace_(settings,'subdivisions=1','#subdivisions=1') #commenting out testing config
replace_(settings,'# batch=64','batch=8')
replace_(settings,'# subdivisions=8','subdivisions=1')
replace_(settings,'max_batches = 500200','max_batches = 10000')
replace_(settings,'steps=400000,450000','steps=3000,6000')
replace_(settings,'classes=80','classes=' + classes)
replace_(settings,'width=416','width=416')
replace_(settings,'height=416','height=416')
replace_(settings,'scales=.1,.1','scales=.1,.1')
replace_(settings,'learning_rate=0.001','learning_rate=0.001')
subprocess.call(['sed','-i',filterstr,'cfg/yolov2.cfg'])



#for coco.data
replace_(paths,'classes= 80','classes=' + classes)
replace_(paths,'train  = /home/pjreddie/data/coco/trainvalno5k.txt','train= imagePaths')
replace_(paths,'valid = data/coco_val_5k.list','valid = imagePaths')
replace_(paths,'names = data/coco.names', 'names = labels.names')
replace_(paths,'backup = /home/pjreddie/backup/','backup = /usr/local/src/darknet')

#subprocess.call(['wget','--no-check-certificate', 'https://pjreddie.com/media/files/darknet19_448.conv.23'])
subprocess.call(['./darknet','detector','train','cfg/coco.data','cfg/yolov2.cfg','darknet19_448.conv.23'])

#subprocess.call(['python3','docker_volume/darknet.py'])
#p=subprocess.Popen(['nvidia-docker', 'run','-it', '--name', 'test', 'blitzingeagle/darknet', '/bin/bash'], stderr = PIPE)
#p = subprocess.Popen(['nvidia-docker', 'run','-it','blitzingeagle/darknet', 'pwd'],stdout=PIPE)
# subprocess.Popen('nvidia-docker')
#output = p.stderr.read()
# print(output)

# subprocess.Popen('exit')


