from dataclasses import dataclass
from typing import List
from .text_atom import TextAtom

@dataclass
class RowCluster:
    page: int
    y_center: float
    atoms: List[TextAtom]

@dataclass
class ColumnCluster:
    page: int
    x_center: float
    atoms: List[TextAtom]

@dataclass
class StructuralBlock:
    page: int
    block_type: str
    atoms: List[TextAtom]
    rows: List[List[TextAtom]] | None = None

@dataclass
class SemanticFact:
    page: int
    label_text: str
    value_text: str
    structure_type: str
    confidence: float
