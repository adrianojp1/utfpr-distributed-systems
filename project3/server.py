#!/usr/bin/env python

from Pyro5.api import expose, behavior, serve
import Pyro5.errors


@expose
@behavior(instance_mode='single')
class Auction(object):
    def __init__(self):
        self.products = {}
        self.users = {} # remote_object_uri => (name, public_key, callback)


    def join(self, name, publick_key, remote_object_uri, callback):
        print(name, publick_key, remote_object_uri, callback)
        # callback é o objeto cliente
        self.users[remote_object_uri] = (name, publick_key, callback)


    def get_active_auctions(self):
        return self.products


    def register_product(self, product_data):
        product_id, product_name, product_description, initial_price, end_date = product_data
        self.products[product_id] = {
                "name": product_name,
                "desciption": product_description,
                "initial_price": initial_price,
                "actual_price": initial_price,
                "current_winner": None,
                "end_date": end_date,
        }
        print(f'Produto recebido: {product_data}')
        return True  # TODO: Mudar isso quando possuir autenticação

    def bid(self, product_id, price, uri):
        if (price > self.products[product_id]["actual_price"]):
            self.products[product_id]["actual_price"] = price
            self.products[product_id]["current_winner"] = uri # TODO: autenticar o lance
            return True
        return False


serve({
    Auction: 'project3.auction.server'
})
