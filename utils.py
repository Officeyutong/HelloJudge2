from main import config


def md5_with_salt(text: str, salt: str) -> str:
    import hashlib
    md5 = hashlib.md5()
    md5.update((text+salt).encode())
    return md5.hexdigest()


def encode_json(obj):
    import json
    encoder = json.JSONEncoder(default=lambda x: str(x))
    return encoder.encode(obj)


def decode_json(obj):
    import json
    decoder = json.JSONDecoder()
    return decoder.decode(obj)


def make_response(code, **data):
    return encode_json(dict(**{
        "code": code
    }, **data))


def generate_file_list(pid: int) -> list:
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


def send_mail(content: str, subject: str, target: str, receiver_username="") -> None:
    import smtplib
    from email.mime.text import MIMEText
    from email.header import Header
    from email.utils import parseaddr, formataddr

    def my_format(s):
        name, addr = parseaddr(s)
        return formataddr((Header(name, "utf-8").encode(), addr.encode("utf-8")))

    content = MIMEText((content), "plain", "utf-8")
    # content["From"] = Header("HelloJudgeV2", "utf-8")
    content["Subject"] = Header(subject, "utf-8")
    content["From"] = my_format(f"HelloJudgeV2 <{config.EMAIL_SENDER}>")
    content["To"] =my_format(f"{receiver_username} <{target}>")
    smtp_client = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT)
    smtp_client.login(config.SMTP_USER, config.SMTP_PASSWORD)
    try:
        smtp_client.sendmail(config.EMAIL_SENDER, target,
                             content.as_string())
    except smtplib.SMTPException as ex:
        return make_response(-1, message="发送失败！\n"+str(ex))
    smtp_client.close()
