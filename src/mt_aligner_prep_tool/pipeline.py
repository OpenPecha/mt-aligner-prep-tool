from pathlib import Path
from typing import List

from mt_aligner_prep_tool.config import (
    BO_FILES_PATH,
    EN_FILES_PATH,
    TOKENIZED_FILES_PATH,
)
from mt_aligner_prep_tool.download import clone_github_repo, find_first_txt_file
from mt_aligner_prep_tool.tokenizers import sent_tokenize
from mt_aligner_prep_tool.upload import create_s3_file_url, upload_file_to_s3


def pipeline(ids: List[str]):
    """Download a repository from GitHub using git clone."""
    for id_ in ids:
        bo_id, en_id = f"BO{id_}", f"EN{id_}"
        bo_file_path = BO_FILES_PATH / bo_id
        en_file_path = EN_FILES_PATH / en_id

        clone_github_repo(repository=bo_id, destination_folder=bo_file_path)
        clone_github_repo(repository=en_id, destination_folder=en_file_path)

        bo_file = find_first_txt_file(bo_file_path)
        en_file = find_first_txt_file(en_file_path)

        if bo_file and en_file:
            tokenize_files(bo_id, en_id, bo_file, en_file)


def tokenize_files(bo_id: str, en_id: str, bo_file: Path, en_file: Path):
    """Tokenize the files and upload to S3"""
    tokenized_bo_text = sent_tokenize(bo_file.read_text(), lang="bo")
    tokenized_en_text = sent_tokenize(en_file.read_text(), lang="en")

    """Write both tokenized texts to files in TOKENIZED_FILES_PATH"""
    tokenized_bo_file_path = TOKENIZED_FILES_PATH / f"tokenized_{bo_id}.txt"
    tokenized_en_file_path = TOKENIZED_FILES_PATH / f"tokenized_{en_id}.txt"

    tokenized_bo_file_path.write_text(tokenized_bo_text)
    tokenized_en_file_path.write_text(tokenized_en_text)

    """Upload both tokenized texts to S3"""
    upload_tokenized_files(tokenized_bo_file_path, tokenized_en_file_path)


def upload_tokenized_files(tokenized_bo_file_path: Path, tokenized_en_file_path: Path):
    """Upload both tokenized texts to S3"""
    upload_file_to_s3(
        local_file_path=tokenized_bo_file_path,
        bucket="monlam.ai.tms",
        s3_file=f"tokenized_bo/{tokenized_bo_file_path.name}",
    )
    upload_file_to_s3(
        local_file_path=tokenized_en_file_path,
        bucket="monlam.ai.tms",
        s3_file=f"tokenized_en/{tokenized_en_file_path.name}",
    )
    """Get presigned url for both tokenized texts"""
    tokenized_tibetan_url = create_s3_file_url(
        "monlam.ai.tms", f"tokenized_bo/{tokenized_bo_file_path.name}"
    )
    tokenized_english_url = create_s3_file_url(
        "monlam.ai.tms", f"tokenized_en/{tokenized_en_file_path.name}"
    )

    if tokenized_tibetan_url and tokenized_english_url:
        """send both urls to api"""
        pass


if __name__ == "__main__":
    pipeline(["0001", "0002", "0003"])
