import os
import re

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

def get_version(filename="__version__.py"):
    """
    Returns the package version number as a string by searching and reading the
    __version__.py file.
    """
    for dirpath, _, filenames in os.walk(".", topdown=True):
        if ".gitignore" in filenames:
            with open(".gitignore") as _f:
                gitignore = [
                    file.strip()
                    for file in _f.readlines()
                    if not re.search(r"\#|\*", file)
                ]

        if any(pattern for pattern in gitignore if re.search(pattern, dirpath)):
            continue
        for file in filenames:
            if filename in file:
                file_path = os.path.join(dirpath, filename)

    _version_info = ""
    try:
        assert os.path.exists(file_path)
        with open(file_path) as f:
            _version_info = "".join(
                [i.strip() for i in f.readlines() if i.startswith("version")]
            )
            _version_info = _version_info.split("=")[-1]  # noqa: C406
            _version_info = eval(_version_info.replace(" ", ""))
    except Exception:
        raise RuntimeError(f"Unable to find version information in '{file_path}'.")
    else:
        return _version_info

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="semiphemeral",
    version=get_version(),
    author="Micah Lee",
    author_email="micah@micahflee.com",
    long_description=long_description,
    description="Automatically delete your old tweets, except for the ones you want to keep",
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/micahflee/semiphemeral",
    packages=['semiphemeral'],
    package_data={'semiphemeral': [
        'templates/*',
        'static/*',
        'static/img/*',
        'static/js/*',
        'static/js/lib/*'
    ]},
    classifiers=(
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License"
    ),
    entry_points={
        'console_scripts': [
            'semiphemeral = semiphemeral:main',
        ],
    },
    install_requires=[
        'click',
        'colorama',
        'tweepy',
        'flask',
        'sqlalchemy'
    ]
)
