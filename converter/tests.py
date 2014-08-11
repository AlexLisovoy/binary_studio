# coding: utf-8
import os
import unittest
import mock

from django.core.files.storage import Storage
from . import file_processor


class MockStorage(Storage):
    def save(self, name, content):
        return name

    def listdir(self, path):
        if not path:
            raise OSError
        return [], os.listdir(os.path.dirname(os.path.abspath(__file__)))

    def url(self, name):
        return u'/test_media/{}'.format(name)

    def path(self, name):
        return name


class MockObject(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


@mock.patch('converter.file_processor.default_storage', new_callable=MockStorage)
class FileProcessorTestCase(unittest.TestCase):

    @mock.patch('converter.file_processor.uuid.uuid4')
    def test_generate_guid(self, uuid_mock, storage_mock):
        uuid_mock.return_value = 123
        self.assertEqual('123', file_processor.generate_guid())

    def test_upload_handler(self, storage_mock):
        guid = file_processor.generate_guid()

        with mock.patch('converter.file_processor.generate_guid') as generator_mock:
            generator_mock.return_value = guid
            the_file = MockObject(name='test.xml')
            self.assertTupleEqual(
                (guid, '{}/test.xml'.format(guid)),
                file_processor.upload_handler(the_file)
            )

    def test_generate_url(self, storage_mock):
        self.assertRaises(RuntimeError, file_processor.generate_url, '', 'xml')

        namespace = 'generating_namespace'
        self.assertEqual('', file_processor.generate_url(namespace, 'xml'))

        self.assertEqual('/test_media/generating_namespace/tests.py',
                         file_processor.generate_url(namespace, 'tests.py'))

    @mock.patch('converter.file_processor.listdir')
    def test_get_original_file(self, listdir_mock, storage_mock):
        namespace = __file__

        listdir_mock.return_value = [namespace]

        self.assertTupleEqual(
            (namespace, 'py'), file_processor.get_original_file(namespace)
        )

    @mock.patch('converter.file_processor.os.listdir')
    def test_listdir(self, listdir_mock, storage_mock):
        path = '/var/log/'

        listdir_mock.return_value = ['ngnix.log', 'celery.log']

        self.assertListEqual(
            ['/var/log/ngnix.log', '/var/log/celery.log'],
            file_processor.listdir(path)
        )