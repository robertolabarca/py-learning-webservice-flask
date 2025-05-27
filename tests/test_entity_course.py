import unittest
from entities.course import Course

class TestCourseEntity(unittest.TestCase):
    def setUp(self):
        self.course=Course(course_id=1,name="computo",description="descrip curso")

    def test_to_entity(self):
        """
        docstring
        """
        course_entity = {
            'id': 1,
            'name': 'computo',
            'description': 'descrip curso'
        }
        self.assertEqual(self.course.to_entity(),course_entity)

if __name__ == '__main__':
    unittest.main()