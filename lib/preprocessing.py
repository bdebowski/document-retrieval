import re

from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

from lib import lexer


class TextProcessor:
    """
    Used to convert input text into a string of stemmed, normalized, and filtered tokens.
    """

    def __init__(self):
        self._stopwords = set(stopwords.words())  # convert to set to speed up 'in' test
        self._stemmer = PorterStemmer()

    def process(self, text: str) -> str:
        """
        Processes the input text to normalize, filter, and stem the words.  Returns a string of space separated tokens.
        """
        # todo: "isn't" is one of the stop words but will get tokenized to isn 't and then isn will be removed as a stop word but not 't
        #  Running stop word removal first doesn't fully solve the problem because some stop words might be entwined with punctuation or hyphens, etc.
        #  Using the nltk word tokenizer doesn't solve the problem either since it tokenizes isn't as "is n't" with "is" being a stopword but
        #  not "n't".
        # todo: "year's" and similar words have their own problem; "year's" gets tokenized to "year's" then stemmed to "year'".  With the nltk
        #  word_tokenizer() it gets tokenized to "year 's" which are then left as they are by stopword removal and stemming.
        processed_tokens = []

        # Filter on token type and split the APOSTROPHE_CARRY token to two tokens
        lexer.lexer.input(text)
        for t in lexer.lexer:
            if t.type == lexer.TYPE_LABEL:
                return text.strip()
            elif t.type == lexer.TYPE_PUNCTUATION or t.type == lexer.TYPE_DELIMITER or t.type == lexer.TYPE_NUMBER:
                continue
            elif t.type == lexer.TYPE_APOSTROPHE_CARRY:
                processed_tokens += t.value.split(" ")
            else:
                if re.match(r"^\d+$", t.value):
                    raise RuntimeError("{} in {} not filtered".format(t.value, text))
                processed_tokens.append(t.value)

        # Normalize, remove stop words, and apply stemming
        processed_tokens = [self._stemmer.stem(t.lower()) for t in processed_tokens if t.lower() not in self._stopwords]

        return " ".join(processed_tokens)
