# -*- coding: utf-8 -*-
# __author__ = xutao

from flask import Flask
from flask import jsonify
import os
from flask import request


app = Flask(__name__)

TOKEN = "TEST"

TRACKER_URL = "http://205.177.85.132/peertracker/mysql/announce.php"


def create_docker(**kwargs):
    """
        创建 docker 容器
    :param kwargs:
    :return:
    """
    pass


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

if __name__ == '__main__':
    app.run()