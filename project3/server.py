from datetime import datetime
from threading import Thread
import time
from flask import request
from flask_sse import sse
import pytz

from models import AuctionBid, AuctionProduct, AuctionUser, ProductRequest, UserRequest


timezone = pytz.timezone('America/Sao_Paulo')


class AuctionServer:
    users: dict[int, AuctionUser]
    products: dict[int, AuctionProduct]
    loop_thread: Thread

    def __init__(self):
        self.products = {}
        self.users = {}
        self.gen_user_id = generate_id()
        self.gen_prod_id = generate_id()

        self.loop_thread = Thread(target=self.verify_expiration_loop)
        self.loop_thread.start()

    def join(self):
        user_req = UserRequest.from_dict(request.json)
        user_id = next(self.gen_user_id)

        auction_user = AuctionUser(user_id, user_req)
        self.users[auction_user._id] = auction_user

        print(f'Usuário registrado: {auction_user.name}')
        return auction_user.to_dict()

    def get_active_auctions(self):
        active_auctions = [str(product)
                           for product in self.products.values() if product.active]
        return active_auctions

    def register_product(self):
        product_req = ProductRequest.from_dict(request.json)
        product_id = next(self.gen_prod_id)

        auction_product = AuctionProduct(product_id, product_req)
        self.products[auction_product._id] = auction_product

        print(f'Produto registrado. {str(auction_product)}')

        for user_id in self.users.keys():
            self.notify_user(
                user_id,
                f'Novo produto registrado. {str(auction_product)}')

        return True

    def bid(self):
        auction_bid = AuctionBid.from_dict(request.json)

        user_id = auction_bid.user_id

        bid_prod_id = int(auction_bid.product_id)
        bid_value = auction_bid.value

        if bid_prod_id not in self.products:
            error = 'Erro: Produto não registrado no leilão'
            self.notify_user(user_id, error)
            return False

        auction_product = self.products[bid_prod_id]

        if not auction_product.active:
            error = 'Erro: Este produto já saiu do leilão'
            self.notify_user(user_id, error)
            return False

        if bid_value <= auction_product.current_price:
            error = 'Erro: Valor do lance deve ser maior que o atual'
            self.notify_user(user_id, error)
            return False

        auction_product.current_price = bid_value
        auction_product.current_winner_id = user_id
        auction_product.subscribers.add(user_id)

        for user_id in auction_product.subscribers:
            self.notify_user(
                user_id,
                f'Novo lance em produto. id: {auction_product._id}, valor: {auction_product.current_price}')

        return True

    def notify_user(self, user_id: int, msg: str):
        sse.publish({'msg': msg}, channel=f'user-{user_id}')

    def verify_expiration_loop(self):
        while True:
            now = datetime.now(timezone)

            for product in self.products.values():

                if product.active and product.end_date <= now:
                    product.active = False

                    if product.current_winner_id is None:
                        msg = f'Leilão finalizado para produto, nenhum lance foi dado. ' + \
                            f'id: {product._id}' + \
                            f'nome: {product.name}'
                    else:
                        winner = self.users[product.current_winner_id]
                        msg = f'Leilão finalizado para produto. ' + \
                            f'id: {product._id} ' + \
                            f'nome: {product.name} ' + \
                            f'ganhador: {winner.name} ' + \
                            f'valor negociado: {product.current_price}'

                    for user_id in product.subscribers:
                        self.notify_user(user_id, msg)
            time.sleep(0.5)


def generate_id():
    _id = 1
    while True:
        yield _id
        _id += 1
