# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name="rp-exporter",
    version="0.1.0",
    description="Redpanda Prometheus exporter for topic disk usage metrics",
    author="sabbasth",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "requests>=2.31.0",
        "prometheus-client>=0.17.1",
    ],
    entry_points={
        "console_scripts": [
            "rp-exporter=app:main",
        ],
    },
    python_requires=">=3.8",
)
