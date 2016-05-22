# -*- coding: utf-8 -*-
# __author__ = xutao

from flask import Flask
from flask import jsonify
import os
from flask import request


app = Flask(__name__)

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
        生成种子
    :param path:
    :param name:
    :return:
    """
    create_cmd = "transmission-create -t %s" \
                 " %s -p %s.torrent" % (TRACKER_URL, path, name)
    os.popen(create_cmd)


@app.route('/')
def hello_world():
    dic = {"username": "xutao"}
    return jsonify(**dic)


@app.route('/torrents/', methods=["POST"])
def create_torrent():
    dic = {"username": "xutao"}
    return jsonify(**dic)

if __name__ == '__main__':
    app.run()