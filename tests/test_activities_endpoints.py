"""Integration tests for API endpoints using AAA (Arrange-Act-Assert) pattern."""

import pytest


class TestGetActivities:
    """Integration tests for GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client, fresh_activities):
        """
        Test that GET /activities returns all activities.
        
        AAA Pattern:
        - Arrange: Use fresh_activities fixture to set up test data
        - Act: Make GET request to /activities endpoint
        - Assert: Verify all activities are returned
        """
        # Arrange
        expected_activity_count = len(fresh_activities)
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert len(activities) == expected_activity_count
        assert "Chess Club" in activities
        assert "Programming Class" in activities

    def test_get_activities_includes_required_fields(self, client):
        """
        Test that each activity includes all required fields.
        
        AAA Pattern:
        - Arrange: None (using fixture setup)
        - Act: Make GET request to /activities endpoint
        - Assert: Verify each activity has required fields
        """
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        assert response.status_code == 200
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)

    def test_get_activities_shows_empty_participants_list(self, client, sample_activities, monkeypatch):
        """
        Test that activities with no participants show empty list.
        
        AAA Pattern:
        - Arrange: Set up sample data with empty participants
        - Act: Make GET request to /activities endpoint
        - Assert: Verify empty participants list is returned
        """
        # Arrange
        monkeypatch.setattr("src.app.activities", sample_activities)
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        assert response.status_code == 200
        assert activities["Programming Class"]["participants"] == []


class TestSignupForActivity:
    """Integration tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_successful(self, client):
        """
        Test successful signup for an activity.
        
        AAA Pattern:
        - Arrange: Prepare email and activity name
        - Act: Make POST request to signup endpoint
        - Assert: Verify signup response and participant is added
        """
        # Arrange
        email = "newstudent@test.edu"
        activity_name = "Chess Club"
        
        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Assert
        assert response.status_code == 200
        assert email in response.json()["message"]

    def test_signup_adds_participant_to_list(self, client):
        """
        Test that signup adds participant to activity's participants list.
        
        AAA Pattern:
        - Arrange: Prepare email and activity name
        - Act: Sign up and then fetch activities
        - Assert: Verify participant appears in the participants list
        """
        # Arrange
        email = "student@test.edu"
        activity_name = "Programming Class"
        
        # Act
        signup_response = client.post(f"/activities/{activity_name}/signup?email={email}")
        fetch_response = client.get("/activities")
        activities = fetch_response.json()
        
        # Assert
        assert signup_response.status_code == 200
        assert email in activities[activity_name]["participants"]

    def test_signup_fails_already_signed_up(self, client):
        """
        Test that signup fails if student is already registered.
        
        AAA Pattern:
        - Arrange: Sign up a student first
        - Act: Attempt to sign up the same student again
        - Assert: Verify 400 error is returned
        """
        # Arrange
        email = "michael@mergington.edu"  # Already in Chess Club from fresh_activities
        activity_name = "Chess Club"
        
        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_fails_activity_not_found(self, client):
        """
        Test that signup fails if activity doesn't exist.
        
        AAA Pattern:
        - Arrange: Prepare email and nonexistent activity name
        - Act: Attempt to sign up for nonexistent activity
        - Assert: Verify 404 error is returned
        """
        # Arrange
        email = "student@test.edu"
        activity_name = "Nonexistent Activity"
        
        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_signup_updates_availability_count(self, client):
        """
        Test that signing up reduces available spots.
        
        AAA Pattern:
        - Arrange: Get initial availability, prepare signup data
        - Act: Sign up a new student
        - Assert: Verify availability is reduced
        """
        # Arrange
        email = "newstudent@test.edu"
        activity_name = "Gym Class"
        
        # Get initial state
        initial_response = client.get("/activities")
        initial_activities = initial_response.json()
        initial_participants = len(initial_activities[activity_name]["participants"])
        initial_spots = initial_activities[activity_name]["max_participants"] - initial_participants
        
        # Act
        client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Get updated state
        updated_response = client.get("/activities")
        updated_activities = updated_response.json()
        updated_participants = len(updated_activities[activity_name]["participants"])
        updated_spots = updated_activities[activity_name]["max_participants"] - updated_participants
        
        # Assert
        assert updated_participants == initial_participants + 1
        assert updated_spots == initial_spots - 1


