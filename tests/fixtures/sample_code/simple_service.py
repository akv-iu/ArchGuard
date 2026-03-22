"""Simple service with 3 classes and basic method calls.

This is a minimal 3-layer architecture example:
- UserController (UI Layer)
- UserService (Service Layer)
- UserRepository (Data Layer)

Used in Phase 2 tests to verify code extraction.
"""


class UserController:
    """UI Layer - handles user requests.

    This class represents the presentation layer that receives
    user requests and delegates to the service layer.
    """

    def __init__(self, service):
        """Initialize controller with service dependency.

        Args:
            service: UserService instance to delegate to
        """
        self.service = service

    def get_user(self, user_id):
        """Get user by ID.

        Args:
            user_id: The user identifier

        Returns:
            User data or None
        """
        return self.service.fetch_user(user_id)

    def update_user(self, user_id, data):
        """Update user data.

        Args:
            user_id: The user identifier
            data: Updated user data

        Returns:
            Success status
        """
        return self.service.save_user(user_id, data)

    def delete_user(self, user_id):
        """Delete a user.

        Args:
            user_id: The user identifier

        Returns:
            Success status
        """
        return self.service.delete_user(user_id)


class UserService:
    """Service Layer - business logic.

    This class contains the business logic for user management.
    It acts as an intermediary between the controller and repository layers.
    """

    def __init__(self, repo):
        """Initialize service with repository dependency.

        Args:
            repo: UserRepository instance for data access
        """
        self.repo = repo

    def fetch_user(self, user_id):
        """Fetch user from repository.

        Args:
            user_id: The user identifier

        Returns:
            User data from repository
        """
        return self.repo.find_by_id(user_id)

    def save_user(self, user_id, data):
        """Save user to repository.

        Args:
            user_id: The user identifier
            data: User data to save

        Returns:
            Updated user data
        """
        return self.repo.update(user_id, data)

    def delete_user(self, user_id):
        """Delete user from repository.

        Args:
            user_id: The user identifier

        Returns:
            Success status
        """
        return self.repo.delete(user_id)


class UserRepository:
    """Data Layer - database access.

    This class handles all database operations for users.
    It provides a clean interface for data persistence.
    """

    def find_by_id(self, user_id):
        """Query database for user by ID.

        Args:
            user_id: The user identifier

        Returns:
            User data dictionary or None
        """
        return {"id": user_id, "name": f"User {user_id}"}

    def update(self, user_id, data):
        """Update user record in database.

        Args:
            user_id: The user identifier
            data: Data to update

        Returns:
            Updated user data
        """
        return {**{"id": user_id}, **data}

    def delete(self, user_id):
        """Delete user record from database.

        Args:
            user_id: The user identifier

        Returns:
            Success status (True)
        """
        return True
