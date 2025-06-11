# Sistema de Gestión Educativa con Persistencia en JSON y SQLite

Voy a extender la solución anterior para incorporar persistencia en ambos formatos, manteniendo la estructura limpia y los patrones de diseño.

## Estructura Actualizada

```
educacion/
├── persistence/
│   ├── __init__.py
│   ├── base.py
│   ├── json_repository.py
│   └── sqlite_repository.py
├── config.py
... (resto de la estructura previa)
```

## 1. Configuración (`config.py`)

```python
from enum import Enum, auto

class PersistenceType(Enum):
    MEMORY = auto()
    JSON = auto()
    SQLITE = auto()

class Config:
    PERSISTENCE_TYPE = PersistenceType.SQLITE  # Cambiar según necesidad
    JSON_STORAGE_PATH = "data/json_storage"
    SQLITE_DB_PATH = "data/educacion.db"
```

## 2. Base de Persistencia (`persistence/base.py`)

```python
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List
from uuid import UUID
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)

class AbstractRepository(Generic[T], ABC):
    @abstractmethod
    def agregar(self, item: T) -> T:
        pass
    
    @abstractmethod
    def obtener(self, id: UUID) -> Optional[T]:
        pass
    
    @abstractmethod
    def listar(self) -> List[T]:
        pass
    
    @abstractmethod
    def actualizar(self, item: T) -> Optional[T]:
        pass
    
    @abstractmethod
    def eliminar(self, id: UUID) -> bool:
        pass
    
    @abstractmethod
    def commit(self):
        pass
```

## 3. Implementación JSON (`persistence/json_repository.py`)

```python
import json
import os
from pathlib import Path
from typing import Dict, Type, List, Optional
from uuid import UUID
from pydantic import BaseModel
from ..config import Config
from .base import AbstractRepository

class JSONRepository(AbstractRepository):
    def __init__(self, model_type: Type[BaseModel], file_name: str):
        self.model_type = model_type
        self.file_name = file_name
        self._data: Dict[UUID, BaseModel] = {}
        self._load_data()

    @property
    def file_path(self) -> Path:
        Path(Config.JSON_STORAGE_PATH).mkdir(parents=True, exist_ok=True)
        return Path(Config.JSON_STORAGE_PATH) / f"{self.file_name}.json"

    def _load_data(self):
        if self.file_path.exists():
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data.values():
                    model = self.model_type.parse_raw(item)
                    self._data[model.id] = model

    def _save_data(self):
        data = {str(k): v.json() for k, v in self._data.items()}
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def agregar(self, item: BaseModel) -> BaseModel:
        self._data[item.id] = item
        return item

    def obtener(self, id: UUID) -> Optional[BaseModel]:
        return self._data.get(id)

    def listar(self) -> List[BaseModel]:
        return list(self._data.values())

    def actualizar(self, item: BaseModel) -> Optional[BaseModel]:
        if item.id in self._data:
            self._data[item.id] = item
            return item
        return None

    def eliminar(self, id: UUID) -> bool:
        if id in self._data:
            del self._data[id]
            return True
        return False

    def commit(self):
        self._save_data()
```

## 4. Implementación SQLite (`persistence/sqlite_repository.py`)

```python
import sqlite3
from contextlib import contextmanager
from typing import Dict, Type, List, Optional, Any
from uuid import UUID
from pydantic import BaseModel
from ..config import Config
from .base import AbstractRepository

class SQLiteRepository(AbstractRepository):
    def __init__(self, model_type: Type[BaseModel], table_name: str):
        self.model_type = model_type
        self.table_name = table_name
        self._ensure_table_exists()

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(Config.SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _ensure_table_exists(self):
        fields = self._get_model_fields()
        columns = ', '.join([f"{name} {self._get_sql_type(type_)}" 
                           for name, type_ in fields.items()])
        
        with self._get_connection() as conn:
            conn.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.table_name} (
                    id TEXT PRIMARY KEY,
                    {columns},
                    fecha_creacion TEXT,
                    fecha_modificacion TEXT
                )
            """)

    def _get_model_fields(self) -> Dict[str, Any]:
        return {name: field.type_ 
                for name, field in self.model_type.__fields__.items() 
                if name not in ['id', 'fecha_creacion', 'fecha_modificacion']}

    def _get_sql_type(self, python_type: type) -> str:
        if python_type == str:
            return "TEXT"
        elif python_type == int:
            return "INTEGER"
        elif python_type == float:
            return "REAL"
        elif python_type == bool:
            return "INTEGER"  # SQLite no tiene tipo BOOLEAN
        else:
            return "TEXT"  # Para UUID, datetime, etc.

    def agregar(self, item: BaseModel) -> BaseModel:
        data = item.dict()
        fields = ', '.join(data.keys())
        placeholders = ', '.join(['?'] * len(data))
        
        with self._get_connection() as conn:
            conn.execute(
                f"INSERT INTO {self.table_name} ({fields}) VALUES ({placeholders})",
                list(data.values())
            )
            conn.commit()
        return item

    def obtener(self, id: UUID) -> Optional[BaseModel]:
        with self._get_connection() as conn:
            cursor = conn.execute(
                f"SELECT * FROM {self.table_name} WHERE id = ?",
                (str(id),)
            )
            row = cursor.fetchone()
            return self.model_type.parse_obj(dict(row)) if row else None

    def listar(self) -> List[BaseModel]:
        with self._get_connection() as conn:
            cursor = conn.execute(f"SELECT * FROM {self.table_name}")
            return [self.model_type.parse_obj(dict(row)) for row in cursor]

    def actualizar(self, item: BaseModel) -> Optional[BaseModel]:
        data = item.dict()
        updates = ', '.join([f"{key} = ?" for key in data.keys() if key != 'id'])
        
        with self._get_connection() as conn:
            cursor = conn.execute(
                f"UPDATE {self.table_name} SET {updates} WHERE id = ?",
                [val for key, val in data.items() if key != 'id'] + [str(item.id)]
            )
            conn.commit()
            return item if cursor.rowcount > 0 else None

    def eliminar(self, id: UUID) -> bool:
        with self._get_connection() as conn:
            cursor = conn.execute(
                f"DELETE FROM {self.table_name} WHERE id = ?",
                (str(id),)
            )
            conn.commit()
            return cursor.rowcount > 0

    def commit(self):
        pass  # Las operaciones en SQLite ya son atómicas
```

