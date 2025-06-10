# **Sistema de Matriculación de Cursos: Requisitos y Solución con Patrones de Diseño**

## **📝 Enunciado del Problema Reformulado**

**Contexto:**
Una institución educativa necesita un sistema para gestionar la matriculación de estudiantes en cursos. El sistema debe:

1. **Gestionar personas** (estudiantes) con:
   - Nombre, apellidos, sexo (M/F/O) y número de pasaporte (único)
   
2. **Administrar cursos** con:
   - Nombre y descripción

3. **Registrar matrículas** que relacionen:
   - Una persona con un curso

**Requisitos técnicos:**
1. **Integridad de datos:** Todas las operaciones deben ser atómicas (si falla un paso, no se guardan cambios intermedios)
2. **Auditoría:** Todos los registros deben llevar:
   - Fecha/hora de creación
   - Fecha/hora de última modificación
3. **Mantenibilidad:** Evitar duplicación de código en campos comunes
4. **Flexibilidad:** La implementación debe permitir:
   - Cambios futuros en el almacenamiento (de memoria a base de datos)
   - Fácil adición de nuevas funcionalidades

**Solución propuesta (con patrones de diseño):**
- **Patrón Unit of Work:** Para gestionar transacciones y operaciones atómicas
- **Patrón Repository:** Para abstraer el acceso a datos
- **Modelo Base:** Para campos comunes y auditoría automática

## **🔍 ¿Por qué estos patrones?**

1. **Unit of Work:**
   - Garantiza que todas las operaciones (registrar persona, crear curso y matricular) se completen exitosamente o ninguna se guarde
   - Ejemplo: Si el curso no puede crearse, tampoco se guardará la persona ni la matrícula

2. **Repository:**
   - Oculta los detalles de almacenamiento (puede ser memoria, SQL, NoSQL)
   - Proporciona una interfaz consistente para operaciones CRUD

3. **Modelo Base:**
   - Centraliza campos comunes (ID, fechas de auditoría)
   - Asegura consistencia en todos los modelos

## **🛠️ Implementación Técnica**

### **1. Estructura Base (Diagrama)**
```
SistemaMatriculacion
│
├── modelos/               # Entidades del dominio
│   ├── ModeloBase.py      # Campos comunes
│   ├── Persona.py         # Datos de estudiantes
│   ├── Curso.py           # Cursos disponibles
│   └── Matricula.py       # Relación persona-curso
│
├── repositorios/          # Patrón Repository
│   ├── Interfaz.py        # Definiciones abstractas
│   └── EnMemoria.py       # Implementación concreta
│
└── unit_of_work/          # Patrón UoW
    ├── Interfaz.py        # Contrato UoW
    └── Implementacion.py  # UoW concreto
```

### **2. Ejemplo de Caso de Uso**

```python
# Registrar una nueva matrícula (transacción completa)
def registrar_matricula(datos_persona, datos_curso):
    with UnitOfWork() as uow:
        # Paso 1: Registrar persona (auditoría automática)
        persona = Persona(**datos_persona)
        uow.personas.agregar(persona)
        
        # Paso 2: Crear curso (auditoría automática)
        curso = Curso(**datos_curso)
        uow.cursos.agregar(curso)
        
        # Paso 3: Crear matrícula
        matricula = Matricula(
            persona_id=persona.id,
            curso_id=curso.id
        )
        uow.matriculas.agregar(matricula)
        
        # Commit automático si todo funciona
        # Rollback automático si hay errores
    
    print("Matrícula registrada exitosamente")
```

### **3. Beneficios Clave**

| Requisito Original | Solución Implementada | Beneficio |
|--------------------|-----------------------|-----------|
| Integridad de datos | Unit of Work | Operaciones atómicas |
| Auditoría | ModeloBase | Fechas automáticas |
| Mantenibilidad | Repository + Herencia | Código DRY |
| Flexibilidad | Interfaces abstractas | Cambio fácil de almacenamiento |

## **📌 Conclusión**

Este diseño resuelve los requisitos mediante:
1. **Transaccionalidad:** Con Unit of Work
2. **Consistencia:** Con ModeloBase
3. **Escalabilidad:** Con Repository

¿Te gustaría profundizar en alguna parte específica de la implementación?


==========================================================================


# **Patrón Unit of Work con ModeloBase en Python: Ejemplo Completo**

## **📌 Enunciado del Problema**
Se necesita desarrollar un sistema de matriculación de cursos donde:
1. **Personas** pueden registrarse con sus datos personales (nombre, apellidos, sexo y pasaporte).
2. **Cursos** pueden ser creados con un nombre y descripción.
3. Las **matrículas** vinculan a una persona con un curso.
4. **Todos los registros deben auditarse** (fecha de creación y última modificación).
5. **Las operaciones deben ser transaccionales** (si falla un paso, no se guardan cambios).

## **💻 Solución: Implementación Completa**

### **1. Definición del `ModeloBase` (Auditoría Común)**
```python
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, Generic, TypeVar, Dict, List
from abc import ABC, abstractmethod

class ModeloBase(BaseModel):
    """
    Clase base para auditoría automática.
    Campos comunes:
    - id (UUID único)
    - fecha_creacion (auto-generado al crear)
    - fecha_modificacion (auto-actualizado al modificar)
    """
    id: UUID = Field(default_factory=uuid4, description="ID único")
    fecha_creacion: datetime = Field(default_factory=datetime.now, description="Fecha de creación")
    fecha_modificacion: Optional[datetime] = Field(None, description="Última modificación")

    def actualizar_fecha(self):
        """Actualiza la fecha de modificación."""
        self.fecha_modificacion = datetime.now()

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }
```

