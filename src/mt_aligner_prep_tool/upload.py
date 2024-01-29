import random
from pathlib import Path

import boto3
import requests
from botocore.exceptions import NoCredentialsError

from mt_aligner_prep_tool.config import load_token


def upload_file_to_s3(local_file_path: Path, bucket: str, s3_file: str):
    """local_file_path: Path to the file to upload"""
    """bucket: Bucket to upload to"""
    """s3_file: file name to be upload to s3, folder path in s3 bucket is included in the file name"""
    s3_client = boto3.client("s3")
    s3_client.upload_file(local_file_path, bucket, s3_file)


def create_s3_file_url(bucket_name: str, s3_file: str, expiration=36000):
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


def generate_random_test_version():
    version = random.randint(1, 1000)
    subversion = random.randint(1, 1000)
    subsubversion = random.randint(1, 1000)

    test_version = f"Testv{version}.{subversion}.{subsubversion}"
    return test_version


def send_api_request_to_aligner(tokenized_tibetan_url: str, tokenized_english_url: str):
    """Send both urls to api"""
    json_data = {
        "inputs": {
            "text_id": generate_random_test_version(),
            "bo_file_url": tokenized_tibetan_url,
            "en_file_url": tokenized_english_url,
            "parameters": {},
        }
    }

    endpoint_url = "https://z4najyef6e0oe9mj.us-east-1.aws.endpoints.huggingface.cloud/"
    bearer_token = load_token()

    result = send_json_request(endpoint_url, bearer_token, json_data)
    return result


def send_json_request(endpoint_url, bearer_token, json_data):
    """
    Send a JSON request to a specified endpoint with a Bearer token.

    :param endpoint_url: URL of the endpoint to send the request to.
    :param bearer_token: Bearer token for authorization.
    :param json_data: JSON data to be sent in the request.
    :return: The response from the server.
    """

    headers = {"Authorization": f"Bearer {bearer_token}"}

    try:
        response = requests.post(endpoint_url, headers=headers, json=json_data)

        if response.status_code == 200:
            return response.json()
        else:
            return f"Error: {response.status_code}", response.text
    except requests.exceptions.RequestException as e:
        return f"Request failed: {e}"
