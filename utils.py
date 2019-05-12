
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
    upload_path = os.path.join(basedir, "uploads/" + str(pid))
    os.makedirs(upload_path, exist_ok=True)
    files = os.listdir(upload_path)
    return list(map(lambda x: {"name": x, "last_modified_time": os.path.getsize(os.path.join(upload_path, x)), "size": os.path.getsize(os.path.join(upload_path, x))}, files))
