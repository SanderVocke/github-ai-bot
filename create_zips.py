#!/usr/bin/env python3

import os
import shutil
import subprocess
import zipfile
import tempfile
import sys

from function_pr_from_patch.create_zip import create_zip as create_zip_pr_from_patch
from layer_github_ai_bot_lib.create_zip import create_zip as create_zip_layer_github_ai_bot_lib

def main():
    create_zip_pr_from_patch()
    create_zip_layer_github_ai_bot_lib()

if __name__ == "__main__":
    main()
