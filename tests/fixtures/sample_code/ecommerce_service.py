"""E-commerce service with inheritance and composition patterns.

This example demonstrates:
- Inheritance: ProductService and OrderService both inherit from BaseService
- Composition: OrderService uses ProductService
- Cross-service calls: OrderService calls ProductService methods

More realistic scenario used in Phase 2 advanced tests.
"""

import logging


class BaseService:
    """Base class for all services.

    Provides common functionality for all service layer classes.
    """

    def __init__(self, repo):
        """Initialize with repository.

        Args:
            repo: Repository instance for data access
        """
        self.repo = repo


class Logger:
    """Simple logger for demonstration.

    Represents an external dependency that services use.
    """

    def info(self, message):
        """Log info message.

        Args:
            message: Message to log
        """
        print(f"[INFO] {message}")

    def error(self, message):
        """Log error message.

        Args:
            message: Message to log
        """
        print(f"[ERROR] {message}")


class ProductService(BaseService):
    """Service for product operations.

    Inherits from BaseService and provides product-specific business logic.
    """

    def __init__(self, repo, logger):
        """Initialize product service.

        Args:
            repo: ProductRepository for data access
            logger: Logger instance
        """
        super().__init__(repo)
        self.logger = logger

    def get_product(self, product_id):
        """Get product by ID.

        Args:
            product_id: The product identifier

        Returns:
            Product data
        """
        return self.repo.find_product(product_id)

    def create_product(self, data):
        """Create a new product.

        Args:
            data: Product data

        Returns:
            Created product data
        """
        self.logger.info("Creating product")
        return self.repo.insert_product(data)

    def update_product(self, product_id, data):
        """Update an existing product.

        Args:
            product_id: The product identifier
            data: Updated product data

        Returns:
            Updated product data
        """
        self.logger.info(f"Updating product {product_id}")
        return self.repo.update_product(product_id, data)

    def get_product_price(self, product_id):
        """Get product price.

        Args:
            product_id: The product identifier

        Returns:
            Product price
        """
        product = self.get_product(product_id)
        return product.get("price", 0) if product else 0


class OrderService(BaseService):
    """Service for order operations.

    Inherits from BaseService and provides order-specific business logic.
    Uses ProductService for product information.
    """

    def __init__(self, repo, product_service):
        """Initialize order service.

        Args:
            repo: OrderRepository for data access
            product_service: ProductService for product lookups
        """
        super().__init__(repo)
        self.product_service = product_service

    def create_order(self, user_id, items):
        """Create a new order.

        This method calls ProductService to validate and get product info.

        Args:
            user_id: The user identifier
            items: List of items to order (each with id and quantity)

        Returns:
            Created order data
        """
        total_price = 0.0

        # Verify all products exist and calculate total
        for item in items:
            product = self.product_service.get_product(item["id"])
            if product:
                price = self.product_service.get_product_price(item["id"])
                total_price += price * item.get("quantity", 1)

        order_data = {
            "user_id": user_id,
            "items": items,
            "total_price": total_price,
        }

        return self.repo.insert_order(order_data)

    def get_order(self, order_id):
        """Get order by ID.

        Args:
            order_id: The order identifier

        Returns:
            Order data
        """
        return self.repo.find_order(order_id)

    def cancel_order(self, order_id):
        """Cancel an order.

        Args:
            order_id: The order identifier

        Returns:
            Success status
        """
        return self.repo.delete_order(order_id)


class NotificationService:
    """Service for sending notifications.

    Independent service that could be used by other services.
    """

    def __init__(self):
        """Initialize notification service."""
        self.logger = Logger()

    def send_email(self, recipient, subject, body):
        """Send email notification.

        Args:
            recipient: Email recipient
            subject: Email subject
            body: Email body

        Returns:
            Success status
        """
        self.logger.info(f"Sending email to {recipient}")
        return True

    def send_sms(self, phone, message):
        """Send SMS notification.

        Args:
            phone: Phone number
            message: SMS message

        Returns:
            Success status
        """
        self.logger.info(f"Sending SMS to {phone}")
        return True


class ProductRepository:
    """Database access for products."""

    def find_product(self, product_id):
        """Query database for product.

        Args:
            product_id: The product identifier

        Returns:
            Product data
        """
        return {"id": product_id, "name": "Product", "price": 99.99}

    def insert_product(self, data):
        """Insert new product into database.

        Args:
            data: Product data

        Returns:
            Inserted product data with ID
        """
        return {**data, "id": 1}

    def update_product(self, product_id, data):
        """Update product in database.

        Args:
            product_id: The product identifier
            data: Updated product data

        Returns:
            Updated product data
        """
        return {**{"id": product_id}, **data}


class OrderRepository:
    """Database access for orders."""

    def insert_order(self, order_data):
        """Insert new order into database.

        Args:
            order_data: Order data

        Returns:
            Inserted order data with ID
        """
        return {**order_data, "id": 1}

    def find_order(self, order_id):
        """Query database for order.

        Args:
            order_id: The order identifier

        Returns:
            Order data
        """
        return {"id": order_id, "user_id": 1, "items": [], "total_price": 0.0}

    def delete_order(self, order_id):
        """Delete order from database.

        Args:
            order_id: The order identifier

        Returns:
            Success status
        """
        return True
