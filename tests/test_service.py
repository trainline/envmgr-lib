# Copyright (c) Trainline Limited, 2017. All rights reserved. See LICENSE.txt in the project root for license information.

import envmgr

from unittest import TestCase
from mock import patch, ANY
from envmgr import Service

class TestService(TestCase):
    
    @classmethod
    def setUpClass(cls):
        envmgr.config('host', 'user', 'dGVzdA==')

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

    @patch('environment_manager.EMApi.get_service_slices')
    def test_get_slices_defaults_to_active(self, mock_get_slices):
        service = Service('TestService', 'TE1')
        slices = service.get_slices()
        mock_get_slices.assert_called_with('TestService', 'TE1', 'true')
        
    @patch('environment_manager.EMApi.get_service_slices')
    def test_get_slices_converts_bool_to_string(self, mock_get_slices):
        service = Service('TestService', 'TE1')
        slices = service.get_slices(False)
        mock_get_slices.assert_called_with('TestService', 'TE1', 'false')
    
    def test_publish_requires_version(self):
        service = Service('TestService', 'TE1')
        with self.assertRaises(Exception) as context:
            service.publish({})
        self.assertTrue('You must provide a version' in context.exception)

    def test_publish_no_reset_version(self):
        service = Service('TestService', 'TE1', '1.0.0')
        with self.assertRaises(Exception) as context:
            service.publish({}, '2.0.0')
        self.assertTrue('You cannot reassign a Service version once it is set' in context.exception)

    @patch('requests.put')
    @patch('environment_manager.EMApi.get_package_upload_url')
    def test_publish_with_version_gets_package_url(self, mock_package_url, mock_requests):
        service = Service('TestService', 'TE1')
        service.publish({}, '1.0.0')
        mock_package_url.assert_called_with('TestService', '1.0.0')

    @patch('requests.put')
    @patch('environment_manager.EMApi.get_package_upload_url_environment')
    def test_publish_with_version_and_env_gets_package_url(self, mock_package_url, mock_requests):
        service = Service('TestService', 'TE1')
        service.publish({}, '1.0.0', 'SomeEnv')
        mock_package_url.assert_called_with('TestService', '1.0.0', 'SomeEnv')
    
    @patch('requests.put')
    @patch('environment_manager.EMApi.get_package_upload_url')
    def test_publish_with_preset_version_gets_package_url(self, mock_package_url, mock_requests):
        service = Service('TestService', 'TE1', '4.2.0')
        service.publish({})
        mock_package_url.assert_called_with('TestService', '4.2.0')
    
    @patch('requests.put')
    @patch('environment_manager.EMApi.get_package_upload_url')
    def test_publish_sets_correct_content_type(self, mock_package_url, mock_put):
        service = Service('TestService', 'TE1', '5.0.0')
        service.publish({})
        (args, kwargs) = mock_put.call_args
        headers = kwargs.get('headers')
        self.assertEqual(headers.get('content-type'), 'application/zip')

    @patch('requests.put')
    @patch('environment_manager.EMApi.get_package_upload_url')
    def test_publishes_to_provided_url(self, mock_package_url, mock_put):
        upload_url = 'https://s3.acme.com/bucket/file?TOKEN'
        mock_package_url.return_value = {'url':upload_url}
        service = Service('TestService', 'TE1', '5.0.0')
        service.publish({})
        (args, kwargs) = mock_put.call_args
        request_url = args[0]
        self.assertEqual(request_url, upload_url)

    def test_deploy_requires_version(self):
        service = Service('TestService', 'TE1')
        with self.assertRaises(Exception) as context:
            service.deploy()
        self.assertTrue('You must provide a version' in context.exception)

    def test_deploy_no_reset_version(self):
        service = Service('TestService', 'TE1', '1.0.0')
        with self.assertRaises(Exception) as context:
            service.deploy('2.0.0')
        self.assertTrue('You cannot reassign a Service version once it is set' in context.exception)

    @patch('environment_manager.EMApi.post_deployments')
    def test_deploy_posts_default_data(self, mock_post_deployments):
        service = Service('TestService', 'TE1', '7.1.0')
        service.deploy()
        mock_post_deployments.assert_called_with('false', {
            'environment':'TE1',
            'service':'TestService',
            'version':'7.1.0',
            'mode':'overwrite'
        })

    @patch('environment_manager.EMApi.post_deployments')
    def test_deploy_slice_sets_correct_mode(self, mock_post_deployments):
        service = Service('TestService', 'TE1', '7.1.0')
        service.deploy(slice='blue')
        mock_post_deployments.assert_called_with('false', {
            'environment':'TE1',
            'service':'TestService',
            'version':'7.1.0',
            'mode':'bg',
            'slice':'blue'
        })

    @patch('environment_manager.EMApi.post_deployments')
    def test_deploy_dry_run_bool_to_string(self, mock_post_deployments):
        service = Service('TestService', 'TE1', '4.5.6')
        service.deploy(dry_run=True)
        mock_post_deployments.assert_called_with('true', {
            'environment':'TE1',
            'service':'TestService',
            'version':'4.5.6',
            'mode':'overwrite',
        })

    @patch('environment_manager.EMApi.post_deployments')
    def test_deploy_provided_version(self, mock_post_deployments):
        service = Service('TestService', 'TE1')
        service.deploy(version='8.9.1')
        mock_post_deployments.assert_called_with('false', {
            'environment':'TE1',
            'service':'TestService',
            'version':'8.9.1',
            'mode':'overwrite',
        })

    @patch('environment_manager.EMApi.post_deployments')
    def test_deploy_returns_response_id(self, mock_post_deployments):
        id = 'a67d92174feadcbeacb8ef'
        mock_post_deployments.return_value = {'id':id}
        service = Service('TestService', 'TE1', '10.0.0')
        deployment = service.deploy()
        self.assertEqual(id, deployment.get('id'))
    
    def test_get_deployment_raises_when_no_id(self):
        service = Service('TestService', 'TE1')
        with self.assertRaises(Exception) as context:
            service.get_deployment()
        self.assertTrue('There is no deploy_id set for this service' in context.exception)

