from setuptools import setup, find_packages

from edgaranalyzer import (
    __version__,
    __description__,
    __author__,
    __author_email__,
    __url__,
)

requires = ["python-edgar", "tqdm", "requests_html"]

setup(
    name="edgar-analyzer",
    version=__version__,
    description=__description__,
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown; charset=UTF-8; variant=GFM",
    author=__author__,
    author_email=__author_email__,
    url=__url__,
    packages=find_packages(),
    install_requires=requires,
    entry_points={
        "console_scripts": ["edgar-analyzer=edgaranalyzer.main:main"],
    },
    package_data={
        "": ["LICENSE", "README.md", "*.c"],
    },
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    license="MIT",
)
