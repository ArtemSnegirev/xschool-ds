import pickle

from flask import Flask
from flask import request
from flask import jsonify

import os
import json

application = Flask(__name__)

vectorizer = pickle.load(open("./models/multiclf_tfidf.pickle", "rb"))
model = pickle.load(open("./models/multiclf_model.pickle", "rb"))


@application.route("/")
def hello():
    resp = {'message': "Hello World!"}

    response = jsonify(resp)

    return response


@application.route("/category_prediction", methods=['GET', 'POST'])
def registration():
    resp = {'message': 'ok', 'category': -1}

    try:
        get_data = request.get_data()
        json_params = json.loads(get_data)

        sample_vec = vectorizer.transform(json_params['message']).toarray()
        resp['category'] = model.predict(sample_vec)[0]

    except Exception as e:
        print(e)
        resp['message'] = e

    response = jsonify(resp)

    return response


if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    application.run(debug=False, port=port, host='0.0.0.0', threaded=True)
