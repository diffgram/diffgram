from shared.database.source_control.file import TextFile
import nltk

nltk.download('punkt')
from nltk.tokenize import word_tokenize, sent_tokenize

from typing import Callable


class TextTokenizer:
    type: str

    def __init__(self, type: str = 'nltk'):
        self.type = type
        self.WORD_TOKENIZER_FUNCTIONS = {
            'nltk': self.__tokenize_word_nltk
        }
        self.SENTENCE_TOKENIZER_FUNCTIONS = {
            'nltk': self.__tokenize_sentence_nltk
        }

    def __tokenize_word_nltk(self, text) -> list:
        paragraphs = [p for p in text.split('\n') if p]
        result = []
        for paragraph in paragraphs:
            tokens = word_tokenize(paragraph)
            for token in tokens:
                result.append({'value': token, 'tag': ''})
            result.append({'value': '\n', 'tag': ''})
        return result

    def __tokenize_sentence_nltk(self, text) -> list:
        tokens = sent_tokenize(text)
        result = []
        for token in tokens:
            result.append({'value': token, 'tag': ''})
        return result

    def get_word_tokenizer_function(self) -> Callable:
        return self.WORD_TOKENIZER_FUNCTIONS.get(self.type)

    def get_sentence_tokenizer_function(self) -> Callable:
        return self.SENTENCE_TOKENIZER_FUNCTIONS.get(self.type)

    def tokenize_words(self, text) -> list:
        tokenize_words = self.get_word_tokenizer_function()
        result = tokenize_words(text)
        return result

    def tokenize_sentences(self, text) -> list:
        tokenize_senteces = self.get_sentence_tokenizer_function()
        result = tokenize_senteces(text)
        return result
