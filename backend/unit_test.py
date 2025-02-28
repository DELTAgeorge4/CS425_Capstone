import unittest
from fastapi.testclient import TestClient
from backend import app
client = TestClient(app)

class TestFastAPI(unittest.TestCase):
    def test_root_endpoint(self):
        # Since "/" returns an HTML template response, we check for a 200 status code
        # and check that the returned content contains an expected string.
        response = client.get("/")
        self.assertEqual(response.status_code, 200)
        # If your index.html contains a particular keyword, test for it:
        # self.assertIn("Welcome", response.text)

    def test_fart_endpoint(self):
        # This endpoint returns a JSON response {"message": "fart"}
        response = client.get("/fart")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "fart"})

    def test_login_success(self):
        # Simulate a login; note that your login function must work properly
        # and your test environment may need to set up dummy user credentials.
        login_data = {"username": "james2", "password": "password123"}
        response = client.post("/login", json=login_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Login successful"})
        
    def test_login_failure(self):
        # Simulate a failed login
        login_data = {"username": "wronguser", "password": "wrongpassword"}
        response = client.post("/login", json=login_data)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Invalid credentials"})
        
    
    

    # Additional tests can be added below to test other endpoints
    # For endpoints that require a logged-in user or admin privileges,
    # you might consider overriding dependencies in your test setup.

if __name__ == "__main__":
    unittest.main()
