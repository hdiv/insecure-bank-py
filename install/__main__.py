#!/usr/bin/env python3

# Set up environment to run this Python project


import os.path
import subprocess
import sys

# Directory where the virtual environment is located.
venv_dir = '.venv'

# Ensure the virtual environment exists.
if not os.path.isdir(venv_dir):
    subprocess.run(['python', './install/create_venv.py'])


# Install project dependencies.
print('Installing project dependencies...')
if '--dev' in sys.argv:
    subprocess.run(['python', './install/install_dependencies.py', '--dev'])
else:
    subprocess.run(['python', './install/install_dependencies.py'])
