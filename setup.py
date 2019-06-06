import setuptools
import semiphemeral

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="semiphemeral",
    version=semiphemeral.version,
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
