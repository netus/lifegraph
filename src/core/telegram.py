"""Telegram 通知工具。"""

import logging
import urllib.request
import urllib.parse
import json

logger = logging.getLogger(__name__)


def send_telegram(message: str, bot_token: str = "", chat_id: str = "", site=None):
    """Send a Telegram message with explicit credentials."""
    if not bot_token or not chat_id:
        return False

    if not bot_token or not chat_id:
        return False

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",
    }).encode()

    try:
        req = urllib.request.Request(url, data=data, method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status != 200:
                logger.warning("Telegram API returned status %d", resp.status)
                return False
            return True
    except Exception:
        logger.exception("Telegram send failed")
        return False
