# Bux ansible services (debian)

## Requirements

First you need some debian packages

```
sudo apt-get install python python-dev build-essential
```

Then install python dependencies (in virtual env)

```
pip install -r requirements.txt
```

## Example with docker

Start a fresh debian container
```
docker run -d --name ansible_sandbox_1 buxx/debian_ansible_sandbox
```

Build hosts file with container ip (it will be a [lamp] and [web] server)
```
python make_hosts.py $(docker inspect --format '{{ .NetworkSettings.IPAddress }}' ansible_sandbox_1)
```

Run playbook on it
```
ansible-playbook -i hosts --private-key docker/sandbox/debian/id_rsa_ansible -u ansible --sudo playbooks/lamp.yml
```
