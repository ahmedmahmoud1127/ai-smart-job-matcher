"""Run from the project folder:  python -m unittest tests.test_auth -v"""
import tempfile
import unittest
from pathlib import Path

import database.db as dbm

dbm.DB_PATH = Path(tempfile.mkdtemp()) / "test_auth.db"  # never touch the real database
dbm.init_db()

from database import auth_repository as auth  # noqa: E402
from database import repository as repo  # noqa: E402
from database.db import get_connection  # noqa: E402


class AuthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        auth.init_auth()
        cls.email = repo.get_user()["email"]

    def test_demo_account_can_sign_in(self):
        self.assertEqual(auth.authenticate(self.email, auth.DEMO_PASSWORD), dbm.SAMPLE_USER_ID)

    def test_email_is_case_and_space_insensitive(self):
        self.assertEqual(auth.authenticate(f"  {self.email.upper()} ", auth.DEMO_PASSWORD), dbm.SAMPLE_USER_ID)

    def test_wrong_password_or_unknown_email_is_rejected(self):
        self.assertIsNone(auth.authenticate(self.email, "wrong-password"))
        self.assertIsNone(auth.authenticate("nobody@example.com", auth.DEMO_PASSWORD))
        self.assertIsNone(auth.authenticate(self.email, ""))

    def test_password_is_stored_hashed_and_init_is_idempotent(self):
        auth.init_auth()
        with get_connection() as c:
            row = c.execute("SELECT salt, password_hash FROM user_credentials").fetchone()
        self.assertNotIn(auth.DEMO_PASSWORD, (row["salt"], row["password_hash"]))
        self.assertEqual(auth.authenticate(self.email, auth.DEMO_PASSWORD), dbm.SAMPLE_USER_ID)

    def test_changing_the_password(self):
        auth.set_password(dbm.SAMPLE_USER_ID, "New-Pass#42")
        self.assertIsNone(auth.authenticate(self.email, auth.DEMO_PASSWORD))
        self.assertEqual(auth.authenticate(self.email, "New-Pass#42"), dbm.SAMPLE_USER_ID)
        auth.set_password(dbm.SAMPLE_USER_ID, auth.DEMO_PASSWORD)

    def test_sign_up_creates_an_empty_profile_that_can_sign_in(self):
        uid = auth.create_user("  Sara Ali ", "Sara.Ali@Example.com", "Passw0rd!")
        self.assertNotEqual(uid, dbm.SAMPLE_USER_ID)
        self.assertEqual(auth.authenticate("sara.ali@example.com", "Passw0rd!"), uid)
        self.assertEqual(repo.get_user(uid)["full_name"], "Sara Ali")
        self.assertEqual(repo.list_rows("skills", uid), [])                      # starts empty, not with the demo data
        self.assertTrue(repo.list_rows("skills", dbm.SAMPLE_USER_ID))            # and the demo user is untouched

    def test_sign_up_rejects_an_email_that_is_already_taken(self):
        with self.assertRaises(auth.AccountExistsError):
            auth.create_user("Someone", self.email.upper(), "Passw0rd!")
        self.assertTrue(auth.email_exists(f" {self.email.upper()} "))

    def test_password_rules(self):
        self.assertIsNone(auth.validate_password("Passw0rd!"))
        for bad in ("", "short1", "onlyletters", "12345678"):
            self.assertIsNotNone(auth.validate_password(bad), bad)

    def test_users_only_see_their_own_data(self):
        a = auth.create_user("User A", "a@example.com", "Passw0rd!")
        b = auth.create_user("User B", "b@example.com", "Passw0rd!")
        repo.insert_row("skills", {"name": "Rust", "category": "Programming Language", "level": "Beginner"}, a)
        self.assertEqual([r["name"] for r in repo.list_rows("skills", a)], ["Rust"])
        self.assertEqual(repo.list_rows("skills", b), [])

    def test_social_account_is_created_linked_and_reused(self):
        uid, created = auth.find_or_create_oauth_user("github", "42", "dev@example.com", True, "Dev Person",
                                                      "https://github.com/devperson")
        self.assertTrue(created)
        self.assertEqual(repo.get_user(uid)["github"], "https://github.com/devperson")
        self.assertIsNone(auth.authenticate("dev@example.com", "anything"))      # no password -> provider only
        self.assertEqual(auth.find_or_create_oauth_user("github", "42", "other@x.com", True, "X"), (uid, False))

    def test_social_login_links_to_existing_account_only_for_verified_email(self):
        uid, created = auth.find_or_create_oauth_user("google", "g1", self.email, True, "Ahmed")
        self.assertEqual((uid, created), (dbm.SAMPLE_USER_ID, False))
        with self.assertRaises(auth.AccountExistsError):                          # unverified email must not take over
            auth.find_or_create_oauth_user("linkedin", "l1", self.email, False, "Impostor")

    def test_social_login_without_email_still_gets_a_profile(self):
        uid, created = auth.find_or_create_oauth_user("github", "777", "", False, "")
        self.assertTrue(created)
        self.assertTrue(repo.get_user(uid)["email"])


if __name__ == "__main__":
    unittest.main()
