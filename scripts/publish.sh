#!/bin/bash
set -e

pushd ..

rm -rf dist
rm -rf build
rm -rf traa.egg-info

sh build_all.sh

twine upload dist/*

popd
