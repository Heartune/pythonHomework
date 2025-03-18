"""
Setup script for the Library Management System.
"""

from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='library-management-system',
    version='1.0.0',
    description='A comprehensive library management system with client-server architecture',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Library Management Team',
    author_email='admin@library.example.com',
    url='https://github.com/example/library-management-system',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'PyQt5>=5.15.0',
        'matplotlib>=3.5.0',
        'pandas>=1.3.0',
        'numpy>=1.20.0',
        'scikit-learn>=1.0.0',
        'requests>=2.25.0',
        'beautifulsoup4>=4.9.0',
        'schedule>=1.1.0',
    ],
    extras_require={
        'dev': [
            'pytest>=6.0.0',
            'flake8>=3.9.0',
            'black>=21.5b2',
        ],
    },
    entry_points={
        'console_scripts': [
            'lms-server=server.main:main',
            'lms-client=client.main:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Education',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    python_requires='>=3.8',
)
