import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

with open('requirements.txt', 'r') as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name="osu",
    version="1.1.0",
    author="Lekuru",
    author_email="contact@lekuru.xyz",
    description="A python library that emulates the osu! stable client",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    install_requires=requirements,
    keywords=["osu", "osugame", "python", "bancho"],
)
