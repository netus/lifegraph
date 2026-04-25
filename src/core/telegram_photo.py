"""Telegram Bot API — 发送图片（multipart/form-data）。"""

import json
import logging
import urllib.request
import uuid

logger = logging.getLogger(__name__)


def send_telegram_photo(photo_bytes, caption, bot_token, chat_id):
    """Send a photo to Telegram chat via sendPhoto API.

    Args:
        photo_bytes: PNG/JPEG image data as bytes
        caption: Text caption (max 1024 chars, HTML parse mode)
        bot_token: Telegram bot token
        chat_id: Target chat ID

    Returns:
        True on success, False on failure
    """
    url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
    boundary = uuid.uuid4().hex

    body = _build_multipart(boundary, {
        "chat_id": str(chat_id),
        "caption": caption[:1024],
        "parse_mode": "HTML",
    }, photo_bytes, "report.png", "image/png")

    headers = {
        "Content-Type": f"multipart/form-data; boundary={boundary}",
    }

    try:
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
            if not result.get("ok"):
                logger.warning("sendPhoto error: %s", result.get("description", "unknown"))
                return False
            return True
    except Exception:
        logger.exception("Failed to send Telegram photo")
        return False


def _build_multipart(boundary, fields, file_data, filename, content_type):
    """Build multipart/form-data body bytes."""
    parts = []
    for key, value in fields.items():
        parts.append(
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="{key}"\r\n\r\n'
            f"{value}\r\n"
        )

    # File part
    parts.append(
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="photo"; filename="{filename}"\r\n'
        f"Content-Type: {content_type}\r\n\r\n"
    )

    body = b""
    for part in parts:
        body += part.encode("utf-8")

    # Insert file data before the closing boundary
    # The last part (file header) needs the binary data appended
    body += file_data
    body += f"\r\n--{boundary}--\r\n".encode("utf-8")

    return body
