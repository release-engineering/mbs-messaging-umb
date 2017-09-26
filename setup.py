from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.readlines()

with open('test-requirements.txt') as f:
    test_requirements = f.readlines()

setup(
    name='mbs-messaging-umb',
    description='A plugin for the Module Build Service to support sending '
    'and receiving messages from the Unified Message Bus',
    version='0.0.2',
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Build Tools"
    ],
    keywords='module build service messaging',
    author='The Factory 2.0 Team',
    author_email='factory2-members@fedoraproject.org',
    url='https://github.com/mikebonnet/mbs-messaging-umb',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requirements,
    tests_require=test_requirements,
    entry_points={
        'mbs.messaging_backends': [
            'umb = mbs_messaging_umb:umb_backend',
        ]
    },
    data_files=[('/etc/mbs-messaging-umb/', ['conf/config.py'])],
)
