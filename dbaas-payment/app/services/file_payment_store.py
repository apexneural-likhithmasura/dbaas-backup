import os
import json
import threading
from typing import Any, Dict, Optional

from ..core.config import settings


class FilePaymentStore:
    """Simple JSON-based storage for payments and events.

    This is intended for local testing without a database. It is thread-safe
    within a single process via a coarse lock and uses atomic file replace
    to avoid partial writes.
    """

    def __init__(self) -> None:
        self.base_dir = settings.payments_data_dir
        os.makedirs(self.base_dir, exist_ok=True)
        self.payments_path = os.path.join(self.base_dir, "payments.json")
        self.events_path = os.path.join(self.base_dir, "payment_events.jsonl")
        self._lock = threading.Lock()

        if not os.path.exists(self.payments_path):
            with open(self.payments_path, "w", encoding="utf-8") as f:
                f.write("{}")

    def _load_payments(self) -> Dict[str, Any]:
        with open(self.payments_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_payments(self, data: Dict[str, Any]) -> None:
        tmp_path = self.payments_path + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, self.payments_path)

    def record_event_if_new(self, event_id: str, event: Dict[str, Any]) -> bool:
        """Append event to JSONL if not already present. Returns True if new."""
        seen = False
        if os.path.exists(self.events_path):
            with open(self.events_path, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        obj = json.loads(line)
                        if obj.get("id") == event_id:
                            seen = True
                            break
                    except Exception:
                        # Skip malformed lines
                        continue
        if seen:
            return False
        with open(self.events_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")
        return True

    def upsert_paypal_payment(
        self,
        *,
        order_id: Optional[str],
        capture_id: Optional[str],
        status: str,
        amount_minor: Optional[int],
        currency: Optional[str],
        email: Optional[str],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        key = f"paypal:{order_id or ''}:{capture_id or ''}"
        with self._lock:
            data = self._load_payments()
            current = data.get(key, {})
            current.update({
                "provider": "paypal",
                "paypal_order_id": order_id,
                "paypal_capture_id": capture_id,
                "status": status,
                "amount": amount_minor,
                "currency": currency,
                "email": email,
                "metadata": metadata or {},
            })
            data[key] = current
            self._save_payments(data)
            return current

    def get_payment_by_paypal(self, order_id: Optional[str], capture_id: Optional[str]) -> Optional[Dict[str, Any]]:
        key = f"paypal:{order_id or ''}:{capture_id or ''}"
        with self._lock:
            data = self._load_payments()
            return data.get(key)


file_payment_store = FilePaymentStore()


