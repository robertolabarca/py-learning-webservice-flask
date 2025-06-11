from typing import Generic, TypeVar, List, Optional, Dict
from uuid import UUID
from pydantic import BaseModel
from datetime import datetime

T = TypeVar('T', bound=BaseModel)

class RepositorioBase(Generic[T]):
    def __init__(self):
        self._datos: Dict[UUID, T] = {}
        
    def agregar(self, item: T) -> T:
        if item.id in self._datos:
            raise ValueError(f"Entidad con ID {item.id} ya existe")
        item.actualizar_fecha_modificacion()
        self._datos[item.id] = item
        return item
        
    def obtener(self, id: UUID) -> Optional[T]:
        return self._datos.get(id)
        
    def listar(self) -> List[T]:
        return list(self._datos.values())
        
    def actualizar(self, item: T) -> Optional[T]:
        if item.id not in self._datos:
            return None
        item.actualizar_fecha_modificacion()
        self._datos[item.id] = item
        return item
        
    def eliminar(self, id: UUID) -> bool:
        return self._datos.pop(id, None) is not None
        
    def existe(self, id: UUID) -> bool:
        return id in self._datos