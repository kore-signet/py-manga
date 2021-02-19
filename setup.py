import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="py-manga",
    version="0.0.4",
    author="Alis Wayland",
    author_email="waylandalis@gmail.com",
    description="A library to get information from mangaupdates.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/alisw/py-manga",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.4',
)
