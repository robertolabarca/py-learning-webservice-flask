
import unittest
from entities.student import Student

class TestStudentEntity(unittest.TestCase):
    def setUp(self):
        self.student=Student(id=1,name="roberto",age=15)

    def test_valores_OK(self):
        """
        docstring
        """
        self.assertEqual(self.student.id,1)
        self.assertEqual(self.student.name,"roberto")
        self.assertEqual(self.student.age,15)
        self.assertEqual(self.student.can_vote,False)

    def  test_update_name(self):
        """
        docstring
        """
        self.student.name = "robe"
        self.assertEqual(self.student.name,"robe")
  

if __name__ == '__main__':
    unittest.main()