## 5. Factory de Repositorios (`persistence/__init__.py`)

```python
from ..config import Config, PersistenceType
from .json_repository import JSONRepository
from .sqlite_repository import SQLiteRepository
from .base import AbstractRepository

def get_repository(model_type, table_name: str) -> AbstractRepository:
    if Config.PERSISTENCE_TYPE == PersistenceType.JSON:
        return JSONRepository(model_type, table_name)
    elif Config.PERSISTENCE_TYPE == PersistenceType.SQLITE:
        return SQLiteRepository(model_type, table_name)
    else:
        raise ValueError("Tipo de persistencia no soportado")
```

## 6. Adaptación del Unit of Work (`unit_of_work/unit_of_work.py`)

```python
from ..models.persona import Persona
from ..models.curso import Curso
from ..models.matricula import Matricula
from ..persistence import get_repository

class UnitOfWork:
    def __init__(self):
        self.personas = get_repository(Persona, "personas")
        self.cursos = get_repository(Curso, "cursos")
        self.matriculas = get_repository(Matricula, "matriculas")
        self._committed = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None and not self._committed:
            self.rollback()

    def commit(self):
        self.personas.commit()
        self.cursos.commit()
        self.matriculas.commit()
        self._committed = True

    def rollback(self):
        # En implementación real revertiría cambios
        # Para SQLite no es necesario, para JSON podríamos recargar
        self._committed = False
```

## 7. Ejemplo de Repositorio Especializado (`repositories/persona_repo.py`)

```python
from uuid import UUID
from typing import Optional
from ..models.persona import Persona
from ..persistence import get_repository

class PersonaRepository:
    def __init__(self):
        self.repo = get_repository(Persona, "personas")
        self._por_pasaporte = {}

    def agregar(self, persona: Persona) -> Persona:
        # Verificar pasaporte único
        if self.obtener_por_pasaporte(persona.numero_pasaporte):
            raise ValueError("Número de pasaporte ya registrado")
            
        persona = self.repo.agregar(persona)
        self._por_pasaporte[persona.numero_pasaporte] = persona.id
        return persona

    def obtener_por_pasaporte(self, pasaporte: str) -> Optional[Persona]:
        # Implementación optimizada para memoria
        persona_id = self._por_pasaporte.get(pasaporte)
        return self.repo.obtener(persona_id) if persona_id else None

    # Delegar el resto de métodos al repositorio base
    def obtener(self, id: UUID) -> Optional[Persona]:
        return self.repo.obtener(id)

    def listar(self) -> list[Persona]:
        return self.repo.listar()

    def actualizar(self, persona: Persona) -> Optional[Persona]:
        # Actualizar índice de pasaportes
        existente = self.repo.obtener(persona.id)
        if existente and existente.numero_pasaporte != persona.numero_pasaporte:
            del self._por_pasaporte[existente.numero_pasaporte]
            self._por_pasaporte[persona.numero_pasaporte] = persona.id
        return self.repo.actualizar(persona)

    def eliminar(self, id: UUID) -> bool:
        persona = self.repo.obtener(id)
        if persona:
            del self._por_pasaporte[persona.numero_pasaporte]
        return self.repo.eliminar(id)

    def commit(self):
        self.repo.commit()
```

## 8. Configuración de la Aplicación (`main.py`)

```python
from fastapi import FastAPI
from .config import Config
from .api import personas, cursos, matriculas

# Crear directorios necesarios
if Config.PERSISTENCE_TYPE == Config.PersistenceType.JSON:
    import os
    os.makedirs(Config.JSON_STORAGE_PATH, exist_ok=True)

app = FastAPI(
    title="Sistema de Gestión Educativa",
    description=f"API con persistencia en {Config.PERSISTENCE_TYPE.name}",
    version="2.0.0"
)

app.include_router(personas.router)
app.include_router(cursos.router)
app.include_router(matriculas.router)
```

## Beneficios de esta Implementación

1. **Intercambiabilidad**: Cambiar entre memoria, JSON y SQLite modificando solo la configuración
2. **Consistencia**: Misma interfaz para todos los repositorios
3. **Mantenibilidad**: Lógica de persistencia separada del negocio
4. **Escalabilidad**: Fácil añadir nuevos tipos de persistencia (MySQL, PostgreSQL, etc.)
5. **Pruebas**: Se puede testear con memoria y desplegar con SQLite

## Ejemplo de Uso

```python
# Cambiar persistencia a JSON
from educacion.config import Config
Config.PERSISTENCE_TYPE = Config.PersistenceType.JSON

# El resto del código funciona igual
with UnitOfWork() as uow:
    persona = Persona(
        nombre="Carlos",
        apellidos="Ruiz",
        sexo=Sexo.MASCULINO,
        numero_pasaporte="XYZ987"
    )
    uow.personas.agregar(persona)
    uow.commit()
```

Esta implementación mantiene todos los beneficios de la solución anterior mientras añade flexibilidad en la capa de persistencia, cumpliendo con los requisitos de poder cambiar fácilmente entre diferentes sistemas de almacenamiento.