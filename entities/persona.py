from pydantic import EmailStr, Field, field_validator, ValidationError
from entities.modelobase import ModeloBase
from entities.modelobasejsonmixin import ModeloBaseJsonMixin

class Persona(ModeloBase,ModeloBaseJsonMixin):
    """
    Clase que representa a una persona con sus datos básicos.
    """
    id: int
    nombre: str
    apellidos: str
    ci: str = Field(..., min_length=11, max_length=11, example='90010112345')
    edad: int = Field(default=0, frozen=True)  # frozen=True hace que sea de solo lectura
    email: EmailStr = Field(..., example="usuario@example.com")
    activo: bool = True

    @field_validator('ci')
    def validate_ci(cls, v):
        if not v.isdigit():
            raise ValueError('El CI debe contener solo dígitos')
        return v