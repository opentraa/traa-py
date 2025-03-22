#!/bin/bash
set -e

pushd ..

rm -rf dist
rm -rf build
rm -rf traa.egg-info

sh build_all.sh

twine upload dist/*

twine upload --repository testpypi dist/* 

popd

# how to download from testpypi
# pip install --index-url https://test.pypi.org/simple/ --no-deps traa -v --trusted-host test.pypi.org
