#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages


install_requires = set()
with open("requirements.txt") as f:
    for dep in f.read().split('\n'):
        if dep.strip() != '' and not dep.startswith('-e'):
            install_requires.add(dep)

setup(
    author="Chenxi Wang, Jianwu Wang",
    author_email='{chenxi,jianwu}@umbc.edu',
    python_requires='>=3.5',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="satellite collocation code",
    entry_points={
        'console_scripts': [
        ],
    },
    install_requires=list(install_requires),
    license="Apache Software License 2.0",
    long_description="satellite collocation",
    include_package_data=True,
    keywords='satellite, collocation',
    name='satellite_collocation',
    packages=find_packages(),
    test_suite='tests',
    url='https://github.com/AI-4-atmosphere-remote-sensing/satellite_collocation',
    version='0.1.0',
    zip_safe=False,
)
