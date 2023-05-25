
from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, "README.md")) as f:
    long_description = "\n" + f.read()

with open(os.path.join(here, "requirements.txt")) as f:
    requirements = f.read().split('\n')

version = '0.1.0'
description = 'A python library that emulates the osu! stable client'

setup(
    name="osu.py",
    version=version,
    author="Lekuru (Levi)",
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=requirements,
    keywords=['python', 'osu', 'osugame', 'bancho'],
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)