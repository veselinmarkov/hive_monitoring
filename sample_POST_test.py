from asymmetric_jwt_auth.keys import PrivateKey, RSAPrivateKey
from asymmetric_jwt_auth.tokens import Token
# from asymmetric_jwt_auth.middleware import JWTAuthMiddleware
# from asymmetric_jwt_auth.models import PublicKey

# from django.contrib.auth.models import User
import sys
import os

import requests

OPENSSH_RSA = b"ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQChfejJdi6Jbg4ealsjfC8Jwy3ucwU7PcLWDEVhEi+rvgLRmWhIbK1Tt8lOGx2JECu6zymbFpYSH7cacUqpZfp/Bm4LMtFLqxXqeXymsGmH5mAJYqd0jKZtk0IM8RAvbn9iUvWtmqYXDcE734+dhvsfPEu8LDP251TIskslbj8XIKwQd4q1ervNmhG7o6culFSTltsLwDQ5LdopRfp2cu5i3umNXKBpbYcYDfa4YASmTra/rF+cp9YMXQkTTpsGBRn9wOnJmxRpFEdJ0QDBDqL4zAHkY0Fc4GJufl/4HoYmkolYxzkiYku6wd8bDMcU+o4XZ/78eNoYLPrjCHHy0ytPtFDZMuYB+e8DLGkVp3lNGfV+BRX+s/bexrBRLZoA9U2B7YHq7BOaZs8VRFehU/q0AICM0AOqKHFX3dJPKtEEUb4wmeFS/MoZQm2DXHIhkOA64A+ltdklGgHEjy8daQBvjJ0yIx5IfPMGFpZgk8/ETRcqHTEmmbU1ri6CevQrM7PFCGnmk3btFYUDUHTgykaTr9IA2W+yTMLwKKXBpJlr8lA4oRQpaNpdkuwUY9ivWtTycpl0v5YwLFYsJPcFQPJD31G8AXXBp58K/0YXlt2SuA+kg4QAlFHmJdOAfs8LeQLD01fWhlIWFJlLRS1NHKOOvWKT8YM8kx76I6Ck861Dxw== writer@foo"  # NOQA
MY_KEY = """-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC6iOt4uSAQQ6K6
0d2bFZ/SbiKnECtObyhqChH5aT7NF8NEjq74SAsRJSJPjsv4S9tXkhQdIoxiZgI5
+pSya9MD/2WGt6WD7rKELzyeaOLF3ac/o9jMzfiiIT0zPXYjJIhwX9kCL9z1nzVp
4Vx+ttbuoB1t5w+HfcO7HDuk8q72vDllmCyb1xv2NVIvRi/Nb1HcVvY3WWrwg46J
QKLRN8tIt0ujSgbun4Ir3TjtDriD4WkMkxUaEZXqEu7a56vJTv4MnRvefnpx1NnX
h90gxYAGUGz8kmHejglews73x+yeOtpJZyGUj/DoFmSdTe/yPtVIDGU5D0VdNa93
ysjhkZq3AgMBAAECggEAFsRlcSuvRSzsLL82vBoMksOMiTWJA56/oQmvnfCBkMjI
tZJwuq8YYrRUlr9IF/syP2L9/3xbBBuNRARYp9pPPBqtCp9ZnVvCAC4/yNnma94c
7sCR0pWFNky2So3C4JEx8f1Q4Fp1LqmK/GxcPL8WRrPWQ7bDB3eLL0hH418XidfD
2PwlWuDiC49OXaQNjTrGon83r7wOBMmBHYFsML4QmtNAVIiD9mKNMgzkAdP9ghQB
5yQWdaw/ooiDNcHEgsCUoyBKVSmCYpUZss/IRljoR2oO/jP/vbwobhkYzrGS4ENn
6lWR9RIvrT/BYbso4UO8QAte3TCbKP5GOynoCLv1uQKBgQDwGvo4ESJHSaVKyLjh
x1tH8zkOmgvwBXYSKqxfuXNfLTvfssH98BmJRHIIudd0d7jhkOm3M9L4ChrwLnzq
ugQ+5w6HSGcq2kNwsgX1p5yIO772aNwq0YES15UB7Hps0rB8Txg5vZ7Ngqhzke5d
lZSnU8sKC3n28m4SAZ73ZF4rewKBgQDG4heXcP/h8Qo4+fsi58KPlSSepZmX82vF
0X0BQV1DJU/b9eGI0kcAeDvqoeLDtZIsz5u+8XSQys8yq9+n++UGhmdDyzDVJE5a
daFMHyixHbxeFeeAw8PDusCjaeT0tf4m4Ayl5A8aIhRHNzOUI/98VsaXfNeTTXM+
z89aOL6a9QKBgGRScVAx4Ie2vsize4Ri3sH+X025kdlU/tNyXxmUDB+tb8H1F9c5
lgHjxl3dAKgaSfZ9rRmuHq0i08SdN/Z/iLyboFdoKisejWUuDQ1qXh4SEKU2hR+i
7/Jmf00ReMm1cqZOCgo+L3cg6692Pwl9MWKEwWZOC0TiYJlHchteJXa3AoGBAKvt
4jUiE6LwLEUrHcaEEfbsGLcpM4lffsiJHAaMyiH0zH+7pNgR6B1o02s3vYAwpAgn
BV3hAEL3gH0uhe+DW+7zG6xIqJNpim67B9B1k0jiCuhPCU2Qbtjyxfu+3JYMCoTy
5Rw39jJCScNy3hzvrbqAjbeBzh7iMoGXRoqZSXVNAoGAP1GcuAoNGjQYGZfFo4We
Hf22rKzlbC03kECJ0GY5sMMzqG9oQpSsOLuzCOHACN9J5r6f6+jokmsKMMvXj9sx
DZbz7gvwKjxiaDN1bxutbwFDm1WqR6rosausx2PPaCy2tHjxo4epcg1z4UMmoQqZ
/X5ZaXj1xJ57XSCnFww2XCs=
-----END PRIVATE KEY-----
"""

