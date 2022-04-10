from setuptools import setup, find_packages

setup(
    name='tcpchatroom',
    version='1.0',
    packages=find_packages(),
    scripts=['tcpchatroom/server', 'tcpchatroom/client'],

)
