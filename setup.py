from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="freed-validator",
    version="1.0.0",
    author="koensayr",
    description="A toolkit for validating and testing FreeD protocol data streams",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/koensayr/freed_test",
    packages=find_packages(include=["freed_validator", "freed_validator.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Video",
        "Topic :: Software Development :: Testing",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    keywords=[
        "freed",
        "protocol",
        "validation",
        "testing",
        "camera tracking",
        "virtual production",
        "unreal engine"
    ],
    install_requires=requirements,
    package_data={
        "freed_validator": ["py.typed"],
    },
    entry_points={
        "console_scripts": [
            "freed=freed_validator.cli:main",
        ],
    },
)
