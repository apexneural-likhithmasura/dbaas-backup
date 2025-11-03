from typing import Dict, Any
import base64
import json
import httpx
import time

from ..core.config import settings


class PayPalProvider:
    """HTTP client for PayPal REST API (no SDK dependency)."""

    def __init__(self) -> None:
        self.base_url = (
            "https://api-m.sandbox.paypal.com" if settings.paypal_env.lower() == "sandbox" else "https://api-m.paypal.com"
        )
        self.client_id = settings.paypal_client_id
        self.client_secret = settings.paypal_client_secret

    def _get_access_token(self) -> str:
        auth = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
        headers = {"Authorization": f"Basic {auth}", "Content-Type": "application/x-www-form-urlencoded"}
        data = {"grant_type": "client_credentials"}
        timeout = httpx.Timeout(connect=15, read=45, write=30, pool=30)
        last_exc: Exception | None = None
        for attempt in range(3):
            try:
                with httpx.Client(timeout=timeout) as client:
                    resp = client.post(f"{self.base_url}/v1/oauth2/token", headers=headers, data=data)
                    resp.raise_for_status()
                    return resp.json()["access_token"]
            except Exception as exc:  # retry on transient network errors
                last_exc = exc
                time.sleep(0.5 * (attempt + 1))
        # If all retries failed, raise the last exception
        raise last_exc  # type: ignore[misc]

    def create_order(self, *, product_code: str, quantity: int, idem_key: str) -> Dict[str, Any]:
        # Demo pricing: 1.00 unit in configured currency per quantity
        unit_amount = 1.00
        total_value = f"{unit_amount * max(1, quantity):.2f}"
        currency = settings.payments_currency or "USD"
        return_url = (settings.paypal_return_url or "").strip()
        cancel_url = (settings.paypal_cancel_url or "").strip()

        # Fail fast: without a proper return URL, PayPal will not redirect back
        if not return_url or not (return_url.startswith("http://") or return_url.startswith("https://")):
            raise ValueError(
                "PAYPAL_RETURN_URL is not configured or invalid. Set PAYPAL_RETURN_URL to a full URL, e.g. "
                "http://localhost:8000/dbas/api/payments/return"
            )
        # If cancel URL missing, fall back to return URL
        if not cancel_url:
            cancel_url = return_url
        token = self._get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "PayPal-Request-Id": idem_key,
            "Prefer": "return=representation",
        }
        body = {
            "intent": "CAPTURE",
            "purchase_units": [{
                "amount": {"currency_code": currency, "value": total_value},
                "custom_id": product_code,
            }],
            "application_context": {
                "brand_name": settings.app_name,
                "landing_page": "BILLING",
                "shipping_preference": "NO_SHIPPING",
                "user_action": "PAY_NOW",
                "return_url": return_url,
                "cancel_url": cancel_url,
            },
        }
        timeout = httpx.Timeout(connect=15, read=60, write=30, pool=30)
        last_exc: Exception | None = None
        for attempt in range(3):
            try:
                with httpx.Client(timeout=timeout) as client:
                    resp = client.post(f"{self.base_url}/v2/checkout/orders", headers=headers, json=body)
                    resp.raise_for_status()
                    data = resp.json()
                    approve_url = None
                    for link in data.get("links", []) or []:
                        if link.get("rel") == "approve":
                            approve_url = link.get("href")
                            break
                    return {"order_id": data.get("id"), "approve_url": approve_url}
            except Exception as exc:
                last_exc = exc
                time.sleep(0.5 * (attempt + 1))
        raise last_exc  # type: ignore[misc]

    def capture(self, order_id: str) -> Dict[str, Any]:
        token = self._get_access_token()
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        timeout = httpx.Timeout(connect=15, read=60, write=30, pool=30)
        last_exc: Exception | None = None
        for attempt in range(3):
            try:
                with httpx.Client(timeout=timeout) as client:
                    resp = client.post(f"{self.base_url}/v2/checkout/orders/{order_id}/capture", headers=headers)
                    resp.raise_for_status()
                    data = resp.json()
                    pu = (data.get("purchase_units") or [{}])[0]
                    cap = ((pu.get("payments") or {}).get("captures") or [{}])[0]
                    return {
                        "capture_id": cap.get("id"),
                        "status": cap.get("status"),
                        "amount": cap.get("amount", {}),
                    }
            except Exception as exc:
                last_exc = exc
                time.sleep(0.5 * (attempt + 1))
        raise last_exc  # type: ignore[misc]

    def verify_webhook(self, headers: Dict[str, str], body: bytes) -> Dict[str, Any]:
        token = self._get_access_token()
        verify_payload = {
            "transmission_id": headers.get("paypal-transmission-id"),
            "transmission_time": headers.get("paypal-transmission-time"),
            "cert_url": headers.get("paypal-cert-url"),
            "auth_algo": headers.get("paypal-auth-algo"),
            "transmission_sig": headers.get("paypal-transmission-sig"),
            "webhook_id": settings.paypal_webhook_id,
            "webhook_event": json.loads(body.decode() or "{}"),
        }
        api_headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        with httpx.Client(timeout=30) as client:
            resp = client.post(
                f"{self.base_url}/v1/notifications/verify-webhook-signature",
                headers=api_headers,
                json=verify_payload,
            )
            resp.raise_for_status()
            if resp.json().get("verification_status") != "SUCCESS":
                raise ValueError("Invalid webhook signature")
        return verify_payload["webhook_event"]


paypal_provider = PayPalProvider()


