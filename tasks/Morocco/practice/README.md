# Morocco - Practice CTF (Safe local sandbox)

This practice package simulates a CTF-style "Flag Keeper" that enforces a small layered protocol.
It's designed for learning protocol analysis, client crafting, and secure server behavior — **locally**.

## What you'll learn
- How a server might validate structured messages (nonce, HMAC, transforms)
- How to implement and reverse the transforms (XOR + base64)
- How to craft valid requests and reason about failures
- How to write basic tests to check protocol conformance

## Files
- `mock_flag_keeper.py` - Flask server implementing the protocol
- `client_submit.py` - Client that crafts valid and invalid payloads
- `test_mock.py` - pytest tests (assumes server running)
- `README.md` - this file

## Quick start
```bash
python -m venv .venv
source .venv/bin/activate
pip install flask requests pytest
python mock_flag_keeper.py
# in another terminal
source .venv/bin/activate
python client_submit.py
# run tests
pytest -q
```

## Notes about safety
- This is a **local** sandbox only. Do not use the scripts against servers you do not own or have permission to test.
- The goal is educational: reproduce the challenge mechanics without attacking or exfiltrating real secrets.
