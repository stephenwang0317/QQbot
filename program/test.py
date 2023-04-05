from flask import Flask, request
from bot import Bot
from concurrent.futures import ThreadPoolExecutor

HttpResponseHeader = '''HTTP/1.1 200 OK\r\n
Content-Type: text/html\r\n\r\n
'''

executor = ThreadPoolExecutor(2)
app = Flask(__name__)
Bot = Bot()


@app.route('/', methods=['POST'])
def create_user():
    json_data = request.get_json()
    executor.submit(Bot, json_data)
    return HttpResponseHeader


if __name__ == '__main__':
    app.run(host='127.0.0.1', port='5701', debug=True)
