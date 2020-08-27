import re

from langdetect import detect
from textblob import Word, TextBlob
from nltk import word_tokenize

from . import text_preprocessing_utils as utils

# list of functions in pipe
default_preprocessing_pipe = [
    'translate',
    'to_lower',
    'clean_contractions',
    'clean_special_chars',
    'clean_email',
    'tokenize',
    'clean_number',
    'remove_special_chars',
    'correct_spelling',
    'remove_stopwords',
    'remove_spaces'
]


class TextPreprocessor:
    """Class preprocess text in pipeline with config and standalone"""

    def __init__(self, pipeline=None):
        """
        Parameters
        ----------
        pipeline: list of str, optional, default=None
            preprocessing_pipe=None means default pipeline will be used

            default_preprocessing_pipe = [
                'translate',
                'to_lower',
                'clean_contractions',
                'clean_special_chars',
                'clean_email',
                'tokenize',
                'clean_number',
                'remove_special_chars',
                'correct_spelling',
                'remove_stopwords',
                'remove_spaces'
            ]


        Attributes
        ----------
        processing_pipe : list of str

        """
        self.processing_pipe = default_preprocessing_pipe if pipeline is None else pipeline

    def preprocess(self, text):
        """Method to predict category probability of input-message, where prediction = [afs, other, ps]

            Parameters
            ----------
            text: str, required

            Returns
            -------
            processed_text

            Notes
            ----------

            Example input:

                $ text = 'Hello Xsolla, when you send me 500$ i lost yesterday? Please let me know user@temp.com'

            Example output (with default pipe config):

                $ processed_text = 'hello xsolla when you send me __number__ i lost yesterday please let me know __email__'
        """
        for step in self.processing_pipe:
            if step in preprocessing_mapper:
                preprocess_method = preprocessing_mapper[step]
                text = preprocess_method(text)
                print(step, text)



        return text

    @staticmethod
    def detect_anomaly(text):
        # TODO
        pass

    @staticmethod
    def to_lower(text):
        return text.lower()

    @staticmethod
    def tokenize(text):
        tokens = word_tokenize(text)
        return ' '.join(tokens)

    @staticmethod
    def translate(text):
        lang = detect(text)

        if lang == 'en':
            return text

        try:
            blob = TextBlob(text)
            translated = str(blob.translate())
        except Exception as e:
            print(e)
            return text

        return translated

    @staticmethod
    def clean_number(text):
        text = re.sub(r'(\d+)([a-zA-Z])', r' \g<1> \g<2> ', text)
        text = re.sub(r'(\d+) (th|st|nd|rd) ', r' \g<1>\g<2> ', text)
        text = re.sub(r'(\d+),(\d+)', r' \g<1>\g<2> ', text)

        text = re.sub(r'([A-Za-z]*[\d]+[\w]*|[\d]+[A-Za-z]+[\w]*)', ' __number__ ', text)

        return text

    @staticmethod
    def remove_special_chars(text):
        special_chars = utils.special_chars
        return ' '.join([t for t in text.split() if t not in special_chars])

    @staticmethod
    def remove_stopwords(text):
        sw = utils.stopwords

        if len(sw) == 0:
            return text

        return ' '.join([t for t in text.split() if not t in sw])

    @staticmethod
    def remove_spaces(text):
        for space in utils.spaces:
            text = text.replace(space, ' ')

        text = text.strip()
        text = re.sub(r'\s+', ' ', text)

        return text

    @staticmethod
    def correct_spelling(text, confidence_threshold=0.7):
        tokens = text.split()

        for i, token in enumerate(tokens):
            r, confidence = Word(token).spellcheck()[0]

            if confidence > confidence_threshold:
                tokens[i] = r

        return ' '.join(tokens).strip()

    @staticmethod
    def clean_contractions(text):
        mapping = utils.contraction_mapping
        return ' '.join([mapping[t] if t in mapping else t for t in text.split()])

    @staticmethod
    def clean_special_chars(text):
        mapping = utils.special_chars_mapping

        for p in mapping:
            text = text.replace(p, mapping[p])

        return text

    @staticmethod
    def segregate_special_chars(text):
        special_chars = utils.special_chars

        for p in special_chars:
            text = text.replace(p, f' {p} ')

        return text

    @staticmethod
    def clean_email(text):
        return re.sub(r'([^@|\s]+@[^@]+\.[^@|\s]+)', ' __email__ ', text)


# TODO write mapper generator
preprocessing_mapper = {
    'to_lower': TextPreprocessor.to_lower,
    'detect_anomaly': TextPreprocessor.detect_anomaly,
    'tokenize': TextPreprocessor.tokenize,
    'translate': TextPreprocessor.translate,
    'clean_number': TextPreprocessor.clean_number,
    'remove_special_chars': TextPreprocessor.remove_special_chars,
    'remove_stopwords': TextPreprocessor.remove_stopwords,
    'remove_spaces': TextPreprocessor.remove_spaces,
    'correct_spelling': TextPreprocessor.correct_spelling,
    'clean_contractions': TextPreprocessor.clean_contractions,
    'clean_special_chars': TextPreprocessor.clean_special_chars,
    'segregate_special_chars': TextPreprocessor.segregate_special_chars,
    'clean_email': TextPreprocessor.clean_email,
}
