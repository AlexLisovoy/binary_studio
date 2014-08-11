# coding: utf-8
import logging
import os
import uuid
import json
import csv
import xmltodict

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
    def parse_file(self, path):
        with open(path) as xml_file:
            data = xmltodict.parse(xml_file)
        return data

    def convert(self, path, data):
        if isinstance(data, list):
            data = {'items': {str(k): v for k, v in enumerate(data)}}

        try:
            with open(path, 'w') as outfile:
                xmltodict.unparse(data, outfile, pretty=True)
        except Exception:
            logger.exception(u'File `{}` can not be parsed in xml'.format(path))
            os.remove(path)
            raise
        return path


class JsonProcessor(ProcessorInterface):
    def parse_file(self, path):
        with open(path) as json_file:
            json_data = json.load(json_file)
        return json_data

    def convert(self, path,  data):
        try:
            with open(path, 'w') as outfile:
                json.dump(data, outfile)
        except Exception:
            logger.exception(
                u'File `{}` can not be parsed in json'.format(path)
            )
            os.remove(path)
            raise
        return path


class CsvProcessor(ProcessorInterface):
    def parse_file(self, path):
        data = []
        with open(path, 'r') as csvfile:
            # sniff to find the format
            file_dialect = csv.Sniffer().sniff(csvfile.read(1024))
            csvfile.seek(0)

            # read the CSV file into a dictionary
            dict_reader = csv.DictReader(csvfile, dialect=file_dialect)
            for row in dict_reader:
                data.append(row)
        return data

    def convert(self, path, data):
        if isinstance(data, dict):
            data = [data]

        try:
            with open(path, 'wb') as outfile:
                dict_writer = csv.DictWriter(outfile, data[0].keys())
                dict_writer.writeheader()
                dict_writer.writerows(data)
        except Exception:
            logger.exception(u'File `{}` can not be parsed in csv'.format(path))
            os.remove(path)
            raise
        return path


processors = {
    'csv': CsvProcessor(),
    'json': JsonProcessor(),
    'xml': XmlProcessor()
}