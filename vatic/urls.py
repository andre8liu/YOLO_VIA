from django.urls import path
from . import views

from django.views.decorators.csrf import csrf_exempt
urlpatterns = [
    #/vatic/
    path('', csrf_exempt(views.viaView.as_view()), name='index'),

    #/vatic/training/
    path('training/',views.train, name = 'training'),

    #/vatic/done_training/
    path('done_training/',views.done_training, name = 'done_training'),
]
