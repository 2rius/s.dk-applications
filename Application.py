from dataclasses import dataclass

@dataclass
class Application:
    rank: str
    name: str
    rooms: int
    grossArea: int
    estPrice: int
    addr: str
    url: str