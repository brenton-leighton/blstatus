#!/usr/bin/env bash

# Directory for this script
SCRIPT_DIR=$(dirname $(realpath "$0"))

# Check that required APT packages are installed
PACKAGES=("python3-dev" "python3-pip" "python3-venv" "libcairo2-dev" "libgirepository1.0-dev")

for PACKAGE in ${PACKAGES[@]}; do
  dpkg -s $PACKAGE 1> /dev/null 2> /dev/null
  if [ $? != 0 ]; then
    echo "Package ${PACKAGE} not found"
    exit
  fi
done

# Create a virtual environment
python3 -m venv ${SCRIPT_DIR}/.venv

# Activate the virtual environment
source ${SCRIPT_DIR}/.venv/bin/activate

# Install Python packages
pip3 install -r ${SCRIPT_DIR}/requirements.txt
