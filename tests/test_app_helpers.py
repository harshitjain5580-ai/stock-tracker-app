import unittest

from app import (
    OTP_REQUESTS,
    can_request_otp,
    generate_otp,
    hash_otp,
    normalize_ticker,
    valid_email_address,
    valid_ticker,
)


class AppHelperTests(unittest.TestCase):
    def test_otp_is_six_digits(self):
        self.assertRegex(generate_otp(), r"^\d{6}$")
        self.assertNotEqual(hash_otp("123456", "key"), hash_otp("123457", "key"))

    def test_otp_request_limit(self):
        email = "limit@example.com"
        OTP_REQUESTS.pop(email, None)
        for _ in range(5):
            self.assertTrue(can_request_otp(email))
        self.assertFalse(can_request_otp(email))

    def test_email_and_ticker_validation(self):
        self.assertTrue(valid_email_address("person@example.com"))
        self.assertFalse(valid_email_address("not-an-email"))
        self.assertTrue(valid_ticker("BRK-B"))
        self.assertFalse(valid_ticker("bad ticker"))

    def test_ticker_normalization(self):
        self.assertEqual(normalize_ticker("TCS", "INDIA"), "TCS.NS")
        self.assertEqual(normalize_ticker("AAPL", "USA"), "AAPL")
        self.assertEqual(normalize_ticker("^NSEI", "INDIA"), "^NSEI")


if __name__ == "__main__":
    unittest.main()
