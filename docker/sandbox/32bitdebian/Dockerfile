FROM 32bit/debian

RUN export DEBIAN_FRONTEND=noninteractive && \
    apt-get update && apt-get install -y sudo libnet-ifconfig-wrapper-perl \
    openssh-server python python-dev

RUN useradd ansible --home /home/ansible --create-home && \
    echo "\nansible ALL=(ALL) NOPASSWD: ALL\n" >> /etc/sudoers

COPY id_rsa_ansible.pub /home/ansible/.ssh/authorized_keys

RUN chown ansible:ansible -R /home/ansible

CMD service ssh start && tailf /var/log/faillog

