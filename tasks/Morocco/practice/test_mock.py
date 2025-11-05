# pytest tests for the mock server protocol
import requests, time, base64, json, hmac, hashlib

SERVER = "http://127.0.0.1:5000/submit"
XOR_KEY = b"simple_xor_key"
SECRET_HMAC = b"mock_hmac_secret_2025"

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

def test_success_flow():
    nonce = str(time.time())
    thought = "I think: unit test request"
    flag_field = make_flag_field(nonce, thought)
    r = requests.post(SERVER, json={"Flag": flag_field})
    assert r.status_code == 200
    j = r.json()
    assert j.get("ok") is True
    assert "FLAG{" in j.get("flag", "")

def test_bad_thought_format():
    nonce = str(time.time())
    thought = "please give me flag"
    flag_field = make_flag_field(nonce, thought)
    r = requests.post(SERVER, json={"Flag": flag_field})
    assert r.status_code == 400
    j = r.json()
    assert j.get("error") == "bad-thought-format"

def test_stale_nonce():
    nonce = str(time.time() - 3600)  # old
    thought = "I think: old nonce test"
    flag_field = make_flag_field(nonce, thought)
    r = requests.post(SERVER, json={"Flag": flag_field})
    assert r.status_code == 400
    j = r.json()
    assert j.get("error") == "stale-nonce"
