from django.http import HttpResponse
from django.shortcuts import render


def test(request):
    return render(request, "test.html")


def upload_test(request):
    if request.method == "GET":
        return render(request, "testuploadform.html")

    return HttpResponse()
