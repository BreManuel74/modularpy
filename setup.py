#!/usr/bin/env python
"""
Setup configuration for the my_module package.
"""

from setuptools import setup, find_packages

setup(
    name='my_module',
    version='0.1.0',
    packages=find_packages(),
    entry_points={
        # This entry point creates a command-line script `modularpy`
        'console_scripts': [
            'modularpy = my_module.__main__:main'
        ]
    },
    install_requires=[
        # Alternatively, dependencies can be read from requirements.txt or listed here.
        # e.g., 'numpy>=1.18.0',
        'click>=8.1.0',
        'numpy>=1.18.0',
        'requests>=2.25.0',
        'matplotlib>=3.10.0',
        'ipykernel>=6.29.5',
        'PyQt6>=6.8.0',
        'pyqtgraph>=0.13.7',
        'pyserial>=3.5',
        'qtconsole==5.6.1',
        'pyyaml>=5.4.1',
        'pandas>=2.2.3',
    ],
    python_requires='>=3.10',
)