import jwt
from time import time

nonce =0
def encode_jwt():
    global nonce
    nonce += 1
    payload = {"username": "writer", "time":int(time()), "nonce": nonce}

    base = os.path.dirname(__file__)
    priv_path = os.path.join(base, "hivebox/test_fixtures/dummy_rsa.privkey")
    with open(priv_path) as f1:
        private_key =f1.read().encode()

    encoded = jwt.encode(
        payload,
        private_key, 
        algorithm="RS512",
        # headers={"kid": "b036f1e14bfaa800d247ce14d5267a56ea7a8c2caa1c8244420fe6d29fa387eb"},
    )
    # print(type(encoded))
    return 'JWT ' + encoded

# Load an RSA private key from file
base = os.path.dirname(__file__)
priv_path = os.path.join(base, "hivebox/test_fixtures/dummy_rsa.privkey")
privkey = PrivateKey.load_pem_from_file(priv_path)
# privkey = RSAPrivateKey.load_pem(MY_KEY.encode())
# privkey = PrivateKey.load_pem_from_file('/home/vesko/cert/Ionos_private_open')
# This is the user to authenticate as on the server

auth = Token(username='writer').create_auth_header(privkey)
good_data2 = {"hive": 0, "sample_time": 1586778791, "temp_low": 28.823, 
            "temp_high": None, "temp_hot": 31.663, "temp_out": 24, "temp_target": -10.000, 
            "humi_in": 47.13, "humi_out": None, "heat_pwr": 0, "fan": 758, 
            "mode": "monitor", "heater_breakers": 10}
r = requests.post('http://localhost:8000/api/sample/', headers={
    'Authorization': encode_jwt()}, 
    json=good_data2,
)
""" r = requests.post('http://localhost:8000/api/sample/', 
    json=good_data2,
) """
""" print('asymm Token->', auth)
print('pyjwt token->', encode_jwt()) """
print('POST result:', r.status_code, r.text)


header = Token(username='writer').create_auth_header(privkey)
response = requests.get('http://localhost:8000/api/sample/', {"hive": 0, "sample": "2020-04-13T11:53:11Z"}, headers={
    'Authorization': encode_jwt()})
# print(response.json())
print('GET result:', response.status_code, response.text)
if response.status_code == 200:
    print('Record delete initiate')
    header = Token(username='writer').create_auth_header(privkey)
    url = 'http://localhost:8000/api/sample/?sample=2020-04-13T11:53:11Z&hive=0'
    r = requests.delete(url, headers={'Authorization': header})
    if r.status_code ==200:
        print('Record deleted ', r.status_code, r.text)
    else:
        print('Deletion problem:', r.status_code, r.text)
        sys.exit()  

