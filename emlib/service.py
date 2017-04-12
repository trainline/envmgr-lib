# Copyright (c) Trainline Limited, 2017. All rights reserved. See LICENSE.txt in the project root for license information.

from emlib import EmClient

class Service(object):

    def __init__(self, name, env):
        self.name = name
        self.env = env
        self.client = EmClient()

    def get_health(self, slice=None):
        if slice is None:
            result = self.client.get_service_overall_health(self.name, self.env)
            return [ asg.get('Services')[0] for asg in result.get('AutoScalingGroups') ]
        else:
            return self.client.get_service_health(self.name, self.env, slice)

    def get_slice(self, active=True):
        active = 'true' if active else 'false'
        return self.client.get_service_slices(self.name, self.env, active)
