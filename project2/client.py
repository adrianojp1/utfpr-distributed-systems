#!/usr/bin/env python

from datetime import datetime
from pprint import pprint
import threading
from Pyro5.api import expose, oneway, Proxy, Daemon
from crypto import generate_key, sign
from models import AuctionBid, User, Product


server_pyroname = 'project2.auction.server'


class UserClient(object):
    def __init__(self):
        self.uri = ''
        self.abort = 0

        self.auction = None

        self.name = ''
        self.sign_key = generate_key()
        self.public_key = self.sign_key.public_key().export_key()

    @expose
    @oneway
    def notify(self, msg):
        print()
        print(f'Notificação: {msg}')

    def list_active_auctions(self):
        active_auctions = self.auction.get_active_auctions()
        print('Leilões ativos:')
        pprint(active_auctions)

    def register_product(self):
        product_name = input("Digite o nome do produto: ")
        product_description = input("Digite a descrição do produto: ")
        initial_price_in = input("Digite o preço inicial: ")
        end_date_in = input(
            "Digite a data final do leilão (dd/mm/yyyy HH:MM:SS): ")

        initial_price = float(initial_price_in)
        try:
            end_date = datetime.strptime(end_date_in, '%d/%m/%Y %H:%M:%S')
        except:
            print('Formato de data inválido!')
            return

        product = Product(product_name, product_description,
                          initial_price, end_date, self.uri)
        success = self.auction.register_product(product.to_json())
        print(
            "Produto registrado com sucesso!!" if success else "Erro ao registrar produto!")

    def auction_bid(self):
        product_id_in = input("Digite o código do produto: ")
        value_in = input("Digite o valor do lance: ")

        product_id = int(product_id_in)
        value = float(value_in)

        bid_data = AuctionBid(self.uri, product_id, value).to_json()
        signature = sign(self.sign_key, bid_data.encode())

        success = self.auction.bid(bid_data, signature)
        print(
            "Lance registrado com sucesso!!" if success else "Erro ao registrar lance!")

    def show_menu(self):
        print()
        print('Selecione uma das opções:')
        print('0. Consultar leilões ativos')
        print('1. Cadastrar produto para leilão')
        print('2. Efetuar lance em um produto')
        print('3. Sair')

        op = input()
        if op == '0':
            self.list_active_auctions()
        if op == '1':
            self.register_product()
        if op == '2':
            self.auction_bid()
        if op == '3':
            print('Saiu.')
            self.abort = 1

    def start(self):
        try:
            self.auction = Proxy(f'PYRONAME:{server_pyroname}')

            self.name = input('Informe seu nome: ')
            auction_user = User(
                self.name, self.public_key.decode(), self.uri)

            success = self.auction.join(auction_user.to_json())

            if success:
                print(f"Usuário registrado com sucesso!! uri: {self.uri}")
                while not self.abort:
                    try:
                        self.show_menu()
                    except:
                        pass
            else:
                print("Erro ao registrar usuário!")

        finally:
            try:
                self.auction.leave(self.uri)
            except:
                pass
            self.abort = 1
            self._pyroDaemon.shutdown()


class DaemonThread(threading.Thread):
    def __init__(self, client):
        threading.Thread.__init__(self)
        self.client = client
        self.daemon = True

    def run(self):
        with Daemon() as daemon:
            client_uri = daemon.register(self.client)
            self.client.uri = str(client_uri)
            daemon.requestLoop(lambda: not self.client.abort)


def main():
    client = UserClient()
    DaemonThread(client).start()
    client.start()


if __name__ == '__main__':
    main()
