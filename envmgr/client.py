# Copyright (c) Trainline Limited, 2017. All rights reserved. See LICENSE.txt in the project root for license information.

from base64 import b64decode
from environment_manager import EMApi

def config(host, user, pword, retries=1, default_headers={}):
    EmClient.configure(host, user, pword, retries, default_headers)

class EmClient(object):
    """
    An API wrapper for sharing configuration between calls
    """

    api = None

    @staticmethod
    def configure(host, user, pword, retries=1, default_headers={}):
        pword = b64decode(pword)
        EmClient.api = EMApi(server=host, user=user, password=pword, retries=retries, default_headers=default_headers)

    def __getattr__(self, name):
        return getattr(EmClient.api, name)

