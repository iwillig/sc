from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="sc",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A Click-based command line tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/sc",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "click",
    ],
    entry_points={
        "console_scripts": [
            "sc=sc.cli:cli",
        ],
    },
)