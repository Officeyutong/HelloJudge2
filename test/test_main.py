import os
import tempfile
import pytest
from flaskr import web_app, init_db, config
import shutil
from flask.testing import FlaskClient
from flask.wrappers import Response
@pytest.fixture
def client():
    fid, dbfile = tempfile.mkstemp(suffix=".db")
    shutil.rmtree("./test/migrations", ignore_errors=True)
    web_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///"+dbfile
    web_app.config["TESTING"] = True
    print("Initing...")
    with web_app.test_client() as client:
        with web_app.app_context() as ctx:
            init_db()
        yield client
    os.close(fid)
    # shutil.rmtree("./test/migrations", ignore_errors=True)


def register(client, username, password, email):
    from utils import md5_with_salt
    ret: Response = client.post("/api/register", data={
        "username": username,
        "email": email, "password": password
    })
    # print(type(ret))
    print(ret.data)
    json = ret.get_json(force=True)
    print(json)
    return json


def logout(client):
    return client.post("/api/logout").get_json(force=True)


def login(client, identifier, password):
    from utils import md5_with_salt
    ret: Response = client.post("/api/login", data={
        "identifier": identifier,
        "password": password
    })
    # print(type(ret))
    json = ret.get_json(force=True)
    return json


def get_login_status(client):
    ret: Response = client.post("/api/query_login_state")
    return ret.get_json(force=True)


def test_auth(client: FlaskClient):
    assert register(client, "qwqqwq", "qwqqwq@qwqqwq.com", "abcd")["code"] == 0
    assert get_login_status(client)["result"]
    assert logout(client)["code"] == 0
    assert login(client, "qwqqwq", "abcd")["code"] == 0
    print("after login ",get_login_status(client)["result"])
    assert logout(client)["code"] == 0
    assert login(client, "qwqqwq@qwqqwq.com", "abcd")["code"] == 0
