from setuptools import setup, find_packages
from os.path import join, dirname

setup(
    name='chat',
    version='1.0',
    packages=find_packages(),
    scripts=['chat/server', 'chat/client'],

)
