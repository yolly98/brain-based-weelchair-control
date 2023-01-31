from flask import Flask, request

app = Flask(__name__)


@app.post('/json')
def post_json():
    if request.json is None:
        return {'error': 'No JSON received'}, 500

    received_json = request.json
    print(received_json)

    return {}, 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='4000', debug=False)