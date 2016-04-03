#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import os
import shutil
import yaml
from jinja2 import Environment, FileSystemLoader


class Described(object):
    def __init__(self, name, description):
        self._name = name
        self._description = description

    @property
    def name(self):
        return self._name

    def __getattr__(self, item):
        return self._description[item]


class Host(Described):
    pass


class Project(Described):

    def get_hosts(self):
        return [Host(name, description) for name, description in self.hosts.items()]

    def get_hosts_groups(self):
        groups = []
        for host_name, host in self.hosts.items():
            for group in host['groups']:
                if group not in groups:
                    groups.append(group)
        # groups = set([group for group in host.groups for host in hosts]) ?
        return groups


class Loader(object):
    @staticmethod
    def load(file_path):
        with open(file_path, 'r') as f:
            description = yaml.load(f.read())
            name = file_path.split('.')[-2]
            return Project(name, description)


class Builder(object):
    def __init__(self, project, output, templates_dir='./templates'):
        self._project = project
        self._env = Environment(loader=FileSystemLoader(templates_dir))
        self._build_dir = "%s/%s" % (output, self._project.name)
        self._templates_dir = templates_dir

    def build(self):
        self.build_hosts()
        self.build_hosts_tasks()

    def build_hosts(self):
        hosts = self.get_hosts_build(self._project.get_hosts())
        self._output('hosts', hosts)

    def build_hosts_tasks(self):
        output_dir = "%s/tasks/group" % self._build_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for group in self._project.get_hosts_groups():
            group_tasks_file = "%s/tasks/groups/%s.yml" % (self._templates_dir, group)
            if not os.path.exists(group_tasks_file):
                raise Exception("Host group tasks file not found: \"%s\"" % group_tasks_file)

            shutil.copyfile(group_tasks_file, "%s/%s.yml" % (output_dir, group))

    def _output(self, file_path, content):
        if not os.path.exists(self._build_dir):
            os.makedirs(self._build_dir)
        with open("%s/%s" % (self._build_dir, file_path), "wb") as f:
            f.write(content)

    def get_hosts_build(self, hosts):
        template = self._env.get_template('hosts')
        groups = self._project.get_hosts_groups()
        return template.render(hosts=hosts, groups=groups)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Build ansible files')
    parser.add_argument('project', help='Project description file path')
    parser.add_argument('--to', default='./builds', dest='to', help='Output directory path')
    args = parser.parse_args()

    project = Loader.load(args.project)
    builder = Builder(project, args.to)
    builder.build()
