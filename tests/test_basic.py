import unittest
import sys
import os

# Add backend directory to path so app.py can find image_manager
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from backend.app import app

class BasicTests(unittest.TestCase):
    def setUp(self):
        # Set up a test client
        self.app = app.test_client()
        self.app.testing = True

    def test_home_page_status_code(self):
        # Send a GET request to the home page
        result = self.app.get('/')
        # Assert the status code is 200 (OK)
        self.assertEqual(result.status_code, 200)

if __name__ == "__main__":
    unittest.main()