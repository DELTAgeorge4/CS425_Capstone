import unittest
from fastapi.testclient import TestClient
from backend.main import app, create_user

client = TestClient(app)

create_user("admin", "admin", "admin")
class TestFastAPI(unittest.TestCase):
    
    
    
    # test the root endpoint
    def test_root_endpoint(self):
        response = client.get("/")
        self.assertEqual(response.status_code, 200)


    # test the /fart endpoint
    def test_fart_endpoint(self):
        response = client.get("/fart")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "fart"})

    # simulate a successful login
    def test_login_success(self):
        login_data = {"username": "admin", "password": "admin"}
        response = client.post("/login", json=login_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Login successful"})
        
    # simulate a failed login
    def test_login_failure(self):
        login_data = {"username": "wronguser", "password": "wrongpassword"}
        response = client.post("/login", json=login_data)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Invalid credentials"})
        

if __name__ == "__main__":
    # to run be in root directory ~/CS425_Capstone and run `./run_test.sh`
    unittest.main()
