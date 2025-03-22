"""
TRAA Python Bindings - Setup Script
"""

import os
import sys
import platform
import shutil
from setuptools import setup, find_packages
from wheel.bdist_wheel import bdist_wheel

class PlatformSpecificWheel(bdist_wheel):
    """Custom wheel builder that creates platform-specific wheels"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Get target platform from environment variable or use current platform
        self.target_platform = os.environ.get('TARGET_PLATFORM', '').lower()
        if not self.target_platform:
            self.target_platform = f"{platform.system().lower()}_{platform.machine().lower()}"

    def get_tag(self):
        # Get the platform-specific tag based on target platform
        python_tag, abi_tag, platform_tag = super().get_tag()
        
        # Map target platform to wheel platform tag
        platform_mapping = {
            'windows_x64': 'win_amd64',
            'windows_x86': 'win32',
            'windows_arm64': 'win_arm64',
            'darwin_x64': 'macosx_10_9_x86_64',
            'darwin_arm64': 'macosx_11_0_arm64',
            'linux_x64': 'manylinux2014_x86_64',
            'linux_arm64': 'manylinux2014_aarch64'
        }
        
        if self.target_platform in platform_mapping:
            platform_tag = platform_mapping[self.target_platform]
        
        return python_tag, abi_tag, platform_tag

    def finalize_options(self):
        super().finalize_options()
        # Mark this as a platform-specific wheel
        self.root_is_pure = False

def get_target_platform():
    """Get the target platform for building wheel"""
    target = os.environ.get('TARGET_PLATFORM', '').lower()
    if not target:
        system = platform.system().lower()
        machine = platform.machine().lower()
        if system == 'windows':
            target = f"windows_{'x64' if machine in ['amd64', 'x86_64'] else 'x86'}"
        elif system == 'darwin':
            target = f"darwin_{'arm64' if machine == 'arm64' else 'x64'}"
        elif system == 'linux':
            target = f"linux_{'arm64' if machine == 'aarch64' else 'x64'}"
    return target

def get_platform_package_data(target_platform):
    """Get platform-specific package data patterns"""
    platform_mapping = {
        'windows_x64': ['libs/windows/x64/*.dll'],
        'windows_x86': ['libs/windows/x86/*.dll'],
        'windows_arm64': ['libs/windows/x64/*.dll'],
        'darwin_x64': ['libs/darwin/*.dylib'],
        'darwin_arm64': ['libs/darwin/*.dylib'],
        'linux_x64': ['libs/linux/x64/*.so'],
        'linux_arm64': ['libs/linux/arm64/*.so']
    }
    
    if target_platform not in platform_mapping:
        return []
    
    return platform_mapping[target_platform]

# Read long description from README.md
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

# Get target platform and package data
target_platform = get_target_platform()
package_data_patterns = get_platform_package_data(target_platform)

setup(
    name='traa',
    version='0.1.4',
    description='Python bindings for the TRAA library',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='opentraa',
    author_email='peilinok@gmail.com',
    url='https://github.com/opentraa/traa-py',
    packages=find_packages(),
    package_data={
        'traa': package_data_patterns,
    },
    include_package_data=True,
    cmdclass={
        'bdist_wheel': PlatformSpecificWheel,
    },
    python_requires='>=3.7',
    platforms=['Windows', 'Linux', 'macOS'],
    install_requires=[
        'numpy>=1.16.0',
    ],
    extras_require={
        'dev': [
            'pytest>=6.0.0',
            'pytest-cov>=2.0.0',
            'black>=21.0.0',
            'isort>=5.0.0',
            'flake8>=3.9.0',
            'wheel>=0.37.0',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
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
