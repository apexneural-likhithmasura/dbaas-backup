"""
Payment Provider Registry

Central registry for managing multiple payment providers.
"""

from typing import Dict
from .base import PaymentProvider


class PaymentRegistry:
    """Registry for payment providers."""
    
    def __init__(self) -> None:
        self._providers: Dict[str, PaymentProvider] = {}
    
    def register(self, name: str, provider: PaymentProvider) -> None:
        """Register a payment provider."""
        self._providers[name.lower()] = provider
    
    def get(self, name: str) -> PaymentProvider:
        """Get a payment provider by name."""
        provider = self._providers.get(name.lower())
        if not provider:
            raise ValueError(f"Payment provider '{name}' not found. Available: {list(self._providers.keys())}")
        return provider
    
    def list_providers(self) -> list:
        """List all registered provider names."""
        return list(self._providers.keys())


# Global registry instance
payment_registry = PaymentRegistry()
