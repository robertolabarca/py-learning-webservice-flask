
import email
import copy
import json
import os
from pathlib import Path
import unittest
from entities.persona import Persona
from pydantic import ValidationError

#from entities.student import Student

class TestPersonEntity(unittest.TestCase):
    def setUp(self):
        self.persona_base={
            "id":1,
            "nombre":"rlb",
            "apellidos":"mis apellidos",
            "ci":"71070301227",
            "email":"eee@x.com"
        }
        self.persona_valida=Persona(**self.persona_base)
        self.default_filename="persona.json"
        self.custom_filename="custom_persona.json"
    
    def tearDown(self):
        """Limpieza después de cada test"""
        # Eliminar archivos creados durante las pruebas
        if os.path.exists(self.default_filename):
            os.remove(self.default_filename)
        if os.path.exists(self.custom_filename):
            os.remove(self.custom_filename)
        # Limpiar archivos con timestamp
        for f in Path('.').glob('persona_*.json'):
            os.remove(f)

   
    def test_crear_persona_igual(self):
        """
        docstring
        """
        persona_entity = {
            "id":1,
            "nombre":"rlb",
            "apellidos":"mis apellidos",
            "ci":"71070301227",
            "email":"eee@x.com"
        }
        persona_tmp=Persona(**persona_entity)
        self.assertEqual(self.persona_valida.id,persona_tmp.id)
        self.assertEqual(self.persona_valida.nombre,persona_tmp.nombre)
        self.assertEqual(self.persona_valida.apellidos,persona_tmp.apellidos)
        self.assertEqual(self.persona_valida.ci,persona_tmp.ci)
        self.assertEqual(self.persona_valida.email,persona_tmp.email)
        self.assertEqual(self.persona_valida.activo,persona_tmp.activo)

    def test_ci_invalido_longitud_forma1(self):
        """
        docstring
        """
        datos_invalidos = dict(self.persona_valida)  # Copia el diccionario
        datos_invalidos["ci"] = "1234567890"  # Solo 10 dígitos
    
        with self.assertRaises(ValidationError):
            Persona(**datos_invalidos)


    def test_ci_invalido_longitud_forma_recomendada(self):
        """Test para verificar validación de longitud del CI"""
        datos_invalidos = {**self.persona_base, "ci": "1234567890"}  # Solo 10 dígitos
        
        with self.assertRaises(ValidationError):
            Persona(**datos_invalidos)

    def test_fechas_iguales_al_crear_persona(self):
        """
        docstring
        """
        persona_tmp = copy.deepcopy(self.persona_valida)
        self.assertEqual(persona_tmp.fecha_actualizacion,persona_tmp.fecha_actualizacion)

    def test_cambio_en_fecha_actualizacion(self):
        """
        docstring
        """
        persona_tmp = copy.deepcopy(self.persona_valida)
        fecha_actualizacion_inicial = persona_tmp.fecha_actualizacion
        persona_tmp.ci = "11234567890"
        self.assertNotEqual(persona_tmp.fecha_actualizacion,fecha_actualizacion_inicial)
        self.assertEqual(persona_tmp.fecha_creacion,fecha_actualizacion_inicial)

    def test_save_to_json_default_filename(self):
        """Test de guardado con nombre de archivo automático"""
        
        saved_path= self.persona_valida.save_to_json()

        self.assertEqual(Path(saved_path).name, self.default_filename)
        self.assertTrue(os.path.exists(saved_path))
        
        # Verificar contenido del archivo
        with open(saved_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.assertEqual(data['nombre'], "rlb")
            self.assertEqual(data['ci'],"71070301227" )
    
    def test_save_to_json_custom_filename(self):
        """
        docstring
        """
        saved_path = self.persona_valida.save_to_json(filename=self.custom_filename)
        self.assertEqual(Path(saved_path).name, self.custom_filename)
        self.assertTrue(os.path.exists(saved_path))

    def test_save_to_json_error_is_exist(self):
        """
        docstring
        """
        self.persona_valida.save_to_json()
        with self.assertRaises(FileExistsError):
            self.persona_valida.save_to_json(if_exists="error")
        
    def test_save_to_json_override(self):
        """Test de añadir timestamp cuando el archivo existe"""
        
        self.persona_valida.save_to_json()
        new_path = self.persona_valida.save_to_json(if_exists='append_timestamp')
        self.assertIn("persona_", Path(new_path).name)
        self.assertTrue(Path(new_path).exists())
    

if __name__ == '__main__':
    unittest.main()

