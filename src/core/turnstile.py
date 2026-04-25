"""Cloudflare Turnstile server-side token verification."""
import json
import logging
import urllib.parse
import urllib.request

logger = logging.getLogger(__name__)


def verify_turnstile(token: str, secret_key: str, remote_ip: str = "") -> bool:
    """Return True if the Turnstile token is valid, False otherwise."""
    if not secret_key or not token:
        return False

    data = urllib.parse.urlencode(
        {"secret": secret_key, "response": token, "remoteip": remote_ip}
    ).encode()

    req = urllib.request.Request(
        "https://challenges.cloudflare.com/turnstile/v0/siteverify",
        data=data,
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            result = json.loads(resp.read())
            return bool(result.get("success", False))
    except Exception:
        logger.warning("Turnstile verification failed for ip=%s", remote_ip, exc_info=True)
        return False
