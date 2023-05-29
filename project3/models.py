from dataclasses import dataclass
from datetime import datetime
from dataclasses_json import DataClassJsonMixin


@dataclass
class UserRequest(DataClassJsonMixin):
    name: str

    def __init__(self, name: str):
        self.name = name


@dataclass
class AuctionUser(DataClassJsonMixin):
    _id: int
    name: str

    def __init__(self, _id: int, user: UserRequest):
        self._id = _id
        self.name = user.name


@dataclass
class AuctionBid(DataClassJsonMixin):
    user_id: int
    product_id: int
    value: float

    def __init__(self, user_id: int, product_id: int, value: float):
        self.user_id = user_id
        self.product_id = product_id
        self.value = value


@dataclass
class ProductRequest(DataClassJsonMixin):
    name: str
    description: str
    initial_price: float
    end_date: datetime
    owner_id: int

    def __init__(
        self,
        name: str,
        description: str,
        initial_price: float,
        end_date: datetime,
        owner_id: int
    ):
        self.name = name
        self.description = description
        self.initial_price = initial_price
        self.end_date = end_date
        self.owner_id = owner_id


@dataclass
class AuctionProduct(DataClassJsonMixin):
    _id: int

    name: str
    description: str
    initial_price: float
    end_date: datetime
    owner_id: int

    current_price: float
    active = True
    subscribers = set()
    current_winner_id = None

    def __init__(self, _id: int, product: ProductRequest):
        self._id = _id

        self.name = product.name
        self.description = product.description
        self.initial_price = product.initial_price
        self.end_date = product.end_date
        self.owner_id = product.owner_id

        self.current_price = self.initial_price
        self.subscribers.add(self.owner_id)

    def __str__(self) -> str:
        return f'id: {self._id}, ' + \
            f'nome: {self.name}, ' + \
            f'descrição: {self.description}, ' + \
            f'preço: {self.current_price}, ' + \
            f'final do leilão: {self.end_date}'
