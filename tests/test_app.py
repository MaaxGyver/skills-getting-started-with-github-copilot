"""
Tests for the Mergington High School Activities API

Uses the Arrange-Act-Assert (AAA) testing pattern for clarity.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Fixture to provide a TestClient instance for all tests"""
    return TestClient(app)


class TestRootEndpoint:
    """Tests for the root endpoint"""

    def test_root_redirect_to_html(self, client):
        """
        Arrange: TestClient is ready
        Act: Make GET request to root endpoint
        Assert: Verify redirect response to static HTML
        """
        # Arrange
        expected_redirect_url = "/static/index.html"

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert expected_redirect_url in response.headers["location"]


class TestActivitiesEndpoint:
    """Tests for the GET /activities endpoint"""

    def test_get_all_activities_returns_dict(self, client):
        """
        Arrange: TestClient is ready with seeded activities
        Act: Make GET request to /activities
        Assert: Verify response is a dict with activity data
        """
        # Arrange
        expected_activities_count = 9

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        assert response.status_code == 200
        assert isinstance(activities, dict)
        assert len(activities) == expected_activities_count

    def test_get_activities_contains_activity_details(self, client):
        """
        Arrange: TestClient is ready
        Act: Make GET request to /activities
        Assert: Verify each activity has required fields
        """
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_name, str)
            assert required_fields.issubset(activity_data.keys())
            assert isinstance(activity_data["participants"], list)


class TestSignupEndpoint:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""

    def test_signup_successful_with_valid_activity_and_email(self, client):
        """
        Arrange: Valid activity name and email, student not yet signed up
        Act: POST request to signup endpoint
        Assert: Verify student is added to participants list
        """
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]

        # Verify student appears in participants list
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities[activity_name]["participants"]

    def test_signup_fails_with_nonexistent_activity(self, client):
        """
        Arrange: Invalid activity name and valid email
        Act: POST request with non-existent activity
        Assert: Verify 404 error is returned
        """
        # Arrange
        invalid_activity = "Nonexistent Club"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{invalid_activity}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_fails_when_student_already_registered(self, client):
        """
        Arrange: Activity and email, student already signed up once
        Act: Attempt POST request for same student and activity
        Assert: Verify 400 error is returned
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already in participants

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]


class TestUnregisterEndpoint:
    """Tests for the DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_successful_with_registered_student(self, client):
        """
        Arrange: Activity name and email of registered student
        Act: DELETE request to unregister endpoint
        Assert: Verify student is removed from participants list
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already registered

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )

        # Assert
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]

        # Verify student removed from participants list
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email not in activities[activity_name]["participants"]

    def test_unregister_fails_with_nonexistent_activity(self, client):
        """
        Arrange: Invalid activity name and valid email
        Act: DELETE request with non-existent activity
        Assert: Verify 404 error is returned
        """
        # Arrange
        invalid_activity = "Nonexistent Club"
        email = "student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{invalid_activity}/unregister?email={email}"
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_unregister_fails_when_student_not_registered(self, client):
        """
        Arrange: Activity and email of student not signed up
        Act: DELETE request for unregistered student
        Assert: Verify 400 error is returned
        """
        # Arrange
        activity_name = "Chess Club"
        email = "notregistered@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )

        # Assert
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]
