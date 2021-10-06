from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

long_description = (here / "README.md").read_text(encoding="utf-8")


setup(
    name="bitnest",
    version="0.1.0",
    description="Conditional Nestest DataStructures",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/costrou/bitnest",
    author="Christopher Ostrouchov",
    author_email="chris.ostrouchov@gmail.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords="struct, python",
    packages=find_packages(where="."),
    install_requires=[
        'graphviz',
        'astor',
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-cov",
            "black==21.5b0",
            "flake8",
            "sphinx",
            "sphinx_rtd_theme",
            "recommonmark",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/costrouc/bitnest",
        "Source": "https://github.com/costrouc/bitnest",
    },
)
