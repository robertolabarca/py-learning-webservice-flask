from pydantic import Field

from shared.estado_curso import EstadoCurso
from .base import ModeloBase

class Curso(ModeloBase):
    nombre: str = Field(..., min_length=3, max_length=100, example="Matemáticas Avanzadas")
    descripcion: str = Field(..., min_length=10, max_length=500, example="Curso de matemáticas para nivel universitario")
    creditos: int = Field(3, ge=1, le=10, description="Créditos académicos del curso")
    activo: EstadoCurso = Field(default=True, description="Indica si el curso está activo")