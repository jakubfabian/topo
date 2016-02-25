from django.http import HttpResponse
from django.conf.urls import patterns, url

hello = lambda request: HttpResponse("Hello .. mehr Power!")

urlpatterns = [
    url(r'^$', hello, name='hipower'),
    ]
