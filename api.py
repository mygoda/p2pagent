# -*- coding: utf-8 -*-
# __author__ = xutao

from flask import Flask
from flask import jsonify
import os
from flask import request
import docker


app = Flask(__name__)

TOKEN = "TEST"

TRACKER_URL = "http://205.177.85.132/peertracker/mysql/announce.php"

DOCKER_API_URL = "tcp://127.0.0.1:6732"

P2P_PORT = 9091

P2P_HOST_DOWNLOAD_DIR = '/var/tmp/downloads/'

P2P_HOST_INCOMPLETE_DIR = "/var/tmp/incomplete/"


def get_docker_client(base_url):
    """
        获取 docker 代理
    :param base_url:
    :return:
    """
    client = docker.Client(base_url=base_url)
    return client


def create_host_config(client):
    """
        配置 host
    :param client:
    :return:
    """
    return client.create_host_config(binds=["%s:/var/lib/transmission-daemon/downloads" % P2P_HOST_DOWNLOAD_DIR,
                                            "%s:/var/lib/transmission-daemon/incomplete" % P2P_HOST_INCOMPLETE_DIR])


def create_run_docker(container_name, image, password):
    """
        创建 transmission docker 容器, 返回容器的 id
    :param kwargs:
    :return:
    """
    client = get_docker_client(base_url=DOCKER_API_URL)
    volume_config = create_host_config(client=client)
    container = client.create_container(image=image, name=container_name, ports=[12345, (12345, "udp"), P2P_PORT],
                                        stdin_open=False, tty=False, environment={"ADMIN_PASS": password},
                                        host_config=volume_config)

    client.start(container=container,  port_bindings={"12345/udp": 12345, 12345: 12345,  P2P_PORT: ("0.0.0.0", P2P_PORT)})

    return container["Id"]


def create_torrent(path, name):
    """
        生成种子, 返回种子的 url
    :param path:
    :param name:
    :return:
    """
    create_cmd = "transmission-create -t %s" \
                 " %s -p %s.torrent" % (TRACKER_URL, path, name)
    os.popen(create_cmd)
    torrent_name = "%s.torrent" % name
    return torrent_name


@app.route('/')
def hello_world():
    dic = {"username": "xutao"}
    return jsonify(**dic)


@app.route('/torrents/', methods=["POST"])
def create_torrent():
    result = {"status": "ok", "msg": "get it"}
    if request.method == "POST":
        data = request.form
        token = data.get("token", "")
        if token == TOKEN:
            # 正常的请求
            path = data.get("path", "")
            name = data.get("name", "")
            torrent = create_torrent(path=path, name=name)
            result["data"] = torrent
            return jsonify(**result)

        else:
            # 非正常的请求
            result["status"] = "error"
            result["msg"] = "you are forbid"
            result["data"] = {}

            return jsonify(**result)


@app.route("/containers/", methods=["POST"])
def create_container():
    result = {"status": "ok", "msg": "do it"}
    if request.method == "POST":
        data = request.form
        token = data.get("token", "")
        if token == TOKEN:
            # 正常的请求
            container_name = data.get("container_name", "")
            image = data.get("image", "")
            password = data.get("password", "")
            container_id = create_run_docker(container_name=container_name, password=password, image=image)
            result["data"] = container_id
            return jsonify(**result)

        else:
            # 非正常的请求
            result["status"] = "error"
            result["msg"] = "you are forbid"
            result["data"] = {}

            return jsonify(**result)


if __name__ == '__main__':
    app.run()