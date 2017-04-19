# Copyright (c) Trainline Limited, 2017. All rights reserved. See LICENSE.txt in the project root for license information.

import envmgr

from unittest import TestCase
from mock import patch
from envmgr import ASG

class TestASG(TestCase):
    
    @classmethod
    def setUpClass(cls):
        envmgr.config('host', 'user', 'dGVzdA==')

    @patch('environment_manager.EMApi.get_asg')
    def test_get_schedule_requests_asg(self, mock_get_asg):
        asg = ASG('test-asg-name', 'TE1')
        schedule = asg.get_schedule()
        mock_get_asg.assert_called_with('TE1', 'test-asg-name')
    
    @patch('environment_manager.EMApi.get_asg')
    def test_get_schedule_with_empty_asg(self, mock_get_asg):
        mock_get_asg.return_value = {}
        asg = ASG('test-asg-name', 'TE1')
        schedule = asg.get_schedule()
        self.assertIsNone(schedule)

    @patch('environment_manager.EMApi.get_asg')
    def test_get_unknown_schedule(self, mock_get_asg):
        mock_get_asg.return_value = {'Tags':[{'Key':'Environment', 'Value':'test'}]}
        asg = ASG('test-asg-name', 'TE1')
        schedule = asg.get_schedule()
        self.assertIsNone(schedule)
    
    @patch('environment_manager.EMApi.get_asg')
    def test_get_schedule_returns_tag(self, mock_get_asg):
        mock_get_asg.return_value = {'Tags':[
            {'Key':'Environment', 'Value':'test'},
            {'Key':'Schedule', 'Value':'Start: * * 2 *; Stop: * * 4 *'}
        ]}
        asg = ASG('test-asg-name', 'TE1')
        schedule = asg.get_schedule()
        self.assertEqual(schedule, {'Key':'Schedule', 'Value':'Start: * * 2 *; Stop: * * 4 *'})

    @patch('environment_manager.EMApi.get_asg')
    def test_not_exists_on_exception(self, mock_get_asg):
        mock_get_asg.side_effect = Exception('')
        asg = ASG('test-asg-name', 'TE1')
        exists = asg.exists()
        self.assertFalse(exists)

    @patch('environment_manager.EMApi.get_asg')
    def test_exists(self, mock_get_asg):
        asg = ASG('test-asg-name', 'TE1')
        exists = asg.exists()
        self.assertTrue(exists)

    @patch('environment_manager.EMApi.put_asg_scaling_schedule')
    def test_set_schedule_data(self, mock_put_schedule):
        asg = ASG('test-asg-name', 'TE1')
        asg.set_schedule('ON')
        mock_put_schedule.assert_called_with(
            environment='TE1', 
            asgname='test-asg-name', 
            data={'propagateToInstances':True, 'schedule':'ON'}
        )

    @patch('environment_manager.EMApi.get_asg_ready')
    def test_get_status_calls_asg_ready(self, mock_get_asg_ready):
        asg = ASG('test-asg-name', 'TE1')
        asg.get_status()
        mock_get_asg_ready.assert_called_once()

