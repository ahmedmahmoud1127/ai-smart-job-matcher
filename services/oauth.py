"""Social sign-in with Google, GitHub and LinkedIn (OAuth 2.0 authorization-code flow).

Flow: ``build_auth_url`` -> the browser goes to the provider -> the provider sends the user back to the app with
``?code=...&state=...`` -> ``complete_login`` swaps the code for the user's profile.

A full-page redirect starts a new Streamlit session, so the ``state`` (CSRF protection) can't live in
``st.session_state``. It is HMAC-signed instead, with a timestamp, and verified when the user comes back.

Credentials are read from environment variables or ``.streamlit/secrets.toml`` (see README):
    GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET, GITHUB_CLIENT_ID / GITHUB_CLIENT_SECRET,
    LINKEDIN_CLIENT_ID / LINKEDIN_CLIENT_SECRET, and optionally OAUTH_REDIRECT_URI (default http://localhost:8501).
"""
import hashlib
import hmac
import os
import secrets
import time
from urllib.parse import urlencode

import requests

from database import auth_repository as auth

TIMEOUT = 15            # seconds for every call to a provider
STATE_TTL = 600         # a sign-in attempt must finish within 10 minutes
DEFAULT_REDIRECT_URI = "http://localhost:8501"

PROVIDERS = {
    "google": {
        "label": "Google",
        "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "userinfo_url": "https://openidconnect.googleapis.com/v1/userinfo",
        "scope": "openid email profile",
        "extra_params": {"prompt": "select_account"},
    },
    "github": {
        "label": "GitHub",
        "auth_url": "https://github.com/login/oauth/authorize",
        "token_url": "https://github.com/login/oauth/access_token",
        "userinfo_url": "https://api.github.com/user",
        "emails_url": "https://api.github.com/user/emails",
        "scope": "read:user user:email",
        "extra_params": {},
    },
    "linkedin": {
        "label": "LinkedIn",
        "auth_url": "https://www.linkedin.com/oauth/v2/authorization",
        "token_url": "https://www.linkedin.com/oauth/v2/accessToken",
        "userinfo_url": "https://api.linkedin.com/v2/userinfo",
        "scope": "openid profile email",
        "extra_params": {},
    },
}


class OAuthError(Exception):
    """A sign-in attempt failed; the message is safe to show to the user."""


# ---------------------------------------------------------------- configuration
def _secret(section: str, key: str) -> str:
    """Look up ``[oauth.<section>] <key>`` in Streamlit secrets (empty string if there is no secrets file)."""
    try:
        import streamlit as st
        return str(st.secrets.get("oauth", {}).get(section, {}).get(key, "") or "")
    except Exception:
        return ""


def credentials(provider: str) -> tuple[str, str]:
    env = provider.upper()
    cid = os.environ.get(f"{env}_CLIENT_ID") or _secret(provider, "client_id")
    secret = os.environ.get(f"{env}_CLIENT_SECRET") or _secret(provider, "client_secret")
    return cid.strip(), secret.strip()


def is_configured(provider: str) -> bool:
    return all(credentials(provider))


def redirect_uri() -> str:
    return (os.environ.get("OAUTH_REDIRECT_URI") or _secret("", "redirect_uri") or DEFAULT_REDIRECT_URI).strip()


def _signing_key() -> bytes:
    return (os.environ.get("AUTH_SECRET") or auth.get_signing_secret()).encode()


# ---------------------------------------------------------------- signed state
def _sign(payload: str) -> str:
    return hmac.new(_signing_key(), payload.encode(), hashlib.sha256).hexdigest()


def make_state(provider: str, now: float | None = None) -> str:
    payload = f"{provider}.{secrets.token_urlsafe(12)}.{int(now or time.time())}"
    return f"{payload}.{_sign(payload)}"


def verify_state(state: str, now: float | None = None) -> str:
    """Return the provider the state was issued for, or raise OAuthError."""
    try:
        provider, nonce, issued, sig = (state or "").split(".")
        if not hmac.compare_digest(sig, _sign(f"{provider}.{nonce}.{issued}")):
            raise ValueError
        age = (now or time.time()) - int(issued)
    except ValueError:
        raise OAuthError("This sign-in link is invalid. Please try again.") from None
    if age > STATE_TTL or age < -60:
        raise OAuthError("This sign-in attempt expired. Please try again.")
    if provider not in PROVIDERS:
        raise OAuthError("Unknown sign-in provider.")
    return provider


