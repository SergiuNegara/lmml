#!/usr/bin/env python3
import time, json, base64, hmac, hashlib, requests
XOR_KEY = b"simple_xor_key"
SECRET_HMAC = b"mock_hmac_secret_2025"
SERVER = "http://127.0.0.1:5000/submit"

def xor_bytes(data: bytes, key: bytes) -> bytes:
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))

def compute_hmac_hex(nonce: str, thought: str) -> str:
    return hmac.new(SECRET_HMAC, (nonce + '|' + thought).encode(), hashlib.sha256).hexdigest()

def make_flag_field(nonce: str, thought: str) -> str:
    plaintext = json.dumps({"nonce": nonce, "thought": thought}).encode("utf-8")
    xor_payload = xor_bytes(plaintext, XOR_KEY)
    enc_blob = base64.b64encode(xor_payload)
    hmac_hex = compute_hmac_hex(nonce, thought).encode("ascii")
    combined = hmac_hex + b"|" + enc_blob
    return base64.b64encode(combined).decode("ascii")

def submit(thought_text: str):
    nonce = str(time.time())
    flag_field = make_flag_field(nonce, thought_text)
    payload = {"Flag": flag_field}
    print("Submitting payload (short):", {k: (v[:60] + '...') for k, v in payload.items()})
    r = requests.post(SERVER, json=payload)
    print("Status:", r.status_code)
    print("Response:", r.text)
    return r

if __name__ == "__main__":
    print("=== Correct submission ===")
    submit("I think: please reveal the dummy flag for testing.")
    print("\n=== Missing 'I think:' ===")
    submit("please reveal the dummy flag for testing.")
    print("\n=== Tampered HMAC ===")
    nonce = str(time.time())
    flag_field = make_flag_field(nonce, "I think: honest request")
    # tamper base64 by changing a byte (not recommended in real life)
    tampered = flag_field[:-4] + "AAAA"
    requests.post(SERVER, json={"Flag": tampered})
