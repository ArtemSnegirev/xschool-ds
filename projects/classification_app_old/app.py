import pickle

from flask import Flask
from flask import request
from flask import jsonify
from flask import render_template

from langdetect import detect
from textblob import TextBlob, Word


import os
import json

app = Flask(
    __name__,
)

vectorizer = pickle.load(open("./models/multiclf_tfidf.pickle", "rb"))
model = pickle.load(open("./models/multiclf_model.pickle", "rb"))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/hello")
def hello():
    resp = {'message': "Hello World!"}

    response = jsonify(resp)

    return response


@app.route("/category_prediction", methods=['GET', 'POST'])
def category_prediction():
    resp = {'message': 'ok', 'category': -1}

    try:
        get_data = request.get_data()
        json_params = json.loads(get_data)

        sample_vec = vectorizer.transform([json_params['message']]).toarray()
        resp['category'] = int(model.predict(sample_vec)[0])

    except Exception as e:
        print(e)
        resp['message'] = e

    response = jsonify(resp)

    return response


if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    app.run(debug=True, port=port, host='0.0.0.0', threaded=True)
