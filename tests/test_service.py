# Copyright (c) Trainline Limited, 2017. All rights reserved. See LICENSE.txt in the project root for license information.

import emlib

from unittest import TestCase
from mock import patch
from emlib import Service

class TestService(TestCase):
    
    @classmethod
    def setUpClass(cls):
        emlib.config('host', 'user', 'dGVzdA==')

    def test_no_set_version(self):
        service = Service('TestService', 'TE1')
        with self.assertRaises(Exception) as context:
            service.version = '1.2.3'

    def test_no_set_deploy_id(self):
        service = Service('TestService', 'TE1')
        with self.assertRaises(Exception) as context:
            service.deploy_id = 'ade12398dbcbc139804278'

    @patch('environment_manager.EMApi.get_service_overall_health')
    def test_get_health_without_slice(self, mock_get_overall_health):
        service = Service('TestService', 'TE1')
        health = service.get_health()
        mock_get_overall_health.assert_called_with('TestService', 'TE1')
    
    @patch('environment_manager.EMApi.get_service_health')
    def test_get_health_with_slice(self, mock_get_service_health):
        service = Service('TestService', 'TE1')
        health = service.get_health('green')
        mock_get_service_health.assert_called_with('TestService', 'TE1', 'green')
