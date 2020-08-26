import fasttext

from .text_preprocessing import TextPreprocessor

class MessageCategorizer:
    def __init__(self, preprocessing_pipe=None):
        # load model (just 2mb)
        self.model = fasttext.load_model('project/ml/fasttext.ftz')

        # create text preprocessor with pipeline config
        self.preprocessor = TextPreprocessor(preprocessing_pipe)

    def predict_proba(self, x):
        x = self.preprocessor.preprocess(x)
        return self.model.predict(x, k=3)[1]


