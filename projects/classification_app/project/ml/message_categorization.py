import fasttext

from .text_preprocessing import TextPreprocessor


class MessageCategorizer:
    label_mapper = {
        '__label__afs': 0,
        '__label__other': 1,
        '__label__ps': 2,
    }

    def __init__(self, preprocessing_pipe=None):
        # load model (just 2mb)
        self.model = fasttext.load_model('project/ml/storage/message_categorizer/fasttext.ftz')

        # create text preprocessor with pipeline config
        self.preprocessor = TextPreprocessor(preprocessing_pipe)

    def predict_proba(self, x):
        print(1, x)
        try:
            x = self.preprocessor.preprocess(x)
        except Exception as e:
            print(e)

        print(2, x)

        pred = self.model.predict(x, k=3)

        formatted_pred = [0, 0, 0]
        for i, label in enumerate(pred[0]):
            idx = self.label_mapper[label]
            formatted_pred[idx] = pred[1][i]

        return formatted_pred
