#!/usr/bin/env python3

import os
import shutil
import subprocess
import zipfile
import tempfile
import sys

from function_create_pr.create_zip import create_zip as create_zip_create_pr
from layer_greptile_pr_bot_lib.create_zip import create_zip as create_zip_layer_greptile_pr_bot_lib

def main():
    create_zip_create_pr()
    create_zip_layer_greptile_pr_bot_lib()

if __name__ == "__main__":
    main()
