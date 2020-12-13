from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class StaticStorage(S3Boto3Storage):
    location = 'static'
    default_acl = 'public-read'


class PublicMediaStorage(S3Boto3Storage):
    location = 'media'
    default_acl = 'public-read'
    file_overwrite = False


class PrivateMediaStorage(S3Boto3Storage):
    location = settings.AWS_PRIVATE_MEDIA_LOCATION
    default_acl = 'private'
    file_overwrite = False
    custom_domain = False

class DPMediaStorage(S3Boto3Storage):
    location = 'media/profile_dp'
    default_acl = 'public-read'
    file_overwrite = False

class ThumbnailMediaStorage(S3Boto3Storage):
    location = 'media/upload_thumbnail'
    default_acl = 'public-read'
    file_overwrite = False

class MusicTracksStorage(S3Boto3Storage):
    location = 'media/music_tracks'
    default_acl = 'public-read'
    file_overwrite = False

class VedioTracksStorage(S3Boto3Storage):
    location = 'media/upload_vedio'
    default_acl = 'public-read'
    file_overwrite = False

class CameraAssetStorage(S3Boto3Storage):
    location = 'media/camera_asset'
    default_acl = 'public-read'
    file_overwrite = False