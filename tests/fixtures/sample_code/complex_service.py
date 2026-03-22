"""Complex service with advanced patterns.

This example demonstrates:
- Abstract base classes (though using Python convention)
- Multiple service dependencies
- Nested service calls
- Static methods and class methods
- Exception handling
- Property methods

Advanced patterns used in Phase 2 comprehensive tests.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict


class CacheManager:
    """Simple cache manager for demonstration."""

    def __init__(self):
        """Initialize cache."""
        self.cache = {}

    def get(self, key):
        """Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None
        """
        return self.cache.get(key)

    def set(self, key, value):
        """Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
        """
        self.cache[key] = value


class BaseRepository(ABC):
    """Abstract base repository.

    Defines interface for all repositories.
    """

    def __init__(self):
        """Initialize repository."""
        self.cache = CacheManager()

    @abstractmethod
    def find_by_id(self, entity_id):
        """Find entity by ID.

        Args:
            entity_id: The entity identifier

        Returns:
            Entity data or None
        """
        pass

    @staticmethod
    def validate_id(entity_id):
        """Static method to validate ID format.

        Args:
            entity_id: The entity identifier

        Returns:
            True if valid, False otherwise
        """
        return isinstance(entity_id, (int, str)) and len(str(entity_id)) > 0


class AnalyticsService:
    """Service for tracking analytics events."""

    def __init__(self):
        """Initialize analytics service."""
        self.events = []

    def track_event(self, event_name, data):
        """Track an analytics event.

        Args:
            event_name: Name of the event
            data: Event data
        """
        self.events.append({"name": event_name, "data": data})

    def get_event_count(self):
        """Get total number of tracked events.

        Returns:
            Number of events
        """
        return len(self.events)


class UserManagementService:
    """Complex user management service.

    Demonstrates multiple dependencies and nested calls.
    """

    def __init__(self, user_repo, notification_service, analytics):
        """Initialize user management service.

        Args:
            user_repo: User repository
            notification_service: Notification service
            analytics: Analytics service
        """
        self.user_repo = user_repo
        self.notification_service = notification_service
        self.analytics = analytics
        self._initialized = True

    @property
    def is_ready(self):
        """Check if service is ready.

        Returns:
            True if initialized
        """
        return self._initialized

    def create_user(self, user_data):
        """Create a new user.

        Args:
            user_data: User data

        Returns:
            Created user
        """
        # Validate input
        if not user_data.get("email"):
            raise ValueError("Email is required")

        # Create user
        user = self.user_repo.create(user_data)

        # Send notification
        self.notification_service.send_email(
            user["email"], "Welcome!", "Account created successfully"
        )

        # Track event
        self.analytics.track_event("user_created", {"user_id": user["id"]})

        return user

    def update_user(self, user_id, updates):
        """Update user information.

        Args:
            user_id: User identifier
            updates: Updated fields

        Returns:
            Updated user
        """
        # Validate ID
        if not BaseRepository.validate_id(user_id):
            raise ValueError("Invalid user ID")

        # Update user
        user = self.user_repo.update(user_id, updates)

        # Notify
        if "email" in updates:
            self.notification_service.send_email(
                updates["email"], "Profile Updated", "Your profile was updated"
            )

        # Track
        self.analytics.track_event("user_updated", {"user_id": user_id})

        return user

    def delete_user(self, user_id):
        """Delete a user.

        Args:
            user_id: User identifier

        Returns:
            Success status
        """
        # Validate
        if not BaseRepository.validate_id(user_id):
            raise ValueError("Invalid user ID")

        # Get user before deletion for notification
        user = self.user_repo.find_by_id(user_id)

        # Delete
        success = self.user_repo.delete(user_id)

        # Notify
        if success and user:
            self.notification_service.send_email(
                user.get("email", ""), "Account Deleted", "Your account was deleted"
            )

        # Track
        self.analytics.track_event("user_deleted", {"user_id": user_id})

        return success

    def get_users(self):
        """Get all users.

        Returns:
            List of users
        """
        # Get from repo
        users = self.user_repo.find_all()

        # Track
        self.analytics.track_event("users_listed", {"count": len(users)})

        return users

    @classmethod
    def create_default_instance(cls, analytics):
        """Factory method to create default instance.

        Args:
            analytics: Analytics service

        Returns:
            Configured service instance
        """
        repo = UserRepository()
        notification = NotificationService()
        return cls(repo, notification, analytics)


class NotificationService:
    """Service for notifications."""

    def __init__(self):
        """Initialize notification service."""
        self.sent_emails = []
        self.sent_smss = []

    def send_email(self, recipient, subject, body):
        """Send email.

        Args:
            recipient: Email recipient
            subject: Subject
            body: Email body

        Returns:
            Success status
        """
        self.sent_emails.append({"to": recipient, "subject": subject})
        return True

    def send_sms(self, phone, message):
        """Send SMS.

        Args:
            phone: Phone number
            message: Message

        Returns:
            Success status
        """
        self.sent_smss.append({"to": phone, "message": message})
        return True


class UserRepository(BaseRepository):
    """User repository implementation."""

    def __init__(self):
        """Initialize user repository."""
        super().__init__()
        self.users = {}
        self.id_counter = 0

    def find_by_id(self, user_id):
        """Find user by ID.

        Args:
            user_id: User identifier

        Returns:
            User data or None
        """
        # Check cache first
        cached = self.cache.get(f"user_{user_id}")
        if cached:
            return cached

        # Get from storage
        user = self.users.get(user_id)

        # Cache result
        if user:
            self.cache.set(f"user_{user_id}", user)

        return user

    def create(self, user_data):
        """Create new user.

        Args:
            user_data: User data

        Returns:
            Created user
        """
        self.id_counter += 1
        user = {**user_data, "id": self.id_counter}
        self.users[self.id_counter] = user
        return user

    def update(self, user_id, updates):
        """Update user.

        Args:
            user_id: User identifier
            updates: Updates to apply

        Returns:
            Updated user or None
        """
        if user_id not in self.users:
            return None

        self.users[user_id].update(updates)
        return self.users[user_id]

    def delete(self, user_id):
        """Delete user.

        Args:
            user_id: User identifier

        Returns:
            Success status
        """
        if user_id in self.users:
            del self.users[user_id]
            return True
        return False

    def find_all(self):
        """Get all users.

        Returns:
            List of all users
        """
        return list(self.users.values())


class PurchaseHistoryService:
    """Service for purchase history.

    Shows how a service might call multiple other services.
    """

    def __init__(self, user_service, order_service):
        """Initialize purchase history service.

        Args:
            user_service: User management service
            order_service: Order service
        """
        self.user_service = user_service
        self.order_service = order_service

    def get_user_purchase_history(self, user_id):
        """Get purchase history for user.

        Args:
            user_id: User identifier

        Returns:
            Purchase history
        """
        # Get user
        user = self.user_service.user_repo.find_by_id(user_id)

        if not user:
            return None

        # Get user's orders
        orders = self.order_service.get_user_orders(user_id)

        return {
            "user": user,
            "orders": orders,
            "total_spent": sum(o.get("total_price", 0) for o in orders),
        }


class OrderService:
    """Order service for demonstration."""

    def __init__(self):
        """Initialize order service."""
        self.orders = {}

    def get_user_orders(self, user_id):
        """Get all orders for a user.

        Args:
            user_id: User identifier

        Returns:
            List of orders
        """
        return [o for o in self.orders.values() if o.get("user_id") == user_id]
