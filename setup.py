from setuptools import setup, find_packages
from dap_taltech import PROJECT_DIR

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
with open(f"requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read()

setup(
    name='taltech_utils',
    version='0.0.0',
    license='MIT',
    description='utils for tutorials for taltech hackweek 2023',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='',
    packages=find_packages(
        exclude=["data", "tutorials"]
    ),
    install_requires=[requirements],
    python_requires='>=3.9',
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
