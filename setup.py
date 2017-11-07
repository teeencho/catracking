from setuptools import (
    find_packages,
    setup)

setup(
    name='catracking',
    version='0.1.0',
    author='ConsumerAffairs',
    description='Tracking for ConsumerAffairs',
    url='https://github.com/ConsumerAffairs/catracking',
    packages=find_packages(exclude=('tests*',)),
    install_requires=[
        'django>=1.9',
        'celery>=3.1',
        'requests>=2.14',
        'arrow>=0.10.0',
        'six'
    ],
)
