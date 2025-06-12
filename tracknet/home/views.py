from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request,"Home.html")

def progress(request):
    return render(request,"myprogress.html")