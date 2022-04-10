from setuptools import setup, find_packages

setup(
    name='chat',
    version='1.0',
    packages=find_packages(),
    scripts=['chat/server', 'chat/client'],

)
