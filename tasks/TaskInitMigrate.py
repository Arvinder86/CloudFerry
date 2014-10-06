# Copyright (c) 2014 Mirantis Inc.
#
# Licensed under the Apache License, Version 2.0 (the License);
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an AS IS BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and#
# limitations under the License.

from migrationlib.os.exporter import osExporter, osResourceExporter
from migrationlib.os.importer import osImporter, osResourceImporter
from scheduler.Task import Task
from fabric.api import env
from utils import get_log, check_config_file
import yaml

__author__ = 'mirrorcoder'

LOG = get_log(__name__)


class TaskInitMigrate(Task):

    @staticmethod
    def get_exporter(config):
        return {
            'os': lambda info: (osResourceExporter.ResourceExporter(info), osExporter.Exporter(info))
        }[config['clouds']['source']['type']](config)

    @staticmethod
    def get_importer(config):
        return {
            'os': lambda info: (osResourceImporter.ResourceImporter(info), osImporter.Importer(info))
        }[config['clouds']['destination']['type']](config)

    @staticmethod
    def init_migrate(name_config):
        config = yaml.load(open(name_config, 'r'))
        if check_config_file(name_config, "networks"):
            config["networks"] = yaml.load(open(check_config_file(name_config, "networks"), 'r'))
        exporter = TaskInitMigrate.get_exporter(config)
        importer = TaskInitMigrate.get_importer(config)
        return config, exporter, importer

    def run(self, __name_config__="", name_instance="", tenant_id="", **kwargs):
        LOG.info("Init migrationlib config")
        config, (res_exporter, inst_exporter), (res_importer, inst_importer) = \
            TaskInitMigrate.init_migrate(__name_config__)
        if name_instance:
            config['instances'] = {'name': name_instance}
            # config['instances']['name'] = name_instance
            if tenant_id:
                config['instances']['tenant_id'] = tenant_id
        env.key_filename = config['key_filename']['name']
        return {
            'config': config,
            'res_exporter': res_exporter,
            'res_importer': res_importer,
            'inst_exporter': inst_exporter,
            'inst_importer': inst_importer
        }
