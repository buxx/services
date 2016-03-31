#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sys import argv
from jinja2 import Template

with open('hosts.tpl', 'r') as f:
    template = Template(f.read())

with open('hosts', 'w') as f:
    hosts_content = template.render(ip=argv[1])
    f.write(hosts_content)
    f.write("\n")

print('Done')
