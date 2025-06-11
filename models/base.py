from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional

class ModeloBase(BaseModel):
    """
    Clase base para todos los modelos que incluye campos comunes:
    - id: Identificador único (UUID)
    - fecha_creacion: Fecha de creación del registro (se establece automáticamente)
    - fecha_modificacion: Fecha de última modificación (se actualiza automáticamente)
    """
    id: UUID = Field(default_factory=uuid4, description="Identificador único")
    fecha_creacion: datetime = Field(default_factory=datetime.now, description="Fecha de creación del registro")
    fecha_modificacion: Optional[datetime] = Field(None, description="Fecha de última modificación")

    def actualizar_fecha_modificacion(self):
        """Actualiza la fecha de modificación al momento actual"""
        self.fecha_modificacion = datetime.now()

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }
        from_attributes = True  # Permite la compatibilidad con ORMs
        arbitrary_types_allowed = True  # Permite tipos como UUID