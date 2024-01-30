import json
from pathlib import Path
from typing import Dict


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


CHECKPOINT_FILE = BASE_PATH / "checkpoint.json"


def load_checkpoint():
    """Load the last checkpoint or create the file if it doesn't exist."""
    if not CHECKPOINT_FILE.exists():
        CHECKPOINT_FILE.touch()  # Create the file if it doesn't exist
        return []

    with CHECKPOINT_FILE.open("r") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return {}


def save_checkpoint(id_, stage: str):
    """
    Save a checkpoint for a specific ID and stage.

    :param id_: The ID to save the checkpoint for.
    :param stage: The stage (e.g., 'Tokenization', 'Alignment') of the process.
    """
    checkpoints = load_checkpoint()
    if id_ not in checkpoints:
        checkpoints[id_] = {"Tokenization": False, "Alignment": False}

    """Save the checkpoint for the ID and stage."""
    checkpoints[id_][stage] = True

    with CHECKPOINT_FILE.open("w") as file:
        json.dump(checkpoints, file, indent=4)


def is_id_already_aligned(id_: str, id_checkpoints: Dict):
    if id_ in id_checkpoints and id_checkpoints[id_]["Alignment"]:
        return True
    return False


def is_id_already_tokenized(id_: str, id_checkpoints: Dict):
    if id_ in id_checkpoints and id_checkpoints[id_]["Tokenization"]:
        return True
    return False


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
