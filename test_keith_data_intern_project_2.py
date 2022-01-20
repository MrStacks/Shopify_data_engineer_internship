import os
import unittest
from unittest.mock import patch
import keith_data_intern_project_2

class TestKeithProject(unittest.TestCase):
    def test_get_key(self):
        result = keith_data_intern_project_2.get_key()
        self.assertTrue(type(result) is bytes)
        self.assertEqual(44, len(result))
    
    def test_get_dataframe(self):
        result = keith_data_intern_project_2.get_dataframe()
        columns = result.columns.to_list()
        self.assertTrue('image_name' in columns)
        self.assertTrue('image_code' in columns)
        self.assertTrue('image_keywords' in columns)
        self.assertTrue('image_features' in columns)
        self.assertTrue('image_access' in columns)
        self.assertTrue('user_pass' in columns)
        self.assertTrue('unique_uuid' in columns)
        
    def test_encrypt_file(self):
        image_path = r"./best_image.png" # WTF
        image_format = "png"
        result = keith_data_intern_project_2.encrypt_file(image_path, image_format)
        self.assertTrue(type(result) is bytes)
        
    @patch('keith_data_intern_project_2.get_input', return_value='n')
    def test_image_data(self, input):
        image_path = r"./best_image.png"
        result = keith_data_intern_project_2.image_data(image_path)
        columns = result.keys()
        self.assertTrue('image_name' in columns)
        self.assertTrue('image_code' in columns)
        self.assertTrue('image_keywords' in columns)
        self.assertTrue('image_features' in columns)
        self.assertTrue('image_access' in columns)
        self.assertTrue('user_pass' in columns)
        self.assertTrue('unique_uuid' in columns)
        self.assertEqual(result['image_name'], 'best_image')
        self.assertEqual(result['image_keywords'], 'n')
        self.assertEqual(result['image_features'], 'n')
        self.assertEqual(result['image_access'], 'private')
        
    @patch('keith_data_intern_project_2.get_input', return_value='n')
    def test_store_images(self, input):
        if os.path.exists('./data.csv'):
            os.remove('./data.csv')
        keith_data_intern_project_2.store_images('./')
        
        result = keith_data_intern_project_2.get_dataframe()
        self.assertEqual(2, result.size)
        self.assertListEqual(['best_image', 'first_dog'], result['image_name'].to_list())
     
    @patch('keith_data_intern_project_2.get_input', 'first_dog')
    def test_search_images(self, input):
        result = keith_data_intern_project_2.search_images('image_name')
        self.assertEqual(1, len(result))      
        
if __name__ == '__main__':
    unittest.main()        