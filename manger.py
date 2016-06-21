# -*- coding: utf-8 -*-
# __author__ = xutao
import codecs
codecs.register(lambda name: codecs.lookup('utf8') if name == 'utf8mb4' else None)
from flask.ext.script import Manager, Shell, Server
import logging

from api import app

app.debug = True

manager = Manager(app=app)

logger = logging.getLogger('file')


def make_shell_context():
    return dict(app=app)


manager.add_command("shell", Shell(make_context=make_shell_context))

if __name__ == '__main__':
    manager.run()