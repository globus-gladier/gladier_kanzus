import os
from setuptools import setup, find_packages


install_requires = []
with open('requirements.txt') as reqs:
    for line in reqs.readlines():
        req = line.strip()
        if not req or req.startswith('#'):
            continue
        install_requires.append(req)

script_list = glob('scripts/gladier_*.sh')

setup(
    name='gladier-kanzus',
    description='The Kanzus Gladier',
    url='https://github.com/globus-gladier/gladier-kanzus',
    maintainer='The Gladier Team',
    maintainer_email='',
    version='0.0.3',
    packages=find_packages(),
    install_requires=install_requires,
    scripts=script_list,
    dependency_links=[],
    license='Apache 2.0',
    classifiers=[]
)
