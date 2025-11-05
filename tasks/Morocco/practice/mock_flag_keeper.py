#!/usr/bin/env python3
"""Mock Flag Keeper - layered protocol (safe practice server)
Protocol (educational):
  Client sends JSON:
  {
    "Flag": "<base64 of payload>",
    "meta": { optional }
  }
Where payload (bytes) = HMAC + b'|' + ENC
  - ENC = base64( XOR( plaintext_json_bytes, key ) )
  - plaintext_json = {"nonce": "...", "thought": "..."}
  - HMAC = hex(hmac_sha256(secret, nonce + '|' + thought))
Server verifies HMAC, nonce freshness, and that thought contains "I think:"
Returns a dummy flag on success.
"""
import os, time, hmac, hashlib, base64, json
from flask import Flask, request, jsonify

app = Flask(__name__)

# Educational secrets (this is a mock server you run locally)
SECRET_HMAC = b"mock_hmac_secret_2025"
XOR_KEY = b"simple_xor_key"

DUMMY_FLAG = "FLAG{practice_morocco_dummy_flag_2025}"

def xor_bytes(data: bytes, key: bytes) -> bytes:
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))

def compute_hmac_hex(nonce: str, thought: str) -> str:
    msg = (nonce + "|" + thought).encode("utf-8")
    return hmac.new(SECRET_HMAC, msg, hashlib.sha256).hexdigest()

@app.route("/submit", methods=["POST"])
def submit():
    try:
        payload = request.get_json(force=True)
    except Exception as e:
        return jsonify({"ok": False, "error": "invalid-json", "detail": str(e)}), 400

    # Expect 'Flag' field containing base64 string
    if "Flag" not in payload:
        return jsonify({"ok": False, "error": "missing-Flag"}), 400

    flag_b64 = payload["Flag"]
    try:
        combined = base64.b64decode(flag_b64)
    except Exception as e:
        return jsonify({"ok": False, "error": "bad-base64", "detail": str(e)}), 400

    # Combined format: hmac_hex (64 ascii hex chars) + b'|' + enc_blob
    try:
        hmac_hex, enc_blob = combined.split(b"|", 1)
    except ValueError:
        return jsonify({"ok": False, "error": "bad-format-combined"}), 400

    try:
        hmac_hex = hmac_hex.decode("ascii")
    except Exception:
        return jsonify({"ok": False, "error": "bad-hmac-encoding"}), 400

    # enc_blob is base64 of XORed plaintext_json
    try:
        xor_payload = base64.b64decode(enc_blob)
    except Exception as e:
        return jsonify({"ok": False, "error": "bad-enc-base64", "detail": str(e)}), 400

    # reverse XOR
    try:
        plaintext_bytes = bytes(b ^ XOR_KEY[i % len(XOR_KEY)] for i, b in enumerate(xor_payload))
        plaintext_json = json.loads(plaintext_bytes.decode("utf-8"))
    except Exception as e:
        return jsonify({"ok": False, "error": "bad-decryption", "detail": str(e)}), 400

    nonce = plaintext_json.get("nonce")
    thought = plaintext_json.get("thought")
    if not nonce or not thought:
        return jsonify({"ok": False, "error": "missing-nonce-or-thought"}), 400

    # verify HMAC
    expected = compute_hmac_hex(nonce, thought)
    if not hmac.compare_digest(expected, hmac_hex):
        return jsonify({"ok": False, "error": "bad-hmac", "expected": expected}), 403

    # check nonce freshness (allow 60s)
    try:
        t = float(nonce)
        age = time.time() - t
        if age > 60 or age < -5:
            return jsonify({"ok": False, "error": "stale-nonce", "age": age}), 400
    except Exception:
        # non-numeric allowed but warn
        pass

    if "I think:" not in thought:
        return jsonify({"ok": False, "error": "bad-thought-format", "hint": "include 'I think:'"}), 400

    # success
    return jsonify({"ok": True, "flag": DUMMY_FLAG}), 200

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
