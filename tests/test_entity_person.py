
import unittest

from entities.persona import Persona

#from entities.student import Student

class TestPersonEntity(unittest.TestCase):
    def setUp(self):
        self.persona=Persona(id=1, nombre="Robe", apellidos="ape",ci="71070301227",activo=True)

    

if __name__ == '__main__':
    unittest.main()