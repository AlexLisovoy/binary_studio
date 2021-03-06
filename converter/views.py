# coding: utf-8
import json


from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.views.generic import FormView
from django.views.generic import View

from .forms import UploadForm
from .file_processor import upload_handler
from .file_processor import get_file


class JSONResponseMixin(object):
    """
    A mixin that can be used to render a JSON response.
    """
    def render_to_json_response(self, context, **kwargs):
        """
        Returns a JSON response, transforming 'context' to make the payload.
        """
        return HttpResponse(
            json.dumps(context), content_type='application/json', **kwargs
        )


class UploadView(JSONResponseMixin, FormView):
    form_class = UploadForm
    http_method_names = ['post']

    def form_valid(self, form):
        """
        Returns a JSON response, with url for access file.
        """
        namespace, filename = upload_handler(self.request.FILES['the_file'])
        access_url = reverse(
            'downloader', kwargs={'namespace': namespace}
        )

        return self.render_to_json_response({'access_url': access_url})

    def form_invalid(self, form):
        """
        Returns a JSON response, with form errors.
        """
        return self.render_to_json_response({'errors': form.errors}, status=400)


class DownloadView(JSONResponseMixin, View):
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        context = {'status': True}

        try:
            filename, url = get_file(
                kwargs.get('namespace'), request.GET.get('format')
            )
            context['url'] = url
            context['filename'] = filename
        except Exception:
            context['status'] = False
            context['error'] = u'Oops! Something went wrong.'

        return self.render_to_json_response(context)