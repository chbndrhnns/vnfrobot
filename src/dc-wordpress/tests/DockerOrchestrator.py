# -*- coding: utf-8 -*-

from robot.api import logger

import requests.exceptions
from compose.cli.main import TopLevelCommand, project_from_options

from Orchestrator import Orchestrator
from exc import SetupError, ConnectionError


class DockerOrchestrator(Orchestrator):
    default_options = {"--no-deps": False,
                       "--abort-on-container-exit": False,
                       "SERVICE": "",
                       "--remove-orphans": False,
                       "--no-recreate": True,
                       "--force-recreate": False,
                       "--build": False,
                       '--no-build': False,
                       '--no-color': False,
                       "--rmi": "none",
                       "--volumes": "",
                       "--follow": False,
                       "--timestamps": True,
                       "--tail": "all",
                       "-d": True,
                       "--scale": ""
                       }

    default_config_options = {"--services": False,
                              "--volumes": False,
                              "--resolve-image-digests": False,
                              "--quiet": True}

    def __init__(self):
        super(DockerOrchestrator, self).__init__()

        self.project = None
        self.volumes = None
        self.networks = None
        self.services = None
        self.commands = None

    def get_instance(self):
        raise NotImplementedError

    def parse_descriptor(self, project_path):
        logger.debug(u'Parsing descriptor at "{}"'.format(project_path))

        self.project = project_from_options(project_dir=project_path, options=self.default_options)
        self.commands = TopLevelCommand(self.project)

    def validate_descriptor(self):
        self.commands.config(config_options=self.default_options, options=self.default_config_options)

        self.services = [getattr(service, 'name') for service in self.project.services]
        self.volumes = [volume for volume in self.project.volumes.volumes]
        self.networks = [getattr(network, 'name') for network in self.project.networks.networks.values()]

    def create_infrastructure(self):
        try:
            logger.debug(u'Creating infrastructure (this can take a while)...')

            return_code = self.commands.up(options=self.default_options)

            if return_code is not 0:
                if return_code is not None:
                    raise SetupError('Could not create infrastructure', return_code)
        except requests.exceptions.ConnectionError as exc:
            logger.error(u'{}'.format(exc))
            if 'No such file or directory' in str(exc.message):
                raise ConnectionError('Could not connect to url={}'.format(exc.request.url), exc)
            else:
                raise ConnectionError('Not specified connection error.')
