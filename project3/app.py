from flask import Flask, render_template, request
from flask_sse import sse

from server import AuctionServer

app = Flask(__name__)
app.config['REDIS_URL'] = 'redis://localhost'
app.register_blueprint(sse, url_prefix='/stream')

server = AuctionServer(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/user', methods=['POST'])
def join():
    return server.join()

@app.route('/product', methods=['GET', 'POST'])
def product():
    if request.method == 'GET':
        print("Get active auctions")
        return server.get_active_auctions()
    elif request.method == 'POST':
        print("register product")
        return server.register_product()

@app.route('/bid', methods=['POST'])
def bid():
    return server.bid()
