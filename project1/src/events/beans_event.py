from dataclasses import dataclass

from dataclasses_json import DataClassJsonMixin


@dataclass
class BeansEvent(DataClassJsonMixin):
    load: int

    def __init__(self, load: int) -> None:
        self.load = load
