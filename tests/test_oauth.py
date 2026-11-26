"""Run from the project folder:  python -m unittest tests.test_oauth -v   (no network: providers are mocked)"""
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock
from urllib.parse import parse_qs, urlparse

import database.db as dbm

dbm.DB_PATH = Path(tempfile.mkdtemp()) / "test_oauth.db"  # never touch the real database
dbm.init_db()

from database import auth_repository as auth  # noqa: E402
from database import repository as repo  # noqa: E402
from services import oauth  # noqa: E402

ENV = {"GOOGLE_CLIENT_ID": "gid", "GOOGLE_CLIENT_SECRET": "gsecret", "GITHUB_CLIENT_ID": "hid",
       "GITHUB_CLIENT_SECRET": "hsecret", "LINKEDIN_CLIENT_ID": "lid", "LINKEDIN_CLIENT_SECRET": "lsecret",
       "OAUTH_REDIRECT_URI": "http://localhost:8501"}


def _resp(payload, status=200):
    r = mock.Mock(status_code=status)
    r.json.return_value = payload
    r.raise_for_status.side_effect = None if status < 400 else oauth.requests.HTTPError("boom")
    return r


class OAuthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        auth.init_auth()

    def setUp(self):
        patcher = mock.patch.dict(os.environ, ENV)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_auth_url_for_each_provider(self):
        for provider, host in (("google", "accounts.google.com"), ("github", "github.com"), ("linkedin", "www.linkedin.com")):
            url = urlparse(oauth.build_auth_url(provider))
            q = parse_qs(url.query)
            self.assertEqual(url.netloc, host)
            self.assertEqual(q["redirect_uri"], ["http://localhost:8501"])
            self.assertEqual(q["response_type"], ["code"])
            self.assertEqual(oauth.verify_state(q["state"][0]), provider)

    def test_unconfigured_provider_is_reported(self):
        with mock.patch.dict(os.environ, {"GITHUB_CLIENT_ID": ""}):
            self.assertFalse(oauth.is_configured("github"))
            with self.assertRaises(oauth.OAuthError):
                oauth.build_auth_url("github")

    def test_state_is_tamper_proof_and_expires(self):
        state = oauth.make_state("google", now=1_000)
        self.assertEqual(oauth.verify_state(state, now=1_100), "google")
        with self.assertRaises(oauth.OAuthError):
            oauth.verify_state(state.replace("google", "github", 1), now=1_100)   # provider swapped
        with self.assertRaises(oauth.OAuthError):
            oauth.verify_state(state, now=1_000 + oauth.STATE_TTL + 1)            # too old
        for junk in ("", "abc", "a.b.c.d"):
            with self.assertRaises(oauth.OAuthError):
                oauth.verify_state(junk)

    def test_google_login_creates_user_and_reuses_it(self):
        info = {"sub": "g-100", "email": "new.user@gmail.com", "email_verified": True, "name": "New User"}
        params = {"code": "abc", "state": oauth.make_state("google")}
        with mock.patch("services.oauth.requests.post", return_value=_resp({"access_token": "tok"})) as post, \
                mock.patch("services.oauth.requests.get", return_value=_resp(info)):
            uid, created = oauth.complete_login(params)
            uid2, created2 = oauth.complete_login({"code": "def", "state": oauth.make_state("google")})
        self.assertTrue(created)
        self.assertEqual((uid2, created2), (uid, False))
        self.assertEqual(repo.get_user(uid)["full_name"], "New User")
        self.assertEqual(post.call_args.kwargs["data"]["code"], "def")

    def test_github_uses_verified_primary_email_when_profile_email_is_hidden(self):
        def fake_get(url, **_):
            if url.endswith("/user/emails"):
                return _resp([{"email": "x@y.com", "primary": False, "verified": True},
                              {"email": "main@dev.io", "primary": True, "verified": True}])
            return _resp({"id": 5, "login": "octo", "name": None, "email": None, "html_url": "https://github.com/octo"})
        with mock.patch("services.oauth.requests.post", return_value=_resp({"access_token": "t"})), \
                mock.patch("services.oauth.requests.get", side_effect=fake_get):
            uid, created = oauth.complete_login({"code": "c", "state": oauth.make_state("github")})
        user = repo.get_user(uid)
        self.assertTrue(created)
        self.assertEqual((user["email"], user["full_name"], user["github"]), ("main@dev.io", "octo", "https://github.com/octo"))

    def test_linkedin_profile(self):
        info = {"sub": "li-9", "given_name": "Lina", "family_name": "Hassan", "email": "lina@corp.com", "email_verified": "true"}
        with mock.patch("services.oauth.requests.post", return_value=_resp({"access_token": "t"})), \
                mock.patch("services.oauth.requests.get", return_value=_resp(info)):
            uid, _ = oauth.complete_login({"code": "c", "state": oauth.make_state("linkedin")})
        self.assertEqual(repo.get_user(uid)["full_name"], "Lina Hassan")

    def test_failures_become_friendly_errors(self):
        with self.assertRaises(oauth.OAuthError):                                  # user pressed "Cancel"
            oauth.complete_login({"error": "access_denied"})
        with self.assertRaises(oauth.OAuthError):                                  # forged state
            oauth.complete_login({"code": "c", "state": "google.x.1.deadbeef"})
        with mock.patch("services.oauth.requests.post", return_value=_resp({}, status=400)):
            with self.assertRaises(oauth.OAuthError):                              # provider rejected the code
                oauth.complete_login({"code": "bad", "state": oauth.make_state("google")})
        with mock.patch("services.oauth.requests.post", side_effect=oauth.requests.ConnectionError()):
            with self.assertRaises(oauth.OAuthError):                              # network down
                oauth.complete_login({"code": "c", "state": oauth.make_state("google")})


if __name__ == "__main__":
    unittest.main()
