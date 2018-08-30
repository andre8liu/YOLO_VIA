from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.




def index(request):
    print("hey")
    return render(request, 'test.html')

def get(request):
    print("hey")
    return render(request, 'via.html')  
