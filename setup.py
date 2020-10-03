import os
import re

from setuptools import find_packages, setup


def get_version(package):
    """
    Return package version as listed in __version__ in __init__.py.
    """
    with open(os.path.join(package, "__init__.py")) as f:
        return re.search("__version__ = ['\"]([^'\"]+)['\"]", f.read()).group(1)


def get_long_description():
    """
    Return the README.
    """
    with open("README.md", encoding="utf8") as f:
        return f.read()


setup(
    name="melodiam",
    python_requires=">=3.7",
    version=get_version("melodiam"),
    description="Melodiam - share the music with people all over the web",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github/HarrySky/melodiam",
    license="Unlicense",
    author="Igor Nehoroshev",
    author_email="mail@neigor.me",
    maintainer="Igor Nehoroshev",
    maintainer_email="mail@neigor.me",
    packages=find_packages(),
    # Use MANIFEST.in for data files
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "uvloop==0.14.0",
        "asyncpg==0.21.0",
        "databases==0.3.2",
        "orm==0.1.5",
        "uvicorn==0.12.1",
        "tekore==3.1.0",
        # Package tekore expects <0.15
        "httpx[http2]==0.14.3",
        # TODO: Remove when httpx don't expect this version to be <0.10
        "h11==0.9",
        # Since 0.12.0 uvicorn does not install httptools (and uvloop)
        "httptools==0.1.*",
        "fastapi==0.61.1",
        # For sessions
        "itsdangerous",
        # Getting Literal annotation when running on Python < 3.8
        'typing-extensions;python_version<"3.8"',
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: POSIX :: Linux",
        "License :: Public Domain",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    entry_points={"console_scripts": ["melodiam-auth = melodiam.bin.auth:main"]},
)
