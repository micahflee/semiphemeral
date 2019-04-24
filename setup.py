import setuptools
import ephemeral

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ephemeral",
    version=ephemeral.version,
    author="Micah Lee",
    author_email="micah@micahflee.com",
    description="delete old tweets based on specific criteria",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="GPLv3+",
    url="https://github.com/micahflee/ephemeral",
    packages=['ephemeral'],
    classifiers=(
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)"
    ),
    entry_points={
        'console_scripts': [
            'ephemeral = ephemeral:main',
        ],
    },
    install_requires=[
        'click',
        'python-twitter'
    ]
)
