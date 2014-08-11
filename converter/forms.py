# coding: utf-8
import os

from django import forms

from .file_processor import processors


def is_valid_file_ext(the_file):
    extension = os.path.splitext(the_file.name)[1]
    return extension.lstrip('.') in processors


class UploadForm(forms.Form):
    the_file = forms.FileField()

    def clean_the_file(self):
        the_file = self.cleaned_data['the_file']

        if not is_valid_file_ext(the_file):
            raise forms.ValidationError(u"Unsupported format")

        return the_file