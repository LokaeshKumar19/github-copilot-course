"""Unit tests for error handling and edge cases using AAA pattern."""

import pytest


class TestErrorResponses:
    """Unit tests for error response handling."""

    def test_http_exception_returns_correct_status_codes(self, client):
        """
        Test that HTTPExceptions return expected status codes.
        
        AAA Pattern:
        - Arrange: Prepare invalid requests
        - Act: Make requests that trigger errors
        - Assert: Verify correct status codes
        """
        # Arrange
        invalid_activity = "Nonexistent Activity"
        invalid_email = "test@test.edu"
        
        # Act & Assert - 404 for nonexistent activity
        response = client.get(f"/activities/{invalid_activity}/info")
        # Note: This specific endpoint doesn't exist, so we test signup endpoint
        signup_response = client.post(f"/activities/{invalid_activity}/signup?email={invalid_email}")
        assert signup_response.status_code == 404

    def test_error_response_includes_detail_message(self, client):
        """
        Test that error responses include detail message.
        
        AAA Pattern:
        - Arrange: Prepare request that triggers error
        - Act: Make request to nonexistent activity
        - Assert: Verify detail message is present
        """
        # Arrange
        invalid_activity = "Fake Activity"
        email = "student@test.edu"
        
        # Act
        response = client.post(f"/activities/{invalid_activity}/signup?email={email}")
        error_data = response.json()
        
        # Assert
        assert "detail" in error_data
        assert isinstance(error_data["detail"], str)
        assert len(error_data["detail"]) > 0


class TestEdgeCases:
    """Unit tests for edge cases and boundary conditions."""

    def test_activity_name_with_spaces(self, client):
        """
        Test handling of activity names with spaces.
        
        AAA Pattern:
        - Arrange: Prepare activity with spaces (exists in real data)
        - Act: Try to fetch and sign up
        - Assert: Verify correct handling
        """
        # Arrange
        activity_name = "Chess Club"  # Contains space
        email = "student@test.edu"
        
        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Assert - Should succeed because activity exists
        assert response.status_code == 200

    def test_email_with_special_characters(self, client):
        """
        Test handling of emails with special characters.
        
        AAA Pattern:
        - Arrange: Prepare email with special characters
        - Act: Attempt signup with special email
        - Assert: Verify handling
        """
        # Arrange
        activity_name = "Programming Class"
        email = "user+test@example.co.uk"  # Valid email with + and multiple domains
        
        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Assert - Should succeed; email format validation is basic
        assert response.status_code == 200

    def test_empty_participants_list_handling(self, client, sample_activities, monkeypatch):
        """
        Test that activities with no participants are handled correctly.
        
        AAA Pattern:
        - Arrange: Set up activity with empty participants
        - Act: Fetch activities and attempt operations
        - Assert: Verify empty list is handled
        """
        # Arrange
        monkeypatch.setattr("src.app.activities", sample_activities)
        activity_name = "Programming Class"  # Has empty participants in sample
        email = "newstudent@test.edu"
        
        # Act
        get_response = client.get("/activities")
        signup_response = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Assert
        assert get_response.status_code == 200
        assert get_response.json()[activity_name]["participants"] == []
        assert signup_response.status_code == 200

    def test_duplicate_signup_attempt(self, client):
        """
        Test that duplicate signup is rejected.
        
        AAA Pattern:
        - Arrange: Identify existing participant
        - Act: Attempt to sign up same person twice
        - Assert: Verify second attempt fails
        """
        # Arrange
        email = "michael@mergington.edu"  # Existing participant
        activity_name = "Chess Club"
        
        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()

    def test_remove_nonexistent_participant(self, client):
        """
        Test removing participant that doesn't exist.
        
        AAA Pattern:
        - Arrange: Prepare email not in activity
        - Act: Attempt to remove nonexistent participant
        - Assert: Verify 400 error
        """
        # Arrange
        email = "doesnotexist@test.edu"
        activity_name = "Chess Club"
        
        # Act
        response = client.delete(f"/activities/{activity_name}/participants/{email}")
        
        # Assert
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"].lower()

    def test_very_long_email_address(self, client):
        """
        Test handling of very long email addresses.
        
        AAA Pattern:
        - Arrange: Create very long email
        - Act: Attempt signup with long email
        - Assert: Verify handling
        """
        # Arrange
        long_email = "a" * 100 + "@test.edu"
        activity_name = "Basketball Team"
        
        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={long_email}")
        
        # Assert - Should succeed as no length validation
        assert response.status_code == 200

    def test_case_sensitivity_in_activity_names(self, client):
        """
        Test that activity names are case-sensitive.
        
        AAA Pattern:
        - Arrange: Prepare activity name in different cases
        - Act: Try to signup with incorrect case
        - Assert: Verify it fails (activity names are case-sensitive)
        """
        # Arrange
        correct_name = "Chess Club"
        incorrect_name = "chess club"
        email = "student@test.edu"
        
        # Act
        correct_response = client.post(f"/activities/{correct_name}/signup?email={email}")
        incorrect_response = client.post(f"/activities/{incorrect_name}/signup?email={email}")
        
        # Assert
        assert correct_response.status_code == 200
        assert incorrect_response.status_code == 404

    def test_url_encoded_special_characters(self, client):
        """
        Test that URL encoding is handled correctly in activity names.
        
        AAA Pattern:
        - Arrange: Get an activity with special characters
        - Act: Make request with properly encoded name
        - Assert: Verify it works
        """
        # Arrange
        activity_name = "Basketball Team"
        email = "student@test.edu"
        
        # Act
        # The space in "Basketball Team" should be handled by client
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Assert
        assert response.status_code == 200


class TestBoundaryConditions:
    """Unit tests for boundary conditions."""

    def test_max_participants_boundary(self, fresh_activities):
        """
        Test max_participants at boundary.
        
        AAA Pattern:
        - Arrange: Check max_participants values
        - Act: Verify they're valid positive integers
        - Assert: All should be > 0
        """
        # Arrange & Act & Assert
        for activity_name, activity_data in fresh_activities.items():
            max_participants = activity_data["max_participants"]
            assert max_participants > 0, f"{activity_name} has invalid max_participants"
            assert isinstance(max_participants, int), f"{activity_name} max_participants not int"

    def test_participants_count_not_exceeding_max(self, fresh_activities):
        """
        Test that current participants don't exceed max.
        
        AAA Pattern:
        - Arrange: Get activities
        - Act: Calculate current vs max participants
        - Assert: Verify count doesn't exceed max
        """
        # Arrange & Act & Assert
        for activity_name, activity_data in fresh_activities.items():
            current = len(activity_data["participants"])
            maximum = activity_data["max_participants"]
            # In valid data, current should not exceed max
            assert current <= maximum, \
                f"{activity_name} has more participants than max_participants"

    def test_empty_activity_name(self, client):
        """
        Test handling of empty activity name.
        
        AAA Pattern:
        - Arrange: Prepare empty activity name
        - Act: Attempt signup
        - Assert: Verify 404
        """
        # Arrange
        activity_name = ""
        email = "student@test.edu"
        
        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Assert
        assert response.status_code == 404  # Empty name won't match any activity

    def test_empty_email(self, client):
        """
        Test handling of empty email.
        
        AAA Pattern:
        - Arrange: Prepare empty email
        - Act: Attempt signup
        - Assert: Verify response (API doesn't validate empty)
        """
        # Arrange
        activity_name = "Chess Club"
        email = ""
        
        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Assert - The API accepts it (no email validation currently)
        assert response.status_code == 200
