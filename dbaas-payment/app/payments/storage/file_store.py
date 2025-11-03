"""
File-based Payment Storage

Wrapper around existing FilePaymentStore for unified interface.
"""

from typing import Dict, Any, Optional
from ...services.file_payment_store import file_payment_store


class PaymentStorage:
    """Unified payment storage interface."""
    
    def __init__(self) -> None:
        self._store = file_payment_store
    
    def upsert_payment(
        self,
        *,
        provider: str,
        order_id: Optional[str],
        capture_id: Optional[str],
        status: str,
        amount_minor: Optional[int],
        currency: Optional[str],
        email: Optional[str],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Store or update payment record.
        
        Args:
            provider: Payment provider name (paypal, razorpay)
            order_id: Provider order ID
            capture_id: Provider capture/payment ID
            status: Payment status
            amount_minor: Amount in minor units (cents/paise)
            currency: Currency code
            email: Customer email
            metadata: Additional metadata
            
        Returns:
            Stored payment data
        """
        if provider == "paypal":
            return self._store.upsert_paypal_payment(
                order_id=order_id,
                capture_id=capture_id,
                status=status,
                amount_minor=amount_minor,
                currency=currency,
                email=email,
                metadata=metadata or {}
            )
        elif provider == "razorpay":
            # Use same storage mechanism with provider prefix
            key = f"razorpay:{order_id or ''}:{capture_id or ''}"
            with self._store._lock:
                data = self._store._load_payments()
                current = data.get(key, {})
                current.update({
                    "provider": "razorpay",
                    "razorpay_order_id": order_id,
                    "razorpay_payment_id": capture_id,
                    "status": status,
                    "amount": amount_minor,
                    "currency": currency,
                    "email": email,
                    "metadata": metadata or {},
                })
                data[key] = current
                self._store._save_payments(data)
                return current
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def get_payment(
        self, 
        provider: str, 
        order_id: Optional[str], 
        capture_id: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        """Retrieve payment by provider and IDs."""
        if provider == "paypal":
            return self._store.get_payment_by_paypal(order_id, capture_id)
        elif provider == "razorpay":
            key = f"razorpay:{order_id or ''}:{capture_id or ''}"
            with self._store._lock:
                data = self._store._load_payments()
                return data.get(key)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def record_event(self, event_id: str, event: Dict[str, Any]) -> bool:
        """Record webhook event if new."""
        return self._store.record_event_if_new(event_id, event)


# Singleton instance
payment_storage = PaymentStorage()
