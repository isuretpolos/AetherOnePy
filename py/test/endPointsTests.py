import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import unittest
from py.main import app

class FlaskEndpointsTestCase(unittest.TestCase):
    
    def setUp(self):
        """Set up a test client for Flask app."""
        self.app = app.test_client()
        self.app.testing = True

    def test_ping(self):
        """Test the /ping endpoint."""
        response = self.app.get('/ping')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode('utf-8'), 'pong')

    def test_qrcode(self):
        """Test the /qrcode endpoint."""
        response = self.app.get('/qrcode')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'image/png')

    def test_case_get(self):
        """Test the /case endpoint for GET method."""
        response = self.app.get('/case')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.is_json)

    def test_case_post(self):
        """Test the /case endpoint for POST method."""
        data = {
            "name": "Test Case",
            "email": "test@example.com",
            "color": "red",
            "description": "Test description",
            "created": "2025-01-01T12:00:00",
            "lastChange": "2025-01-02T12:00:00"
        }
        response = self.app.post('/case', json=data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.is_json)

    def test_collect_hotbits_post(self):
        """Test the /collectHotBits endpoint for POST method."""
        response = self.app.post('/collectHotBits')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.is_json)

    def test_collect_hotbits_delete(self):
        """Test the /collectHotBits endpoint for DELETE method."""
        response = self.app.delete('/collectHotBits')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.is_json)

    def test_non_existent_endpoint(self):
        """Test a non-existent endpoint to confirm 404 error."""
        response = self.app.get('/nonexistent')
        self.assertEqual(response.status_code, 404)

if __name__ == "__main__":
    unittest.main()
