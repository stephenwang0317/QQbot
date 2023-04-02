from flask import Flask, request
from main import Bot

HttpResponseHeader = '''HTTP/1.1 200 OK\r\n
Content-Type: text/html\r\n\r\n
'''

app = Flask(__name__)
Bot = Bot()


@app.route('/', methods=['POST'])
def create_user():
    json_data = request.get_json()
    Bot(rev=json_data)
    return HttpResponseHeader


if __name__ == '__main__':
    app.run(host='127.0.0.1', port='5701', debug=True)
