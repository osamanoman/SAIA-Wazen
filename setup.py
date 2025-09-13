#!/usr/bin/env python
"""
Setup script for SAIA Business Management System
This file is required for CI/CD systems that expect Python package structure.
"""

import os
import sys
from setuptools import setup, find_packages

# Read the requirements.txt file
def read_requirements():
    """Read requirements from requirements.txt file."""
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            requirements = []
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if line and not line.startswith('#'):
                    # Handle version specifiers and remove comments
                    if '#' in line:
                        line = line.split('#')[0].strip()
                    requirements.append(line)
            return requirements
    return []

# Read the README file for long description
def read_readme():
    """Read README.md file for long description."""
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "SAIA Business Management System - A comprehensive Django-based business management platform with AI assistants."

# Get version from Django settings or use default
def get_version():
    """Get version from the project."""
    return "1.0.0"

# Find all packages in the project
packages = find_packages(exclude=['tests', 'tests.*', 'venv', 'venv.*'])

# Include additional data files
package_data = {
    '': [
        '*.txt', '*.md', '*.yml', '*.yaml', '*.json', '*.cfg', '*.ini',
        'templates/*', 'templates/**/*',
        'static/*', 'static/**/*',
        'locale/*', 'locale/**/*',
        'fixtures/*', 'fixtures/**/*',
    ],
}

# Setup configuration
setup(
    name="saia-business-system",
    version=get_version(),
    description="SAIA Business Management System - Multi-tenant SaaS platform with AI assistants",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="SAIA Development Team",
    author_email="admin@saia-system.com",
    url="https://github.com/osamanoman/SAIA-Wazen",
    
    # Package configuration
    packages=packages,
    package_data=package_data,
    include_package_data=True,
    zip_safe=False,
    
    # Dependencies
    install_requires=read_requirements(),
    
    # Python version requirement
    python_requires=">=3.11",
    
    # Classifiers
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 5.0",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    
    # Entry points for management commands
    entry_points={
        'console_scripts': [
            'saia-manage=manage:main',
        ],
    },
    
    # Additional metadata
    keywords="django, business, management, ai, assistant, multi-tenant, saas",
    project_urls={
        "Bug Reports": "https://github.com/osamanoman/SAIA-Wazen/issues",
        "Source": "https://github.com/osamanoman/SAIA-Wazen",
        "Documentation": "https://github.com/osamanoman/SAIA-Wazen/blob/main/README.md",
    },
)
