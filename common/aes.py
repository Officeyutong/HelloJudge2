from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from io import BytesIO
import base64


def encrypt(key: str, plaintext: str) -> str:
    aes_obj = AES.new(key.encode("utf-8"), AES.MODE_EAX)
    encoded_bytes = plaintext.encode("utf-8")
    buf = BytesIO()
    ciphertext, tag = aes_obj.encrypt_and_digest(encoded_bytes)
    buf.write(aes_obj.nonce)
    buf.write(tag)
    buf.write(ciphertext)
    return base64.encodebytes(buf.getvalue()).decode().replace("\n", "")


def decrypt(key: str, cipher: str) -> str:

    buf = BytesIO(base64.decodebytes(cipher.encode("utf-8")))
    nonce = buf.read(16)
    tag = buf.read(16)
    ciphertext = buf.read(-1)
    aes_obj = AES.new(key.encode("utf-8"), AES.MODE_EAX, nonce=nonce)
    plain = aes_obj.decrypt_and_verify(ciphertext, tag)
    return plain.decode("utf-8")
