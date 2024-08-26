import os
import shutil
import subprocess
import zipfile

# Configuration
LAMBDA_FUNCTION_DIR = 'function'  # Directory where your lambda function code is located
OUTPUT_ZIP = 'lambda_function.zip'       # Name of the output ZIP file
REQUIREMENTS_FILE = 'requirements.txt'   # Name of the requirements file

def create_virtualenv(env_dir):
    """Create a virtual environment."""
    subprocess.check_call(['python3', '-m', 'venv', env_dir])

def install_requirements(env_dir):
    """Install the packages listed in the requirements.txt file."""
    pip_path = os.path.join(env_dir, 'bin', 'pip')
    subprocess.check_call([pip_path, 'install', '-r', REQUIREMENTS_FILE])

def copy_files_to_lambda_dir(lambda_dir, env_dir):
    """Copy the necessary files to the lambda function directory."""
    # Copy the site-packages
    site_packages_dir = os.path.join(env_dir, 'lib', 'python3.8', 'site-packages')
    if not os.path.exists(site_packages_dir):  # Some systems might use python3.9
        site_packages_dir = os.path.join(env_dir, 'lib', 'python3.9', 'site-packages')
    shutil.copytree(site_packages_dir, lambda_dir, dirs_exist_ok=True)

    # Copy the lambda function code
    for item in os.listdir('.'):
        if item not in [env_dir, OUTPUT_ZIP, REQUIREMENTS_FILE]:
            s = os.path.join('.', item)
            d = os.path.join(lambda_dir, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)

def zip_lambda_function(lambda_dir, output_zip):
    """Zip the lambda function directory."""
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(lambda_dir):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, lambda_dir))

def clean_up(lambda_dir, env_dir):
    """Clean up the directories created during the process."""
    shutil.rmtree(lambda_dir)
    shutil.rmtree(env_dir)

def main():
    # Directory names
    lambda_dir = 'lambda_package'
    env_dir = 'lambda_env'

    try:
        # Step 1: Create a virtual environment
        print("Creating virtual environment...")
        create_virtualenv(env_dir)

        # Step 2: Install dependencies in the virtual environment
        print("Installing dependencies...")
        install_requirements(env_dir)

        # Step 3: Copy dependencies and lambda function code to a new directory
        print("Copying files...")
        copy_files_to_lambda_dir(lambda_dir, env_dir)

        # Step 4: Zip the directory into a package
        print(f"Zipping files into {OUTPUT_ZIP}...")
        zip_lambda_function(lambda_dir, OUTPUT_ZIP)

        print(f"Package {OUTPUT_ZIP} created successfully.")

    finally:
        # Clean up temporary directories
        print("Cleaning up...")
        clean_up(lambda_dir, env_dir)
        print("Done.")

if __name__ == "__main__":
    main()
