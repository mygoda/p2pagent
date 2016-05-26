#!/bin/bash
docker build -t xutaomac/flask_agent .
mkdir /var/tmp/torrent_tmp
docker run -d --name agent -p 0.0.0.0:5000:5000  -v /var/run/docker.sock:/var/run/docker.sock -v /var/tmp/torrent_tmp:/var/tmp/torrent_tmp xutaomac/flask_agent