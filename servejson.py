from flask import Flask, send_file
from flask_cors import CORS, cross_origin
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route('/')
@cross_origin()
def root():
    return send_file('Stocks_Sentiment.json')

app.run()