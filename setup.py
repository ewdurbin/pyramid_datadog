from setuptools import setup, find_packages
import os

version = '0.1.0'

requires = ['pyramid']

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

README = read('README.rst')
CHANGES = read('CHANGES.rst')

setup(
    name='pyramid_datadog',
    version=version,
    author='Paola Castro',
    author_email='paolac@surveymonkey.com',
    description='Datadog integration for Pyramid',
    license='MIT License',
    keywords='datadog pyramid metrics integration',
    url='https://github.com/SurveyMonkey/pyramid_datadog',
    zip_safe=False,
    include_package_data=True,
    packages=find_packages(exclude=['tests']),
    setup_requires=['setuptools_git'],
    install_requires=requires,
    long_description='%s\n\n%s' % (README, CHANGES),
    classifiers = [
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
)
