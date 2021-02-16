from django.urls import path

from . import views


app_name = 'resizer'

urlpatterns = [
    path('', views.startpage, name='startpage'),
    path('<str:image_name>', views.viewimage, name='viewimage'),
    path('/new', views.inputimage, name='inputimage'),
    path('/append', views.appendimage, name='appendimage'),
    path('/resize', views.resizeimage, name='resizeimage')

]