# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
from setuptools import setup, find_packages

setup(
    name="rp-exporter",
    version="0.1.0",
    description="Redpanda Prometheus exporter for disk usage metrics",
    author="Meltwater",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "prometheus-client>=0.17.1",
        "fastapi>=0.103.1",
        "uvicorn>=0.23.2",
    ],
    entry_points={
        "console_scripts": [
            "rp-exporter=src.app:main",
        ],
    },
    python_requires=">=3.8",
)
