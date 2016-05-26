#!/bin/bash
docker build -t xutaomac/flask_agent .
docker run -d --name agent -p 0.0.0.0:5000:5000  -v /var/run/docker.sock:/var/run/docker.sock xutaomac/flask_agent