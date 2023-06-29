from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read()

setup(
    name='taltechhackweek2023',
    version='0.0.0',
    license='MIT',
    description='tutorials for taltech hackweek 2023',
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
