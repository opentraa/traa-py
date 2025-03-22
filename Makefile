.PHONY: clean build publish publish-staging

clean:
	rm -rf dist
	rm -rf build
	rm -rf traa.egg-info

build: clean
	sh build_all.sh

# Prepare .pypirc for release
prepare-release:
	cp ~/.pypirc.release ~/.pypirc
	@echo "Using ~/.pypirc.release for release"

# Prepare .pypirc for staging
prepare-staging:
	cp ~/.pypirc.test ~/.pypirc
	@echo "Using ~/.pypirc.test for staging"

# Publish to main PyPI
publish: build prepare-release
	twine upload dist/*

# Publish to TestPyPI
publish-staging: build prepare-staging
	twine upload --repository testpypi dist/*

help:
	@echo "Available targets:"
	@echo "  clean         - Remove all build artifacts"
	@echo "  build         - Clean and build the package"
	@echo "  publish       - Build and publish to PyPI"
	@echo "  publish-staging - Build and publish to TestPyPI"
	@echo "  help          - Show this help message"
