import json
import pickle

import sklearn
import textblob


class MessageCategorizer:
    def __init__(self):
        # TODO create project config and default path for models
        # self.vectorizer = pickle.load(open("storage/message_categorizer/.pickle", "rb"))
        # self.model = pickle.load(open("storage/message_categorizer/.pickle", "rb"))
        self.model = None

    def preprocessing(self, x):
        pass

    def predict_proba(self, x):
        if 'predict_proba' in dir(self.model):
            return self.model.predict_proba(x)

    def predict(self, x):
        return self.model.predict(x)
