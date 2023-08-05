#!/usr/bin/env python3

import os
import venv

if __name__ == '__main__':
    # Directory where the virtual environment should be created.
    venv_dir = '.venv'

    if not os.path.isdir(venv_dir):
        # Create a virtual environment in the specified directory.
        venv.create(venv_dir, with_pip=True)
        print(f'Virtual environment created in "{venv_dir}".')
    else:
        print(f'Virtual environment already exists in "{venv_dir}".')

    print(
        'To activate the virtual environment, '
        f'run ". {venv_dir}/bin/activate" (Unix/macOS)'
        f' or "source {venv_dir}/Scripts/activate" (Windows).'
    )
