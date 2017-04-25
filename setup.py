""" Copyright (c) Trainline Limited, 2017. All rights reserved. See LICENSE.txt in the project root for license information. """

import sys
from setuptools import find_packages, setup
from codecs import open
from os.path import abspath, dirname, join

needs_pytest = {'pytest', 'test'}.intersection(sys.argv)
pytest_runner = ['pytest-runner', 'nose'] if needs_pytest else []

setup(name='envmgr-lib',
        version='0.2.0',
        description="Tools for the EM API",
        url="https://github.com/trainline/envmgr-lib",
        author="Trainline Engineering",
        author_email="platform.development@thetrainline.com",
        install_requires = [
            'requests',
            'simplejson',
            'repoze.lru',
            'environment_manager==0.2.5'
            ],
        setup_requires = pytest_runner,
        tests_require = [
            'pytest',
            'mock',
            'nose',
            'nose-parameterized',
            'responses'
            ],
        license='Apache 2.0',
        package_data={'': ['LICENSE.txt']},
        packages=['envmgr'],
        zip_safe=True)

