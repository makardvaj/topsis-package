from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="Topsis-Vaibhav-102316037",
    version="1.0.0",
    author="Vaibhav Srivastva",
    author_email="vaibhavsrivastva73@gmail.com",
    description="A Python package for implementing TOPSIS",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/makardvaj/topsis-package", # Optional
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "topsis=Topsis_Vaibhav_102316037.topsis:main",
        ],
    },
    python_requires='>=3.6',
)