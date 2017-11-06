from setuptools import setup

setup(
    name='catracking',
    version='0.1.0',
    author='ConsumerAffairs',
    description='Tracking for ConsumerAffairs',
    url='https://github.com/ConsumerAffairs/catracking',
    install_requires=[
        'django>=1.9',
        'celery>=3.1',
        'requests>=2.14',
    ],
)
