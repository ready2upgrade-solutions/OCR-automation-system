from dataclasses import dataclass

@dataclass
class TextAtom:
    text: str
    page: int

    x0: float
    y0: float
    x1: float
    y1: float

    width: float
    height: float
    x_center: float
    y_center: float

    confidence: float = 1.0
