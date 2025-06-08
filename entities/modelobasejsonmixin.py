from datetime import datetime
from pathlib import Path
from typing import Type, TypeVar, Literal, Any, Optional
from pydantic import BaseModel, ConfigDict
import json

T = TypeVar('T', bound='BaseModel')

class ModeloBaseJsonMixin:
    """
    Mixin que añade funcionalidad de guardado/carga en JSON con nombre de archivo automático
    """
    
    def save_to_json(
        self: BaseModel,
        filename: Optional[str] = None,
        if_exists: Literal['overwrite', 'error', 'append_timestamp'] = 'overwrite',
        **dump_kwargs: Any
    ) -> str:
        """
        Guarda el modelo en un archivo JSON.
        
        Args:
            filename: Ruta del archivo (opcional). Si no se proporciona, usa el nombre de la clase.
            if_exists: Comportamiento si existe:
                - 'overwrite': Sobrescribe (por defecto)
                - 'error': Lanza error
                - 'append_timestamp': Añade timestamp al nombre
            dump_kwargs: Argumentos adicionales para model_dump_json()
        
        Returns:
            Ruta donde se guardó el archivo
        """
        # Determinar el nombre del archivo
        if filename is None:
            filename = f"{self.__class__.__name__.lower()}.json"
        
        path = Path(filename)
        
        if path.exists():
            if if_exists == 'error':
                raise FileExistsError(f"El archivo {filename} ya existe")
            elif if_exists == 'append_timestamp':
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                new_filename = f"{path.stem}_{timestamp}{path.suffix}"
                path = path.with_name(new_filename)
        
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(self.model_dump_json(**dump_kwargs))
        
        return str(path.resolve())

    @classmethod
    def open_from_json(
        cls: Type[T],
        filename: Optional[str] = None
    ) -> T:
        """
        Carga un modelo desde archivo JSON.
        
        Args:
            filename: Ruta del archivo (opcional). Si no se proporciona, usa el nombre de la clase.
            
        Returns:
            Instancia del modelo cargado
        """
        # Determinar el nombre del archivo
        if filename is None:
            filename = f"{cls.__name__.lower()}.json"
        
        path = Path(filename)
        
        if not path.exists():
            raise FileNotFoundError(f"El archivo {filename} no existe")
        
        with open(path, 'r', encoding='utf-8') as f:
            return cls.model_validate_json(f.read())

    @classmethod
    def open_or_default(
        cls: Type[T],
        filename: Optional[str] = None,
        default: Optional[T] = None
    ) -> T:
        """
        Intenta cargar desde JSON o devuelve valor por defecto.
        
        Args:
            filename: Ruta del archivo (opcional)
            default: Valor por defecto si no existe (opcional, crea nueva instancia si es None)
            
        Returns:
            Modelo cargado o valor por defecto
        """
        try:
            return cls.open_from_json(filename)
        except FileNotFoundError:
            if default is not None:
                return default
            # Crear una instancia por defecto si no se proporciona
            return cls()  # Asume que el modelo tiene valores por defecto
