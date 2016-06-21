# -*- coding: utf-8 -*-
# __author__ = xutao

from flask import Flask
from flask import jsonify
import os
from flask import request
import docker
from celery import Celery
import subprocess
from subprocess import PIPE

app = Flask(__name__)

# just for other celery task
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/2'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/2'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

TOKEN = "TEST"

TRACKER_URL = "http://205.177.85.132/peertracker/mysql/announce.php"

DOCKER_API_URL = "unix:///var/run/docker.sock"

P2P_PORT = 9091

P2P_HOST_DOWNLOAD_DIR = '/var/tmp/downloads/'

P2P_HOST_INCOMPLETE_DIR = "/var/tmp/incomplete/"

P2P_CENTER_HOST = ""


def task_callback(task_id, status, msg):
    """
        任务完成回调
    :return:
    """

    url = "http://%s/task/callback/" % P2P_CENTER_HOST

    data = {
        "type": "create_torrent",
        "task_id": task_id,
        "status": status,
        "msg": msg
    }

    response = request.post(url, data=data)
    if response.ok:
        return True
    return False


def stop(client, container_id):
    """
        停止指定的容器
    :param container_id:
    :return:
    """
    client.stop(container_id=container_id)
    return True


def get_docker_client(base_url):
    """
        获取 docker 代理
    :param base_url:
    :return:
    """
    client = docker.Client(base_url=base_url)
    return client


def my_create_host_config(client, port):
    """
        配置 host
    :param client:
    :return:
    """
    return client.create_host_config(binds=["%s:/var/lib/transmission-daemon/downloads" % P2P_HOST_DOWNLOAD_DIR,
                                            "%s:/var/lib/transmission-daemon/incomplete" % P2P_HOST_INCOMPLETE_DIR],
                                     port_bindings={port: ("0.0.0.0", port), "64321/udp": 64321, 64321: 64321})


def create_test_container(container_name):
    """
        创建测试容器
    :param client:
    :return:
    """
    try:
        client = get_docker_client(base_url=DOCKER_API_URL)
        container = client.create_container(image="ubuntu", tty=True, name=container_name)
        client.start(container=container)
        return container
    except Exception as e:
        print(e)


def create_run_docker(container_name, image, password, port):
    """
        创建 transmission docker 容器, 返回容器的 id
    :param kwargs:
    :return:
    """
    try:
        client = get_docker_client(base_url=DOCKER_API_URL)
        config = my_create_host_config(client=client, port=port)
        container = client.create_container(image=image, name=container_name, ports=[64321, (64321, "udp"), port],
                                            stdin_open=False, tty=False, environment={"ADMIN_PASS": password},
                                            host_config=config)

        client.start(container=container)

        return container["Id"]
    except Exception as e:
        print(str(e))


@celery.task
def create_torrent(path, name, comment, task_id):
    """
        生成种子, 返回种子的 url
    :param path:
    :param name:
    :return:
    """
    try:
        server_path = "%s/%s" % ("/var/tmp/torrents", name)
        create_cmd = "transmission-create -t %s" \
                     "-c %s %s -o %s.torrent" % (TRACKER_URL, comment, path, server_path)
        process = subprocess.Popen(create_cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        result = process.communicate()
        task_callback(task_id=task_id, status="SUCCESS", msg="create torrent ok")
        return True
    except Exception as e:
        print(str(e))
        task_callback(task_id=task_id, status="ERROR", msg=str(e))


@app.route('/', methods=["POST"])
def hello_world():
    dic = request.form
    name = dic.get("name")
    container_id = create_test_container(container_name=name)
    dic = {"id": container_id}

    return jsonify(**dic)


@app.route('/test/', methods=["POST"])
def hello_test():
    dic = {
        "test": "yes"
    }
    return jsonify(**dic)


@app.route('/torrents/', methods=["POST"])
def torrents():
    """
        创建种子
    :return:
    """
    result = {"status": "ok", "msg": "get it"}
    if request.method == "POST":
        data = request.form
        token = data.get("token", "")
        if token == TOKEN:
            # 正常的请求
            path = data.get("path", "")
            name = data.get("name", "")
            comment = data.get("comment", "tests")
            task_id = data.get("task_id")
            create_torrent.delay(path, name, comment, task_id)
            return jsonify(**result)

        else:
            # 非正常的请求
            result["status"] = "error"
            result["msg"] = "you are forbid"
            result["data"] = {}

            return jsonify(**result)


@app.route("/containers/", methods=["POST", "PUT"])
def containers():
    """
        创建容器
    :return:
    """
    result = {"status": "ok", "msg": "do it"}
    if request.method == "POST":
        data = request.form
        token = data.get("token", "")
        if token == TOKEN:
            # 正常的请求
            container_name = data.get("container_name", "")
            image = data.get("image", "")
            password = data.get("password", "")
            port = data.get("port", 9091)
            container_id = create_run_docker(container_name=container_name, password=password, image=image, port=port)
            result["data"] = container_id
            return jsonify(**result)

        else:
            # 非正常的请求
            result["status"] = "error"
            result["msg"] = "you are forbid"
            result["data"] = {}

            return jsonify(**result)

    if request.method == "PUT":
        # 目前支持 关闭 操作
        data = request.form
        action = data.get("action", "stop")
        container_id = data.get("container_id", "")
        if action == "stop":
            client = get_docker_client(base_url=DOCKER_API_URL)
            stop(client=client, container_id=container_id)
            result["data"] = {}
            return jsonify(**result)

if __name__ == '__main__':
    app.run(host="0.0.0.0")