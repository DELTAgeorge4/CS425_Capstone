import unittest
from fastapi.testclient import TestClient
from backend import app
client = TestClient(app)

class TestFastAPI(unittest.TestCase):
    def test_root_endpoint(self):
        response = client.get("/")
        self.assertEqual(response.status_code, 200)


    def test_fart_endpoint(self):

        response = client.get("/fart")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "fart"})

    def test_login_success(self):
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
        

if __name__ == "__main__":
    unittest.main()
