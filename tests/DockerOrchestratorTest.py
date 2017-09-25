# -*- coding: utf-8 -*-
from unittest import TestCase

import docker
import os
import requests
import requests.exceptions
from docker import DockerClient
from docker.errors import DockerException, TLSParameterError
from mock import patch

from DockerOrchestrator import DockerOrchestrator
from exc import SetupError, ConnectionError

absolute_dir = os.path.normpath(os.path.join(os.path.abspath(__file__), '..'))


class DockerOrchestratorTest(TestCase):
    def setUp(self):
        self.orchestrator = DockerOrchestrator()
        self.project_base_path = os.path.join(absolute_dir, 'fixtures/')

    def test__parse_descriptor__valid_descriptor__pass(self):
        # do
        self.orchestrator.parse_descriptor(os.path.join(self.project_base_path, 'docker-compose'))

        # check
        self.assertIsNotNone(self.orchestrator.project)

    def test__validate_descriptor__valid_descriptor__pass(self):
        # prepare
        self.orchestrator.parse_descriptor(os.path.join(self.project_base_path, 'docker-compose'))
        expected_services = ['web', 'redis']
        expected_networks = ['default']
        expected_volumes = []

        # do
        self.orchestrator.validate_descriptor()

        # check
        self.assertEqual(self.orchestrator.services, expected_services)
        self.assertEqual(self.orchestrator.volumes, expected_volumes)
        self.assertEqual(self.orchestrator.networks, expected_networks)

    @patch('DockerOrchestrator.TopLevelCommand.up', return_value=0)
    def test__create_infrastructure__pass(self, command):
        # Prepare
        self.orchestrator.parse_descriptor(os.path.join(self.project_base_path, 'docker-compose'))

        # do
        try:
            self.orchestrator.create_infrastructure()
        except Exception as exc:
            self.fail('Exception "{}" raised.'.format(exc.message))

        # check
        self.assertEqual(command.call_count, 1)

    @patch('DockerOrchestrator.TopLevelCommand.up', return_value=1)
    def test__create_infrastructure__exception(self, command):
        # Prepare
        self.orchestrator.parse_descriptor(os.path.join(self.project_base_path, 'docker-compose'))

        # do
        with self.assertRaises(SetupError):
            self.orchestrator.create_infrastructure()

        # check
        self.assertEqual(command.call_count, 1)

    @patch('DockerOrchestrator.TopLevelCommand.up', return_value=0)
    @patch('DockerOrchestrator.TopLevelCommand.down', return_value=1)
    def test__stop_infrastructure__pass(self, down, up):
        # prepare
        self.orchestrator.parse_descriptor(os.path.join(self.project_base_path, 'docker-compose'))
        self.orchestrator.create_infrastructure()
        down.return_value = None

        # do
        self.orchestrator.destroy_infrastructure()

        # check
        self.assertEqual(up.call_count, 1)
        self.assertEqual(down.call_count, 1)

    @patch('DockerOrchestrator.docker.client.APIClient.get')
    def test__get_instance__no_explicit_host__pass(self, get):
        # prepare
        get.return_value = requests.Response()
        get.return_value.status = 200

        # do
        try:
            self.orchestrator.get_instance()
        except DockerException as exc:
            self.fail('get_instance() should not fail with "{}"'.format(exc.__repr__()))

        # check
        self.assertEqual(get.call_count, 1)

    @patch('DockerOrchestrator.docker.client.APIClient.get')
    def test__get_instance__explicit_host__pass(self, get):
        # prepare
        get.return_value = requests.Response()
        get.return_value.status = 200

        hosts = [
            'unix:///var/run/docker.sock',
            'tcp://128.104.222.48:2376'
        ]

        # do
        try:
            for host in hosts:
                self.orchestrator.settings.docker['DOCKER_HOST'] = host
                self.orchestrator.get_instance()
        except DockerException as exc:
            self.fail('get_instance() should not fail with "{}"'.format(exc.__repr__()))

        # check
        self.assertEqual(get.call_count, len(hosts))

    @patch('DockerOrchestrator.docker.api.daemon.DaemonApiMixin.ping')
    def test__get_instance__host_unreachable__exception(self, ping):
        # prepare
        ping.side_effect = docker.errors.APIError(message='')
        self.orchestrator.settings.docker['DOCKER_HOST'] = 'unix:///var/run/docker.sock'

        # do
        with self.assertRaises(docker.errors.APIError):
            self.orchestrator.get_instance()

        # check
        self.assertEqual(ping.call_count, 1)

    @patch('DockerOrchestrator.docker.api.daemon.DaemonApiMixin.ping')
    def test__get_instance__tls_host__pass(self, ping):
        # prepare
        self.orchestrator.settings.docker['DOCKER_HOST'] = 'tcp://192.168.99.100:2376'
        self.orchestrator.settings.docker['DOCKER_CERT_PATH'] = os.path.join(self.project_base_path, 'certs')

        ping.return_value = None

        # do
        try:
            self.orchestrator.get_instance()
        except DockerException as exc:
            self.fail('get_instance() should not fail with "{}"'.format(exc.__repr__()))

        self.assertIsInstance(self.orchestrator.docker, DockerClient)

    @patch('DockerOrchestrator.docker.api.daemon.DaemonApiMixin.ping')
    def test__get_instance__tls_host_invalid__exception(self, ping):
        # prepare
        self.orchestrator.settings.docker['DOCKER_HOST'] = 'tcp://192.168.99.100:2376'
        self.orchestrator.settings.docker['DOCKER_CERT_PATH'] = 'not-existing-dir'

        ping.side_effect = docker.errors.TLSParameterError(msg='Path to a certificate and key files')

        # do
        with self.assertRaisesRegexp(TLSParameterError, 'Path to a certificate and key files') as exc:
            self.orchestrator.get_instance()

    @patch('DockerOrchestrator.docker.api.daemon.DaemonApiMixin.ping')
    def test__get_instance__insecure_request_fails__exception(self, mock_ping):
        # prepare
        self.orchestrator.settings.docker['DOCKER_HOST'] = 'tcp://192.168.99.100:2376'
        mock_ping.side_effect = requests.exceptions.ConnectionError('BadStatusLine')

        # do
        with self.assertRaisesRegexp(ConnectionError, 'BadStatusLine'):
            self.orchestrator.get_instance()

    @patch('DockerOrchestrator.docker.api.daemon.DaemonApiMixin.ping')
    def test__get_instance__unreachable_host__exception(self, mocked_ping):
        # prepare
        self.orchestrator.settings.docker['DOCKER_HOST'] = 'tcp://127.8.8.8:2376'
        mocked_ping.side_effect = requests.exceptions.ConnectionError('timed out')

        # do
        with self.assertRaisesRegexp(ConnectionError, 'timed out'):
            self.orchestrator.get_instance()
            self.fail()

