import argparse
import logging
from  multiprocessing import Pool
from pathlib import Path
from typing import Optional

from tqdm import tqdm

from mt_aligner_prep_tool.config import (
    BO_FILES_PATH,
    EN_FILES_PATH,
    TOKENIZED_FILES_PATH,
    is_id_already_aligned,
    is_id_already_realigned,
    is_id_already_tokenized,
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
from mt_aligner_prep_tool.utility import execution_time

log_fn = "errors.log"
error_id_log_fn = "error_ids.log"


logging.basicConfig(
    filename=str(log_fn),
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def log_error_with_id(id_: str):
    """Log error message with ID to a separate file."""
    with open(error_id_log_fn, "a") as log_file:
        log_file.write(f"{id_}\n")


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


def pipeline(
    file_path: Path, re_align: bool = False, alignment_version: Optional[str] = "v1"
):
    """
    file_path: a file containing ids of the repositories to be aligned
                ,ids should be separated by new lines
    re_align: if True, realign the ids with the specific version
    alignment_version: version you want to name for realign

    """

    ids = get_file_content_by_lines(file_path)

    """load progress"""
    id_checkpoints = load_checkpoint()
    files_tobe_aligned = []

    for id_ in tqdm(ids, desc="Tokenizing files"):
        try:
            bo_id, en_id = f"BO{id_}", f"EN{id_}"

            """if id is already realigned with the specific version, skip it"""
            if re_align and is_id_already_realigned(
                id_, alignment_version, id_checkpoints
            ):
                continue

            """if id is already tokenized and aligned, skip it"""
            if not re_align and is_id_already_aligned(id_, id_checkpoints):
                continue

            """if id is not tokenized, tokenize it"""
            if not is_id_already_tokenized(id_, id_checkpoints):
                bo_file_path = BO_FILES_PATH / bo_id
                en_file_path = EN_FILES_PATH / en_id

                clone_github_repo(repository=bo_id, destination_folder=bo_file_path)
                clone_github_repo(repository=en_id, destination_folder=en_file_path)

                bo_file = find_first_txt_file(bo_file_path)
                en_file = find_first_txt_file(en_file_path)
                if bo_file and en_file:
                    tokenized_bo_file_path, tokenized_en_file_path = tokenize_files(
                        id_, bo_file, en_file
                    )
                    """save the id to checkpoint file for tokenization"""
                    save_checkpoint(id_, "Tokenization")

            tokenized_bo_file_path = TOKENIZED_FILES_PATH / f"tokenized_{bo_id}.txt"
            tokenized_en_file_path = TOKENIZED_FILES_PATH / f"tokenized_{en_id}.txt"

            if not re_align:
                alignment_version = None
            files_tobe_aligned.append(
                (
                    id_,
                    tokenized_bo_file_path,
                    tokenized_en_file_path,
                    alignment_version,
                )
            )

        except Exception as e:
            logging.error(f"{id_}: {e}")
            log_error_with_id(id_)
            continue
    num_processes = 10
    if len(files_tobe_aligned)== 0:
        return
    try:
        with Pool(processes=num_processes) as pool:
            list(
                tqdm(
                    pool.imap(upload_tokenized_files, files_tobe_aligned),
                    total=len(files_tobe_aligned),
                    desc="Uploading and aligning files",
                )
            )
    except Exception as e:
        logging.error(f"Alignment Failed {id_}: {e}")
        log_error_with_id(id_)


def tokenize_files(id_: str, bo_file: Path, en_file: Path):
    bo_id, en_id = f"BO{id_}", f"EN{id_}"
    """Tokenize the files"""
    tokenized_bo_text = sent_tokenize(bo_file.read_text(), lang="bo")
    tokenized_en_text = sent_tokenize(en_file.read_text(), lang="en")

    """Write both tokenized texts to files in TOKENIZED_FILES_PATH"""
    tokenized_bo_file_path = TOKENIZED_FILES_PATH / f"tokenized_{bo_id}.txt"
    tokenized_en_file_path = TOKENIZED_FILES_PATH / f"tokenized_{en_id}.txt"

    tokenized_bo_file_path.write_text(tokenized_bo_text)
    tokenized_en_file_path.write_text(tokenized_en_text)

    return tokenized_bo_file_path, tokenized_en_file_path


@execution_time(custom_name="upload_tokenized_files_and_aligning")
def upload_tokenized_files(
   args
):
    id_, tokenized_bo_file_path, tokenized_en_file_path, alignment_version = args
    print(f"Uploading tokenized files to s3 bucket for {id_}")
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

        print(f"Sending request to aligner for {id_}")

        response = send_api_request_to_aligner(
            id_, tokenized_tibetan_url, tokenized_english_url, alignment_version
        )
        if isinstance(response, dict) and "error" in response:
            raise Exception(response["error"])

        print(f"Alignment successful for {id_}")
        """save the id to checkpoint file"""
        save_checkpoint(id_, "Alignment")

        if alignment_version:
            """save the id to checkpoint file for re-alignment"""
            save_checkpoint(id_, "re_alignment", alignment_version)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Add TMs to dataset or update existing TMs"
    )
    parser.add_argument(
        "file_path",
        type=Path,
        help="TM ids to be added",
    )
    parser.add_argument(
        "--re_align", type=bool, default=False, help="Boolean flag for re-alignment"
    )
    parser.add_argument(
        "--alignment_version",
        type=str,
        default="v1",
        help="The version of the alignment process",
    )
    args = parser.parse_args()

    if args.file_path:
        pipeline(args.file_path, args.re_align, args.alignment_version)
    else:
        print("Please provide a file path that contains TM ids")
