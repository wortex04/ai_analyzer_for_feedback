from abc import ABC
from typing import Any

import boto3

from fastapi_service.settings.default import settings, Settings

# LOCAL_MODELS_PATH = os.path.dirname(settings.project.base_dir) + settings.project.models_path

# Initialize the S3 client with the custom endpoint URL
session = boto3.session.Session()
s3_client = session.client(
    service_name='s3',
    endpoint_url='https://hb.vkcs.cloud'
)

class AbstractModelGetter(ABC):

    def get_model(self, conf: Settings) -> Any:
        """Get model from S3 if possible
        """

        raise NotImplemented

#https://feedback_s3.hb.ru-msk.vkcs.cloud/model_weights/bert.pth
class ModelLoader(AbstractModelGetter):
    def get_model(self, conf: Settings) -> bytes:
        response = s3_client.get_object(Bucket=conf.s3.bucket, Key=conf.s3.tg_model_key)
        model_bytes = response['Body'].read()
        return model_bytes


def get_torch_models() -> bytes:
    return ModelLoader().get_model(settings)
