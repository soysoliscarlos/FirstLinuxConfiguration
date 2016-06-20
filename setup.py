# -*- coding: utf-8 -*-
from distutils.core import setup

setup(
    # Application name:
    name="FLC",
    # Version number (initial):
    version="0.1.0",
    description='First Linux Configuration (FLC) is a python script that looking for load all package that I need in my Linux',
    # Application author details:
    author="Carlos Solís Salazar",
    author_email="carlos@solis.com.ve",

    # Packages
    packages=["app"],

    # Include additional files into the package
    include_package_data=True,

    # Details
    url="https://github.com/csoliss/FLC/",
    #
    license="LICENSE.txt",

    # long_description=open("README.txt").read(),

    # Dependent packages (distributions)
    install_requires=[
        #"flask",
    ],
)