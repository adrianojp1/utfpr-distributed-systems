from dataclasses import dataclass

from dataclasses_json import DataClassJsonMixin


@dataclass
class TruckEvent(DataClassJsonMixin):
    _id: int
    state: str
    load: int

    def __init__(self, _id: int, state: str, load: int) -> None:
        self._id = _id
        self.state = state
        self.load = load
