import json
import unittest
from app import app
from database import init_db, get_user_profile, get_chat_history
from calculators import calculate_bmr, calculate_tdee, calculate_macros, calculate_one_rep_max

class FitCoachTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
        with app.app_context():
            init_db()

    def test_scientific_calculators(self):
        # Test 70kg, 175cm, 25yo male
        bmr = calculate_bmr(70, 175, 25, "male")
        self.assertEqual(bmr, 1673.8)

        tdee = calculate_tdee(bmr, "moderate")
        self.assertGreater(tdee, 2000)

        macros = calculate_macros(tdee, "muscle_gain", "high_protein", 70)
        self.assertIn("target_calories", macros)
        self.assertGreater(macros["protein_g"], 100)

        orm = calculate_one_rep_max(100, 5)
        self.assertGreater(orm["one_rep_max"], 100)

    def test_pages_render(self):
        pages = ["/", "/chat", "/workout-generator", "/diet-generator", "/calculators", "/saved-plans", "/progress"]
        for page in pages:
            res = self.client.get(page)
            self.assertEqual(res.status_code, 200, f"Page {page} failed with {res.status_code}")

    def test_api_chat(self):
        res = self.client.post("/api/chat", json={"message": "How much protein do I need daily?"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIn("protein", data["reply"].lower())

    def test_api_generate_workout(self):
        res = self.client.post("/api/generate-workout", json={
            "goal": "muscle_gain",
            "experience_level": "intermediate",
            "days_per_week": 4,
            "equipment": "Full Gym",
            "injury_notes": "None"
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIn("plan", data)

    def test_api_generate_diet(self):
        res = self.client.post("/api/generate-diet", json={
            "goal": "muscle_gain",
            "diet_type": "high_protein",
            "target_calories": 2400,
            "allergies": "None",
            "meals_per_day": 4
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["plan"]["target_calories"], 2400)

if __name__ == '__main__':
    unittest.main()
