#!/usr/bin/env python3

import os
import shutil
import subprocess
import zipfile
import tempfile

DIRS = [
    'python-dynamodb-pydeps',
    'create-pr',
]

def zip_up(lambda_dir, output_zip):
    """Zip the lambda function directory."""
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(lambda_dir):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, lambda_dir))

def create_zip(directory):
    # Use a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Install dependencies in the folder
        if os.path.exists(directory + "/requirements.txt"):
            print("Installing layer dependencies...")
            with tempfile.TemporaryDirectory() as venv_dir:
                subprocess.check_call(['python', '-m', 'venv', venv_dir])
                subprocess.check_call([venv_dir + '/bin/python', '-m', 'pip',
                                       "install", "-r", directory + '/requirements.txt'])
                os.makedirs(temp_dir + "/python")
                shutil.copytree(venv_dir + "/lib", temp_dir + "/python/lib", dirs_exist_ok=True)

        # Copy dependencies and lambda function code to the lambda function directory
        print("Copying files...")
        shutil.copytree(directory, temp_dir, dirs_exist_ok=True)

        # Step 4: Zip the directory into a package
        output_zip = directory + '.zip'
        print(f"Zipping files into {output_zip}...")
        zip_up(temp_dir, output_zip)

        print(f"Package {output_zip} created successfully.")

def main():
    for d in DIRS:
        create_zip(d)

if __name__ == "__main__":
    main()
