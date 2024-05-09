import re
from typing import List

import botok
from spacy.lang.en import English

from mt_aligner_prep_tool.utility import SuppressStdout

bo_word_tokenizer = None
en_nlp = English()
en_nlp.add_pipe("sentencizer")
en_nlp.max_length = 5000000

# Types
SENT_PER_LINE_STR = str  # sentence per line string
IS_AFFIX_PART = bool


def get_bo_word_tokenizer():
    global bo_word_tokenizer
    if bo_word_tokenizer is None:
        bo_word_tokenizer = botok.WordTokenizer()
    return bo_word_tokenizer


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


def bo_preprocess(text: str) -> str:
    text = text.replace("\r", "").replace("\n", "")
    return text


def bo_sent_tokenizer(text: str) -> SENT_PER_LINE_STR:
    """Tokenize a text into sentences."""

    def get_token_text(token):
        if hasattr(token, "text_cleaned") and token.text_cleaned:
            return token.text_cleaned
        else:
            return token.text

    # fmt: off
    opening_puncts = ['༁', '༂', '༃', '༄', '༅', '༆', '༇', '༈', '༉', '༊', '༑', '༒', '༺', '༼', '༿', '࿐', '࿑', '࿓', '࿔', '࿙']  # noqa: E501
    closing_puncts = ['།', '༎', '༏', '༐', '༔', '༴', '༻', '༽', '༾', '࿚']  # noqa: E501
    skip_chunk_types = [botok.vars.CharMarkers.CJK.name, botok.vars.CharMarkers.LATIN.name]
    # fmt: on

    # Regex to improve the chunking of shunits, this will be replaced by a better sentence segmentation in botok
    r_replace = [
        (r"༼༼[༠-༩]+[བན]༽", r""),  # delete source image numbers `ས་༼༤བ༽མེད་བ`
        (
            r"([^ང])་([༔།])",
            r"\1\2",
        ),  # delete spurious spaces added by botok in the cleantext values
        (
            r"([།གཤ]{1,2})\s+(།{1,2})",
            r"\1\2 ",
        ),  # Samdong Rinpoche style double shad. This needs to be applied on inference input
        # (r"", r""),
    ]

    text = bo_preprocess(text)
    sents_words = []
    current_sentence = []
    tokenizer = get_bo_word_tokenizer()
    tokens = tokenizer.tokenize(text, split_affixes=False)
    for token in tokens:
        if token.chunk_type in skip_chunk_types:
            continue
        token_text = get_token_text(token)
        if any(punct in token_text for punct in opening_puncts):
            current_sentence.append(token_text.strip())
        elif any(punct in token_text for punct in closing_puncts):
            current_sentence.append(token_text.strip())
            sents_words.append("".join(current_sentence))
            current_sentence = []
        else:
            current_sentence.append(token_text)

    # If there's any remaining text in the current_sentence
    if current_sentence:
        sents_words.append("".join(current_sentence))

    # Join all sentences with a newline
    sents_text = "\n".join(sents_words)

    # Apply replacements
    for fr, to in r_replace:
        sents_text = re.sub(fr, to, sents_text)

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

