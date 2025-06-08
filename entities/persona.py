from ast import Try
from datetime import datetime
import re
from pydantic import EmailStr, Field, computed_field, field_validator, ValidationError
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
   # edad: int = Field(frozen=True)  # frozen=True hace que sea de solo lectura
    email: EmailStr = Field(..., example="usuario@example.com")
    activo: bool = True


    @field_validator('ci')
    def validate_ci(cls, v):
        
        if not v.isdigit():
            raise ValueError('El CI debe contener solo dígitos')
        
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
        
    
    def _calcula_edad(self,fn:datetime) -> int:
        """
        docstring
        """
        yy_actual = datetime.now().year
        
        return yy_actual - fn.year
    
    @computed_field
    @property
    def edad(self) -> int:
        """
        docstring
        """
        if not self.ci or len(self.ci) != 11:
            raise ValueError("CI invalido para calcular edad")
        self._validar_ci_existente()
        v=self.ci
        yy, mm, dd = self._extraer_fecha_ci(v)
        r=self._determinar_nacimiento(yy,mm,dd)

        return self._calcula_edad(r)
    
    def _validar_ci_existente(self):
        """Valida que exista CI para cálculo"""
        if not hasattr(self, 'ci') or not self.ci:
            raise AttributeError("No se puede calcular la edad sin CI válido")
        
    @classmethod
    def _determinar_nacimiento(cls, yy: int, mm: int, dd: int) -> datetime:
        """Determina la fecha de nacimiento con el siglo correcto"""
        hoy = datetime.now()
        try:
            fecha=datetime(2000 + yy, mm, dd)
            if fecha > hoy :
                fecha=datetime(1900 + yy, mm, dd)
            return fecha
        except ValueError as e:
            raise ValueError("Fecha de nacimiento en CI no válida") from e
        