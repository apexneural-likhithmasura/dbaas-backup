"""
Payment Routes - Multi-Provider Support

Unified endpoints supporting PayPal, Razorpay, and future providers.
"""

import logging
import json
from typing import Optional

from fastapi import APIRouter, HTTPException, Request, status, Query
from fastapi.responses import HTMLResponse
from starlette.responses import RedirectResponse

from ..models.response_models import AdminResponse
from ..middleware.rbac_middleware import rate_limit_middleware
from ..core.config import settings
from .providers import payment_registry
from .storage import payment_storage


logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/checkout-session", response_model=AdminResponse, summary="Create Payment Order")
async def create_checkout_session(request: Request, body: dict):
    """
    Create payment order with specified provider.
    
    Request body:
        - provider: "paypal" or "razorpay" (default: "paypal")
        - product_code: Product identifier
        - quantity: Quantity of items
        - idempotency_key: Unique key for idempotency
    """
    await rate_limit_middleware.check_rate_limit(request)
    
    provider_name: str = str(body.get("provider", "paypal")).lower()
    product_code: str = str(body.get("product_code", "test"))
    quantity: int = int(body.get("quantity", 1))
    idem_key: str = str(body.get("idempotency_key", "test-idem-key"))
    
    try:
        # Get provider from registry
        provider = payment_registry.get(provider_name)
        
        # Create order
        order = provider.create_order(
            product_code=product_code,
            quantity=quantity,
            idem_key=idem_key
        )
        
        # Store initial status
        payment_storage.upsert_payment(
            provider=provider_name,
            order_id=order.get("order_id"),
            capture_id=None,
            status="created",
            amount_minor=order.get("amount"),
            currency=order.get("currency", settings.payments_currency),
            email=None,
            metadata={"product_code": product_code}
        )
        
        return AdminResponse(
            status="success",
            message=f"{provider_name.title()} order created",
            data={**order, "provider": provider_name}
        )
    except ValueError as e:
        logger.error(f"Provider error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.exception(f"Failed to create {provider_name} order")
        raise HTTPException(status_code=500, detail=f"Failed to create order: {str(e)}") from e


@router.post("/capture/{provider}/{order_id}", response_model=AdminResponse, summary="Capture Payment")
async def capture_payment(request: Request, provider: str, order_id: str):
    """Capture/finalize payment for specified provider."""
    await rate_limit_middleware.check_rate_limit(request)
    
    provider_name = provider.lower()
    
    try:
        # Get provider from registry
        payment_provider = payment_registry.get(provider_name)
        
        # Capture payment
        result = payment_provider.capture(order_id)
        amount = result.get("amount", {})
        
        try:
            minor = int(round(float(amount.get("value", 0))))
        except Exception:
            minor = None
        
        # Store capture result
        payment_storage.upsert_payment(
            provider=provider_name,
            order_id=order_id,
            capture_id=result.get("capture_id"),
            status=result.get("status", "succeeded"),
            amount_minor=minor,
            currency=amount.get("currency_code"),
            email=None,
            metadata=result
        )
        
        return AdminResponse(
            status="success",
            message=f"{provider_name.title()} payment captured",
            data={**result, "provider": provider_name}
        )
    except ValueError as e:
        logger.error(f"Provider error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.exception(f"Failed to capture {provider_name} payment")
        raise HTTPException(status_code=500, detail=f"Failed to capture payment: {str(e)}") from e


@router.post("/webhook/paypal", status_code=status.HTTP_200_OK, summary="PayPal Webhook")
async def paypal_webhook(request: Request):
    """PayPal webhook receiver."""
    body = await request.body()
    headers = dict(request.headers)
    
    try:
        provider = payment_registry.get("paypal")
        event = provider.verify_webhook(headers, body)
    except Exception as e:
        logger.error(f"PayPal webhook verification failed: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid signature") from e

    event_id = event.get("id")
    if not event_id:
        logger.warning("Webhook event missing id, skipping dedup check")
        return {"received": True}
    
    if not payment_storage.record_event(str(event_id), event):
        return {"received": True}

    event_type = event.get("event_type")
    resource = event.get("resource", {})
    
    try:
        if event_type == "PAYMENT.CAPTURE.COMPLETED":
            cap_id = resource.get("id")
            amt = resource.get("amount", {})
            currency = amt.get("currency_code")
            try:
                minor = int(round(float(amt.get("value", 0))))
            except Exception:
                minor = None
            related = (resource.get("supplementary_data", {}).get("related_ids", {}) or {})
            order_id = related.get("order_id")
            payment_storage.upsert_payment(
                provider="paypal",
                order_id=order_id,
                capture_id=cap_id,
                status="succeeded",
                amount_minor=minor,
                currency=currency,
                email=None,
                metadata={"event_id": event_id}
            )
        elif event_type == "CHECKOUT.ORDER.APPROVED":
            order_id = resource.get("id")
            payment_storage.upsert_payment(
                provider="paypal",
                order_id=order_id,
                capture_id=None,
                status="approved",
                amount_minor=None,
                currency=None,
                email=None,
                metadata={"event_id": event_id}
            )
        elif event_type in ("PAYMENT.CAPTURE.DENIED", "PAYMENT.CAPTURE.REFUNDED"):
            new_status = "refunded" if "REFUNDED" in event_type else "failed"
            cap_id = resource.get("id")
            related = (resource.get("supplementary_data", {}).get("related_ids", {}) or {})
            order_id = related.get("order_id") or None
            payment_storage.upsert_payment(
                provider="paypal",
                order_id=order_id,
                capture_id=cap_id,
                status=new_status,
                amount_minor=None,
                currency=None,
                email=None,
                metadata={"event_id": event_id}
            )
    except Exception:
        logger.exception("Webhook processing error")
        return {"received": True}

    return {"received": True}


@router.post("/webhook/razorpay", status_code=status.HTTP_200_OK, summary="Razorpay Webhook")
async def razorpay_webhook(request: Request):
    """Razorpay webhook receiver."""
    body = await request.body()
    headers = dict(request.headers)
    
    try:
        provider = payment_registry.get("razorpay")
        event = provider.verify_webhook(headers, body)
    except Exception as e:
        logger.error(f"Razorpay webhook verification failed: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid signature") from e

    event_id = event.get("event", {}).get("id")
    if not event_id:
        logger.warning("Razorpay webhook event missing id")
        return {"received": True}
    
    if not payment_storage.record_event(str(event_id), event):
        return {"received": True}

    event_type = event.get("event")
    payload = event.get("payload", {}).get("payment", {}).get("entity", {})
    
    try:
        if event_type == "payment.captured":
            payment_id = payload.get("id")
            order_id = payload.get("order_id")
            amount = payload.get("amount", 0)
            currency = payload.get("currency")
            
            payment_storage.upsert_payment(
                provider="razorpay",
                order_id=order_id,
                capture_id=payment_id,
                status="succeeded",
                amount_minor=amount,
                currency=currency,
                email=payload.get("email"),
                metadata={"event_id": event_id, "payload": payload}
            )
        elif event_type == "payment.failed":
            payment_id = payload.get("id")
            order_id = payload.get("order_id")
            
            payment_storage.upsert_payment(
                provider="razorpay",
                order_id=order_id,
                capture_id=payment_id,
                status="failed",
                amount_minor=None,
                currency=None,
                email=None,
                metadata={"event_id": event_id, "payload": payload}
            )
    except Exception:
        logger.exception("Razorpay webhook processing error")
        return {"received": True}

    return {"received": True}


@router.get("/return", summary="PayPal return - auto-capture and redirect", response_class=HTMLResponse, include_in_schema=True)
async def paypal_return(token: str = Query(..., description="PayPal order_id from return URL")):
    """Handle PayPal return after user approves payment."""
    try:
        provider = payment_registry.get("paypal")
        result = provider.capture(token)
        amount = result.get("amount", {})
        
        try:
            minor = int(round(float(amount.get("value", 0))))
        except Exception:
            minor = None
        
        payment_storage.upsert_payment(
            provider="paypal",
            order_id=token,
            capture_id=result.get("capture_id"),
            status=result.get("status", "succeeded"),
            amount_minor=minor,
            currency=amount.get("currency_code"),
            email=None,
            metadata=result
        )
        
        if settings.paypal_success_redirect:
            return RedirectResponse(url=settings.paypal_success_redirect, status_code=303)
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Payment Successful</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                }}
                .container {{
                    background: white;
                    padding: 50px;
                    border-radius: 10px;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                    text-align: center;
                    max-width: 500px;
                }}
                .success-icon {{ font-size: 80px; color: #28a745; }}
                h1 {{ color: #333; margin: 20px 0; }}
                p {{ color: #666; font-size: 18px; margin: 20px 0; }}
                .details {{ background: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0; text-align: left; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="success-icon">✅</div>
                <h1>Payment Successful!</h1>
                <p>Your payment has been processed successfully.</p>
                <div class="details">
                    <p><strong>Order ID:</strong> {token}</p>
                    <p><strong>Capture ID:</strong> {result.get('capture_id', 'N/A')}</p>
                    <p><strong>Amount:</strong> {amount.get('value', 'N/A')} {amount.get('currency_code', '')}</p>
                    <p><strong>Status:</strong> {result.get('status', 'N/A')}</p>
                </div>
                <p>Thank you for your purchase!</p>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        logger.exception("Payment capture failed")
        if settings.paypal_failure_redirect:
            return RedirectResponse(url=settings.paypal_failure_redirect, status_code=303)
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Payment Failed</title>
            <style>
                body {{ font-family: Arial, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }}
                .container {{ background: white; padding: 50px; border-radius: 10px; text-align: center; max-width: 500px; }}
                .error-icon {{ font-size: 80px; color: #dc3545; }}
                h1 {{ color: #333; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="error-icon">❌</div>
                <h1>Payment Failed</h1>
                <p>Error: {str(e)}</p>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content, status_code=500)


@router.get("/cancel", summary="Payment cancellation handler", response_class=HTMLResponse, include_in_schema=True)
async def payment_cancel(token: str = Query(None, description="Payment order_id")):
    """Handle payment cancellation."""
    if token:
        payment_storage.upsert_payment(
            provider="paypal",  # Assumes PayPal for now
            order_id=token,
            capture_id=None,
            status="cancelled",
            amount_minor=None,
            currency=None,
            email=None,
            metadata={"cancelled_at": "user_action"}
        )
    
    if settings.paypal_failure_redirect:
        return RedirectResponse(url=settings.paypal_failure_redirect, status_code=303)
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Payment Cancelled</title>
        <style>
            body { font-family: Arial, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
            .container { background: white; padding: 50px; border-radius: 10px; text-align: center; max-width: 500px; }
            .cancel-icon { font-size: 80px; color: #ffc107; }
            h1 { color: #333; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="cancel-icon">⚠️</div>
            <h1>Payment Cancelled</h1>
            <p>You have cancelled the payment process.</p>
            <p>No charges have been made to your account.</p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@router.get("/test/{provider}/{order_id}", response_model=AdminResponse, summary="Read stored payment state (test)")
async def get_test_payment(provider: str, order_id: str):
    """Test endpoint to retrieve payment by provider and order ID."""
    try:
        data = payment_storage.get_payment(provider.lower(), order_id, None)
        return AdminResponse(status="success", message="OK", data=data or {})
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
