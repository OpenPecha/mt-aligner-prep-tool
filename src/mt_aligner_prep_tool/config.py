from pathlib import Path


def _mkdir(path):
    if path.is_dir():
        return path
    path.mkdir(exist_ok=True, parents=True)
    return path


BASE_PATH = _mkdir(Path.home() / ".mt_files")
BO_FILES_PATH = _mkdir(BASE_PATH / "tibetan_files")
EN_FILES_PATH = _mkdir(BASE_PATH / "english_files")

"""Path to the folder where the tokenized files(both english and tibetan files) will be stored"""
TOKENIZED_FILES_PATH = _mkdir(BASE_PATH / "tokenized_files")


CHECKPOINT_FILE = BASE_PATH / "checkpoint.txt"


def load_checkpoint():
    """Load the last checkpoint or create the file if it doesn't exist."""
    if not CHECKPOINT_FILE.exists():
        CHECKPOINT_FILE.touch()  # Create the file if it doesn't exist
        return []

    return CHECKPOINT_FILE.read_text().splitlines()


def save_checkpoint(item):
    with CHECKPOINT_FILE.open("a") as file:
        file.write(item + "\n")


def load_token():
    """Load credentials from a file"""
    credentials_file_path = Path.home() / ".hugging_face/credentials"
    if credentials_file_path.exists():
        credentials = credentials_file_path.read_text()
        bearer_token = credentials.splitlines()[0].split("=")[1].strip()
        return bearer_token
    else:
        raise FileNotFoundError(
            f"Credentials file not found at{str(credentials_file_path)}"
        )
