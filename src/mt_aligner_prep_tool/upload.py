from pathlib import Path

import boto3
from botocore.exceptions import NoCredentialsError


def upload_file_to_s3(local_file_path: Path, bucket: str, s3_file: str):
    """local_file_path: Path to the file to upload"""
    """bucket: Bucket to upload to"""
    """s3_file: file name to be upload to s3, folder path in s3 bucket is included in the file name"""
    s3_client = boto3.client("s3")
    s3_client.upload_file(local_file_path, bucket, s3_file)


def create_s3_file_url(bucket_name: str, s3_file: str, expiration=3600):
    """
    Generate a presigned URL to share an S3 object
    :return: Presigned URL as string. If error, returns None.
    """
    s3_client = boto3.client("s3", region_name="us-east-1")
    try:
        response = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket_name, "Key": s3_file},
            ExpiresIn=expiration,
        )
    except NoCredentialsError:
        print("Credentials not available")
        return None

    return response
