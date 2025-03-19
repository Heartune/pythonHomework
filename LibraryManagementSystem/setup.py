"""
Setup script for the Library Management System.
"""

from setuptools import setup, find_packages

setup(
    name="LibraryManagementSystem",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "PyQt5>=5.15.0",
        "matplotlib>=3.5.0",
        "numpy>=1.20.0",
        "pandas>=1.3.0",
        "requests>=2.25.0",
        "scikit-learn>=1.0.0",
        "seaborn>=0.11.0",
        "beautifulsoup4>=4.9.0",
        "pyjwt>=2.0.0",
    ],
    entry_points={
        "console_scripts": [
            "library-server=LibraryManagementSystem.server.main:main",
            "library-client=LibraryManagementSystem.client.main:main",
            "library=LibraryManagementSystem.__main__:main",
        ],
    },
    python_requires=">=3.6",
    author="Library Management System Team",
    author_email="admin@library.com",
    description="A library management system with client-server architecture",
    keywords="library, management, system",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
