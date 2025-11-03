"""
Payment Providers

Interfaces and implementations for various payment gateways.
"""

from .base import PaymentProvider
from .registry import payment_registry
from .paypal import paypal_payment_provider
from .razorpay import razorpay_payment_provider

# Register providers
payment_registry.register("paypal", paypal_payment_provider)
payment_registry.register("razorpay", razorpay_payment_provider)

__all__ = ["PaymentProvider", "payment_registry", "paypal_payment_provider", "razorpay_payment_provider"]
