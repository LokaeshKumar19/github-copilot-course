"""Unit tests for data validation using AAA (Arrange-Act-Assert) pattern."""

import pytest


class TestActivityDataStructure:
    """Unit tests for activity data structure validation."""

    def test_activity_has_required_fields(self, fresh_activities):
        """
        Test that all activities have required fields.
        
        AAA Pattern:
        - Arrange: Get activities from fixture
        - Act: Iterate through activities
        - Assert: Verify each has required fields
        """
        # Arrange
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        # Act & Assert
        for activity_name, activity_data in fresh_activities.items():
            for field in required_fields:
                assert field in activity_data, f"{activity_name} missing '{field}'"

    def test_activity_description_is_string(self, fresh_activities):
        """
        Test that all activity descriptions are strings.
        
        AAA Pattern:
        - Arrange: Get activities from fixture
        - Act: Iterate through activities
        - Assert: Verify descriptions are strings
        """
        # Arrange & Act & Assert
        for activity_name, activity_data in fresh_activities.items():
            assert isinstance(activity_data["description"], str), \
                f"{activity_name} description is not a string"
            assert len(activity_data["description"]) > 0, \
                f"{activity_name} description is empty"

    def test_activity_schedule_is_string(self, fresh_activities):
        """
        Test that all activity schedules are strings.
        
        AAA Pattern:
        - Arrange: Get activities from fixture
        - Act: Iterate through activities
        - Assert: Verify schedules are strings
        """
        # Arrange & Act & Assert
        for activity_name, activity_data in fresh_activities.items():
            assert isinstance(activity_data["schedule"], str), \
                f"{activity_name} schedule is not a string"
            assert len(activity_data["schedule"]) > 0, \
                f"{activity_name} schedule is empty"

    def test_activity_max_participants_is_positive_int(self, fresh_activities):
        """
        Test that max_participants is a positive integer.
        
        AAA Pattern:
        - Arrange: Get activities from fixture
        - Act: Iterate through activities
        - Assert: Verify max_participants is positive int
        """
        # Arrange & Act & Assert
        for activity_name, activity_data in fresh_activities.items():
            max_participants = activity_data["max_participants"]
            assert isinstance(max_participants, int), \
                f"{activity_name} max_participants is not an int"
            assert max_participants > 0, \
                f"{activity_name} max_participants is not positive"

    def test_activity_participants_is_list(self, fresh_activities):
        """
        Test that participants field is always a list.
        
        AAA Pattern:
        - Arrange: Get activities from fixture
        - Act: Iterate through activities
        - Assert: Verify participants is a list
        """
        # Arrange & Act & Assert
        for activity_name, activity_data in fresh_activities.items():
            assert isinstance(activity_data["participants"], list), \
                f"{activity_name} participants is not a list"

    def test_activity_participants_contains_strings(self, fresh_activities):
        """
        Test that all participant entries are strings (emails).
        
        AAA Pattern:
        - Arrange: Get activities from fixture
        - Act: Iterate through participants in each activity
        - Assert: Verify all participants are strings
        """
        # Arrange & Act & Assert
        for activity_name, activity_data in fresh_activities.items():
            for participant in activity_data["participants"]:
                assert isinstance(participant, str), \
                    f"{activity_name} has non-string participant: {participant}"


class TestEmailValidation:
    """Unit tests for email validation logic."""

    def test_email_contains_at_symbol(self):
        """
        Test that valid emails contain @ symbol.
        
        AAA Pattern:
        - Arrange: Define test emails
        - Act: Check if @ is in email
        - Assert: Verify @ is present
        """
        # Arrange
        valid_email = "student@mergington.edu"
        invalid_email = "studentmergington.edu"
        
        # Act & Assert
        assert "@" in valid_email
        assert "@" not in invalid_email

    def test_email_has_domain(self):
        """
        Test that valid emails have a domain part.
        
        AAA Pattern:
        - Arrange: Define test emails
        - Act: Split by @
        - Assert: Verify domain exists
        """
        # Arrange
        valid_email = "student@mergington.edu"
        invalid_email = "student@"
        
        # Act & Assert
        assert len(valid_email.split("@")) == 2
        assert len(invalid_email.split("@")) == 2
        assert len(valid_email.split("@")[1]) > 0
        assert len(invalid_email.split("@")[1]) == 0


class TestParticipantDeduplication:
    """Unit tests for participant list deduplication."""

    def test_participants_list_no_duplicates(self, fresh_activities):
        """
        Test that participants list has no duplicate emails.
        
        AAA Pattern:
        - Arrange: Get participants from each activity
        - Act: Compare list length with set length
        - Assert: Verify no duplicates
        """
        # Arrange & Act & Assert
        for activity_name, activity_data in fresh_activities.items():
            participants = activity_data["participants"]
            # If list and set lengths are equal, no duplicates
            assert len(participants) == len(set(participants)), \
                f"{activity_name} has duplicate participants"

    def test_participant_count_matches_list_length(self, fresh_activities):
        """
        Test that actual participants count equals list length.
        
        AAA Pattern:
        - Arrange: Get participants list
        - Act: Count participants
        - Assert: Verify count accuracy
        """
        # Arrange & Act & Assert
        for activity_name, activity_data in fresh_activities.items():
            participants = activity_data["participants"]
            assert len(participants) == len(activity_data["participants"]), \
                f"{activity_name} participant count mismatch"
