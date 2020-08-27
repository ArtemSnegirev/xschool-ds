from flask import jsonify, request, current_app
from ..ml.message_categorization import MessageCategorizer

from . import api

# TODO create time-depend key-accessible model storage as util

model_mc = MessageCategorizer()


@api.route('/support_department/categorize_message', methods=['POST'])
def categorize_message():
    """Method to predict category probability of input-message, where prediction = [afs, other, ps]

        Parameters
        ----------
        user_message: str, required
            text data to calculate prediction

        Returns
        -------
        message
            str represented calculation result
            `ok` if successful, `error` otherwise
        prediction
            3-components 1d-array of floats
            where indexes: 0 - afs, 1 - other, 2 - ps

        Notes
        ----------

        Example input:

            $ correct_request = {'user_message': 'hello xsolla, i have problems with epic store payments'}
            $ empty_request = ''
            $ wrong_key_request = {'wrong_key': 'hello xsolla, i have problems with epic store payments'}

        Example output:

            $ {"message":"ok","prediction":[0.9648057818412781,0.035207804292440414,1.6475680240546353e-05]}
            $ {"message":"expected data in json","prediction":-1}
            $ {"message":"expected user_message field","prediction":-1}

    """
    current_app.logger.info('request: categorize user message')

    # default prediction is -1 if something wrong
    response = {'message': 'ok', 'prediction': -1}
    status = 200

    try:
        if request.get_data() != b'':
            data = request.get_json(force=True)

            if 'user_message' in data:
                # get final prediction like 3-components 1d-array of floats
                response['prediction'] = model_mc.predict_proba(data['user_message'])
            else:
                status = 404
                response['message'] = 'expected user_message field'
        else:
            status = 404
            response['message'] = 'expected data in json'

    except Exception as e:
        current_app.logger.info(f'exception: {e}')
        response['message'] = 'bad'
        status = 500

    response = jsonify(response)

    return response, status
