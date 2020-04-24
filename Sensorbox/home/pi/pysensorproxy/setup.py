# -*- coding: utf-8 -*-
"""Based on the pypa sample-project

See: https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages

# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

dependencies = [
    "influxdb",
    "pytimeparse",
    "Adafruit_DHT",
    "tsl2561",
    "Adafruit_GPIO",
    "picamera",
    "RPi.GPIO",
    "pyyaml",
    "schedule",
    "psutil",
    "gpiozero",
    "w1thermsensor",
]

setup(
    name="sensorproxy",
    version="0.1",
    description="Python software to read out sensors",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nature40/pysensorproxy",
    author=u"Jonas Höchst & Alvar Penning",
    author_email="hoechst@mathematik.uni-marburg.de",
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    keywords="sensor proxy nature40",
    license="MIT",
    packages=find_packages(exclude=["docs", "tests", "examples"]),
    install_requires=dependencies,
    zip_safe=True,
    project_urls={
        "Bug Reports": "https://github.com/nature40/pysensorproxy/issues",
        "Source": "https://github.com/nature40/pysensorproxy",
    },
    entry_points={'console_scripts': [
        'sensorproxy=sensorproxy.app:main']},
)