# ---------------------------------------------------------------- the flow
def build_auth_url(provider: str) -> str:
    cfg, (client_id, _) = PROVIDERS[provider], credentials(provider)
    if not client_id:
        raise OAuthError(f"{cfg['label']} sign-in isn't configured yet.")
    params = {"response_type": "code", "client_id": client_id, "redirect_uri": redirect_uri(),
              "scope": cfg["scope"], "state": make_state(provider), **cfg["extra_params"]}
    return f"{cfg['auth_url']}?{urlencode(params)}"


def _json(resp: requests.Response, what: str) -> dict | list:
    try:
        resp.raise_for_status()
        return resp.json()
    except (requests.RequestException, ValueError):
        raise OAuthError(f"Could not {what}. Please try again.") from None


def _exchange_code(provider: str, code: str) -> str:
    cfg, (client_id, client_secret) = PROVIDERS[provider], credentials(provider)
    try:
        resp = requests.post(cfg["token_url"], timeout=TIMEOUT, headers={"Accept": "application/json"},
                             data={"grant_type": "authorization_code", "code": code, "redirect_uri": redirect_uri(),
                                   "client_id": client_id, "client_secret": client_secret})
    except requests.RequestException:
        raise OAuthError(f"Could not reach {cfg['label']}. Please try again.") from None
    token = _json(resp, f"sign in with {cfg['label']}").get("access_token")
    if not token:
        raise OAuthError(f"{cfg['label']} did not return an access token. Please try again.")
    return token


def _get(url: str, token: str, what: str) -> dict | list:
    try:
        resp = requests.get(url, timeout=TIMEOUT, headers={"Authorization": f"Bearer {token}",
                                                           "Accept": "application/json"})
    except requests.RequestException:
        raise OAuthError(f"Could not {what}. Please try again.") from None
    return _json(resp, what)


def fetch_profile(provider: str, token: str) -> dict:
    """Normalise each provider's user info to {subject, email, email_verified, name, profile_url}."""
    cfg = PROVIDERS[provider]
    info = _get(cfg["userinfo_url"], token, f"read your {cfg['label']} profile")
    if provider == "github":
        email, verified = info.get("email") or "", False
        try:  # the public email can be hidden; the emails endpoint lists the verified ones
            emails = _get(cfg["emails_url"], token, "read your GitHub email")
            primary = next((e for e in emails if e.get("primary") and e.get("verified")), None) \
                or next((e for e in emails if e.get("verified")), None)
            if primary:
                email, verified = primary["email"], True
        except OAuthError:
            pass
        return {"subject": str(info.get("id", "")), "email": email, "email_verified": verified,
                "name": info.get("name") or info.get("login") or "", "profile_url": info.get("html_url", "")}
    verified = info.get("email_verified")
    return {"subject": str(info.get("sub", "")), "email": info.get("email", ""),
            "email_verified": verified is True or str(verified).lower() == "true",
            "name": info.get("name") or " ".join(filter(None, [info.get("given_name"), info.get("family_name")])),
            "profile_url": ""}


def complete_login(params: dict) -> tuple[int, bool]:
    """Handle the redirect back from a provider. Returns ``(user_id, created)`` or raises OAuthError."""
    if params.get("error"):
        denied = params["error"] in ("access_denied", "user_cancelled_login", "user_cancelled_authorize")
        raise OAuthError("Sign-in was cancelled." if denied else "The provider could not sign you in. Please try again.")
    provider = verify_state(params.get("state", ""))
    code = params.get("code", "")
    if not code:
        raise OAuthError("The provider did not send back a sign-in code. Please try again.")
    token = _exchange_code(provider, code)
    profile = fetch_profile(provider, token)
    if not profile["subject"]:
        raise OAuthError("The provider did not return your account id. Please try again.")
    try:
        return auth.find_or_create_oauth_user(provider, profile["subject"], profile["email"],
                                              profile["email_verified"], profile["name"], profile["profile_url"])
    except auth.AccountExistsError:
        raise OAuthError("An account with this email already exists. Please sign in with your email and password.") from None
