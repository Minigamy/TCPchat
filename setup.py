from setuptools import setup, find_packages
from os.path import join, dirname

setup(
    name='tcpchat',
    version='0.0.1',
    packages=find_packages(),
    scripts=["tcpchat/server.py", "tcpchat/client.py"],

)
