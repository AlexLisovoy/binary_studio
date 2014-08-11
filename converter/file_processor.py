# coding: utf-8
import logging
import os
import uuid

from django.core.files.storage import default_storage


logger = logging.getLogger('debug.{}'.format(__name__))


def generate_guid():
    """
    Generate a random UUID. For example: 0afdb760-efb6-48da-bbaa-462c772e86c0.
    """
    return str(uuid.uuid4())


def upload_handler(the_file):
    """
    Store uploaded file under MEDIA_ROOT/generated namespace.
    """
    namespace = generate_guid()
    file_path = os.path.join(namespace, the_file.name)

    return namespace, default_storage.save(file_path, the_file)


def generate_url(namespace, file_format):
    """
    Finds file by namespace and file format and returns url on it.
    If file is not found, returns  empty string.
    """
    try:
        folders, files = default_storage.listdir(namespace)
    except OSError:
        raise RuntimeError(u'Unknown namespace `{}`'.format(namespace))
    for filename in files:
        if filename.endswith(file_format):
            return default_storage.url(os.path.join(namespace, filename))
    return ''


def get_original_file(namespace):
    """
    Finds the first downloaded file in namespace and returns info about it
    in format: full path, file extension(without dot).
    """
    file_path = min(
        listdir(default_storage.path(namespace)), key=os.path.getctime
    )

    file_format = os.path.splitext(file_path)[1]
    return file_path, file_format.lstrip('.')


def listdir(path):
    """
    Returns a list of all files (and directories) with full path in a
    given path.
    """
    return [os.path.join(path, f) for f in os.listdir(path)]


def get_file(namespace, file_format):
    """
    Finds file by namespace and file format and returns name and url on it.
    If file is not found, converts uploaded file to provided format.
    """
    if file_format not in processors:
        raise RuntimeError(u'Unknown file format `{}`'.format(file_format))

    url = generate_url(namespace, file_format)

    if not url:
        original_file, original_file_format = get_original_file(namespace)
        data = processors.get(original_file_format).parse_file(original_file)

        file_path = os.path.splitext(original_file)[0] + '.' + file_format

        processors.get(file_format).convert(file_path, data)

        url = generate_url(namespace, file_format)

    return os.path.basename(url), url


class ProcessorInterface(object):
    def parse_file(self, path):
        """
        Read data from file and converts to python data structures.
        """
        raise NotImplementedError()

    def convert(self, path, data):
        """
        Converts data and save it to file.
        """
        raise NotImplementedError()


class XmlProcessor(ProcessorInterface):
    pass


class JsonProcessor(ProcessorInterface):
    pass


class CsvProcessor(ProcessorInterface):
    pass


processors = {
    'csv': CsvProcessor(),
    'json': JsonProcessor(),
    'xml': XmlProcessor()
}