#!/usr/bin/env python

import threading
import contextlib
from Pyro5.api import expose, oneway, Proxy, Daemon


class User(object):
    def __init__(self):
        self.auction = Proxy('PYRONAME:project3.auction.server')
        self.abort = 0

        self.name = input('Informe seu nome: ')
        self.public_key = input('Informe sua chave pública: ')
        self.remote_object_uri = input('Informe sua URI: ') # TODO: obter o object uri
        self.auction.join(self.name, self.public_key, self.remote_object_uri, "self") # TODO: enviar a callback para o servidor

    
    # @expose
    # @oneway
    # def message(self, nick, msg):
    #     if nick != self.name:
    #         print('[{0}] {1}'.format(nick, msg))

    def show_options(self):
        print('0) Consultar leilões ativos')
        print('1) Codastrar produto para leilão')
        print('2) Efetuar lance em um produto')
        print('3) Sair')


    def list_active_auctions(self):
        active_auctions = self.auction.get_active_auctions()
        print(active_auctions)


    def register_product(self):
        product_id = input("Digite o código do produto: ")
        product_name = input("Digite o nome do produto: ")
        product_description = input("Digite a descrição do produto: ")
        initial_price = input("Digite o preço inicial: ")
        end_date = input("Digite a data final do leilão (dd/mm/yyyy HH:MM): ")
        sucess = self.auction.register_product(
            [product_id, product_name, product_description, initial_price, end_date])
        print("Produto registrado com sucesso!!" if sucess else "Produto não registrado")


    def auction_bid(self):
        product_id = input("Digite o código do produto: ")
        price = input("Digite o valor do lance: ")

        # TODO: fazer a autenticação e tratar os outros erros
        if self.auction.bid(product_id, price, self.remote_object_uri):
            print("Lance registrado com sucesso")
        else:
            print("Lance não registrado: O valor deve ser maior que o lance atual")


    def start(self):
        self.show_options()
        try:
            with contextlib.suppress(EOFError):
                while not self.abort:
                    op = input('Digite a opção desejada: ')
                    if op == '0':
                        self.list_active_auctions()
                    if op == '1':
                        self.register_product()
                    if op == '2':
                        self.auction_bid()
                    if op == '3':
                        print("Abort")
                        self.abort = 1
                        self._pyroDaemon.shutdown()
        finally:
            self.abort = 1
            self._pyroDaemon.shutdown()


class DaemonThread(threading.Thread):
    def __init__(self, user):
        threading.Thread.__init__(self)
        self.user = user
        self.daemon = True

    def run(self):
        with Daemon() as daemon:
            daemon.register(self.user)
            daemon.requestLoop(lambda: not self.user.abort)


user = User()
daemonthread = DaemonThread(user)
daemonthread.start()
user.start()
print('Exit.')
