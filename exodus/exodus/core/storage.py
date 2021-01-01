from IPython.core.magics import logging
from django.conf import settings
from minio import Minio
from minio.error import (ResponseError, BucketAlreadyOwnedByYou, BucketAlreadyExists)


class RemoteStorageHelper():
    def __init__(self, prefix=''):
        if prefix:
            self.prefix = prefix
        self.minio_client = Minio(settings.MINIO_STORAGE_ENDPOINT,
                                  access_key=settings.MINIO_STORAGE_ACCESS_KEY,
                                  secret_key=settings.MINIO_STORAGE_SECRET_KEY,
                                  secure=settings.MINIO_STORAGE_USE_HTTPS)
        # Create Minio storage if needed
        try:
            self.minio_client.make_bucket(settings.MINIO_STORAGE_MEDIA_BUCKET_NAME, location="")
        except BucketAlreadyOwnedByYou:
            pass
        except BucketAlreadyExists:
            pass

    def get_prefix(self):
        return self.prefix

    def clear_prefix(self, prefix=None):
        """
        Remove all files having the given prefix from the Minio storage.
        :param prefix: files prefix
        """
        if prefix is None:
            prefix = self.prefix
        try:
            objects = self.minio_client.list_objects(
                settings.MINIO_STORAGE_MEDIA_BUCKET_NAME,
                prefix=prefix,
                recursive=True
            )
            for obj in objects:
                self.minio_client.remove_object(settings.MINIO_STORAGE_MEDIA_BUCKET_NAME, obj.object_name)
        except ResponseError as err:
            logging.info(err)

    def put_file(self, local_path, remote_name):
        """
        Upload the given file to the Minio storage.
        :param local_path: local file to upload
        :param remote_name: file name in Minio storage
        """
        self.minio_client.fput_object(settings.MINIO_STORAGE_MEDIA_BUCKET_NAME, remote_name, local_path)

    def get_file(self, remote_name, local_path):
        """
        Download a file from the Minio storage.
        :param remote_name: file name in Minio storage
        :param local_path: local destination file
        :return:
        """
        data = self.minio_client.get_object(settings.MINIO_STORAGE_MEDIA_BUCKET_NAME, remote_name)
        with open(local_path, 'wb') as file_data:
            for d in data.stream(32 * 1024):
                file_data.write(d)

    def download_and_put(self, url, remote_name):
        """
        Download a file and put it on Minio storage.
        :param url: URL of the file to download
        :param remote_name: file name in Minio storage
        :return: the destination name if succeed, empty string otherwise
        """
        import urllib.request
        import tempfile
        try:
            f = urllib.request.urlopen(url)
            with tempfile.NamedTemporaryFile(delete=True) as fp:
                fp.write(f.read())
                try:
                    self.minio_client.fput_object(settings.MINIO_STORAGE_MEDIA_BUCKET_NAME, remote_name, fp.name)
                except ResponseError as err:
                    logging.info(err)
                    return ''
                return remote_name
        except Exception as e:
            logging.info(e)
            return ''
