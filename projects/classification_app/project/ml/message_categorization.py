import fasttext

from .text_preprocessing import TextPreprocessor


class MessageCategorizer:
    """Class to classify category of input-message, where categories = {afs, other, ps}"""

    """map fasttext labels to their position at response proba-array"""
    label_mapper = {
        '__label__afs': 0,
        '__label__other': 1,
        '__label__ps': 2,
    }

    def __init__(self, preprocessing_pipe=None):
        """
        Parameters
        ----------
        preprocessing_pipe: list of str, optional, default=None
            preprocessing_pipe=None means default pipeline will be used
            Default pipe list can be found in text_preprocessing module

        Attributes
        ----------
        model : fasttext
            fasttext compressed custom-trained classificator from original fasttext lib
        preprocessor : TextPreprocessor
            instance of TextPreprocessor to preprocess input messages with pipeline config

        """
        # load model (just 2mb)
        self.model = fasttext.load_model('project/ml/storage/message_categorizer/fasttext.ftz')

        # create text preprocessor with pipeline config
        self.preprocessor = TextPreprocessor(preprocessing_pipe)

    def predict_proba(self, x):
        """Method for calculation workload scoring based on historical data

        Parameters
        ----------
        x: str, required
            raw message (before preprocessing) to predict category

        Returns
        -------
        prediction
            3-components 1d-array of floats
            where indexes: 0 - afs, 1 - other, 2 - ps

        Notes
        ----------

        Example input:

            $ x = 'hello xsolla, i have problems with epic store payments'

        Example output:

            $ formatted_pred = [0.14, 0.01, 0.85]

        """

        try:
            x = self.preprocessor.preprocess(x)
        except Exception as e:
            print(e)

        pred = self.model.predict(x, k=3)

        # fasttext predict has specific format: it ranged by prediction proba
        # code below transform fasttext to format [afs, other, ps] by label_mapper
        formatted_pred = [0, 0, 0]
        for i, label in enumerate(pred[0]):
            # idx – correct position in array
            # i – current position in array
            # label – string in format __label__{afs|other|ps}

            idx = self.label_mapper[label]
            formatted_pred[idx] = pred[1][i]

        # little hack
        max_prob = max(formatted_pred)

        if max_prob > 0.5:
            max_id = formatted_pred.index(max_prob)
            for i, x in enumerate(formatted_pred):
                formatted_pred[i] = 1.0 if i == max_id else 0.0

        return formatted_pred
