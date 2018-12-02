import hmac
message = b'GETcvm.tencentcloudapi.com/?Action=DescribeRegions&Nonce=11886&Offset=0&Region=ap-shanghai&SecretId=AKID73kBMLhXkhOp32LKcfT1JK5ZnkStAyc1&Timestamp=1543319071&Version=2017-03-12'
# -*- coding: utf8 -*-
import base64
import hashlib
import hmac
import time
import requests

secret_id = "AKID73kBMLhXkhOp32LKcfT1JK5ZnkStAyc1"
secret_key = "HI4b1C7nDNGtHPHsHQJwKSL7dsqY0C7m"

def get_string_to_sign(method, endpoint, params):
    s = method + endpoint + "/?"
    query_str = "&".join("%s=%s" % (k, params[k]) for k in sorted(params))
    return s + query_str

def sign_str(key, s, method):
    hmac_str = hmac.new(key.encode("utf8"), s.encode("utf8"), method).digest()
    return base64.b64encode(hmac_str)

if __name__ == '__main__':
    endpoint = "cvm.tencentcloudapi.com"
    data = {
        'Action' : 'DescribeRegions',
        'Nonce' : 11886,
        'Offset' : 0,
        'Region' : 'ap-guangzhou',
        'SecretId' : secret_id,
        'Timestamp' : int(time.time()),
        'Version': '2017-03-12'
    }
    s = get_string_to_sign("GET", endpoint, data)
    data["Signature"] = sign_str(secret_key, s, hashlib.sha1)
    print(data["Signature"])
    # 此处会实际调用，成功后可能产生计费
resp = requests.get("https://" + endpoint, params=data)
print(resp.content)