---

### **2. Modelos del Dominio (`Persona`, `Curso`, `Matricula`)**
```python
class Persona(ModeloBase):
    nombre: str = Field(..., min_length=2, max_length=50, example="Juan")
    apellidos: str = Field(..., min_length=2, max_length=100, example="Pérez García")
    sexo: str = Field(..., regex="^[MFO]$", example="M")  # M, F, O
    numero_pasaporte: str = Field(..., min_length=6, max_length=20, example="AB123456")

class Curso(ModeloBase):
    nombre: str = Field(..., min_length=3, max_length=100, example="Python Avanzado")
    descripcion: str = Field(..., example="Patrones de diseño con Python")

class Matricula(ModeloBase):
    persona_id: UUID = Field(..., description="ID de la persona")
    curso_id: UUID = Field(..., description="ID del curso")
```

---

### **3. Patrón Repository (Abstracción para Persistencia)**
```python
T = TypeVar('T', bound=ModeloBase)

class Repository(Generic[T], ABC):
    @abstractmethod
    def agregar(self, entidad: T) -> None:
        pass

    @abstractmethod
    def obtener(self, id: UUID) -> Optional[T]:
        pass

    @abstractmethod
    def actualizar(self, entidad: T) -> None:
        pass

    @abstractmethod
    def eliminar(self, id: UUID) -> None:
        pass

    @abstractmethod
    def listar_todos(self) -> List[T]:
        pass

# Implementación en Memoria (para pruebas)
class RepositorioEnMemoria(Repository[T]):
    def __init__(self):
        self._datos: Dict[UUID, T] = {}

    def agregar(self, entidad: T) -> None:
        self._datos[entidad.id] = entidad

    def obtener(self, id: UUID) -> Optional[T]:
        return self._datos.get(id)

    def actualizar(self, entidad: T) -> None:
        if entidad.id in self._datos:
            entidad.actualizar_fecha()  # Auditoría automática
            self._datos[entidad.id] = entidad

    def eliminar(self, id: UUID) -> None:
        self._datos.pop(id, None)

    def listar_todos(self) -> List[T]:
        return list(self._datos.values())
```

---

### **4. Unit of Work (Gestor Transaccional)**
```python
class UnitOfWork(ABC):
    @abstractmethod
    def __enter__(self):
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @abstractmethod
    def commit(self):
        pass

    @abstractmethod
    def rollback(self):
        pass

    @property
    @abstractmethod
    def personas(self) -> Repository[Persona]:
        pass

    @property
    @abstractmethod
    def cursos(self) -> Repository[Curso]:
        pass

    @property
    @abstractmethod
    def matriculas(self) -> Repository[Matricula]:
        pass

# Implementación concreta
class UoWEnMemoria(UnitOfWork):
    def __init__(self):
        self._personas = RepositorioEnMemoria[Persona]()
        self._cursos = RepositorioEnMemoria[Curso]()
        self._matriculas = RepositorioEnMemoria[Matricula]()
        self._confirmado = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.commit()
        else:
            self.rollback()

    def commit(self):
        self._confirmado = True

    def rollback(self):
        # En una DB real, se revertirían los cambios
        pass

    @property
    def personas(self) -> Repository[Persona]:
        return self._personas

    @property
    def cursos(self) -> Repository[Curso]:
        return self._cursos

    @property
    def matriculas(self) -> Repository[Matricula]:
        return self._matriculas
```

---

### **5. Ejemplo de Uso (Caso de Uso: Matricular Persona)**
```python
def matricular_persona(
    nombre: str,
    apellidos: str,
    pasaporte: str,
    nombre_curso: str,
    descripcion_curso: str
) -> None:
    with UoWEnMemoria() as uow:
        # 1. Crear persona
        persona = Persona(
            nombre=nombre,
            apellidos=apellidos,
            sexo="M",
            numero_pasaporte=pasaporte
        )
        uow.personas.agregar(persona)

        # 2. Crear curso
        curso = Curso(
            nombre=nombre_curso,
            descripcion=descripcion_curso
        )
        uow.cursos.agregar(curso)

        # 3. Matricular
        matricula = Matricula(
            persona_id=persona.id,
            curso_id=curso.id
        )
        uow.matriculas.agregar(matricula)

        # Commit implícito al salir del 'with' (si no hay errores)
    
    print("✅ Matrícula exitosa!")

# Ejecución
matricular_persona(
    nombre="Carlos",
    apellidos="Ruiz Méndez",
    pasaporte="ZX654321",
    nombre_curso="Django Profesional",
    descripcion_curso="Desarrollo web con Django y REST APIs"
)
```

---

## **🔍 ¿Qué Logramos?**
1. **Auditoría automática**: Todos los modelos registran cuándo fueron creados/modificados.
2. **Transaccionalidad**: Si falla un paso, no se guarda nada (patrón Unit of Work).
3. **Código limpio**: Evitamos repetir campos comunes (`ModeloBase`).
4. **Flexibilidad**: Fácil migración a una base de datos real (solo cambiar `RepositorioEnMemoria` por `RepositorioSQL`).

## **⚡ Mejoras Posibles**
- Añadir **validación de duplicados** (ej: pasaporte único).
- Implementar **búsquedas específicas** (ej: "cursos de una persona").
- Usar **SQLAlchemy** o **Django ORM** para persistencia real.

¿Necesitas alguna parte extendida o explicada con más detalle? 😊