# YOLO_VIA

This application combines several steps of training a DNN using YOLO. You just upload
your images, annotate the images, configure the YOLO settings, then press train and
the application will begin the training and allow you to download the weights file
when it is done. The application also has a auto annotating feature where you annotate
only a portion of your images. The application will take these pictures and train a
premodel. It will then use this premodel to detect objects in the remaining pictures
and display those annotations to you so you can edit them. 


####Items to download for Server setup:
1. Django
2. Python3
3. Docker
4. Nvidia-Docker/CUDA
5. Open-CV


#### Please use Google Chrome! ####


Basic work flow:
1.  When images are selected to load onto the annotator, they are saved to the server
    via POST request
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



 
