import re
from typing import List

from spacy.lang.en import English
from bo_sent_tokenizer import segment

from mt_aligner_prep_tool.utility import SuppressStdout

en_nlp = English()
en_nlp.add_pipe("sentencizer")
en_nlp.max_length = 5000000

# Types
SENT_PER_LINE_STR = str  # sentence per line string


def join_sentences(sentences):
    """Join sentences into a text with one sentence per line."""
    return "\n".join(sentences)


def en_preprocess(text: str) -> str:
    re_sub = [(r"\r\n", " "), (r"\n", " "), (r"\s{2,}", " "), (r"\t", " ")]
    for pattern, repl in re_sub:
        text = re.sub(pattern, repl, text)
    return text


def en_sent_tokenizer(text: SENT_PER_LINE_STR) -> SENT_PER_LINE_STR:
    """Tokenize a text into sentences."""
    text = en_preprocess(text)
    doc = en_nlp(text)
    sentences = [sent.text for sent in doc.sents]
    return join_sentences(sentences)


def en_word_tokenizer(text: str) -> List[str]:
    """Tokenize a text into words."""
    doc = en_nlp(text)
    words = [token.text for token in doc]
    return words



def bo_sent_tokenizer(text: str) -> SENT_PER_LINE_STR:
    text = remove_emojis(text)
    sents_text = segment(text)
    return sents_text


def remove_emojis(text):
    emojis_to_remove = ["1️⃣", "2️⃣", "3️⃣"]
    for emoji in emojis_to_remove:
        text = text.replace(emoji, "")
    return text

def split_text_into_mb_chunks(text, chunk_size_mb=1):
    chunk_size_bytes = chunk_size_mb * 1024 * 1024  # Convert MB to bytes
    chunks = []
    current_chunk = []
    current_size = 0

    lines = text.splitlines(keepends=True)  # Split text into lines, preserving line breaks

    for line in lines:
        line_size = len(line.encode('utf-8'))
        
        if current_size + line_size > chunk_size_bytes:
            # If adding this line exceeds the chunk size, store the current chunk and reset
            if current_chunk:  # Ensure there's something to append
                chunks.append(''.join(current_chunk))
                current_chunk = []
                current_size = 0

            # If the line itself is larger than the chunk size, split it further
            while line_size > chunk_size_bytes:
                part = line[:chunk_size_bytes - current_size]
                line = line[chunk_size_bytes - current_size:]
                line_size = len(line.encode('utf-8'))
                current_chunk.append(part)
                chunks.append(''.join(current_chunk))
                current_chunk = []
                current_size = 0

        # Add the line to the current chunk
        current_chunk.append(line)
        current_size += line_size

    # Add the last chunk if any
    if current_chunk:
        chunks.append(''.join(current_chunk))

    return chunks


def sent_tokenize(text, lang) -> SENT_PER_LINE_STR:
    """Tokenize a text into sentences."""
    text = remove_emojis(text)

    if lang == "en":
        return en_sent_tokenizer(text)
    elif lang == "bo":
        with SuppressStdout():
            splited_text = split_text_into_mb_chunks(text)
            tokenized_text = [bo_sent_tokenizer(chunk).strip() for chunk in splited_text]
            joined_tokenized_text = "\n".join(filter(None, tokenized_text)) # Only join non-empty entries
            return  f"{joined_tokenized_text}\n"
    else:
        raise NotImplementedError

