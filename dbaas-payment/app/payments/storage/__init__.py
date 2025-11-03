"""
Payment Storage

Storage layer for payment data (file-based or database).
"""

from .file_store import payment_storage

__all__ = ["payment_storage"]
