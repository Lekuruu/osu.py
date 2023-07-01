import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="osu",
    version="1.0.3",
    author="Lekuru",
    author_email="contact@lekuru.xyz",
    description="A python library that emulates the osu! stable client",
    long_description=long_description,
    packages=["osu"],
    install_requires=["requests", "psutil", "python-dateutil"],
    keywords=["osu", "osugame", "python", "bancho"],
)
