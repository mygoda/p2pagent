# -*- coding: utf-8 -*-
# __author__ = xutao

from flask import Flask
from flask import jsonify
import os
from flask import request
import requests
from celery import Celery
import subprocess
from subprocess import PIPE

app = Flask(__name__)

# just for other celery task
app.config['CELERY_BROKER_URL'] = 'redis://:@localhost:6379/2'
app.config['CELERY_RESULT_BACKEND'] = 'redis://:@localhost:6379/2'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

TOKEN = "p2pagent"

TRACKER_URL = "http://205.177.85.132/peertracker/mysql/announce.php"

P2P_PORT = 9091

P2P_HOST_DOWNLOAD_DIR = '/var/tmp/downloads/'

P2P_HOST_INCOMPLETE_DIR = "/var/tmp/incomplete/"

P2P_CENTER_HOST = "101.251.255.234:9999"


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

    response = requests.post(url, data=data)
    if response.ok:
        return True
    return False


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
        create_cmd = "transmission-create -t %s -c " \
                     "%s %s -o %s.torrent" % (TRACKER_URL, comment, path, server_path)
        process = subprocess.Popen(create_cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        result = process.communicate()
        cmd = "chmod 755 %s.torrent" % server_path
        chmod_cmd = subprocess.Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        chmod_cmd.communicate()

        task_callback(task_id=task_id, status="SUCCESS", msg="create torrent ok")
        return True
    except Exception as e:
        print(str(e))
        task_callback(task_id=task_id, status="ERROR", msg=str(e))


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
            name = data.get("vm_name", "")
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


if __name__ == '__main__':
    app.run(host="0.0.0.0")
