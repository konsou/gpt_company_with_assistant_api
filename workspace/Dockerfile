FROM python:3.11
RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y openssh-server

# SSH config
RUN mkdir /var/run/sshd
COPY ssh/workspace-ssh-key.pub /root/.ssh/authorized_keys
RUN chmod 600 /root/.ssh/authorized_keys
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN sed -i 's/#PubkeyAuthentication yes/PubkeyAuthentication yes/' /etc/ssh/sshd_config

WORKDIR /root/workspace

ENTRYPOINT ["/usr/sbin/sshd", "-D"]
