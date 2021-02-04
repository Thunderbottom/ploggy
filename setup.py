import io
import os

from setuptools import setup, find_packages

DESCRIPTION = "A dead-simple, extensible logging framework for Python"
PY_REQUIRES = ">=3.7.0"
VERSION = "0.1"

here = os.path.abspath(os.path.dirname(__file__))
try:
    with io.open(os.path.join(here, "README.md"), encoding="utf-8") as r:
        long_description = "\n" + r.read()
except FileNotFoundError:
    long_description = DESCRIPTION

setup(
    name="ploggy",
    packages=find_packages(exclude=("example.py",)),
    version=VERSION,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    author="Chinmay D. Pai",
    include_package_data=True,
    python_requires=PY_REQUIRES,
    author_email="chinmaydpai@gmail.com",
    url="https://github.com/Thunderbottom/ploggy",
    keywords=["logging", "monitoring", "framework"],
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Logging",
    ],
    install_requires=[],
)
