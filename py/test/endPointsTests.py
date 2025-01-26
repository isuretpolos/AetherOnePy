import sys
import os
from typing import Optional

# Add the project root and py directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
py_dir = os.path.join(project_root, 'py')
sys.path.extend([project_root, py_dir])

from py.domains.aetherOneDomains import Case, Session, Analysis, Catalog, Rate, AnalysisRate
from py.services.databaseService import get_case_dao

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
        # Input data for the POST request
        data = {
            "name": "Test Case",
            "email": "test@example.com",
            "color": "red",
            "description": "Test description",
            "created": "2025-01-01T12:00:00",
            "lastChange": "2025-01-02T12:00:00"
        }

        # Mock the database insert to return a specific user_id
        expected_user_id = 42
        case_dao = get_case_dao()
        case_dao.insert_case = lambda case: expected_user_id  # Mock method

        # Send POST request
        response = self.app.post('/case', json=data)

        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.is_json)

        # Verify response contains the correct user_id
        response_data = response.get_json()
        self.assertIn("user_id", response_data)
        self.assertEqual(response_data["user_id"], expected_user_id)

        # Optional: Check if the other fields match the input data
        self.assertEqual(response_data["name"], data["name"])
        self.assertEqual(response_data["email"], data["email"])
        self.assertEqual(response_data["color"], data["color"])
        self.assertEqual(response_data["description"], data["description"])
        self.assertEqual(response_data["created"], data["created"])
        self.assertEqual(response_data["lastChange"], data["lastChange"])

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
