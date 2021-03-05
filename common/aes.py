from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from io import BytesIO
import base64


def encrypt(key: str, plaintext: str) -> str:
    aes_obj = AES.new(key.encode("utf-8"), AES.MODE_EAX)
    encoded_bytes = plaintext.encode("utf-8")
    buf = BytesIO()
    # 写上长度用于校验
    buf.write(len(encoded_bytes).to_bytes(8, "little"))
    buf.write(encoded_bytes)
    padded = pad(buf.getvalue(), AES.block_size)
    return base64.encodebytes(aes_obj.encrypt(padded)).decode().replace("\n", "")


def decrypt(key: str, cipher: str) -> str:
    aes_obj = AES.new(key.encode("utf-8"), AES.MODE_EAX)
    plain = aes_obj.decrypt(base64.decodebytes(cipher.encode("utf-8")))
    data_length = int.from_bytes(plain[:8], "little")
    real_data = plain[8:8+data_length]
    return real_data.decode("utf-8")
