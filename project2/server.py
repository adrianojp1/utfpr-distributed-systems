#!/usr/bin/env python

import base64
from datetime import datetime
from Pyro5.api import expose, behavior, Daemon, Proxy
import Pyro5.errors
import pytz
from crypto import verify
import traceback


from models import AuctionBid, AuctionProduct, AuctionUser, Product, User


Pyro5.config.SERVERTYPE = 'multiplex'
Pyro5.config.POLLTIMEOUT = 3

server_pyroname = 'project2.auction.server'
timezone = pytz.timezone('America/Sao_Paulo')


@behavior(instance_mode='single')
class AuctionServer(object):
    products: dict[int, AuctionProduct]
    users: dict[str, AuctionUser]

    def __init__(self):
        self.products = {}
        self.users = {}
        self.id_gen = generate_id()

    @expose
    def join(self, user_data: str):
        user = User.from_json(user_data)
        auction_user = AuctionUser(user)
        self.users[auction_user.uri] = auction_user
        print(f'Usuário registrado: {auction_user.name}')
        return True

    @expose
    def leave(self, user_uri):
        if user_uri in self.users:
            name = self.users[user_uri].name
            print(f'Usuário excluído: {name}')
            del self.users[user_uri]

    @expose
    def get_active_auctions(self):
        active_auctions = [str(product)
                           for product in self.products.values() if product.active]
        return active_auctions

    @expose
    def register_product(self, product_data: str):
        product = Product.from_json(product_data)
        auction_product = AuctionProduct(product)

        auction_product._id = next(self.id_gen)
        self.products[auction_product._id] = auction_product

        print(f'Produto registrado. {str(auction_product)}')

        for user_uri in self.users.keys():
            self.notify_user(
                user_uri,
                f'Novo produto registrado. {str(auction_product)}')

        return True

    @expose
    def bid(self, bid_data: str, sign_dict: dict):
        try:
            auction_bid = AuctionBid.from_json(bid_data)

            user_uri = auction_bid.user_uri
            user_key = self.users[user_uri].public_key
            signature = base64.b64decode(sign_dict['data'])
            verified = verify(user_key, bid_data.encode(), signature)

            bid_prod_id = int(auction_bid.product_id)
            bid_value = auction_bid.value

            if not verified:
                error = 'Erro: Assinatura digital inválida'
                self.notify_user(user_uri, error)
                return False

            if bid_prod_id not in self.products:
                error = 'Erro: Produto não registrado no leilão'
                self.notify_user(user_uri, error)
                return False

            auction_product = self.products[bid_prod_id]

            if not auction_product.active:
                error = 'Erro: Este produto já saiu do leilão'
                self.notify_user(user_uri, error)
                return False

            if bid_value <= auction_product.current_price:
                error = 'Erro: Valor do lance deve ser maior que o atual'
                self.notify_user(user_uri, error)
                return False

            auction_product.current_price = bid_value
            auction_product.current_winner_uri = user_uri
            auction_product.subscribers.add(user_uri)

            for user_uri in auction_product.subscribers:
                self.notify_user(
                    user_uri,
                    f'Novo lance em produto. id: {auction_product._id}, valor: {auction_product.current_price}')

            return True
        except:
            traceback.print_exc()
            return False

    def notify_user(self, user_uri, msg):
        user = Proxy(user_uri)
        try:
            user.notify(msg)
        except:
            pass

    def conditional_loop(self):
        now = datetime.now(timezone)

        for product in self.products.values():

            if product.active and product.end_date <= now:
                product.active = False

                if product.current_winner_uri is None:
                    msg = f'Leilão finalizado para produto, nenhum lance foi dado. ' + \
                        f'id: {product._id}' + \
                        f'nome: {product.name}'
                else:
                    winner = self.users[product.current_winner_uri]
                    msg = f'Leilão finalizado para produto. ' + \
                        f'id: {product._id} ' + \
                        f'nome: {product.name} ' + \
                        f'ganhador: {winner.name} ' + \
                        f'valor negociado: {product.current_price}'

                for user_uri in product.subscribers:
                    self.notify_user(user_uri, msg)

        return True


def generate_id():
    _id = 1
    while True:
        yield _id
        _id += 1


def main():
    nameserver_uri, name_server_daemon, _ = Pyro5.nameserver.start_ns()
    print(f'Name server uri: {nameserver_uri}')

    auction_server = AuctionServer()

    with Daemon() as daemon:
        server_uri = daemon.register(auction_server)

        name_server_daemon.nameserver.register(server_pyroname, server_uri)
        print('Auction server pyro:')
        print(f'{server_pyroname} : {server_uri}')

        daemon.combine(name_server_daemon)
        daemon.requestLoop(auction_server.conditional_loop)

    name_server_daemon.close()
    daemon.close()


if __name__ == '__main__':
    main()
