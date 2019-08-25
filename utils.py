from main import config
def md5_with_salt(text: str, salt: str)->str:
    import hashlib
    md5 = hashlib.md5()
    md5.update((text+salt).encode())
    return md5.hexdigest()


def encode_json(obj):
    import json
    encoder = json.JSONEncoder()
    return encoder.encode(obj)


def decode_json(obj):
    import json
    decoder = json.JSONDecoder()
    return decoder.decode(obj)


def make_response(code, **data):
    return encode_json(dict(**{
        "code": code
    }, **data))


def generate_file_list(pid: int)->list:
    import os
    from main import basedir
    upload_path = os.path.join(basedir, f"{config.UPLOAD_DIR}/" + str(pid))
    os.makedirs(upload_path, exist_ok=True)
    files = filter(lambda x: not x.endswith(".lock"), os.listdir(upload_path))
    files = filter(lambda x: os.path.exists(
        os.path.join(upload_path, x+".lock")), files)
    def read_file(x):
        with open(x, "r") as f:
            return f.read()
    return list(map(lambda x: {"name": x, "last_modified_time": float(read_file(os.path.join(upload_path, x)+".lock")), "size": os.path.getsize(os.path.join(upload_path, x))}, files))
