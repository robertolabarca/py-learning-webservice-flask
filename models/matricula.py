from pydantic import Field
from datetime import datetime
from .base import ModeloBase

class Matricula(ModeloBase):
    persona_id: str = Field(..., description="ID de la persona matriculada")
    curso_id: str = Field(..., description="ID del curso")
    fecha_matricula: datetime = Field(default_factory=datetime.now)
    estado: str = Field("activa", pattern=r'^(activa|completada|cancelada)$')