# -*- coding: utf-8 -*-
import setuptools
import re

version = None
with open('of_mirror/__init__.py') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('version is not set')

long_description = ""
with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="of-mirror",
    version=version,
    author="Jan Drögehoff",
    author_email="jandroegehoff@gmail.com",
    description="winreg implementation for non NT systems",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Jan200101/of-mirror",
    packages=["of_mirror"],
    license="MIT",
    include_package_data=True,
    classifiers=[
        "Development Status :: 3 - Alpha",

        "Programming Language :: Python :: 3",

        "License :: OSI Approved :: MIT License",

        "Operating System :: POSIX",
        "Operating System :: POSIX :: BSD",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.6",

    entry_points={
        'console_scripts': [
            'of-mirror=of_mirror.__main__:main',
        ],
    },

)
