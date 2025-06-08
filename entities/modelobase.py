from pydantic import BaseModel, Field, PrivateAttr
from datetime import datetime
from typing import Any

class ModeloBase(BaseModel):
    """
    Clase base que proporciona:
    - fecha_creacion automática (solo lectura)
    - fecha_actualizacion automática (inicialmente igual a fecha_creacion)
    """
    fecha_creacion: datetime = Field(
        default_factory=datetime.now,
        frozen=True,
        description="Fecha de Creación Automática (solo lectura)",
        alias="_fechaCreacion"
    )
    
    fecha_actualizacion: datetime = Field(
        default_factory=datetime.now,
        frozen=True,
        description="Fecha de última actualización (solo lectura)",
        alias="_fechaActualizacion"
    )

    # Atributo privado para rastrear cambios
    _prev_values: dict = PrivateAttr(default_factory=dict)

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        # Guardamos los valores iniciales usando model_dump()
        self._prev_values = self.model_dump()
        # Establecemos fecha_actualizacion igual a fecha_creacion al crear
        object.__setattr__(self, 'fecha_actualizacion', self.fecha_creacion)

    def __setattr__(self, name: str, value: Any) -> None:
        """Sobreescribimos para detectar cambios y actualizar fecha_actualizacion"""
        # Accedemos a los campos de la CLASE, no de la instancia
        model_fields = self.__class__.model_fields
        
        if name in model_fields and name not in ['fecha_creacion', 'fecha_actualizacion']:
            # Actualizamos el valor primero
            super().__setattr__(name, value)
            # Luego verificamos si realmente cambió
            current_values = self.model_dump()
            if self._prev_values.get(name) != current_values.get(name):
                object.__setattr__(self, 'fecha_actualizacion', datetime.now())
                self._prev_values = current_values
        else:
            super().__setattr__(name, value)

    class Config:
        extra = "forbid"
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        allow_population_by_field_name = True