"""
Comprehensive tests for the Mergington High School Activities API
"""

import pytest
from src.app import activities


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_200(self, client):
        """Test that GET /activities returns status code 200"""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        data = response.json()
        
        # Check that all expected activities are present
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
        assert "Basketball Team" in data
        assert "Tennis Club" in data
        assert "Art Studio" in data
        assert "Drama Club" in data
        assert "Robotics Club" in data
        assert "Science Club" in data

    def test_get_activities_returns_activity_structure(self, client):
        """Test that each activity has correct structure"""
        response = client.get("/activities")
        data = response.json()
        
        # Check one activity has all required fields
        activity = data["Chess Club"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity

    def test_get_activities_participants_is_list(self, client):
        """Test that participants field is a list"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert isinstance(activity_data["participants"], list)

    def test_get_activities_contains_initial_participants(self, client):
        """Test that activities contain initial participants"""
        response = client.get("/activities")
        data = response.json()
        
        # Chess Club should have michael and daniel
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in data["Chess Club"]["participants"]


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_success(self, client):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "newstudent@mergington.edu" in data["message"]

    def test_signup_adds_participant(self, client):
        """Test that signup adds participant to activity"""
        client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]

    def test_signup_increments_participant_count(self, client):
        """Test that signup increments participant count"""
        before = len(activities["Chess Club"]["participants"])
        client.post("/activities/Chess Club/signup?email=test@mergington.edu")
        after = len(activities["Chess Club"]["participants"])
        
        assert after == before + 1

    def test_signup_activity_not_found(self, client):
        """Test signup for non-existent activity returns 404"""
        response = client.post(
            "/activities/Fake Activity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_duplicate_participant(self, client):
        """Test that same student cannot signup twice for same activity"""
        response = client.post(
            "/activities/Chess Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_duplicate_participant_preserves_count(self, client):
        """Test that duplicate signup doesn't change participant count"""
        before = len(activities["Chess Club"]["participants"])
        client.post(
            "/activities/Chess Club/signup?email=michael@mergington.edu"
        )
        after = len(activities["Chess Club"]["participants"])
        
        assert after == before

    def test_signup_same_student_different_activities(self, client):
        """Test that student can signup for multiple activities"""
        response1 = client.post(
            "/activities/Chess Club/signup?email=student123@mergington.edu"
        )
        response2 = client.post(
            "/activities/Art Studio/signup?email=student123@mergington.edu"
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert "student123@mergington.edu" in activities["Chess Club"]["participants"]
        assert "student123@mergington.edu" in activities["Art Studio"]["participants"]

    def test_signup_returns_success_message(self, client):
        """Test that successful signup returns message"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        data = response.json()
        assert "message" in data
        assert "Signed up" in data["message"]
        assert "newstudent@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_success(self, client):
        """Test successful unregister from activity"""
        response = client.delete(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]

    def test_unregister_removes_participant(self, client):
        """Test that unregister removes participant from activity"""
        client.delete(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]

    def test_unregister_decrements_participant_count(self, client):
        """Test that unregister decrements participant count"""
        before = len(activities["Chess Club"]["participants"])
        client.delete(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        after = len(activities["Chess Club"]["participants"])
        
        assert after == before - 1

    def test_unregister_activity_not_found(self, client):
        """Test unregister from non-existent activity returns 404"""
        response = client.delete(
            "/activities/Fake Activity/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_unregister_student_not_registered(self, client):
        """Test unregister when student is not registered returns 400"""
        response = client.delete(
            "/activities/Chess Club/unregister?email=notstudent@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"]

    def test_unregister_student_not_registered_preserves_participants(self, client):
        """Test that failed unregister doesn't change participant list"""
        before = activities["Chess Club"]["participants"].copy()
        client.delete(
            "/activities/Chess Club/unregister?email=notstudent@mergington.edu"
        )
        after = activities["Chess Club"]["participants"]
        
        assert before == after

    def test_unregister_returns_message(self, client):
        """Test that unregister returns appropriate message"""
        response = client.delete(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        data = response.json()
        assert "message" in data
        assert "michael@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]


class TestIntegrationScenarios:
    """Integration tests for realistic usage scenarios"""

    def test_signup_then_unregister(self, client):
        """Test full flow: signup and then unregister"""
        email = "integration@mergington.edu"
        
        # Signup
        response1 = client.post(
            f"/activities/Chess Club/signup?email={email}"
        )
        assert response1.status_code == 200
        assert email in activities["Chess Club"]["participants"]
        
        # Unregister
        response2 = client.delete(
            f"/activities/Chess Club/unregister?email={email}"
        )
        assert response2.status_code == 200
        assert email not in activities["Chess Club"]["participants"]

    def test_multiple_signups_and_unregisters(self, client):
        """Test multiple signup and unregister operations"""
        emails = [
            "student1@mergington.edu",
            "student2@mergington.edu",
            "student3@mergington.edu"
        ]
        
        # Sign up multiple students
        for email in emails:
            response = client.post(
                f"/activities/Art Studio/signup?email={email}"
            )
            assert response.status_code == 200
        
        # Verify all are signed up
        for email in emails:
            assert email in activities["Art Studio"]["participants"]
        
        # Unregister all
        for email in emails:
            response = client.delete(
                f"/activities/Art Studio/unregister?email={email}"
            )
            assert response.status_code == 200
        
        # Verify all are unregistered
        for email in emails:
            assert email not in activities["Art Studio"]["participants"]

    def test_student_signup_multiple_activities(self, client):
        """Test student signing up for multiple activities"""
        email = "versatile@mergington.edu"
        activities_list = ["Chess Club", "Art Studio", "Drama Club"]
        
        for activity in activities_list:
            response = client.post(
                f"/activities/{activity}/signup?email={email}"
            )
            assert response.status_code == 200
            assert email in activities[activity]["participants"]
