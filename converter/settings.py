# coding: utf-8
from django.conf import settings

# 5 mb
FILE_UPLOAD_MAX_SIZE = getattr(settings, 'FILE_UPLOAD_MAX_SIZE', 5242880)