

from enum import Enum


class EstadoCurso(str, Enum):
    """
    docstring
    """
    ACTIVO="A"
    COMPLETADO="C"
    CANCELADO="N"