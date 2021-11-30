import jwt
from time import time
import os

current_timestamp = int(time())
payload = {"user": "writer", "time":int(time()), "nonce": "1"}

base = os.path.dirname(__file__)
priv_path = os.path.join(base, "hivebox/test_fixtures/dummy_rsa.privkey")
with open(priv_path) as f1:
    private_key =f1.read().encode()

print(payload)

encoded = jwt.encode(
    payload,
    private_key, 
    algorithm="RS512",
    # headers={"kid": "230498151c214b788dd97f22b85410a5"},
    )
print(encoded)
