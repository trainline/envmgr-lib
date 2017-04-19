# Copyright (c) Trainline Limited, 2017. All rights reserved. See LICENSE.txt in the project root for license information.

from envmgr import EmClient
from envmgr.utils import get_properties
from repoze.lru import lru_cache

class AMI(object):
    __property_map = [
        ('ImageId','id'),('CreationDate','created'),('Platform','platform'),('Name','name'),
        ('Description','description'),('AmiType','type'),('AmiVersion','version'),
        ('IsCompatibleImage','is_compatible'),('IsStable','is_stable'),('Encrypted','is_encrypted'),
        ('RootVolumeSize','root_volume_size'),('Rank','rank'),('IsLatest','is_latest'),
        ('IsLatestStable','is_latest_stable'),('DaysBehindLatest','days_behind_latest'),
        ('AccountName','account')
    ]

    @staticmethod
    def get_all():
        client = EmClient()
        raw = client.get_images()
        return map(AMI.__from_raw, raw)

    @staticmethod
    def __from_raw(image):
        args = {}
        for prop in AMI.__property_map:
            args[prop[1]] = image.get(prop[0])
        return AMI(**args)

    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.created = kwargs.get('created')
        self.platform = kwargs.get('platform')
        self.name = kwargs.get('name')
        self.description = kwargs.get('description')
        self.type = kwargs.get('type')
        self.version = kwargs.get('version')
        self.is_compatible = kwargs.get('is_compatible')
        self.is_stable = kwargs.get('is_stable')
        self.is_encrypted = kwargs.get('is_encrypted')
        self.root_volume_size = kwargs.get('root_volume_size')
        self.rank = int(kwargs.get('rank'))
        self.is_latest = kwargs.get('is_latest')
        self.is_latest_stable = kwargs.get('is_latest_stable') 
        self.days_behind_latest = int(kwargs.get('days_behind_latest'))
        self.account_name = kwargs.get('account_name')

    def __repr__(self):
        return get_properties(self)
