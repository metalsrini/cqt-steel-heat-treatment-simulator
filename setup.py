#!/usr/bin/env python3
"""
Setup configuration for Integrated C-Q-T Modeling Framework
Implementation of "Integrated Modeling of Carburizing-Quenching-Tempering of Steel Gears for an ICME Framework"
"""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Integrated C-Q-T Modeling Framework for Steel Gears"

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="cqt-modeling-framework",
    version="1.0.0",
    author="C-Q-T Framework Development Team",
    author_email="contact@cqt-framework.org",
    description="Integrated Computational Materials Engineering Framework for Steel Gear Manufacturing",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/cqt-framework/integrated-modeling",
    project_urls={
        "Documentation": "https://cqt-framework.readthedocs.io/",
        "Source": "https://github.com/cqt-framework/integrated-modeling",
        "Tracker": "https://github.com/cqt-framework/integrated-modeling/issues",
        "Research Paper": "https://doi.org/10.1007/s40192-018-0107-x"
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Manufacturing",
        "Topic :: Scientific/Engineering :: Chemistry",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Mathematics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Natural Language :: English",
    ],
    keywords=[
        "carburizing", "quenching", "tempering", "steel", "gears", "ICME",
        "materials engineering", "finite element analysis", "phase transformation",
        "carbon diffusion", "hardness prediction", "manufacturing", "metallurgy",
        "automotive", "heat treatment", "microstructure", "simulation"
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.8.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.971",
            "pre-commit>=2.20.0"
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
            "nbsphinx>=0.8.0",
            "sphinx-autodoc-typehints>=1.19.0"
        ],
        "viz": [
            "plotly>=5.0.0",
            "seaborn>=0.11.0",
            "bokeh>=2.4.0",
            "mayavi>=4.8.0",
            "vtk>=9.1.0"
        ],
        "fem": [
            "fenics>=2019.1.0",
            "mshr>=2019.1.0",
            "scikit-fem>=7.0.0",
            "petsc4py>=3.17.0"
        ],
        "ml": [
            "scikit-learn>=1.1.0",
            "tensorflow>=2.9.0",
            "torch>=1.12.0",
            "scikit-optimize>=0.9.0"
        ],
        "full": [
            "pytest>=7.0.0", "pytest-cov>=4.0.0", "black>=22.0.0",
            "sphinx>=5.0.0", "plotly>=5.0.0", "fenics>=2019.1.0",
            "scikit-learn>=1.1.0", "tensorflow>=2.9.0"
        ]
    },
    entry_points={
        "console_scripts": [
            "cqt-simulate=icme_framework.cli:main",
            "cqt-gear-design=icme_framework.gear_module.cli:main",
            "cqt-validate=validation_cases.cli:main",
            "cqt-optimize=icme_framework.optimization:main"
        ]
    },
    package_data={
        "core": ["data/*.json", "data/*.yaml"],
        "validation_cases": ["data/*.csv", "data/*.json"],
        "icme_framework": ["templates/*.yaml", "config/*.json"],
        "applications": ["examples/*.py", "examples/*.yaml"]
    },
    include_package_data=True,
    zip_safe=False,
    platforms=["any"],
    license="MIT",
    test_suite="tests",
    cmdclass={},
    options={
        "bdist_wheel": {
            "universal": False
        }
    }
)