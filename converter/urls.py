# coding: utf-8
from django.conf.urls import patterns, url
from .views import UploadView
from .views import DownloadView


urlpatterns = patterns(
    '',
    url(r'^upload/$', UploadView.as_view(), name='uploader'),
    url(r'^download/(?P<namespace>[-|\w]+)/$', DownloadView.as_view(),
        name='downloader'),
)
