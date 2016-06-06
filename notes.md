# notes

Notes on getting performance things working for keystone.

## steps

1.) install modern pip
  curl https://bootstrap.pypa.io/get-pip.py | sudo python
2.)_install common dependencies
  sudo apt-get install build-essential python-dev libffi-dev libssl-dev
3.) make /etc/ansible
  sudo mkdir /etc/ansible
4.) make sure the user we are using can access it
  sudo chown -R ubuntu:ubuntu /etc/ansible/
5.) install ansible-galaxy requirements
  ansible-galaxy install --role-file=ansible-role-requirements.yml --force
6.) setup performance host
  ansible-playbook -i inventory_localhost --user='root' --sudo setup_perf_host.yml

