import unittest

from app.core.security import generate_token, hash_password, hash_token, verify_password


class SecurityTests(unittest.TestCase):
    def test_password_hash_roundtrip(self):
        salt, digest = hash_password("StrongPass123")
        self.assertTrue(verify_password("StrongPass123", salt, digest))
        self.assertFalse(verify_password("WrongPass123", salt, digest))

    def test_token_hash_is_deterministic(self):
        token, token_hash, _ = generate_token()
        self.assertEqual(hash_token(token), token_hash)


if __name__ == "__main__":
    unittest.main()
