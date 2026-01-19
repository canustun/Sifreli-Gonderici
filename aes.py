from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM 
import os 

def generate_key():
    a_private = x25519.X25519PrivateKey.generate()
    a_public = a_private.public_key()

    b_private = x25519.X25519PrivateKey.generate()
    b_public = b_private.public_key()

    shared_A = a_private.exchange(b_public)
    shared_B = b_private.exchange(a_public)
    assert shared_A == shared_B 


    aes_key = HKDF(
        algorithm = hashes.SHA256(),
        length = 32,
        salt = None,
        info = b"file-transfer",
    ).derive(shared_A)

    return aes_key


def encrypt(aes_key : bytes,plaintext : bytes,aad : bytes = None)-> bytes:
    aesgcm = AESGCM(aes_key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce,plaintext,aad)
    return nonce + ciphertext


def decrypt(aes_key: bytes , blob: bytes, aad: bytes = None)-> bytes:
    aesgcm = AESGCM(aes_key)
    nonce,ct = blob[:12] , blob[12:]
    return aesgcm.decrypt(nonce , ct , aad)

def verial(mesaj):
    aes_key = generate_key()
    enc = encrypt(aes_key , mesaj , aad = b"meta")
    return [enc, aes_key]
