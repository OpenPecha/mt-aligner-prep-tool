from pathlib import Path
from typing import List

import boto3
from botocore.exceptions import NoCredentialsError

from mt_aligner_prep_tool.config import (
    BO_FILES_PATH,
    EN_FILES_PATH,
    TOKENIZED_FILES_PATH,
)
from mt_aligner_prep_tool.download import clone_github_repo, find_first_txt_file
from mt_aligner_prep_tool.tokenizers import sent_tokenize


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


def download_tibetan_english_files(ids: List[str]):
    """Download a repository from GitHub using git clone."""
    for id_ in ids:
        tibetan_id, english_id = f"BO{id_}", f"EN{id_}"
        tibetan_path = BO_FILES_PATH / tibetan_id
        english_path = EN_FILES_PATH / english_id

        clone_github_repo(repository=tibetan_id, destination_folder=tibetan_path)
        clone_github_repo(repository=english_id, destination_folder=english_path)

        tibetan_txt_file = find_first_txt_file(tibetan_path)
        english_txt_file = find_first_txt_file(english_path)

        if not tibetan_txt_file or not english_txt_file:
            continue

        tokenized_tibetan_text = sent_tokenize(tibetan_txt_file.read_text(), lang="bo")
        tokenized_english_text = sent_tokenize(english_txt_file.read_text(), lang="en")

        """Write both tokenized texts to files in TOKENIZED_FILES_PATH"""
        tokenized_tibetan_file_path = (
            TOKENIZED_FILES_PATH / f"tokenized_{tibetan_id}.txt"
        )
        tokenized_english_file_path = (
            TOKENIZED_FILES_PATH / f"tokenized_{english_id}.txt"
        )

        tokenized_tibetan_file_path.write_text(tokenized_tibetan_text)

        tokenized_english_file_path.write_text(tokenized_english_text)

        """Upload both tokenized texts to S3"""
        upload_file_to_s3(
            local_file_path=tokenized_tibetan_file_path,
            bucket="monlam.ai.tms",
            s3_file=f"tokenized_bo/{tokenized_tibetan_file_path.name}",
        )
        upload_file_to_s3(
            local_file_path=tokenized_english_file_path,
            bucket="monlam.ai.tms",
            s3_file=f"tokenized_en/{tokenized_english_file_path.name}",
        )
        """Get presigned url for both tokenized texts"""
        tokenized_tibetan_url = create_s3_file_url(
            "monlam.ai.tms", f"tokenized_bo/{tokenized_tibetan_file_path.name}"
        )
        tokenized_english_url = create_s3_file_url(
            "monlam.ai.tms", f"tokenized_en/{tokenized_english_file_path.name}"
        )

        if tokenized_tibetan_url and tokenized_english_url:
            """send both urls to api"""
            pass


if __name__ == "__main__":
    download_tibetan_english_files(["0001", "0002", "0003"])
