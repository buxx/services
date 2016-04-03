#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import os
import shutil
import yaml
from jinja2 import Environment, FileSystemLoader, Template
from slugify import slugify


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

    def get_service(self, service_name):
        for service in self.services:
            if service['name'] == service_name:
                return service
        raise Exception("Service %s not found" % service_name)

    def get_vars(self):
        return self.vars


class Loader(object):
    @staticmethod
    def load(file_path):
        with open(file_path, 'r') as f:
            description = yaml.load(f.read())
            name = file_path.split('.')[-2]
            return Project(name, description)


class Model(object):
    name = NotImplemented
    defaults = {}

    def __init__(self, builder, service):
        self._builder = builder
        self._service = service

    @property
    def service_slug(self):
        return slugify(self._service['name'])

    @property
    def service_name(self):
        return self._service['name']

    def get_parameter(self, parameter_name):
        return self.get_parameters()[parameter_name]

    def get_parameters(self):
        parameters = self._service['parameters'][self.name]
        for default_parameter in self.defaults:
            if default_parameter not in parameters:
                parameters[default_parameter] = self.defaults[default_parameter](self)
        return parameters

    def render(self, **kwargs):
        template_file_path = "%s/tasks/services/%s.yml" % (self._builder.template_dir, self.name)
        with open(template_file_path, 'r') as f:
            template = Template(f.read())
            kwargs.update(self._builder.project.get_vars())
            kwargs.update(self.get_parameters())
            kwargs.update({
                '__service_name__': self.service_name,
                '__model_name__': self.name
            })
            return template.render(**kwargs)

    def get_task(self):
        return self.render()


class LAMPWebsiteModel(Model):
    name = 'lamp_website'
    defaults = {
        'mysql_user_name': lambda model: model.service_slug,
        'mysql_database': lambda model: model.service_slug,
    }


class Models(object):
    _models = {
        LAMPWebsiteModel.name: LAMPWebsiteModel,
        # LAMPWebsiteBackupedModel.name: LAMPWebsiteBackupedModel,
    }

    @classmethod
    def get(cls, model_name, service, builder):
        return cls._models[model_name](builder, service)


class Services(object):
    def __init__(self, builder):
        self._builder = builder
        self._project = builder.project

    def get_tasks(self):
        tasks = []
        for service in self._project.services:
            service_name = service['name']
            for model_name in service['models']:
                task = self.get_task(service_name, model_name)
                task_name = "%s_%s" % (slugify(service_name), model_name)
                tasks.append((task_name, task))
        return tasks

    def get_task(self, service_name, model_name):
        service = self._project.get_service(service_name)
        model = Models.get(model_name, service, builder=self._builder)
        return model.get_task()


class Builder(object):
    def __init__(self, project, output, templates_dir='./templates'):
        self._project = project
        self._env = Environment(loader=FileSystemLoader(templates_dir))
        self._build_dir = "%s/%s" % (output, self._project.name)
        self._templates_dir = templates_dir

    @property
    def project(self):
        return self._project

    @property
    def template_dir(self):
        return self._templates_dir

    def build(self):
        self.build_hosts()
        self.build_project_vars()
        self.build_groups_tasks()
        services = self.get_services()
        self.build_services_tasks(services)
        self.build_hosts_tasks(services)

    def build_hosts(self):
        hosts = self.get_hosts_build(self._project.get_hosts())
        self._output('hosts', hosts)

    def get_services(self):
        return Services(self)

    def build_groups_tasks(self):
        from_dir = "%s/tasks/groups" % self._templates_dir
        to_dir = "%s/tasks/groups" % self._build_dir
        group_tasks = self._project.get_hosts_groups()

        self._copy_files(from_dir, to_dir, group_tasks)

        from_dir = "%s/playbooks/groups" % self._templates_dir
        to_dir = "%s/playbooks/groups" % self._build_dir
        group_tasks = self._project.get_hosts_groups()

        self._copy_files(from_dir, to_dir, group_tasks)

    def build_project_vars(self):
        self._output("vars.yml", yaml.safe_dump(self._project.vars, default_flow_style=False, indent=4))

    def build_hosts_tasks(self, services):
        pass

    def build_services_tasks(self, services):
        for task_name, task in services.get_tasks():
            self._output("tasks/services/%s.yml" % task_name, task)

    @staticmethod
    def _copy_files(from_dir, to_dir, files):
        if not os.path.exists(to_dir):
            os.makedirs(to_dir)

        for file_name in files:
            from_file_path = "%s/%s.yml" % (from_dir, file_name)
            if not os.path.exists(from_file_path):
                raise Exception("File not found: \"%s\"" % from_file_path)

            shutil.copyfile(from_file_path, "%s/%s.yml" % (to_dir, file_name))

    def _output(self, file_path, content):
        complete_file_path = "%s/%s" % (self._build_dir, file_path)
        complete_dir_path = '/'.join(complete_file_path.split('/')[0:-1])
        if not os.path.exists(complete_dir_path):
            os.makedirs(complete_dir_path)
        with open(complete_file_path, "wb") as f:
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
