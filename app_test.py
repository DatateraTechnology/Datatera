from flask import Flask

app = Flask(__name__)

@app.route('/')
def example():
    return 'The value of __name__ is {}'.format(__name__)
