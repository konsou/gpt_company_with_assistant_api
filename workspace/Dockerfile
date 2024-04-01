FROM python:3.11
RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y tini openssh-server

# SSH config
RUN mkdir /var/run/sshd
COPY ssh/workspace-ssh-key.pub /root/.ssh/authorized_keys
RUN chmod 600 /root/.ssh/authorized_keys
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN sed -i 's/#PubkeyAuthentication yes/PubkeyAuthentication yes/' /etc/ssh/sshd_config

WORKDIR /root/workspace

# Use tini as the entrypoint and keep the container running
# tini forwards exit signals, thus fixing "docker stop" taking 10 seconds
ENTRYPOINT ["/usr/sbin/sshd", "-D"]
# ENTRYPOINT ["/usr/bin/tini", "--", "/usr/sbin/sshd", "-D"]
