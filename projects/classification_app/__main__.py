import os

from .app import create_app

app = create_app()

port = int(os.getenv('PORT', 5000))
app.run(debug=True, port=port, host='0.0.0.0', threaded=True)
