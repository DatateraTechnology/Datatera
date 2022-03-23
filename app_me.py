from flask import Flask
from flask_swagger import swagger
from flask import Flask, jsonify, render_template

app = Flask(__name__)

@app.route('/')
def example():
    return 'The value of __name__ is {}'.format(__name__)

@app.route("/spec")
def spec():
    swag = swagger(app)
    swag['info']['version'] = "1.0"
    swag['info']['title'] = "Datatera Alpha"
    return jsonify(swag)

@app.route('/api/docs')
def get_docs():
    print('sending docs')
    return render_template('swaggerui.html')
