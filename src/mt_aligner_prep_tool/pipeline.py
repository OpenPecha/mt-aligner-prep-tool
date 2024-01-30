import logging
from pathlib import Path

from mt_aligner_prep_tool.config import (
    BO_FILES_PATH,
    EN_FILES_PATH,
    TOKENIZED_FILES_PATH,
    load_checkpoint,
    save_checkpoint,
)
from mt_aligner_prep_tool.download import clone_github_repo, find_first_txt_file
from mt_aligner_prep_tool.tokenizers import sent_tokenize
from mt_aligner_prep_tool.upload import (
    create_s3_file_url,
    send_api_request_to_aligner,
    upload_file_to_s3,
)

log_fn = "errors.log"

logging.basicConfig(
    filename=str(log_fn),
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def get_file_content_by_lines(file_path):
    """
    Reads a file and returns its content split into lines.

    :param file_path: Path to the file to be read.
    :return: List of lines in the file.
    """
    file_path = Path(file_path)
    if file_path.exists() and file_path.is_file():
        with file_path.open("r") as file:
            return [line.strip() for line in file if line.strip()]
    else:
        raise FileNotFoundError(f"No file found at {file_path}")


def pipeline(file_path: Path):
    """file_path: a file containing ids of the repositories to be aligned"""
    """ids should be separated by new lines"""
    ids = get_file_content_by_lines(file_path)

    """load progress"""
    already_aligned_ids = load_checkpoint()

    for id_ in ids:
        try:
            if id_ in already_aligned_ids:
                continue
            bo_id, en_id = f"BO{id_}", f"EN{id_}"
            bo_file_path = BO_FILES_PATH / bo_id
            en_file_path = EN_FILES_PATH / en_id

            clone_github_repo(repository=bo_id, destination_folder=bo_file_path)
            clone_github_repo(repository=en_id, destination_folder=en_file_path)

            bo_file = find_first_txt_file(bo_file_path)
            en_file = find_first_txt_file(en_file_path)

            if bo_file and en_file:
                tokenize_files(id_, bo_id, en_id, bo_file, en_file)
        except Exception as e:
            logging.error(f"{id_}: {e}")
            continue


def tokenize_files(id_: str, bo_id: str, en_id: str, bo_file: Path, en_file: Path):
    """Tokenize the files"""
    tokenized_bo_text = sent_tokenize(bo_file.read_text(), lang="bo")
    tokenized_en_text = sent_tokenize(en_file.read_text(), lang="en")

    """Write both tokenized texts to files in TOKENIZED_FILES_PATH"""
    tokenized_bo_file_path = TOKENIZED_FILES_PATH / f"tokenized_{bo_id}.txt"
    tokenized_en_file_path = TOKENIZED_FILES_PATH / f"tokenized_{en_id}.txt"

    tokenized_bo_file_path.write_text(tokenized_bo_text)
    tokenized_en_file_path.write_text(tokenized_en_text)

    """Upload both tokenized texts to S3"""
    upload_tokenized_files(id_, tokenized_bo_file_path, tokenized_en_file_path)


def upload_tokenized_files(
    id_: str, tokenized_bo_file_path: Path, tokenized_en_file_path: Path
):
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

    """Get corresponding url for both tokenized texts"""
    tokenized_tibetan_url = create_s3_file_url(
        "monlam.ai.tms", f"tokenized_bo/{tokenized_bo_file_path.name}"
    )
    tokenized_english_url = create_s3_file_url(
        "monlam.ai.tms", f"tokenized_en/{tokenized_en_file_path.name}"
    )

    if tokenized_tibetan_url and tokenized_english_url:
        """send both urls to api"""
        """get github url where tm result is stored"""

        tm_url = send_api_request_to_aligner(  # noqa
            tokenized_tibetan_url, tokenized_english_url
        )
        """save the id to checkpoint file"""
        save_checkpoint(id_)


if __name__ == "__main__":
    ROOT_DIR = Path(__file__).parent.parent.parent
    test_file_path = ROOT_DIR / "test_file.txt"
    pipeline(test_file_path)
