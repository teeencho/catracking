from setuptools import (
    find_packages,
    setup)

setup(
    name='catracking',
    version='0.1.6',
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
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
