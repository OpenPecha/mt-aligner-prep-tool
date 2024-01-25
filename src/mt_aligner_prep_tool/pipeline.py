from typing import List

from mt_aligner_prep_tool.config import BO_FILES_PATH, EN_FILES_PATH
from mt_aligner_prep_tool.download import clone_github_repo, find_first_txt_file
from mt_aligner_prep_tool.tokenizers import sent_tokenize


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

        if tibetan_txt_file and english_txt_file:
            tokenized_tibetan_text = sent_tokenize(
                tibetan_txt_file.read_text(), lang="bo"
            )
            tokenized_english_text = sent_tokenize(
                english_txt_file.read_text(), lang="en"
            )
            print(tokenized_tibetan_text)
            print(tokenized_english_text)


if __name__ == "__main__":
    download_tibetan_english_files(["0001", "0002", "0003"])
