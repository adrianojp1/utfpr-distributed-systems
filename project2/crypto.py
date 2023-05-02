# Based on https://pycryptodome.readthedocs.io/en/latest/src/signature/pkcs1_v1_5.html

from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import pkcs1_15


def generate_key():
    return RSA.generate(2048)


def sign(key, message: bytes):
    hs = SHA256.new(message)
    signature = pkcs1_15.new(key).sign(hs)
    return signature


def verify(key, message: bytes, signature):
    hs = SHA256.new(message)
    try:
        pkcs1_15.new(key).verify(hs, signature)
        return True
    except (ValueError, TypeError):
        return False
