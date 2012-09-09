#!/usr/bin/env python
# -*- coding: utf-8 -
from gevent import monkey
monkey.patch_all()

worker_class = "socketio.sgunicorn.GeventSocketIOWorker"
