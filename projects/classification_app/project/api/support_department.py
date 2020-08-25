import json

from flask import jsonify, request, current_app
from ..ml.message_categorization import MessageCategorizer

from . import api

# TODO create time-depend key-accessible model storage as util

model_mc = MessageCategorizer()


@api.route('/support_department/categorize_message', methods=['POST'])
def categorize_message():
    current_app.logger.info('request: categorize user message')

    response = {'message': 'ok', 'category': -1}
    status = 200

    try:
        raw_data = request.get_data()
        data = json.loads(raw_data)

        response['category'] = model_mc.predict_proba(data['message'])

    except Exception as e:
        current_app.logger.info(f'exception: {e}')
        response['message'] = e
        status = 500

    response = jsonify(response)

    return response, status
