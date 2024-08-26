import os
import shutil
import subprocess
import zipfile
import tempfile

# Configuration
LAMBDA_FUNCTION_DIR = 'function'  # Directory where your lambda function code is located
OUTPUT_ZIP = 'lambda_function.zip'       # Name of the output ZIP file
REQUIREMENTS_FILE = 'requirements.txt'   # Name of the requirements file

def create_virtualenv(env_dir):
    """Create a virtual environment."""
    subprocess.check_call(['python3', '-m', 'venv', env_dir])

def install_requirements(into_dir):
    """Install the packages listed in the requirements.txt file."""
    subprocess.check_call([
        'python',
        '-m', 'pip', 'install',
        '-r', REQUIREMENTS_FILE,
        '-t', into_dir
        ])

def copy_files_to_lambda_dir(lambda_dir):
    """Copy the necessary files to the lambda function directory."""
    shutil.copytree(LAMBDA_FUNCTION_DIR, lambda_dir, dirs_exist_ok=True)

def zip_lambda_function(lambda_dir, output_zip):
    """Zip the lambda function directory."""
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(lambda_dir):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, lambda_dir))

def main():
    # Use a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:

        # Install dependencies in the folder
        print("Installing dependencies...")
        install_requirements(temp_dir)

        # Copy dependencies and lambda function code to the lambda function directory
        print("Copying files...")
        copy_files_to_lambda_dir(temp_dir)

        # Step 4: Zip the directory into a package
        print(f"Zipping files into {OUTPUT_ZIP}...")
        zip_lambda_function(temp_dir, OUTPUT_ZIP)

        print(f"Package {OUTPUT_ZIP} created successfully.")

if __name__ == "__main__":
    main()
