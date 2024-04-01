FROM python:3.11
RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y tini
WORKDIR /root/workspace

# Use tini as the entrypoint and keep the container running
# tini forwards exit signals to sleep, thus fixing "docker stop" taking 10 seconds
ENTRYPOINT ["/usr/bin/tini", "--", "sleep", "infinity"]
