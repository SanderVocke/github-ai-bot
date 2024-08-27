#!/usr/bin/env python3

import os
import shutil
import subprocess
import zipfile
import tempfile
import sys

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
        # Copy dependencies and lambda function code to the lambda function directory
        print("Copying files...")
        shutil.copytree(script_dir, temp_dir, dirs_exist_ok=True)

        # Step 4: Zip the directory into a package
        output_zip = os.path.basename(script_dir) + '.zip'
        print(f"Zipping files into {output_zip}...")
        zip_up(temp_dir, output_zip)

        print(f"Package {output_zip} created successfully.")

if __name__ == "__main__":
    create_zip()
