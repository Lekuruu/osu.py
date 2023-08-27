import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="osu",
    version="1.1.0",
    author="Lekuru",
    author_email="contact@lekuru.xyz",
    description="A python library that emulates the osu! stable client",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=["osu", "osu/api", "osu/bancho", "osu/objects"],
    install_requires=["requests", "psutil", "python-dateutil", "wmi"],
    keywords=["osu", "osugame", "python", "bancho"],
)
