from datetime import datetime
from threading import Thread
import time
from flask import request
from flask_sse import sse
import pytz

from models import AuctionBid, AuctionProduct, AuctionUser, ProductRequest, UserRequest


timezone = pytz.timezone("America/Sao_Paulo")


class AuctionServer:
    users: dict[int, AuctionUser]
    products: dict[int, AuctionProduct]
    loop_thread: Thread

    def __init__(self, app):
        self.products = {}
        self.users = {}
        self.gen_user_id = generate_id()
        self.gen_prod_id = generate_id()
        self.app = app

        self.loop_thread = Thread(target=self.verify_expiration_loop)
        self.loop_thread.start()

    def join(self):
        user_req = UserRequest.from_dict(request.json)
        user_id = next(self.gen_user_id)

        auction_user = AuctionUser(user_id, user_req)
        self.users[auction_user._id] = auction_user

        print(f"Usuário registrado: {auction_user.name}")
        return auction_user.to_dict()

    def get_active_auctions(self):
        active_auctions = [
            str(product) for product in self.products.values() if product.active
        ]
        return active_auctions

    def register_product(self):
        product_req = ProductRequest.from_dict(request.json)
        product_id = next(self.gen_prod_id)

        auction_product = AuctionProduct(product_id, product_req)
        self.products[auction_product._id] = auction_product

        print(f"Produto registrado. {auction_product}")

        for user_id in self.users.keys():
            self.notify_user(user_id, "Novo produto registrado", str(auction_product))
        return {"code": 201}

    def bid(self):
        auction_bid = AuctionBid.from_dict(request.json)

        user_id = auction_bid.user_id

        bid_prod_id = int(auction_bid.product_id)
        bid_value = auction_bid.value

        if bid_prod_id not in self.products:
            self.notify_user(user_id, "Erro", "Produto não registrado no leilão")
            return {"code": 400}

        auction_product = self.products[bid_prod_id]

        if not auction_product.active:
            self.notify_user(user_id, "Erro", "Este produto já saiu do leilão")
            return {"code": 400}

        if bid_value <= auction_product.current_price:
            self.notify_user(
                user_id, "Erro", "Valor do lance deve ser maior que o atual"
            )
            return {"code": 400}

        auction_product.current_price = bid_value
        auction_product.current_winner_id = user_id
        auction_product.subscribers.add(user_id)

        for user_id in auction_product.subscribers:
            self.notify_user(
                user_id,
                "Novo lance em produto",
                f"id: {auction_product._id}\nvalor: {auction_product.current_price}",
            )

        return {"code": 201}

    def notify_user(self, user_id: int, title: str, message: str):
        with self.app.app_context():
            print(f"Notificando usuário [{user_id}]: {title}, {message}")
            sse.publish(
                {"title": title, "message": message},
                type="notification",
                channel=f"user-{user_id}",
            )

    def verify_expiration_loop(self):
        while True:
            now = datetime.now(timezone)

            for product in self.products.values():
                if product.active and product.end_date <= now:
                    product.active = False

                    if product.current_winner_id is None:
                        msg = (
                            f"Nenhum lance foi dado.\n"
                            + f"id: {product._id}\n"
                            + f"nome: {product.name}\n"
                        )
                    else:
                        winner = self.users[product.current_winner_id]
                        msg = (
                            f"id: {product._id} \n"
                            + f"nome: {product.name} \n"
                            + f"ganhador: {winner.name} \n"
                            + f"valor negociado: {product.current_price}\n"
                        )

                    for user_id in product.subscribers:
                        self.notify_user(user_id, "Leilão finalizado para produto", msg)
            time.sleep(0.5)


def generate_id():
    _id = 1
    while True:
        yield _id
        _id += 1
