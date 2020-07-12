#!/usr/bin/env python

from distutils.core import setup

setup(
    name="floodgate",
    version="1.0.1",
    description="Request rate limiter for Flask",
    author="Bhavesh Pareek",
    author_email="bhavesh.pareek36@gmail.com",
    packages=["floodgate", "floodgate/gates"],
    license="MIT",
    install_requires=["flask"],
)

