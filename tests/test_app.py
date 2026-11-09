import unittest

from app import app


class PortalTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_dashboard(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("VėjoEnergija".encode("utf-8"), response.data)

    def test_health(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["status"], "ok")

    def test_api(self):
        response = self.client.get("/api/turbines")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json["turbines"]), 4)


if __name__ == "__main__":
    unittest.main()
