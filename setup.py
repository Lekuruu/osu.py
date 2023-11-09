import setuptools
import os

current_directory = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(current_directory, "README.md"), "r") as f:
    long_description = f.read()

with open(os.path.join(current_directory, "requirements.txt"), "r") as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name="osu",
    version="1.3.0",
    author="Lekuru",
    author_email="contact@lekuru.xyz",
    description="A python library that emulates the osu! stable client",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    install_requires=requirements,
    keywords=["osu", "osugame", "python", "bancho"],
)
