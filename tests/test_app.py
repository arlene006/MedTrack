import unittest
from app import app
import uuid

class MedTrackTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        # Unique email for testing to avoid conflicts in DynamoDB
        self.test_email = f"test_{uuid.uuid4().hex[:6]}@example.com"
        self.test_password = "password123"

    def test_index_page(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'MEDTRACK', response.data)

    def test_patient_registration_flow(self):
        # 1. Test Registration
        response = self.app.post('/register', data={
            'name': 'Test Patient',
            'email': self.test_email,
            'password': self.test_password,
            'phone': '1234567890'
        }, follow_redirects=True)
        self.assertIn(b'Registration successful', response.data)

        # 2. Test Login
        response = self.app.post('/login', data={
            'email': self.test_email,
            'password': self.test_password,
            'role': 'patient'
        }, follow_redirects=True)
        self.assertIn(b'Welcome back', response.data)
        self.assertIn(b'Test Patient', response.data)

    def test_unauthorized_access(self):
        # Try to access dashboard without login
        response = self.app.get('/dashboard', follow_redirects=True)
        self.assertIn(b'Welcome Back', response.data) # Redirected to login

    def test_doctor_login_failure(self):
        # Test wrong password
        response = self.app.post('/login', data={
            'email': 'sarah@medtrack.com', # Assuming seeded doctor
            'password': 'wrongpassword',
            'role': 'doctor'
        }, follow_redirects=True)
        self.assertIn(b'Invalid email or password', response.data)

if __name__ == '__main__':
    unittest.main()
