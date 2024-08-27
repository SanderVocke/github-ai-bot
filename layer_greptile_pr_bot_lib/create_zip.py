#!/usr/bin/env python3

import os
import shutil
import subprocess
import zipfile
import tempfile
import sys
import glob

import os
script_dir = os.path.dirname(os.path.abspath(__file__))

def zip_up(lambda_dir, output_zip):
    """Zip the lambda function directory."""
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(lambda_dir):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, lambda_dir))

def create_zip():
    # Use a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        install_dir = temp_dir + "/install"
        # Install lib and dependencies in the folder
        print("Building and installing library...")
        with tempfile.TemporaryDirectory() as venv_dir:
            subprocess.check_call([sys.executable, '-m', 'pip',
                                    "install", "-r", script_dir + '/build_requirements.txt'])

            # Build wheel
            subprocess.check_call([sys.executable, '-m', 'build', '--wheel', '--outdir', 'dist', script_dir],
                                   cwd=temp_dir)

            # Install
            subprocess.check_call([sys.executable, '-m', 'venv', venv_dir])
            venv_python = venv_dir + '/bin/python'
            wheel = glob.glob(f'{temp_dir}/dist/*.whl')[0]
            subprocess.check_call([venv_python, '-m', 'pip', 'install', wheel])

            os.makedirs(install_dir + "/python")
            shutil.copytree(venv_dir + "/lib", install_dir + "/python/lib", dirs_exist_ok=True)

        # Zip the directory into a package
        output_zip = os.path.basename(script_dir) + '.zip'
        print(f"Zipping files into {output_zip}...")
        zip_up(install_dir, output_zip)

        print(f"Package {output_zip} created successfully.")

if __name__ == "__main__":
    create_zip()
