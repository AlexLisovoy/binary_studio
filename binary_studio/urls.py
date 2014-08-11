# coding: utf-8
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import patterns, url

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import TemplateView


urlpatterns = patterns(
    '',
    url(r'^$', TemplateView.as_view(template_name="base.html"), name='home'),
)

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)