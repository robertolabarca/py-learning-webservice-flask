from pydantic import Field

from shared.sexo import Sexo
from .base import ModeloBase
from typing import Optional



class Persona(ModeloBase):
    nombre: str = Field(..., min_length=1, max_length=50, description="Nombre(s) de la persona")
    apellidos: str = Field(..., min_length=1, max_length=100, description="Apellidos de la persona")
    sexo: Sexo = Field(..., description="Sexo biológico")
    numero_pasaporte: str = Field(
        ...,
        min_length=5,
        max_length=20,
        regex=r'^[A-Z0-9]+$',
        description="Número único de pasaporte"
    )
    email: Optional[str] = Field(
        None,
        regex=r'^[\w\.-]+@[\w\.-]+\.\w+$',
        description="Correo electrónico opcional"
    )

    def __hash__(self):
        return hash(self.id)