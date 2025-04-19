from dataclasses import dataclass


@dataclass
class Passenger:
    name: str
    src: object
    dst: object
    t_dep_bracket: tuple[float, float]


@dataclass
class Place:
    name: str

    def __hash__(self) -> int:
        return id(self)


@dataclass
class Road:
    ends: set[Place]
    fare: float
