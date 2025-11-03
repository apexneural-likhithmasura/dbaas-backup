"""
Razorpay Payment Provider

HTTP client for Razorpay REST API.
"""

from typing import Dict, Any
import base64
import json
import httpx
import hmac
import hashlib

from .base import PaymentProvider
from ...core.config import settings


class RazorpayProvider(PaymentProvider):
    """HTTP client for Razorpay REST API (no SDK dependency)."""
    
    def __init__(self) -> None:
        self.base_url = "https://api.razorpay.com/v1"
        self.key_id = settings.razorpay_key_id
        self.key_secret = settings.razorpay_key_secret
        self.webhook_secret = settings.razorpay_webhook_secret
    
    def _get_auth_header(self) -> str:
        """Generate Basic Auth header."""
        auth_string = f"{self.key_id}:{self.key_secret}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        return f"Basic {auth_b64}"
    
    def create_order(
        self, 
        *, 
        product_code: str, 
        quantity: int, 
        idem_key: str
    ) -> Dict[str, Any]:
        """
        Create Razorpay order.
        
        Returns:
            Dict with order_id and approve_url (checkout URL)
        """
        # Demo pricing: 100.00 INR per unit
        unit_amount = 100.00
        total_value = int(unit_amount * max(1, quantity) * 100)  # Convert to paise (minor units)
        currency = settings.payments_currency or "INR"
        
        headers = {
            "Authorization": self._get_auth_header(),
            "Content-Type": "application/json",
        }
        
        body = {
            "amount": total_value,
            "currency": currency,
            "receipt": idem_key,
            "notes": {
                "product_code": product_code,
                "quantity": str(quantity)
            }
        }
        
        timeout = httpx.Timeout(connect=15, read=60, write=30, pool=30)
        
        try:
            with httpx.Client(timeout=timeout) as client:
                resp = client.post(
                    f"{self.base_url}/orders",
                    headers=headers,
                    json=body
                )
                resp.raise_for_status()
                data = resp.json()
                
                # Razorpay doesn't provide a direct checkout URL like PayPal
                # Frontend needs to use Razorpay Checkout with order_id
                return {
                    "order_id": data.get("id"),
                    "approve_url": None,  # Frontend handles checkout
                    "amount": data.get("amount"),
                    "currency": data.get("currency"),
                    "status": data.get("status")
                }
        except httpx.HTTPStatusError as e:
            raise ValueError(f"Razorpay API error: {e.response.text}") from e
        except Exception as e:
            raise ValueError(f"Failed to create Razorpay order: {str(e)}") from e
    
    def capture(self, order_id: str) -> Dict[str, Any]:
        """
        Razorpay doesn't have a separate capture endpoint for orders.
        Payment is auto-captured on successful checkout.
        This method fetches order details to verify status.
        """
        headers = {
            "Authorization": self._get_auth_header(),
            "Content-Type": "application/json",
        }
        
        timeout = httpx.Timeout(connect=15, read=60, write=30, pool=30)
        
        try:
            with httpx.Client(timeout=timeout) as client:
                resp = client.get(
                    f"{self.base_url}/orders/{order_id}",
                    headers=headers
                )
                resp.raise_for_status()
                data = resp.json()
                
                return {
                    "capture_id": None,  # Razorpay uses payment_id, not capture_id
                    "status": data.get("status"),
                    "amount": {
                        "value": str(data.get("amount", 0) / 100),  # Convert paise to rupees
                        "currency_code": data.get("currency")
                    }
                }
        except httpx.HTTPStatusError as e:
            raise ValueError(f"Razorpay API error: {e.response.text}") from e
        except Exception as e:
            raise ValueError(f"Failed to fetch Razorpay order: {str(e)}") from e
    
    def verify_payment_signature(
        self, 
        order_id: str, 
        payment_id: str, 
        signature: str
    ) -> bool:
        """
        Verify Razorpay payment signature.
        
        Args:
            order_id: Razorpay order ID
            payment_id: Razorpay payment ID
            signature: Signature from Razorpay
            
        Returns:
            True if signature is valid
        """
        message = f"{order_id}|{payment_id}"
        expected_signature = hmac.new(
            self.key_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected_signature, signature)
    
    def verify_webhook(self, headers: Dict[str, str], body: bytes) -> Dict[str, Any]:
        """
        Verify Razorpay webhook signature.
        
        Args:
            headers: Request headers
            body: Raw request body
            
        Returns:
            Parsed and verified event data
        """
        signature = headers.get("x-razorpay-signature", "")
        
        if not self.webhook_secret:
            raise ValueError("RAZORPAY_WEBHOOK_SECRET not configured")
        
        # Verify webhook signature
        expected_signature = hmac.new(
            self.webhook_secret.encode('utf-8'),
            body,
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(expected_signature, signature):
            raise ValueError("Invalid Razorpay webhook signature")
        
        # Parse and return event
        return json.loads(body.decode('utf-8'))


# Singleton instance
razorpay_payment_provider = RazorpayProvider()
