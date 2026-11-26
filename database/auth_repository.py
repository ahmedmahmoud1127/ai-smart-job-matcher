"""Accounts and authentication: email + password sign-up/sign-in, and social (OAuth) accounts.

Credentials live in their own table (``user_credentials``) so the ``users`` table is untouched.
Passwords are never stored: only a random per-user salt and a PBKDF2-HMAC-SHA256 hash.
Social logins (Google / GitHub / LinkedIn) are linked through ``oauth_accounts``; a user created that way has no
password row, so it can only sign in through its provider until a password is set.
"""
import re
import hashlib
import hmac
import secrets

from database.db import SAMPLE_USER_ID, get_connection

ITERATIONS = 200_000
DEMO_PASSWORD = "Demo@1234"  # password of the seeded sample account (change it with set_password)

AUTH_SCHEMA = """
CREATE TABLE IF NOT EXISTS user_credentials (
    user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    salt TEXT NOT NULL, password_hash TEXT NOT NULL,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS oauth_accounts (
    provider TEXT NOT NULL, provider_user_id TEXT NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (provider, provider_user_id)
);
CREATE TABLE IF NOT EXISTS auth_meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
"""
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MIN_PASSWORD_LENGTH = 8


class AccountExistsError(Exception):
    """An account with this email already exists."""


def _hash(password: str, salt_hex: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), ITERATIONS).hex()


def set_password(user_id: int, password: str) -> None:
    salt = secrets.token_hex(16)
    with get_connection() as c:
        c.execute("INSERT INTO user_credentials (user_id, salt, password_hash) VALUES (?,?,?) "
                  "ON CONFLICT(user_id) DO UPDATE SET salt=excluded.salt, password_hash=excluded.password_hash, "
                  "updated_at=CURRENT_TIMESTAMP", (user_id, salt, _hash(password, salt)))


def init_auth() -> None:
    """Create the credentials table and give the seeded sample account its demo password (only once)."""
    with get_connection() as c:
        c.executescript(AUTH_SCHEMA)
        has_user = c.execute("SELECT 1 FROM users WHERE id=?", (SAMPLE_USER_ID,)).fetchone()
        has_pw = c.execute("SELECT 1 FROM user_credentials WHERE user_id=?", (SAMPLE_USER_ID,)).fetchone()
    if has_user and not has_pw:
        set_password(SAMPLE_USER_ID, DEMO_PASSWORD)


def authenticate(email: str, password: str) -> int | None:
    """Return the user id when the email/password pair is valid, otherwise None."""
    email = (email or "").strip().lower()
    with get_connection() as c:
        row = c.execute("SELECT u.id, k.salt, k.password_hash FROM users u JOIN user_credentials k ON k.user_id = u.id "
                        "WHERE lower(u.email) = ?", (email,)).fetchone()
    if row is None:
        _hash(password or "", secrets.token_hex(16))  # same work for unknown emails (no timing hint)
        return None
    ok = hmac.compare_digest(_hash(password or "", row["salt"]), row["password_hash"])
    return row["id"] if ok else None


# ---------------------------------------------------------------- sign-up (email + password)
def validate_password(password: str) -> str | None:
    """Return a message describing what is wrong with the password, or None when it is acceptable."""
    if len(password or "") < MIN_PASSWORD_LENGTH:
        return f"Password must be at least {MIN_PASSWORD_LENGTH} characters."
    if not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
        return "Password must contain at least one letter and one number."
    return None


def email_exists(email: str) -> bool:
    with get_connection() as c:
        return c.execute("SELECT 1 FROM users WHERE lower(email)=?", ((email or "").strip().lower(),)).fetchone() is not None


def _insert_user(c, full_name: str, email: str, **extra: str) -> int:
    """Insert a brand-new, empty profile (the same shape the profile pages expect) and return its id."""
    cols = ["full_name", "email"] + [k for k, v in extra.items() if v]
    vals = [full_name, email] + [v for v in extra.values() if v]
    uid = c.execute(f"INSERT INTO users ({','.join(cols)}) VALUES ({','.join('?' * len(cols))})", vals).lastrowid
    c.execute("INSERT INTO career_preferences (user_id) VALUES (?)", (uid,))
    return uid


def _set_password(c, user_id: int, password: str) -> None:
    salt = secrets.token_hex(16)
    c.execute("INSERT INTO user_credentials (user_id, salt, password_hash) VALUES (?,?,?)",
              (user_id, salt, _hash(password, salt)))


def create_user(full_name: str, email: str, password: str) -> int:
    """Create an account with email + password. Raises AccountExistsError if the email is taken."""
    email = email.strip()
    with get_connection() as c:
        if c.execute("SELECT 1 FROM users WHERE lower(email)=?", (email.lower(),)).fetchone():
            raise AccountExistsError(email)
        uid = _insert_user(c, full_name.strip(), email)
        _set_password(c, uid, password)
    return uid


# ---------------------------------------------------------------- social sign-in (OAuth)
_PROFILE_URL_FIELD = {"github": "github", "linkedin": "linkedin"}


def find_or_create_oauth_user(provider: str, subject: str, email: str, email_verified: bool, full_name: str,
                              profile_url: str = "") -> tuple[int, bool]:
    """Resolve a social identity to a local user. Returns ``(user_id, created)``.

    1. Already linked  -> that user.
    2. Same *verified* email as an existing account -> link to it (an unverified email is never trusted).
    3. Otherwise -> create a new empty profile and link it.
    """
    email = (email or "").strip()
    with get_connection() as c:
        row = c.execute("SELECT user_id FROM oauth_accounts WHERE provider=? AND provider_user_id=?",
                        (provider, subject)).fetchone()
        if row:
            return row["user_id"], False
        existing = (c.execute("SELECT id FROM users WHERE lower(email)=?", (email.lower(),)).fetchone()
                    if email and email_verified else None)
        if existing:
            uid, created = existing["id"], False
        else:
            if not email:  # provider gave no email: use a stable placeholder so the profile still has one
                email = f"{provider}-{subject}@users.noreply.local"
            elif c.execute("SELECT 1 FROM users WHERE lower(email)=?", (email.lower(),)).fetchone():
                raise AccountExistsError(email)  # unverified email that belongs to someone else
            name = (full_name or "").strip() or email.split("@")[0]
            extra = {_PROFILE_URL_FIELD[provider]: profile_url} if provider in _PROFILE_URL_FIELD else {}
            uid, created = _insert_user(c, name, email, **extra), True
        c.execute("INSERT INTO oauth_accounts (provider, provider_user_id, user_id) VALUES (?,?,?)",
                  (provider, subject, uid))
    return uid, created


def get_signing_secret() -> str:
    """Random per-installation secret (used to sign OAuth state); created once and kept in the database."""
    with get_connection() as c:
        row = c.execute("SELECT value FROM auth_meta WHERE key='signing_secret'").fetchone()
        if row:
            return row["value"]
        value = secrets.token_hex(32)
        c.execute("INSERT OR IGNORE INTO auth_meta (key, value) VALUES ('signing_secret', ?)", (value,))
        return c.execute("SELECT value FROM auth_meta WHERE key='signing_secret'").fetchone()["value"]
