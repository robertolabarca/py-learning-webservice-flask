from datetime import datetime
import re
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional


class ModeloBase(BaseModel):
    """
    docstring
    """
    fecha_creacion:datetime=Field(
        default_factory=datetime.now(),
        frozen=True,
        description="Fecha de Creación Automática (solo lectura)"
        alias="_fechaCreacion",
        examples="2023-01-01T00:00:00.000Z
    )

    fecha_actualizacion: Optional[datetime] = Field(
        default=None,
        frozen=True,
        description="Fecha de última actualización (solo lectura)",
        alias="_fechaActualizacion",
        example="2023-01-02T00:00:00.000Z"
    )

    def actualizar_fecha_modificacion(self):
        """Actualiza internamente la fecha de modificación"""
        object.__setattr__(self, 'fecha_actualizacion', datetime.now())

    class Config:
        extra = "forbid"
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        allow_population_by_field_name = True  # Permite usar alias


class Persona(ModeloBase):
    """
    docstring
    """
    id:int
    nombre:str
    apellidos:str
    ci: str = Field(..., min_length=11, max_length=11, example="90010112345")
    edad:int=0  # valor debe ser solo lectura 
    email: EmailStr = Field(..., example="usuario@example.com")
    activo:bool=True

   
    @field_validator('ci')
    def validar_ci(cls, v):
        cls._validar_formato_ci(v)
        yy, mm, dd = cls._extraer_fecha_ci(v)
        fecha_nacimiento = cls._determinar_fecha_nacimiento(yy, mm, dd)
        cls._validar_edad(fecha_nacimiento)
        return v

    @classmethod
    def _validar_formato_ci(cls, ci: str):
        """Valida el formato básico del CI"""
        if not re.match(r'^\d{11}$', ci):
            raise ValueError("El CI debe tener exactamente 11 dígitos numéricos")

    @classmethod
    def _extraer_fecha_ci(cls, ci: str) -> tuple[int, int, int]:
        """Extrae los componentes de fecha del CI"""
        return int(ci[:2]), int(ci[2:4]), int(ci[4:6])
    
    @classmethod
    def _determinar_fecha_nacimiento(cls, yy: int, mm: int, dd: int) -> datetime:
        """Determina la fecha de nacimiento con el siglo correcto"""
        hoy = datetime.now()
        
        # Intentar primero con siglo XXI
        try:
            fecha = datetime(2000 + yy, mm, dd)
            if fecha <= hoy:
                return fecha
        except ValueError:
            pass
        
        # Si falla o es futura, intentar con siglo XX
        try:
            fecha = datetime(1900 + yy, mm, dd)
            if fecha > hoy:
                raise ValueError("Fecha de nacimiento no puede ser futura")
            return fecha
        except ValueError as e:
            raise ValueError("Fecha de nacimiento en CI no válida") from e
        
    @classmethod
    def _validar_edad(cls, fecha_nacimiento: datetime):
        """Valida que la edad no exceda el máximo permitido"""
        hoy = datetime.now()
        edad = hoy.year - fecha_nacimiento.year
        
        if (hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day):
            edad -= 1
        
        if edad > 120:
            raise ValueError("La edad no puede ser mayor de 120 años")
            
    @property
    def edad(self) -> int:
        """Calcula la edad exacta con límites 0-120 años"""
        self._validar_ci_existente()
        fecha_nacimiento = self._obtener_fecha_nacimiento_validada()
        return self._calcular_edad_limites(fecha_nacimiento)

    def _validar_ci_existente(self):
        """Valida que exista CI para cálculo"""
        if not hasattr(self, 'ci') or not self.ci:
            raise AttributeError("No se puede calcular la edad sin CI válido")

    def _obtener_fecha_nacimiento_validada(self) -> datetime:
        """Obtiene fecha de nacimiento con manejo de errores"""
        try:
            return self.fecha_nacimiento
        except Exception as e:
            raise ValueError(f"Error calculando la edad: {str(e)}") from e

    def _calcular_edad_limites(self, fecha_nacimiento: datetime) -> int:
        """Calcula edad aplicando límites"""
        edad = self._calcular_edad_bruta(fecha_nacimiento)
        return max(0, min(edad, 120))

    def _calcular_edad_bruta(self, fecha_nacimiento: datetime) -> int:
        """Calcula edad sin límites"""
        hoy = datetime.now()
        edad = hoy.year - fecha_nacimiento.year
        if not self._ha_cumplido_anios_este_anio(fecha_nacimiento, hoy):
            edad -= 1
        return edad
