import sys
import json
import traceback

from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.services.paypal_provider import PayPalProvider  # noqa: E402
from app.core.config import settings  # noqa: E402


def main() -> None:
    info = {
        "paypal_env": settings.paypal_env,
        "client_id_present": bool(settings.paypal_client_id),
        "client_secret_present": bool(settings.paypal_client_secret),
    }
    print(json.dumps({"config": info}))
    try:
        token = PayPalProvider()._get_access_token()
        print(json.dumps({"token_ok": bool(token)}))
    except Exception as e:  # pragma: no cover
        print(json.dumps({"token_error": f"{type(e).__name__}: {e}"}))
        traceback.print_exc()


if __name__ == "__main__":
    main()


