#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== TRAA Installation Test ===${NC}"

# Create a temporary virtual environment
echo -e "\n${GREEN}Creating virtual environment...${NC}"
python -m venv test_venv
source test_venv/bin/activate

# Install build dependencies
echo -e "\n${GREEN}Installing build dependencies...${NC}"
pip install --upgrade pip wheel setuptools

# Test development installation
echo -e "\n${GREEN}Testing development installation...${NC}"
pip install -e .
python tools/test_install.py
pip uninstall -y traa

# Clean build artifacts
echo -e "\n${GREEN}Cleaning build artifacts...${NC}"
rm -rf build/ dist/ *.egg-info/

# Test regular installation
echo -e "\n${GREEN}Testing regular installation...${NC}"
pip install .
python tools/test_install.py

# Clean up
echo -e "\n${GREEN}Cleaning up...${NC}"
deactivate
rm -rf test_venv/

echo -e "\n${GREEN}Installation tests completed!${NC}" 