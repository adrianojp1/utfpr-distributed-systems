from dataclasses import dataclass
from datetime import datetime
from Crypto.PublicKey import RSA
from dataclasses_json import DataClassJsonMixin


@dataclass
class User(DataClassJsonMixin):
    name: str
    public_key: str
    uri: str

    def __init__(self, name: str, public_key: str, uri: str):
        self.name = name
        self.public_key = public_key
        self.uri = uri


class AuctionUser:
    def __init__(self, user: User):
        self.name = user.name
        self.public_key = RSA.import_key(user.public_key)
        self.uri = user.uri


@dataclass
class AuctionBid(DataClassJsonMixin):
    user_uri: str
    product_id: int
    value: float

    def __init__(self, user_uri: str, product_id: int, value: float):
        self.user_uri = user_uri
        self.product_id = product_id
        self.value = value


@dataclass
class Product(DataClassJsonMixin):
    name: str
    description: str
    initial_price: float
    end_date: datetime
    owner_uri: str

    def __init__(
        self,
        name: str,
        description: str,
        initial_price: float,
        end_date: datetime,
        owner_uri: str
    ):
        self.name = name
        self.description = description
        self.initial_price = initial_price
        self.end_date = end_date
        self.owner_uri = owner_uri


class AuctionProduct:
    _id: int

    def __init__(self, product: Product):
        self.name = product.name
        self.description = product.description
        self.initial_price = product.initial_price
        self.end_date = product.end_date
        self.owner_uri = product.owner_uri

        self.current_price = self.initial_price
        self.active = True
        self.subscribers = set()
        self.current_winner_uri = None

        self.subscribers.add(self.owner_uri)

    def __str__(self) -> str:
        return f'id: {self._id}, ' + \
            f'nome: {self.name}, ' + \
            f'descrição: {self.description}, ' + \
            f'preço: {self.current_price}, ' + \
            f'final do leilão: {self.end_date}'
