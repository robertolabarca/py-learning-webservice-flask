import unittest
import json
from app import app

class TestAppEntity(unittest.TestCase):
    def setUp(self):
        """
        docstring
        """
        self.app = app.test_client()
        self.app.testing = True

    def test_get_course_empty(self):
        """
        docstring
        """
        
        response = self.app.get('/get-course')
        self.assertEqual(response.status_code,404)
        data=json.loads(response.data)
        self.assertIn('error',data)

    def test_create_course(self):
        """
        docstring
        """
        response=self.app.post('/set-course',
                               data=json.dumps({
                                   'id':'2',
                                   'name':'Curso 2',
                                   'description':'descrip'
                               }),
                               content_type='application/json')
        self.assertEqual(response.status_code,200)
        data = json.loads(response.data)
        self.assertEqual(data['id'], '2')
        self.assertEqual(data['name'], 'Curso 2')
        self.assertEqual(data['description'], 'descrip')

    def test_create_and_get_course(self):
        """
        docstring
        """
        response=self.app.post('/set-course',
                               data=json.dumps({
                                   'id':'2',
                                   'name':'Curso 2',
                                   'description':'descrip'
                               }),
                               content_type='application/json')
        self.assertEqual(response.status_code,200)
       
    
if __name__ == '__main__':
    unittest.main()