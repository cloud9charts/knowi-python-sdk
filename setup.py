from codecs import open
import os

from setuptools import find_packages, setup

from knowipy import __version__

here = os.path.abspath(os.path.dirname(__file__))

description = "The official Python3 Knowi API SDK."

try:
    with open(os.path.join(here, "README.md"), encoding="utf-8") as readme:
        long_description = readme.read()
except FileNotFoundError as fnfe:
    long_description = description

setup(
        name='knowipy',
        version=__version__,
        description=description,
        long_description=long_description,
        author='Manny Ezeagwula',
        author_email='manny@knowi.com',
        url='https://github.com/ezeagwulae/knowi-python-sdk',
        long_description_content_type="text/markdown",
        include_package_data=True,
        keywords='knowi single-sign-on management-api api sdk analytics',
        license='MIT',
        packages=find_packages(exclude=['examples']),
        install_requires=[
            "requests",
            "pytz"
        ],
        python_requires=">=3.6",
)
