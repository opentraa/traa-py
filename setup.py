"""
TRAA Python Bindings - Setup Script
"""

import os
import sys
import platform
import shutil
from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.develop import develop

def get_platform_lib_path():
    """Get the platform-specific library path"""
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    if system == 'windows':
        if machine == 'amd64' or machine == 'x86_64':
            return 'libs/windows/x64'
        else:
            return 'libs/windows/x86'
    elif system == 'darwin':
        return 'libs/darwin'
    elif system == 'linux':
        if machine == 'aarch64':
            return 'libs/linux/arm64'
        else:
            return 'libs/linux/x64'
    else:
        raise RuntimeError(f"Unsupported platform: {system} {machine}")

def copy_libs(lib_dir):
    """Copy library files to the package directory"""
    platform_lib_path = get_platform_lib_path()
    print(f"Looking for libraries in: {platform_lib_path}")
    if not os.path.exists(platform_lib_path):
        print(f"Warning: Platform-specific library path not found: {platform_lib_path}")
        return
    
    # Create the target directory if it doesn't exist
    os.makedirs(lib_dir, exist_ok=True)
    print(f"Created target directory: {lib_dir}")
    
    # List all files before copying
    print("Available files in source directory:")
    print(os.listdir(platform_lib_path))
    
    for file in os.listdir(platform_lib_path):
        src = os.path.join(platform_lib_path, file)
        dst = os.path.join(lib_dir, file)
        shutil.copy2(src, dst)
        print(f"Copied {src} -> {dst}")

class CustomInstall(install):
    def run(self):
        # Copy library files
        lib_dir = os.path.join(self.install_lib, 'traa/libs')
        copy_libs(lib_dir)
        install.run(self)

class CustomDevelop(develop):
    def run(self):
        # Copy library files
        lib_dir = os.path.join('traa/libs')
        copy_libs(lib_dir)
        develop.run(self)

# Read long description from README.md
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='traa',
    version='0.1.0',
    description='Python bindings for the TRAA library',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='opentraa',
    author_email='peilinok@gmail.com',
    url='https://github.com/opentraa/traa-py',
    packages=find_packages(),
    package_data={
        'traa': [
            'libs/**/*.dll',
            'libs/**/*.so',
            'libs/**/*.dylib',
        ],
    },
    include_package_data=True,
    cmdclass={
        'install': CustomInstall,
        'develop': CustomDevelop,
    },
    python_requires='>=3.7',
    install_requires=[
        'numpy>=1.16.0',
        'Pillow>=8.0.0',
    ],
    extras_require={
        'dev': [
            'pytest>=6.0.0',
            'pytest-cov>=2.0.0',
            'black>=21.0.0',
            'isort>=5.0.0',
            'flake8>=3.9.0',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
