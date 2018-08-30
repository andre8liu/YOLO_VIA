from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
# Create your views here.
#from django.http import HttpResponse
from django.views import View


class premodel(View):
    def get(self,request):
        print("hey")
        return render(request, 'test.html')  


    #can only make label files for ones that have annotations.
    #now need to only send pictures 
    def post(self,request):
        print("HEY FROM PREMODEL POST")
        #need to get json data through post
        return HttpResponse("HEY")


#FOR PREMODEL
def preConvertToYolo():
    imgdirname = './media/images/'
    dockimgdir = './trainData/images/'
    jsonname = 'data.json'
    namefile = 'prelabels.names'

    # creating files and getting filenames
    lbldirname = imgdirname.rstrip('images/')+'/labels/'

    #subprocess.call(['rm','-rf',imgdirname])
    #subprocess.call(['mkdir','-p',imgdirname])
    subprocess.call(['mkdir','-p',lbldirname])
    #dir for images to be sent for premodel training
    subprocess.call(['mkdir','-p','premodel_images'])

    #os.system('mkdir -p '+lbldirname)
    # listname = jsonname.strip('.json')
    listname = 'imagePaths'
    listdata = open(listname, 'wb')
    labelNames = open(namefile, 'w+')  # creates names file

    # for names file
    objDict = {}
    objcount = 0
    count = 0

    with open(jsonname, 'r') as f:
        data = json.loads(f.readline())
        # print data
        print(len(data))
        for key1 in data.keys():  # goes through each file

            filename = imgdirname+data[key1]['filename']  # gets file name
            filepath = dockimgdir +data[key1]['filename']
            print(filename, count, type(filename))
            listdata.write(filepath.encode('gbk'))
            listdata.write('\n'.encode('gbk'))

            if os.path.isfile(filename):
                print("FOUNDIT")
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
                    if rectangles == {}:
                        print("NO ANNOTATIONS FOR THIS PIC")
                        continue
                    with open(lbldirname+'/'+os.path.splitext(os.path.basename(filename))[0]+'.txt', 'w') as ff:
                        for key2 in rectangles.keys():
                            objType = rectangles[key2]["region_attributes"]
                            obj = str(objType["Animal"])
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
                    # cv2.imshow('test', image) DONT NEED TO SHOW IMAGE
                    # cv2.waitKey(0)
                    count += 1

def index(request):
    print("hey")
    return render(request, 'test.html')

