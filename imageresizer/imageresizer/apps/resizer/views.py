from django.shortcuts import render
from django.http import Http404, HttpResponsePermanentRedirect
from django.urls import reverse
from django.utils import timezone

from .models import Image

from PIL import Image as img

from io import BytesIO
from os import environ, getenv
import base64

import requests


IMAGES_PATH = "imageresizer/imagestorage/"


def startpage(request):
    """
    the logic returns the last 10 images and returns the html of the start page
    :param request:
    :return:
    """
    latest_images = Image.objects.order_by('-add_time')[:10]
    return render(request, 'resizer/welcome.html',
                  {'latest_images': latest_images})


def viewimage(request, image_name):
    """
    The logic of getting the name of the image after searching for
    the image in the database returns the view of the html file with the image.
    :param request:
    :param image_name:
    :return:
    """
    try:
        image = Image.objects.get(image_name=image_name)

        original_image = img.open(image.image_path)
        width, height = original_image.size

        with open(image.image_path, "rb") as image_file:
            encoded_string = 'data:image/gif;base64,' + \
                             base64.b64encode(image_file.read()).decode()

    except Exception as e:
        print("Exception", e)
        raise Http404('Изображение не найдено!')

    return render(request, 'resizer/viewimage.html', {"image": encoded_string,
                                                      'name': image.image_name,
                                                      'width': width,
                                                      'height': height
                                                      })


def inputimage(request):
    """
    The logic returns input image html file
    :param request:
    :return:
    """
    return render(request, 'resizer/inputimage.html', {'exception': ''})


def appendimage(request):
    """
    The logic of appends new file in data base,
    checks data on validation, and checks fields validation,
    returns  the view of the html file with the image
    :param request:
    :return:
    """
    try:
        IMAGE_EXTENSIONS = ['jpg', 'png', 'JPEG', 'icon', 'gif', "JPG"]

        if 'myFile' in request.FILES and request.POST['link']:
            return render(request, 'resizer/inputimage.html',
                          {'exception': 'Выберите только один типов загрузки файла!'})

        elif 'myFile' not in request.FILES and not request.POST['link']:
            return render(request, 'resizer/inputimage.html',
                          {'exception': 'Файл не выбран, выберите файл!'})

        if 'myFile' in request.FILES:
            file_name = request.FILES['myFile'].name
            file_path = IMAGES_PATH + file_name

            if file_name.split('.')[1] in IMAGE_EXTENSIONS:
                request_file = request.FILES
                my_file = request_file['myFile']
                image = BytesIO(my_file.read())
                with open(file_path, 'wb') as f:
                    f.write(image.getvalue())
            else:
                return render(request, 'resizer/inputimage.html',
                              {'exception': 'Не верный формат файла!'})

        elif 'link' in request.POST:
            file_name = request.POST['link']
            file_name = file_name.replace('//', '/').split('/')[-1]
            file_path = IMAGES_PATH + file_name
            if file_name.split('.')[1] in IMAGE_EXTENSIONS:
                resp = requests.get(request.POST['link'])
                with open(file_path, 'wb') as fw:
                    fw.write(resp.content)
            else:
                return render(request, 'resizer/inputimage.html',
                              {'exception': 'Не верный формат файла!'})

        if Image.objects.filter(image_name=file_name).exists():
            im = Image.objects.get(image_name=file_name)
            im.image_path = file_path
            im.add_time = timezone.now()

        else:
            im = Image(image_name=file_name,
                       image_path=file_path,
                       add_time=timezone.now()
                       )

        im.save()

        return HttpResponsePermanentRedirect(
            reverse('resizer:viewimage', args=(file_name,)))

    except Exception as e:
        return render(request, 'resizer/inputimage.html',
                      {'exception': 'Файл или ссылка повреждены! Выберите другой файл.'})


def resizeimage(request):
    """
    The logic does the resizing of the image and returns
      view html file with image..
    :param request:
    :return:
    """
    try:
        image_name = request.POST['name']

        image = Image.objects.get(image_name=image_name)

        original_image = img.open(image.image_path)
        origin_width, origin_height = original_image.size
        width = request.POST['width'] if len(
            request.POST['width']) > 0 else origin_width

        height = request.POST['height'] if len(
            request.POST['height']) > 0 else origin_height

        resized_image = original_image.resize((int(width), int(height)))

        width, height = resized_image.size

        output = BytesIO()
        if image_name.split('.')[1] == 'jpg':
            format = "JPEG"
        else:
            format = image_name.split('.')[1]
        resized_image.save(output, format=format)

        image_bynary = output.getvalue()

        encoded_string = 'data:image/gif;base64,' + \
                         base64.b64encode(image_bynary).decode()

        return render(request,
                      'resizer/viewimage.html',
                      {"image": encoded_string,
                       'name': image.image_name,
                       'width': width,
                       'height': height})

    except Exception as e:
        raise Http404('Изображение не найдено!')
