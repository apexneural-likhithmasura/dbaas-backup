"""
PayPal Payment Provider

Wraps the existing PayPal implementation to conform to PaymentProvider interface.
"""

from typing import Dict, Any
from .base import PaymentProvider
from ...services.paypal_provider import paypal_provider as _paypal_provider


class PayPalProvider(PaymentProvider):
    """PayPal payment provider implementation."""
    
    def __init__(self) -> None:
        self._provider = _paypal_provider
    
    def create_order(
        self, 
        *, 
        product_code: str, 
        quantity: int, 
        idem_key: str
    ) -> Dict[str, Any]:
        """Create PayPal order."""
        return self._provider.create_order(
            product_code=product_code,
            quantity=quantity,
            idem_key=idem_key
        )
    
    def capture(self, order_id: str) -> Dict[str, Any]:
        """Capture PayPal payment."""
        return self._provider.capture(order_id)
    
    def verify_webhook(self, headers: Dict[str, str], body: bytes) -> Dict[str, Any]:
        """Verify PayPal webhook."""
        return self._provider.verify_webhook(headers, body)


# Singleton instance
paypal_payment_provider = PayPalProvider()
