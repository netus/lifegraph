"""媒体上传安全验证：扩展名白名单 + 文件头魔数校验 + 大小限制 + SVG 安全检查。"""

import os
import re

ALLOWED_EXTENSIONS = {
    "jpg", "jpeg", "png", "gif", "webp", "svg", "pdf",
    "heic", "heif", "avif",
    "mp4", "mp3",
}

# 文件头魔数（前几个字节）
MAGIC_BYTES = {
    "jpg":  [b"\xff\xd8\xff"],
    "jpeg": [b"\xff\xd8\xff"],
    "png":  [b"\x89PNG\r\n\x1a\n"],
    "gif":  [b"GIF87a", b"GIF89a"],
    "webp": [b"RIFF"],       # RIFF....WEBP
    "pdf":  [b"%PDF"],
    "mp4":  [b"\x00\x00\x00", b"ftyp"],  # ISO base media (offset 4 has 'ftyp')
    "mp3":  [b"\xff\xfb", b"\xff\xf3", b"\xff\xf2", b"ID3"],
}


def validate_upload(uploaded_file, max_size_mb=20):
    """
    校验上传文件。

    返回 (is_valid: bool, error_message: str)。
    error_message 为空字符串表示验证通过。
    """
    filename = uploaded_file.name or ""
    ext = os.path.splitext(filename)[1].lstrip(".").lower()

    # Fallback: infer extension from content_type when filename has none (e.g. clipboard paste)
    if not ext:
        _MIME_TO_EXT = {
            "image/jpeg": "jpg", "image/png": "png", "image/gif": "gif",
            "image/webp": "webp", "image/svg+xml": "svg", "image/avif": "avif",
            "image/heic": "heic", "image/heif": "heif",
            "video/mp4": "mp4", "audio/mpeg": "mp3", "application/pdf": "pdf",
        }
        ct = getattr(uploaded_file, "content_type", "") or ""
        ext = _MIME_TO_EXT.get(ct, "")

    # 1. 扩展名白名单
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"不允许的文件类型: .{ext}。允许的类型: {', '.join(sorted(ALLOWED_EXTENSIONS))}"

    # 2. 文件大小
    size_limit = max_size_mb * 1024 * 1024
    if uploaded_file.size > size_limit:
        return False, f"文件大小 ({uploaded_file.size / 1024 / 1024:.1f} MB) 超过限制 ({max_size_mb} MB)。"

    # 3. 魔数校验（SVG 是文本格式，跳过二进制检查）
    if ext == "svg":
        # SVG 是 XML 文本，检查是否包含 <svg 标签并检查危险内容
        try:
            uploaded_file.seek(0)
            svg_content = uploaded_file.read().decode("utf-8", errors="ignore")
            uploaded_file.seek(0)
            head = svg_content[:1024].lower()
            if "<svg" not in head and "<?xml" not in head:
                return False, "SVG 文件格式无效。"
            # Check for dangerous elements and attributes (XXE, scripts, event handlers)
            dangerous_patterns = re.compile(
                r'<\s*script'
                r'|<\x00*\s*script'
                r'|on\w+\s*='
                r'|javascript\s*:'
                r'|data\s*:\s*text/html'
                r'|<\s*foreignObject'
                r'|<!ENTITY'
                r'|&#x?[0-9a-fA-F]+;\s*s\s*c\s*r\s*i\s*p\s*t'
                r'|expression\s*\('
                r'|url\s*\(\s*["\']?\s*javascript'
                r'|-moz-binding\s*:'
                r'|behavior\s*:',
                re.IGNORECASE,
            )
            if dangerous_patterns.search(svg_content):
                return False, "SVG 文件包含潜在危险内容（脚本、事件处理器或外部实体）。"
        except Exception:
            return False, "无法读取 SVG 文件内容。"
        return True, ""

    magic_patterns = MAGIC_BYTES.get(ext)
    if magic_patterns:
        try:
            uploaded_file.seek(0)
            header = uploaded_file.read(16)

            matched = False
            for pattern in magic_patterns:
                if header.startswith(pattern):
                    matched = True
                    break
                # MP4 的 ftyp 标记在第 4 字节
                if ext == "mp4" and pattern == b"ftyp" and len(header) >= 8:
                    if header[4:8] == b"ftyp":
                        matched = True
                        break
                # WEBP 额外校验
                if ext == "webp" and header.startswith(b"RIFF") and len(header) >= 12:
                    if header[8:12] == b"WEBP":
                        matched = True
                        break

            if not matched:
                return False, f"文件内容与 .{ext} 格式不匹配，可能是伪装文件。"
        except Exception:
            return False, "无法读取文件头信息。"
        finally:
            uploaded_file.seek(0)

    return True, ""
