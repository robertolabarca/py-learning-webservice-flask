from uuid import UUID
from typing import Dict, Optional
from ..models.persona import Persona
from .base import RepositorioBase

class PersonaRepositorio(RepositorioBase[Persona]):
    def __init__(self):
        super().__init__()
        self._por_pasaporte: Dict[str, UUID] = {}
        
    def agregar(self, persona: Persona) -> Persona:
        if persona.numero_pasaporte in self._por_pasaporte:
            raise ValueError("Número de pasaporte ya registrado")
            
        persona = super().agregar(persona)
        self._por_pasaporte[persona.numero_pasaporte] = persona.id
        return persona
        
    def obtener_por_pasaporte(self, pasaporte: str) -> Optional[Persona]:
        persona_id = self._por_pasaporte.get(pasaporte)
        return self.obtener(persona_id) if persona_id else None
        
    def actualizar(self, persona: Persona) -> Optional[Persona]:
        persona_existente = self.obtener(persona.id)
        if persona_existente and persona_existente.numero_pasaporte != persona.numero_pasaporte:
            del self._por_pasaporte[persona_existente.numero_pasaporte]
            self._por_pasaporte[persona.numero_pasaporte] = persona.id
        return super().actualizar(persona)