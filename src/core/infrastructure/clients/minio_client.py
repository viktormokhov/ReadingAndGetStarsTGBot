import logging

import urllib3
from minio import Minio
from minio.error import S3Error

async def init_minio(app, minio_settings):
    """
    Инициализация Minio клиента и проверка бакета avatars.
    """
    minio_client = Minio(
        minio_settings.endpoint_url,
        access_key=minio_settings.access_key,
        secret_key=minio_settings.secret_key,
        secure=minio_settings.minio_secure,
        http_client=urllib3.PoolManager(cert_reqs='CERT_NONE')
    )
    app.state.minio_client = minio_client

    bucket_name = "avatars"
    try:
        found = minio_client.bucket_exists(bucket_name)
        if not found:
            minio_client.make_bucket(bucket_name)
            logging.info(f"✅ Minio bucket '{bucket_name}' created")
        else:
            logging.info(f"✅ Minio bucket '{bucket_name}' exists")
    except S3Error as err:
        if err.code == "BucketAlreadyOwnedByYou":
            logging.info(f"✅ Minio bucket '{bucket_name}' already owned")
        elif err.code == "BucketAlreadyExists":
            logging.info(f"✅ Minio bucket '{bucket_name}' already exists globally")
        else:
            logging.error(f"❌ Minio bucket error: {err}")
            raise
    return minio_client