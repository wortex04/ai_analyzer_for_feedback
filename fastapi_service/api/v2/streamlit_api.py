import io

import boto3
from fastapi import APIRouter
from starlette.responses import StreamingResponse
from fastapi_service.settings.default import settings

router = APIRouter()

session = boto3.session.Session()
s3_client = session.client(
    service_name='s3',
    endpoint_url='https://hb.vkcs.cloud'
)

@router.get("/get_csv_from_s3")
async def get_csv():
    response = s3_client.get_object(Bucket=settings.s3.bucket, Key=settings.s3.full_csv_key)
    csv_data = response['Body'].read().decode('utf-8')

    return StreamingResponse(io.StringIO(csv_data), media_type="text/csv")


@router.get("/get_sum_json")
async def get_sum():
    return {"prediction"}