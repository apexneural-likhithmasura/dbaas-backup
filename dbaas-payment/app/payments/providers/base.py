"""
Base Payment Provider Interface

Defines the contract that all payment providers must implement.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class PaymentProvider(ABC):
    """Abstract base class for payment providers."""
    
    @abstractmethod
    def create_order(
        self, 
        *, 
        product_code: str, 
        quantity: int, 
        idem_key: str
    ) -> Dict[str, Any]:
        """
        Create a payment order.
        
        Args:
            product_code: Product identifier
            quantity: Quantity of items
            idem_key: Idempotency key
            
        Returns:
            Dict containing order_id and approve_url (or equivalent)
        """
        pass
    
    @abstractmethod
    def capture(self, order_id: str) -> Dict[str, Any]:
        """
        Capture/finalize a payment.
        
        Args:
            order_id: The order/payment identifier
            
        Returns:
            Dict containing capture_id, status, amount
        """
        pass
    
    @abstractmethod
    def verify_webhook(self, headers: Dict[str, str], body: bytes) -> Dict[str, Any]:
        """
        Verify and parse webhook payload.
        
        Args:
            headers: Request headers
            body: Raw request body
            
        Returns:
            Parsed and verified event data
        """
        pass
