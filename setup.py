import re
import os
from setuptools import setup, find_packages  # type: ignore


def fpath(name):
    return os.path.join(os.path.dirname(__file__), name)


def read(fname):
    return open(fpath(fname)).read()


def desc():
    return read("README.md")


# grep cibo/__init__.py since python 3.x cannot
# import it before using 2to3
file_text = read(fpath("cibo/__init__.py"))


def grep(attrname):
    pattern = r'{0}\W*=\W*"([^\']+)"'.format(attrname)
    (strval,) = re.findall(pattern, file_text)
    return strval


setup(
    name="cibo",
    version=grep("__version__"),
    license="MIT",
    author=grep("__author__"),
    author_email=grep("__email__"),
    description="a CBV(class base views) web framework based on flask",
    long_description=desc(),
    long_description_content_type="text/markdown",
    packages=find_packages(
        exclude=["tests", "tests.*", "examples", "examples.*", "demo", "demo.*", "etc", "etc.*"]
    ),
    include_package_data=True,
    zip_safe=False,
    platforms="any",
    install_requires=[
        "Flask==1.1.1",
        "pydantic==1.6.1",
        "flasgger==0.9.3",
    ],
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7.5",
    ],
    # entry_points={
    #     'flask.commands': [
    #         'generate-api-schema=flasgger.commands:generate_api_schema',
    #     ],
    # },
)
