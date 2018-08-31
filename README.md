# YOLO_VIA

@Author: Andre Liu 
@Date:   8/31/2018

This application combines several steps of training a DNN using YOLO. You upload
your images, annotate the images, configure the YOLO settings, then press train and
the application will begin the training and allow you to download the weights file
when it is done. The application also has a auto annotating feature where you annotate
only a portion of your images. The application will take these pictures and train a
premodel. It will then use this premodel to detect objects in the remaining pictures
and display those annotations to you so you can edit them. 


#### Items to download for Server setup: ####
1. Django
2. Python3
3. Docker
4. Nvidia-Docker/CUDA
5. Open-CV

#### Set up steps for server: ####
1.  Install all the above, then pull code from github. 
2.  You must add the IP address of the server to the webapp/settings.py file under
    'ALLOWED_HOSTS'.
3.  Then to run the server, enter 'python3 manage.py runserver 0.0.0.0:PORTNUMBER' into
    the terminal and the server should start. 


#### Please use Google Chrome to run applciation!! ####


How to use:

1.  Start off by going to the /vatic url. Click on 'Load Images' on the bottom to start 
    loading images into the annotator. If you wish to add more images later, navigate to the images tab on the top nav bar and click 'Load or Add Images'.
2.  Once the images are loaded, you may start annotating them by clicking and dragging on     the pictures. When you have made the box for your first annotation, click on 'Region 
    Attributes' on the left column. A table will then appear and you can label that annotation. Please only use rectangles to annotate the pictures.
3.  Once you are done annotating the pictures for the premodel training, you can edit the 
    YOLO setttings to your desired values. Then click 'Train Premodel' and the model will
    begin training in the server. When it is done, you will see the objects that YOLO has decected show up on the pictures. The premodel will only train on pictures you have annotated.
4.  You can then edit these annotations however you like by resizing or pressing delete       to remove an annotation once it is selected. When you are finished, you can then          click 'Train Model' to train the model on all the pictures. When this training is         done, you will see a page that says "Training done!" and a button that will allow you     to download the weights file. 



Basic work flow:
1.  When images are selected to load onto the annotator, they are saved to the server
    via POST request.
2.  When 'Train Premodel' is clicked, the configerations  and annotations are sent to the     server. The annotations are then converted to yolo format and container for darknet       is started. 
3.  All the files and images are copied into the container and all the configeration files
    are edited to match the ones given. The premodel training is then started. 
4.  When the premodel is finished training, a script is run inside the container that         will use the completed model to run inference on the remaining images. These              annotations are then converted to JSON format and sent back to the server.
5.  They are then sent back to the client side and shown to the user where they are
    free to edit the annotations. 
6.  When the user is finished editing the annotations, they may click the 'Train Model'
    button that will execute a similar process as the premodel training. 
7.  When training is completed, the resulting weights file will be copied to the server.
8.  Since the weights file can range from 50MB to several GB, the file will be sent
    as chunks to the client side for the user to download when they click the download
    button. 



 
