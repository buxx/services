FROM debian

RUN export DEBIAN_FRONTEND=noninteractive && \
    apt-get update && apt-get install -y sudo libnet-ifconfig-wrapper-perl \
    openssh-server python python-dev

RUN useradd ansible --home /home/ansible --create-home && \
    echo "\nansible ALL=(ALL) NOPASSWD: ALL\n" >> /etc/sudoers && \
    chown ansible:ansible -R /home/ansible

COPY id_rsa_ansible.pub /home/ansible/.ssh/authorized_keys

CMD service ssh start && tailf /var/log/faillog

