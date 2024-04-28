import io
from io import StringIO
from typing import Dict

import boto3
from fastapi import APIRouter
from fastapi_service.services.model_cls import infer_model
from fastapi_service.settings.default import settings
import pandas as pd

session = boto3.session.Session()
s3_client = session.client(
    service_name='s3',
    endpoint_url='https://hb.vkcs.cloud'
)


router = APIRouter()


@router.post("/extend_csv")
async def process_csv(data: Dict[str, str]):

    new_json = infer_model(data)
    df1 = pd.DataFrame(new_json, index=[0])

    response = s3_client.get_object(Bucket=settings.s3.bucket, Key=settings.s3.full_csv_key)
    df2 = pd.read_csv(io.BytesIO(response['Body'].read()))
    df = pd.concat([df1, df2], ignore_index=True)

    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_data = csv_buffer.getvalue()

    s3_client.put_object(Bucket=settings.s3.bucket, Key=settings.s3.full_csv_key, Body=csv_data.encode('utf-8'))

    return True


