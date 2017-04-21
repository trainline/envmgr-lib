# Copyright (c) Trainline Limited, 2017. All rights reserved. See LICENSE.txt in the project root for license information.

import dateutil.parser

from datetime import date
from envmgr import EmClient, AMI
from envmgr.utils import get_properties
from repoze.lru import lru_cache

class Instance(object):

    @staticmethod
    def get_all(env=None, cluster=None, account=None):
        client = EmClient()
        raw = client.get_instances(env, cluster, account)
        return map(Instance.__from_raw, raw)

    @staticmethod
    def get_instances_by_ami_age(age, env=None, cluster=None, account=None):
        instances = Instance.get_all(env, cluster, account)
        amis = AMI.get_all()
        map_amis_to_instances = InstanceAmiMapper(instances, amis)
        map_amis_to_instances.run()
        age = int(age)
        matchers = [
            lambda ami,instance: ami.id == instance.ami_id,
            lambda ami,instance: ami.days_behind_latest >= age
        ]
        old_instances = [ instance for instance in instances if 
            any(ami for ami in amis if all([ match(ami,instance) for match in matchers ]) )
        ]
        return list(old_instances)

    @staticmethod
    def __from_raw(instance):
        tags = instance.get('Tags', [])
        args = {
            'id': instance.get('InstanceId'),
            'type': instance.get('InstanceType'),
            'state': instance.get('State').get('Name'),
            'age': (date.today() - dateutil.parser.parse(instance.get('LaunchTime')).date()).days,
            'name': get_tag_value(tags, 'Name'),
            'role': get_tag_value(tags, 'Role'),
            'cluster': get_tag_value(tags, 'OwningCluster'),
            'env': get_tag_value(tags, 'Environment'),
            'ami_id': instance.get('ImageId'),
            'ami_name': None,
            'ami_age': None
        }
        return Instance(**args)
    
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.type = kwargs.get('type')
        self.age = kwargs.get('age')
        self.name = kwargs.get('name')
        self.role = kwargs.get('role')
        self.cluster = kwargs.get('cluster')
        self.env = kwargs.get('env')
        self.state = kwargs.get('state')
        self.ami_name = kwargs.get('ami_name')
        self.ami_age = kwargs.get('ami_age')
        self.ami_id = kwargs.get('ami_id')

    def __repr__(self):
        return get_properties(self)


class InstanceAmiMapper(object):
    def __init__(self, instances, amis):
        self.instances = instances
        self.amis = amis

    def run(self):
        for instance in self.instances:
            (name, age) = self.get_ami_meta_by_id(instance.ami_id)
            instance.ami_name = name
            instance.ami_age = age
    
    @lru_cache(256)
    def get_ami_meta_by_id(self, ami_id):
        ami = [ ami for ami in self.amis if ami.id == ami_id ]
        if ami:
            return (ami[0].name, ami[0].days_behind_latest)
        else:
            return (None, None)


def get_tag_value(tags, key):
    tag = [ tag.get('Value') for tag in tags if tag.get('Key') == key ]
    return tag[0] if tag else None

