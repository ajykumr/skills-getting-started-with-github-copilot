import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestRoot:
    def test_root_redirect(self):
        """Root endpoint redirects to static index.html"""
        # Arrange
        # (no setup needed)
        
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestActivities:
    def test_get_activities_returns_dict(self):
        """GET /activities returns activities dictionary"""
        # Arrange
        # (no setup needed)
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0

    def test_get_activities_contains_chess_club(self):
        """GET /activities includes Chess Club with correct structure"""
        # Arrange
        expected_fields = {"description", "schedule", "max_participants", "participants"}
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert "Chess Club" in data
        assert expected_fields.issubset(data["Chess Club"].keys())
        assert isinstance(data["Chess Club"]["participants"], list)

    def test_get_activities_all_have_required_fields(self):
        """All activities have required fields"""
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_name, activity in activities.items():
            assert required_fields.issubset(activity.keys()), f"{activity_name} missing fields"
            assert isinstance(activity["participants"], list)


class TestSignup:
    def test_signup_success_returns_message(self):
        """Successful signup returns confirmation message"""
        # Arrange
        activity = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity in data["message"]

    def test_signup_nonexistent_activity_returns_404(self):
        """Signup for nonexistent activity returns 404"""
        # Arrange
        nonexistent_activity = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{nonexistent_activity}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_missing_email_returns_422(self):
        """Signup without email returns validation error"""
        # Arrange
        activity = "Chess Club"
        
        # Act
        response = client.post(f"/activities/{activity}/signup")
        
        # Assert
        assert response.status_code == 422

    def test_signup_adds_participant_to_activity(self):
        """Signup successfully adds participant to activity roster"""
        # Arrange
        activity = "Programming Class"
        email = "testuser123@mergington.edu"
        before_response = client.get("/activities")
        initial_count = len(before_response.json()[activity]["participants"])
        
        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")
        after_response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        new_count = len(after_response.json()[activity]["participants"])
        assert new_count == initial_count + 1
        assert email in after_response.json()[activity]["participants"]

    def test_signup_with_special_characters_in_email(self):
        """Signup handles emails with special characters (dots, underscores, hyphens)"""
        # Arrange
        activity = "Art Workshop"
        email = "user_test.name-123@mergington.edu"
        
        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")
        after_response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        assert email in after_response.json()[activity]["participants"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
