from setuptools import setup, find_packages


setup(
    name='qreu',
    version='0.15.4',
    packages=find_packages(),
    url='https://github.com/gisce/qreu',
    install_requires=[
        'html2text',
        'six',
        'unidecode'
    ],
    license='MIT',
    author='GISCE-TI, S.L.',
    author_email='devel@gisce.net',
    description='EMail Wrapper',
    long_description='EMail Wrapper',
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries',
        'Topic :: Communications :: Email'
    ]
)
