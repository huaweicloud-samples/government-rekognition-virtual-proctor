# -*- coding: utf-8 -*-
"""
登录认证函数：校验账号密码并签发 JWT（HS256，标准库实现）。

环境变量：
  JWT_SECRET   JWT 签名密钥
  ADMIN_USERS  账号列表，格式 user1:sha256(password1),user2:sha256(password2)

事件：POST /auth/login
  body: {"username": "...", "password": "..."}
响应：200 {"token": "...", "username": "..."} | 401 凭据错误
"""
import base64
import hashlib
import hmac
import json
import os
import time


def _b64url(data):
    return base64.urlsafe_b64encode(data).rstrip(b"=")


def _sign(secret, message):
    return hmac.new(secret.encode("utf-8"), message, hashlib.sha256).digest()


def _issue_token(secret, username, ttl=12 * 3600):
    header = _b64url(json.dumps({"alg": "HS256", "typ": "JWT"},
                                separators=(",", ":")).encode("utf-8"))
    now = int(time.time())
    payload = _b64url(json.dumps({"sub": username, "iat": now,
                                  "exp": now + ttl},
                                 separators=(",", ":")).encode("utf-8"))
    signing_input = header + b"." + payload
    signature = _b64url(_sign(secret, signing_input))
    return (signing_input + b"." + signature).decode("utf-8")


def _respond(status, payload):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(payload),
    }


def handler(event, context):
    try:
        body = json.loads(event.get("body") or "{}")
    except Exception:
        return _respond(400, {"error": "invalid request body"})

    username = (body.get("username") or "").strip()
    password = body.get("password") or ""

    expected = {}
    for entry in os.environ.get("ADMIN_USERS", "").split(","):
        entry = entry.strip()
        if ":" in entry:
            user, digest = entry.split(":", 1)
            expected[user] = digest

    digest = hashlib.sha256(password.encode("utf-8")).hexdigest()
    if username not in expected or expected[username] != digest:
        return _respond(401, {"error": "invalid username or password"})

    token = _issue_token(os.environ["JWT_SECRET"], username)
    return _respond(200, {"token": token, "username": username})
