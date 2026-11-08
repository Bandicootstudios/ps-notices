"""Answers eBay's marketplace account deletion challenge and acknowledges its notices.

Pulling Strings stores no eBay usernames or user IDs, so a notice has nothing to delete.
Notice contents are neither stored nor logged.
"""
import hashlib
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

PATH = "/notices"


class Handler(BaseHTTPRequestHandler):
    def _reply(self, status, body=b"", kind="application/json"):
        self.send_response(status)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        url = urlsplit(self.path)
        if url.path == "/":
            return self._reply(200, b"ok", "text/plain")
        code = parse_qs(url.query).get("challenge_code", [""])[0]
        if url.path != PATH or not code:
            return self._reply(404)
        token, endpoint = os.environ["VERIFICATION_TOKEN"], os.environ["ENDPOINT_URL"]
        digest = hashlib.sha256((code + token + endpoint).encode()).hexdigest()
        self._reply(200, json.dumps({"challengeResponse": digest}).encode())

    def do_POST(self):
        if urlsplit(self.path).path != PATH:
            return self._reply(404)
        self.rfile.read(min(int(self.headers.get("Content-Length") or 0), 65536))
        print("deletion notice acknowledged; no user data held", flush=True)
        self._reply(204)

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", int(os.environ.get("PORT", 10000))), Handler).serve_forever()
