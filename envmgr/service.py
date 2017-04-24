# Copyright (c) Trainline Limited, 2017. All rights reserved. See LICENSE.txt in the project root for license information.

import requests

from envmgr import EmClient, Upstream

class Service(object):

    @staticmethod
    def get_deployment_by_id(deploy_id):
        client = EmClient()
        return client.get_deployment(deploy_id)

    def __init__(self, name, env=None, version=None, deploy_id=None):
        self.name = name
        self.env = env
        self.__version = version
        self.__deploy_id = deploy_id
        self.client = EmClient()

    @property
    def version(self):
        return self.__version

    @property
    def deploy_id(self):
        return self.__deploy_id
    
    def __set_version(self, value):
        if self.__version is not None:
            raise Exception('You cannot reassign a Service version once it is set')
        self.__version = value

    def __require_version_set(self, value):
        if value is None and self.__version is None:
            raise Exception('You must provide a version')
        if value is not None:
            self.__set_version(value)

    def get_health(self, slice=None):
        if slice is None:
            result = self.client.get_service_overall_health(self.name, self.env)
            result = [ asg.get('Services') for asg in result.get('AutoScalingGroups') ]
            if result:
                return result[0]
            else:
                return None
        else:
            return self.client.get_service_health(self.name, self.env, slice)

    def get_slices(self, active=True):
        active = 'true' if active else 'false'
        return self.client.get_service_slices(self.name, self.env, active)

    def get_deployment(self):
        if self.__deploy_id is None:
            raise Exception('There is no deploy_id set for this service')
        return self.client.get_deployment(self.__deploy_id)

    def publish(self, file, version=None):
        """
        Accept an open file object and publish it as a given
        version of this service. Raises on HTTP error
        """
        self.__require_version_set(version)
        package_path = self.client.get_package_upload_url(self.name, self.version)
        is_dict = isinstance(package_path, dict)
        upload_url = package_path.get('url') if is_dict else package_path
        headers = {'content-type':'application/zip'}
        r = requests.put(upload_url, data=file, headers=headers)
        r.raise_for_status()
        return True

    def deploy(self, version=None, slice=None, role=None, dry_run=False):
        self.__require_version_set(version)
        data = {
            'environment':self.env,
            'service':self.name,
            'version':self.__version
        }
        if slice is not None:
            data['slice'] = slice
            data['mode'] = 'bg'
        else:
            data['mode'] = 'overwrite'

        if role is not None:
            data['serverRole'] = role

        is_dry_run = 'true' if dry_run else 'false'
        result = self.client.post_deployments(is_dry_run, data)
        self.__deploy_id = result.get('id')
        return result

    def toggle(self):
        self.client.put_service_slices_toggle(self.name, self.env)
        new_active_slices = self.get_slices()
        if new_active_slices:
            active_slice = new_active_slices[0].get('Name').lower()
            return Upstream(self.name, active_slice, self.env)
        else:
            raise Exception('Could not determine active slice')

