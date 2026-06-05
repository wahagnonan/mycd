import logging
import re
import time
from collections import defaultdict
from threading import Lock

from django.conf import settings
from django.http import HttpResponseForbidden

logger = logging.getLogger(__name__)

_ip_access: dict[str, list[float]] = defaultdict(list)
_ip_lock = Lock()

SENSITIVE_PATHS = [
    re.compile(r"^/api/auth/"),
    re.compile(r"^/api/mon-profil/"),
]

SUSPICIOUS_PATTERNS = [
    re.compile(r"admin", re.IGNORECASE),
    re.compile(r"wp-admin", re.IGNORECASE),
    re.compile(r"\.env", re.IGNORECASE),
    re.compile(r"\.git", re.IGNORECASE),
    re.compile(r"config\.json", re.IGNORECASE),
    re.compile(r"sql", re.IGNORECASE),
    re.compile(r"backup", re.IGNORECASE),
    re.compile(r"db\.sqlite", re.IGNORECASE),
]


def _get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "127.0.0.1")


class SecurityLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = _get_client_ip(request)
        path = request.path
        method = request.method

        for pattern in SUSPICIOUS_PATTERNS:
            if pattern.search(path):
                logger.warning(
                    "SUSPICIOUS_PATTERN | IP=%s | Method=%s | Path=%s | Pattern=%s",
                    ip, method, path, pattern.pattern,
                )
                return HttpResponseForbidden("Accès refusé")

        now = time.time()
        with _ip_lock:
            window = [t for t in _ip_access[ip] if now - t < 60]
            _ip_access[ip] = window
            if len(window) > 200:
                logger.warning(
                    "RATE_LIMIT_IP | IP=%s | Count=%d | Path=%s",
                    ip, len(window), path,
                )
                _ip_access[ip] = []
                return HttpResponseForbidden("Trop de requêtes")
            _ip_access[ip].append(now)

        for sensitive_re in SENSITIVE_PATHS:
            if sensitive_re.match(path):
                user = request.user
                user_str = (
                    f"{user.email} (id={user.id})"
                    if user.is_authenticated
                    else "anonymous"
                )
                logger.info(
                    "SENSITIVE_ACCESS | IP=%s | User=%s | Method=%s | Path=%s",
                    ip, user_str, method, path,
                )
                break

        response = self.get_response(request)

        if response.status_code in (401, 403) and path.startswith("/api/"):
            user = request.user
            user_str = (
                f"{user.email} (id={user.id})"
                if user.is_authenticated
                else "anonymous"
            )
            logger.warning(
                "UNAUTHORIZED_ACCESS | IP=%s | User=%s | Method=%s | Path=%s | Status=%d",
                ip, user_str, method, path, response.status_code,
            )

        return response
