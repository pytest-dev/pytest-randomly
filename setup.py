import re

from setuptools import setup


def get_version(filename):
    with open(filename, 'r') as fp:
        contents = fp.read()
    return re.search(r"__version__ = ['\"]([^'\"]+)['\"]", contents).group(1)


version = get_version('pytest_randomly.py')


with open('README.rst', 'r') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst', 'r') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

setup(
    name='pytest-randomly',
    version=version,
    description="Pytest plugin to randomly order tests and control "
                "random.seed.",
    long_description=readme + '\n\n' + history,
    author="Adam Johnson",
    author_email='me@adamj.eu',
    url='https://github.com/pytest-dev/pytest-randomly',
    py_modules=['pytest_randomly'],
    include_package_data=True,
    install_requires=[
        'pytest',
    ],
    python_requires='>=3.5',
    license="BSD",
    zip_safe=False,
    keywords='pytest, random, randomize, randomise, randomly',
    entry_points={
        'pytest11': ['randomly = pytest_randomly'],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Pytest',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
