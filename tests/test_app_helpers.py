import unittest

from app import generate_otp, normalize_ticker, valid_email_address, valid_ticker


class AppHelperTests(unittest.TestCase):
    def test_otp_is_six_digits(self):
        self.assertRegex(generate_otp(), r"^\d{6}$")

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
