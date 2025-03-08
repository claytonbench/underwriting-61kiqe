import os
import re
import io
from setuptools import setup, find_packages  # setuptools - latest

# Constants
README = 'README.md'
VERSION = '0.1.0'
PACKAGE_NAME = 'loan_management_system_backend'
DESCRIPTION = 'Backend services for the educational loan management system'
AUTHOR = 'UNISA Development Team'
AUTHOR_EMAIL = 'dev@example.com'
URL = 'https://github.com/unisa/loan-management-system'

def read_requirements(filename):
    """
    Reads requirements from a requirements file and returns a list of package specifications.
    
    Args:
        filename (str): Path to the requirements file
        
    Returns:
        list: List of package requirement strings
    """
    requirements = []
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if not line or re.match(r'^\s*#', line):
                    continue
                # Skip references to other requirements files
                if re.match(r'^\s*-r\s+|^\s*--requirement\s+', line):
                    continue
                # Remove inline comments
                line = re.sub(r'#.*$', '', line).strip()
                if line:
                    requirements.append(line)
    return requirements

def read_long_description():
    """
    Reads the long description from README.md file.
    
    Returns:
        str: Content of the README.md file
    """
    if os.path.exists(README):
        with io.open(README, encoding='utf-8') as f:
            return f.read()
    return DESCRIPTION  # Default to the short description if README is missing

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=read_long_description(),
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    packages=find_packages(where='src/backend', exclude=['*.tests', '*.tests.*', 'tests.*', 'tests']),
    package_dir={'': 'src/backend'},
    include_package_data=True,
    python_requires='>=3.11',
    install_requires=read_requirements('requirements.txt'),
    extras_require={
        'dev': read_requirements('requirements-dev.txt'),
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django :: 4.2',
        'Intended Audience :: Financial and Insurance Industry',
        'Programming Language :: Python :: 3.11',
        'Topic :: Office/Business :: Financial',
        'Operating System :: OS Independent',
    ],
    zip_safe=False,
)