import json
import unittest

from game import DEMO_SECRET, check_guess, filter_reply, request_payload


class GameTests(unittest.TestCase):
    def test_secret_boundary(self):
        for level in (1, 2):
            self.assertIn(DEMO_SECRET, json.dumps(request_payload(level, "hello")))
        payload = request_payload(3, "hello")
        self.assertNotIn(DEMO_SECRET, json.dumps(payload))
        self.assertNotIn("tools", payload)
        self.assertNotIn("previous_response_id", payload)
        self.assertEqual(payload["input"], [{"role": "user", "content": "hello"}])

    def test_filter_demonstrates_encoding_gap(self):
        self.assertTrue(filter_reply(2, DEMO_SECRET.lower())[1])
        spaced = " ".join(DEMO_SECRET)
        self.assertEqual(filter_reply(2, spaced), (spaced, False))
        self.assertEqual(filter_reply(1, DEMO_SECRET), (DEMO_SECRET, False))

    def test_guess(self):
        self.assertTrue(check_guess(" parameterized ", DEMO_SECRET))
        self.assertFalse(check_guess(DEMO_SECRET, "FRESHSECRET"))
        self.assertFalse(check_guess("", DEMO_SECRET))

    def test_python_reconstruction_bypasses_literal_filter(self):
        codes = [80, 65, 82, 65, 77, 69, 84, 69, 82, 73, 90, 69, 68]
        reply = f"''.join([chr(c) for c in {codes}])"
        self.assertEqual("".join(map(chr, codes)), DEMO_SECRET)
        self.assertEqual(filter_reply(2, reply), (reply, False))

    def test_invalid_requests(self):
        for level, prompt in [(0, "hello"), (1, " "), (2, "x" * 4001)]:
            with self.assertRaises(ValueError):
                request_payload(level, prompt)


if __name__ == "__main__":
    unittest.main()
