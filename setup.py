
import setuptools

setuptools.setup(
    name="osu.py",
    version='1.0.0',
    author="Lekuru",
    author_email='contact@lekuru.xyz',
    description='A python library that emulates the osu! stable client',
    long_description='osu.py is a python library that emulates part of the online functionality of the osu! stable client.',
    packages=[
        'osu'
    ],
    install_requires=[
        'requests',
        'psutil'
    ],
    keywords=[
        'osu',
        'osugame',
        'python',
        'bancho'
    ]
)