class TestRemoveParticipant:
    """Integration tests for DELETE /activities/{activity_name}/participants/{email} endpoint."""

    def test_remove_participant_successful(self, client):
        """
        Test successful removal of a participant.
        
        AAA Pattern:
        - Arrange: Identify existing participant to remove
        - Act: Make DELETE request to remove participant
        - Assert: Verify removal response
        """
        # Arrange
        email = "michael@mergington.edu"
        activity_name = "Chess Club"
        
        # Act
        response = client.delete(f"/activities/{activity_name}/participants/{email}")
        
        # Assert
        assert response.status_code == 200
        assert email in response.json()["message"]

    def test_remove_participant_removes_from_list(self, client):
        """
        Test that removal actually removes participant from participants list.
        
        AAA Pattern:
        - Arrange: Identify existing participant
        - Act: Remove participant and fetch activities
        - Assert: Verify participant no longer in list
        """
        # Arrange
        email = "michael@mergington.edu"
        activity_name = "Chess Club"
        
        # Act
        client.delete(f"/activities/{activity_name}/participants/{email}")
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        assert email not in activities[activity_name]["participants"]

    def test_remove_participant_fails_not_found(self, client):
        """
        Test that removal fails if participant isn't registered.
        
        AAA Pattern:
        - Arrange: Prepare email not in participant list
        - Act: Attempt to remove nonexistent participant
        - Assert: Verify 400 error is returned
        """
        # Arrange
        email = "nonexistent@test.edu"
        activity_name = "Chess Club"
        
        # Act
        response = client.delete(f"/activities/{activity_name}/participants/{email}")
        
        # Assert
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

    def test_remove_participant_fails_activity_not_found(self, client):
        """
        Test that removal fails if activity doesn't exist.
        
        AAA Pattern:
        - Arrange: Prepare email and nonexistent activity name
        - Act: Attempt to remove from nonexistent activity
        - Assert: Verify 404 error is returned
        """
        # Arrange
        email = "michael@test.edu"
        activity_name = "Nonexistent Activity"
        
        # Act
        response = client.delete(f"/activities/{activity_name}/participants/{email}")
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_remove_participant_increases_availability(self, client):
        """
        Test that removing a participant increases available spots.
        
        AAA Pattern:
        - Arrange: Get initial availability
        - Act: Remove a participant
        - Assert: Verify availability increased
        """
        # Arrange
        email = "michael@mergington.edu"
        activity_name = "Chess Club"
        
        # Get initial state
        initial_response = client.get("/activities")
        initial_activities = initial_response.json()
        initial_participants = len(initial_activities[activity_name]["participants"])
        initial_spots = initial_activities[activity_name]["max_participants"] - initial_participants
        
        # Act
        client.delete(f"/activities/{activity_name}/participants/{email}")
        
        # Get updated state
        updated_response = client.get("/activities")
        updated_activities = updated_response.json()
        updated_participants = len(updated_activities[activity_name]["participants"])
        updated_spots = updated_activities[activity_name]["max_participants"] - updated_participants
        
        # Assert
        assert updated_participants == initial_participants - 1
        assert updated_spots == initial_spots + 1


class TestIntegrationFlow:
    """Integration tests for complete workflows."""

    def test_signup_and_remove_flow(self, client):
        """
        Test complete flow: signup -> verify -> remove -> verify.
        
        AAA Pattern:
        - Arrange: Prepare test data
        - Act: Perform signup, verify, remove, verify again
        - Assert: Verify state changes at each step
        """
        # Arrange
        email = "testuser@test.edu"
        activity_name = "Art Studio"
        
        # Act & Assert - Step 1: Verify not in list initially
        response = client.get("/activities")
        activities = response.json()
        assert email not in activities[activity_name]["participants"]
        
        # Act & Assert - Step 2: Sign up
        signup_response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert signup_response.status_code == 200
        
        # Act & Assert - Step 3: Verify in list after signup
        response = client.get("/activities")
        activities = response.json()
        assert email in activities[activity_name]["participants"]
        
        # Act & Assert - Step 4: Remove participant
        remove_response = client.delete(f"/activities/{activity_name}/participants/{email}")
        assert remove_response.status_code == 200
        
        # Act & Assert - Step 5: Verify removed from list
        response = client.get("/activities")
        activities = response.json()
        assert email not in activities[activity_name]["participants"]

    def test_multiple_signups_and_removals(self, client):
        """
        Test multiple signups and removals on the same activity.
        
        AAA Pattern:
        - Arrange: Prepare multiple emails and activity
        - Act: Perform multiple signups and removals
        - Assert: Verify final state
        """
        # Arrange
        emails = ["user1@test.edu", "user2@test.edu", "user3@test.edu"]
        activity_name = "Science Club"
        
        # Act & Assert - Sign up all
        for email in emails:
            response = client.post(f"/activities/{activity_name}/signup?email={email}")
            assert response.status_code == 200
        
        response = client.get("/activities")
        activities = response.json()
        for email in emails:
            assert email in activities[activity_name]["participants"]
        
        # Act & Assert - Remove two
        for email in emails[:2]:
            response = client.delete(f"/activities/{activity_name}/participants/{email}")
            assert response.status_code == 200
        
        response = client.get("/activities")
        activities = response.json()
        assert emails[0] not in activities[activity_name]["participants"]
        assert emails[1] not in activities[activity_name]["participants"]
        assert emails[2] in activities[activity_name]["participants"]
