from mt_aligner_prep_tool.tokenizers import sent_tokenize


def test_tibetan_tokenizer():
    tibetan_text = (
        "ཁྱོད་འཆི་དུས་སུ་ངུ་སྲིད། རོ་བྷེན་ཤར་མས་བརྩམས། ཁྱེད་ཀྱི་འཇོན་ནུས་རྟོགས་པར་གྱིས།"
    )
    tokenized_text = sent_tokenize(tibetan_text, lang="bo")
    assert (
        tokenized_text
        == "ཁྱོད་འཆི་དུས་སུ་ངུ་སྲིད།\nརོ་བྷེན་ཤར་མས་བརྩམས།\nཁྱེད་ཀྱི་འཇོན་ནུས་རྟོགས་པར་གྱིས།\n"
    )


def test_english_tokenizer():
    english_text = "I am a student. I am a student. I am a student."
    tokenized_text = sent_tokenize(english_text, lang="en")
    assert tokenized_text == "I am a student.\nI am a student.\nI am a student."
