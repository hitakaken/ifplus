# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    licenses = f.read()

install_requires = [
    'flask',
    'six',
    'python-ldap',
    'PyJWT',
    'flask-restplus',
    'apispec',
    'webargs',
    'flask-marshmallow',
    'flask-cors',
    'flatdict',
    'bidict',
    'bson',
    'pymongo',
    'watchdog',
    'PyYAML',
]

setup(
    name='ifplus',
    version='0.0.1',
    description='IF+',
    long_description=readme,
    author='CaoKe',
    author_email='hitakaken@gmail.com',
    url='https://github.com/hitakaken/ifplus',
    license=licenses,
    platforms=["any"],
    packages=[
        'ifplus',
        'ifplus/auth',
        'ifplus/auth/helpers',
        'ifplus/auth/models',
        'ifplus/auth/views',
        'ifplus/chat',
        'ifplus/chat/helpers',
        'ifplus/chat/models',
        'ifplus/chat/views',
        'ifplus/pm',
        'ifplus/pm/helpers',
        'ifplus/pm/models',
        'ifplus/pm/views',
        'ifplus/rbac',
        'ifplus/rbac/helpers',
        'ifplus/rbac/models',
        'ifplus/rbac/views',
        'ifplus/res',
        'ifplus/res/helpers',
        'ifplus/res/models',
        'ifplus/res/views',
        'ifplus/restful',
        'ifplus/restful/patched',
    ],
    test_suite="test.tests",
    install_requires=install_requires,
    tests_require=['nose'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    # data_files=[('', ['README'])]
)
