
import unittest

from entities.persona import Persona

#from entities.student import Student

class TestPersonEntity(unittest.TestCase):
    def setUp(self):
        self.persona=Persona(id=1, nombre="Robe", apellidos="ape",ci="71070301227",email="eee@ss.com",activo=True)

    def test_to_entity(self):
        """
        docstring
        """
        persona_entity = {
            'id': 1,
            'nombre':'robe',
            'apellidos': 'mis apellidos',
            'ci': '71070301221',
            'email': 'pp@mai.com',
            'activo': 'true'
        }
        self.assertEqual(self.persona.id,persona_entity.id)

if __name__ == '__main__':
    unittest.main()

